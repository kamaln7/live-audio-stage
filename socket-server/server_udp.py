import optirx as rx
import optirx_utils
import eventlet
import math
from oscpy.client import OSCClient
from utils import clip_value, remap_range, round_to_precision
import json

eventlet.monkey_patch()

UDP_IP = "192.168.43.186"
UDP_PORT = 5000

max_udp_client = OSCClient(UDP_IP, UDP_PORT)
def send_udp(message):
    max_udp_client.send_message("/", message)

DEFAULT_NOTE_DURATION_PRECISION = 0.125
# rh roll implemented for future use
AXIS_RANGES = {
    'x': (-1.286, 0.863),
    'y': (-1.132, 1.059),
    'z': (-0.979, 0.803),
    'roll': (-180, 180)
}
MAP_RANGES = {
    'x': (75, 170),
    'y': (0, 100),
    'z': (-55, 0),
    'roll': (0, 1)
}

def get_zero_bounding_rect():
    def axis_length(axis):
        values = AXIS_RANGES[axis]
        return abs(values[1] - values[0])


    def axis_midpoint(axis):
        values = AXIS_RANGES[axis]
        return (values[1] + values[0]) / 2

    offsets = {}
    for axis in ["x", "y", "z"]:
        length = axis_length(axis)
        midpoint = axis_midpoint(axis)
        offset = length * 0.1
        offsets[axis] = (midpoint - offset, midpoint + offset)

    return offsets

ZERO_BOUNDING_RECT = get_zero_bounding_rect()
print(ZERO_BOUNDING_RECT)

def inside_zero_rect(p):
    for i, axis in enumerate(["x", "y", "z"]):
        rect = ZERO_BOUNDING_RECT[axis]
        if p[i] < rect[0] or p[i] > rect[1]:
            return False

    return True

def transform_params(position, roll):
    """
    Transforms OptiTrack params into rtscs params
    :param position: a (x, y, z) tuple holding the position of the right hand "rigid body"
    :param roll: roll angle in degrees of the right hand "rigid body"
    :return: rtscs params tuple as defined in BaseRtscsParamReceiver.get_rtscs_params()
    """
    transformed_params = position + [roll]

    # Remap rh position onto rtscs internal ranges
    # x -> frequency
    # y -> number of waves which define the complex wave.
    # z -> amplitude.

    for i, n in enumerate(["x", "y", "z", "roll"]):
        source_low = AXIS_RANGES[n][0]
        source_high = AXIS_RANGES[n][1]
        destination_low = MAP_RANGES[n][0]
        destination_high = MAP_RANGES[n][1]

        # clip Optritrack param to the limits of its defined valid range
        transformed_params[i] = clip_value(transformed_params[i],
                                           source_low, source_high)
        # translate Optritrack param to rtscs param
        transformed_params[i] = remap_range(transformed_params[i],
                                            source_low, source_high,
                                            destination_low, destination_high)

    return transformed_params

def zero_range_params(p):
    if inside_zero_rect(p):
        print 'inside'
        return [0, 0, 0]

    return p

def get_rtscs_params_body(rh):
    """
    Get input from the OptiTrack system streaming engine, transform the data to rtscs_params and return it.
    """
    if rh is None or rh.mrk_mean_error == 0:
        return 0, 0, 0, 0

    # mul by -1 to fix flipped coordinates if not fully compatible Motive calibration square
    rh_position = list(rh.position)  # map(lambda coordinate: -1 * coordinate, rh.position)
    # Convert right hand convention to left hand convention for Motive 1.73+ used with CS-200
    # rh_position[0] = -rh_position[0]
    # For convenience convert roll angle from radians to degrees
    rh_roll = math.degrees(optirx_utils.orientation2radians(rh.orientation)[0])

    rh_position = zero_range_params(rh_position)
    print(rh_position)

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
            if params != (0, 0, 0, 0):
                print(params)
                msg = [json.dumps({
                    'tempo': params[0],
                    'senda': params[1],
                    'mastervol': params[2],
                })]
                send_udp(msg)
                #print(msg)
                eventlet.sleep(0.1)

t_data = eventlet.spawn(get_optirx_data)
t_data.wait()