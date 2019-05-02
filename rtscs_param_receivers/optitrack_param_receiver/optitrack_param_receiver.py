import time
import math
from rtscs_param_receivers.base_rtscs_param_receiver import BaseRtscsParamReceiver
from optitrack_packet_receiver import OptitrackPacketReceiver
from utils import clip_value, remap_range, round_to_precision, dicts_have_same_keys
import optirx_utils

DEFAULT_NOTE_DURATION_PRECISION = 0.125
# rh roll implemented for future use
DEFAULT_OPTITRACK_RANGES_DICT = {'x': (-2, 1.8), 'y': (0.0, 3.0), 'z': (-1.9, 2), 'rh_roll': (-180, 180)}
DEFAULT_RTSCS_PARAM_RANGES_DICT = {'frequency': (0, 700), 'sins': (0, 0.45),
                                   'amplitude': (0.1, 1), 'numerical_hint': (0, 1)}


class OptitrackParamReceiver(BaseRtscsParamReceiver):
    """
    A concrete class derived form BaseRtscsParamReceiver.
    When requested, takes the last packet received from the OptiTrack server and transforms the
    data it carries regrading objects in space into rtscs params.
    Please consult the RTSMCS setup guide to get a better understanding of how to use OptitrackParamReceiver.
    For the right hand "rigid body", the transformation is as follows:
    - X coordinate is remapped to frequency
    - Y coordinate is remapped to Number of sine waves
    - Z coordinate is remapped to Amplitude

    """
    def __init__(self, server_ip_address,
                 optitrx_valid_ranges_dict=DEFAULT_OPTITRACK_RANGES_DICT,
                 rtscs_valid_ranges_dict=DEFAULT_RTSCS_PARAM_RANGES_DICT,
                 note_duration_precision=DEFAULT_NOTE_DURATION_PRECISION):
        """
        :param server_ip_address: IP address of the OptiTrack server
        :param optitrx_valid_ranges_dict: A dict with ranges of the bounding box of the space in which
                                          the system operator will be working, and the extreme angles of rotation that
                                          the operator's hand can be held and at which it is still
                                          detected by the cameras.
                                          The dict is to be structured as DEFAULT_OPTITRACK_RANGES_DICT.
                                          Bounds can be measured using "measurement_util.py" in setup_utils
        :param rtscs_valid_ranges_dict:   A dict with desired ranges of rtscs params.
                                          The dict is to be structured as DEFAULT_RTSCS_PARAM_RANGES_DICT.
        :param note_duration_precision:   duration_factor precision to be rounded to
        """
        self._optirx_valid_ranges_dict = optitrx_valid_ranges_dict
        self._rtscs_valid_ranges_dict = rtscs_valid_ranges_dict
        self._validate_user_dict_keys()
        self._note_duration_precision = note_duration_precision
        # Thread that continuously collects data from OptiTrack streaming engine
        self._optirx_packet_receiver = OptitrackPacketReceiver(server_ip_address)
        self._optirx_packet_receiver.start()

    def _validate_user_dict_keys(self):
        """
        Check that the users ranges dict are structured correctly.
        """
        if not dicts_have_same_keys(self._optirx_valid_ranges_dict, DEFAULT_OPTITRACK_RANGES_DICT):
            raise ValueError('The keys of optirx_valid_ranges_dict are invalid')
        if not dicts_have_same_keys(self._rtscs_valid_ranges_dict, DEFAULT_RTSCS_PARAM_RANGES_DICT):
            raise ValueError('The keys of _rtscs_valid_ranges_dict are invalid')

    def transform_params(self, rh_position, rh_roll, lh_position=None):
        """
        Transforms OptiTrack params into rtscs params
        :param rh_position: a (x, y, z) tuple holding the position of the right hand "rigid body"
        :param rh_roll: roll angle in degrees of the right hand "rigid body"
        :param lh_position: a (x, y, z) tuple holding the position of the left hand "rigid body"
        :return: rtscs params tuple as defined in BaseRtscsParamReceiver.get_rtscs_params()
        """
        is_sustain = False  # TODO: derive is_sustain from distance between rh_position and lh_position
        transformed_params = rh_position + [rh_roll, is_sustain]

        # Remap rh position onto rtscs internal ranges
        # x -> frequency
        # y -> number of waves which define the complex wave.
        # z -> amplitude.

        for i, mapped_pair in enumerate((('x', 'frequency'), ('y', 'sins'),
                               ('z', 'amplitude'), ('rh_roll', 'numerical_hint'))):
            source_low = self._optirx_valid_ranges_dict[mapped_pair[0]][0]
            source_high = self._optirx_valid_ranges_dict[mapped_pair[0]][1]
            destination_low = DEFAULT_RTSCS_PARAM_RANGES_DICT[mapped_pair[1]][0]
            destination_high = DEFAULT_RTSCS_PARAM_RANGES_DICT[mapped_pair[1]][1]

            # clip Optritrack param to the limits of its defined valid range
            transformed_params[i] = clip_value(transformed_params[i],
                                            source_low, source_high)
            # translate Optritrack param to rtscs param
            transformed_params[i] = remap_range(transformed_params[i],
                                             source_low, source_high,
                                             destination_low, destination_high)

        # convert frequency and number of sins to int
        for i in range(1):
            transformed_params[i] = int(round(transformed_params[i]))

        # round amplitude factor to precision
        transformed_params[2] = round_to_precision(transformed_params[2], DEFAULT_NOTE_DURATION_PRECISION)

        return transformed_params

    def get_rtscs_params_body(self, rh):
        """
        Get input from the OptiTrack system streaming engine, transform the data to rtscs_params and return it.
        """
        if rh is None or rh.mrk_mean_error == 0:
            return 0, 0, 1, 0, False

        # mul by -1 to fix flipped coordinates if not fully compatible Motive calibration square
        rh_position = list(rh.position)  # map(lambda coordinate: -1 * coordinate, rh.position)
        # Convert right hand convention to left hand convention for Motive 1.73+ used with CS-200
        rh_position[0] = -rh_position[0]
        # For convenience convert roll angle from radians to degrees
        rh_roll = math.degrees(optirx_utils.orientation2radians(rh.orientation)[0])

        # print rh_position
        # print rh_roll; return

        transformed_params = self.transform_params(rh_position, rh_roll)

        # print transformed_params

        return transformed_params

    def get_rtscs_params(self):
        """
        Get input from the OptiTrack system streaming engine, transform the data to rtscs_params and return it.
        """
        packet = self._optirx_packet_receiver.get_last_packet()
        rh = optirx_utils.get_first_rigid_body(packet)
        if rh is None or rh.mrk_mean_error == 0:
            return 0, 0, 1, 0, False

        # mul by -1 to fix flipped coordinates if not fully compatible Motive calibration square
        rh_position = list(rh.position)  # map(lambda coordinate: -1 * coordinate, rh.position)
        # Convert right hand convention to left hand convention for Motive 1.73+ used with CS-200
        rh_position[0] = -rh_position[0]
        # For convenience convert roll angle from radians to degrees
        rh_roll = math.degrees(optirx_utils.orientation2radians(rh.orientation)[0])

        # print rh_position
        # print rh_roll; return

        transformed_params = self.transform_params(rh_position, rh_roll)

        # print transformed_params

        return transformed_params

    def shutdown_receiver(self):
        self._optirx_packet_receiver.shutdown()


if __name__ == '__main__':
    optirxrec = OptitrackParamReceiver('127.0.0.1')

    while True:
        time.sleep(0.2)
        optirxrec.get_rtscs_params()