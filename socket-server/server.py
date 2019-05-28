import optirx as rx
import optirx_utils
import eventlet
import socketio
eventlet.monkey_patch()

from utils import clip_value, remap_range, round_to_precision
import math

sio = socketio.Server(cors_allowed_origins=None)
app = socketio.WSGIApp(sio)

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)
    #eventlet.spawn(deb, sio)
    #sio.emit("rh", [1, 2, 3])

@sio.on('my message')
def message(sid, data):
    print('message ', data)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


def start_sio():
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

DEFAULT_NOTE_DURATION_PRECISION = 0.125
# rh roll implemented for future use
DEFAULT_OPTITRACK_RANGES_DICT = {
    'x': (-0.9, 1.5),
    'y': (-2.1, 1.2),
    'z': (-0.1, 1.7),
    'rh_roll': (-180, 180)
}
DEFAULT_RTSCS_PARAM_RANGES_DICT = {
    #'frequency': (0, 700),
    #'sins': (0, 0.45),
    'frequency': (0, 7),
    'sins': (0, 7),
    'amplitude': (5, 200),
    'numerical_hint': (0, 1)
}
def transform_params(rh_position, rh_roll, lh_position=None):
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
        source_low = DEFAULT_OPTITRACK_RANGES_DICT[mapped_pair[0]][0]
        source_high = DEFAULT_OPTITRACK_RANGES_DICT[mapped_pair[0]][1]
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

def get_rtscs_params_body(rh):
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

    return transform_params(rh_position, rh_roll)

def get_optirx_data():
    dsock = rx.mkdatasock(ip_address="127.0.0.1", multicast_address='239.255.42.99', port=1511)
    natnetsdk_version = (2, 8, 0, 0)
    while True:
        data = dsock.recv(rx.MAX_PACKETSIZE)
        # parse packet and store it locally
        packet = rx.unpack(data, natnetsdk_version)
        if type(packet) is rx.SenderData:
            natnetsdk_version = packet.natnet_version
        rh = optirx_utils.get_first_rigid_body(packet)

        if rh is not None:
            params = get_rtscs_params_body(rh)
            print(params)
            sio.emit("rh", params)

eventlet.spawn(start_sio)
t_data = eventlet.spawn(get_optirx_data)
t_data.wait()