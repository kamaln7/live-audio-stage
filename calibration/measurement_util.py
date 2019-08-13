"""
This script is part of the calibration flow.
While it runs, it maps the room and calculates the boundaries of the 3D space that the Motive system can track.
It outputs the value ranges of each axis (mininum, maximum) in a format that can be directly copied
to config.py.
"""
#from tabulate import tabulate
import time
import math
from utils import make_motive_sock, read_motive_packet
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
    sock = make_motive_sock()
    while True:
        packet = read_motive_packet(sock)
        # print packet
        rh = optirx_utils.get_first_rigid_body(packet)

        if rh is not None:
            # mul by -1 to fix flipped coordinates if not fully compatible Motive calibration square
            rh_position = list(rh.position)
            rh_position[0] = -rh_position[0]
            # rh_position = map(lambda coordinate: -1 * coordinate, rh.position)
            rh_roll = math.degrees(
                optirx_utils.orientation2radians(rh.orientation)[0])

            currentNumbers = rh_position + [rh_roll]
            for method in ["min", "max"]:
                for idx, value in enumerate(currentNumbers, start=0):
                    totalNumbers[method][idx] = fns[method](
                        totalNumbers[method][idx], value)

            print '\n' * 20
            # print tabulate([totalNumbers["min"], totalNumbers["max"],
            #                currentNumbers], headers=["x", "y", "z", "roll"])
            print """
AXIS_RANGES = {
    'x': (%0.3f, %0.3f),
    'y': (%0.3f, %0.3f),
    'z': (%0.3f, %0.3f),
    'roll': (-180, 180)
}""" % (totalNumbers["min"][0], totalNumbers["max"][0],
                totalNumbers["min"][1], totalNumbers["max"][1],
                totalNumbers["min"][2], totalNumbers["max"][2])
            time.sleep(0.05)
