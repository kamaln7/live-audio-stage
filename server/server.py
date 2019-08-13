import optirx as rx
import optirx_utils
import eventlet
import math
from oscpy.client import OSCClient
from utils import clip_value, remap_range, make_motive_sock, read_motive_packet, three_dim_dist
from config import motiveConfig, abletonMaxConfig, AXIS_RANGES
import json

eventlet.monkey_patch(all=True)

max_udp_client = OSCClient(abletonMaxConfig['ip'], abletonMaxConfig['port'])


def send_udp(message):
    max_udp_client.send_message("/", message)


def axis_length(axis):
    values = AXIS_RANGES[axis]
    return abs(values[1] - values[0])


def axis_midpoint(axis):
    values = AXIS_RANGES[axis]
    return (values[1] + values[0]) / 2


def get_zero_bounding_rect():
    offsets = {}
    for axis in ["x", "y", "z"]:
        length = axis_length(axis)
        midpoint = axis_midpoint(axis)
        offset = length * 0.15
        print "[zero] axis=%s offset=%f length=%f" % (axis, offset, length)
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


def remap_and_clip(source_low, source_high, destination_low, destination_high, value):
    # clip Optritrack param to the limits of its defined valid range
    value = clip_value(value, source_low, source_high)
    # translate Optritrack param to rtscs param
    value = remap_range(value,
                        source_low, source_high,
                        destination_low, destination_high)

    return value


def remap_value_of_axis_range(axis, destination_low, destination_high, value):
    source_low = AXIS_RANGES[axis][0]
    source_high = AXIS_RANGES[axis][1]

    return remap_and_clip(source_low, source_high, destination_low, destination_high, value)


def zero_range_params(p):
    if inside_zero_rect(p):
        #print "inside"
        return [0.0, 0.0, 0.0]

    return p


def get_rtscs_params_body(rh):
    """
    Get input from the OptiTrack system streaming engine, transform the data to rtscs_params and return it.
    """
    if rh is None or rh.mrk_mean_error == 0:
        return 0, 0, 0, 0

    # mul by -1 to fix flipped coordinates if not fully compatible Motive calibration square
    # map(lambda coordinate: -1 * coordinate, rh.position)
    rh_position = list(rh.position)
    # Convert right hand convention to left hand convention for Motive 1.73+ used with CS-200
    rh_position[0] = -rh_position[0]
    # For convenience convert roll angle from radians to degrees
    rh_roll = math.degrees(optirx_utils.orientation2radians(rh.orientation)[0])

    rh_position = zero_range_params(rh_position)

    return rh_position + [rh_roll]


udp_msg_to_send = None
xAxisLength = axis_length("x")/2
zAxisMidpoint = axis_midpoint("z")
distMax = three_dim_dist(
    AXIS_RANGES['x'][0], AXIS_RANGES['y'][0], AXIS_RANGES['z'][0],
    AXIS_RANGES['x'][1], AXIS_RANGES['y'][1], AXIS_RANGES['z'][1]
)


def get_optirx_data():
    sock = make_motive_sock()
    while True:
        packet = read_motive_packet(sock)
        bodies = optirx_utils.get_all_rigid_bodies(packet)
        if len(bodies) == 0:
            continue

        b1 = bodies[0]
        b2 = bodies[1]
        if b1 is not None and b2 is not None:
            params1 = get_rtscs_params_body(b1)
            params2 = get_rtscs_params_body(b2)

            if params1 != (0, 0, 0, 0) and params2 != (0, 0, 0, 0):
                body_dist = three_dim_dist(
                    params1[0], params1[1], params1[2],
                    params2[0], params2[1], params2[2]
                )

                berlinPos = params1[2]
                if params1[0] > params2[0]:
                    body_dist = -body_dist

                msg = [json.dumps({
                    'drumVolume': remap_value_of_axis_range("y", 0.10, 0.8, params1[1]),
                    'groupCVolume': remap_value_of_axis_range("y", 0.10, 0.8, params2[1]),
                    'tempo': int(remap_and_clip(-distMax, distMax, 60, 132, body_dist)),
                    'berlin': remap_and_clip(zAxisMidpoint, AXIS_RANGES['z'][1]*2, 0, 0.5, berlinPos)
                })]

                global udp_msg_to_send
                udp_msg_to_send = msg


def send_udp_interval():
    while True:
        global udp_msg_to_send
        if udp_msg_to_send != None:
            print "sending %s" % udp_msg_to_send
            send_udp(udp_msg_to_send)
            udp_msg_to_send = None

        eventlet.sleep(0.05)


eventlet.spawn(send_udp_interval)
t_data = eventlet.spawn(get_optirx_data)


t_data.wait()
