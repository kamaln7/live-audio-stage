from config import motiveConfig
import optirx as rx


def make_motive_sock():
    return rx.mkdatasock(ip_address=motiveConfig['ip'],
                         multicast_address=motiveConfig['multicast_address'], port=motiveConfig['port'])


def read_motive_packet(socket):
    data = socket.recv(rx.MAX_PACKETSIZE)
    # parse packet and store it locally
    packet = rx.unpack(data, motiveConfig['natnetsdk_version'])
    if type(packet) is rx.SenderData:
        motiveConfig['natnetsdk_version'] = packet.natnet_version

    return packet


def clip_value(value, lower, upper):
    return max(lower, min(upper, value))


def remap_range(value, range1_from, range1_to, range2_from=0, range2_to=1):
    if range1_from >= range1_to or range2_from >= range2_to:
        raise ValueError(
            'One or more of the given ranges is either an empty range or out of order')

    if value < range1_from or value > range1_to:
        raise ValueError('Value {} is not in given range ({}, {})'.format(
            value, range1_from, range1_to))

    return float(value - range1_from) / (range1_from - range1_to) * (range2_from - range2_to) + range2_from


def round_to_precision(number, precision):
    return round(number * 1.0 / precision) / (1.0 / precision)


def dicts_have_same_keys(dict1, dict2):
    return (set(dict1.keys()) - set(dict2.keys())) == set([])


def display_shutdown_prompt(shutdown_token='q'):
    shutdown_msg = 'Enter "{}" to shutdown the system and end the session:'.format(
        shutdown_token)
    print shutdown_msg
    while raw_input().lower() != shutdown_token:
        print 'Invalid input. ' + shutdown_msg
