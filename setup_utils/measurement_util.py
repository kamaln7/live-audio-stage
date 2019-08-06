"""
A utility to help determine the desired bounding box of the space in which the system operator will be working,
and the extreme angles of rotation that the operator hand can be held and at which it is still detected by the cameras.
"""
from tabulate import tabulate
import time
import math
from rtscs_param_receivers.optitrack_param_receiver.optitrack_packet_receiver import OptitrackPacketReceiver
import optirx_utils
import sys

minint = -sys.maxint - 1
maxint = sys.maxint

fns = {
    "min": min,
    "max": max,
}
totalNumbers = {
    "max": [minint, minint, minint, minint],
    "min": [maxint, maxint, maxint, maxint],
}

if __name__ == '__main__':
    optritrack_packet_recv = OptitrackPacketReceiver('127.0.0.1')  # adjust OptriTrack server IP if needed
    optritrack_packet_recv.start()
    while True:
        packet = optritrack_packet_recv.get_last_packet()
        #print packet
        rh = optirx_utils.get_first_rigid_body(packet)

        if rh is not None:
            # mul by -1 to fix flipped coordinates if not fully compatible Motive calibration square
            rh_position = rh.position
            #rh_position = map(lambda coordinate: -1 * coordinate, rh.position)
            rh_roll = math.degrees(optirx_utils.orientation2radians(rh.orientation)[0])

            currentNumbers = list(rh_position) + [rh_roll]
            for method in ["min", "max"]:
                for idx, value in enumerate(currentNumbers, start=0):
                    totalNumbers[method][idx] = fns[method](totalNumbers[method][idx], value)

            print '\n' * 20
            #print tabulate([totalNumbers["min"], totalNumbers["max"], currentNumbers], headers=["x", "y", "z", "roll"])
            print """
AXIS_RANGES = {
    'x': (%0.3f, %0.3f),
    'y': (%0.3f, %0.3f),
    'z': (%0.3f, %0.3f),
    'rh_roll': (-180, 180)
}""" % (
                        totalNumbers["min"][0], totalNumbers["max"][0],
                        totalNumbers["min"][1], totalNumbers["max"][1],
                        totalNumbers["min"][2], totalNumbers["max"][2],
                        totalNumbers["min"][3], totalNumbers["max"][3]
                    )
            time.sleep(0.05)
