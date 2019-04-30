import optirx as rx
from nibabel import eulerangles


def get_first_unlabeled_marker(optirx_packet):
    if type(optirx_packet) is rx.FrameOfData and len(optirx_packet.other_markers) > 0:
        return optirx_packet.other_markers[0]
    return None


def get_first_rigid_body(optirx_packet):
    if type(optirx_packet) is rx.FrameOfData and len(optirx_packet.rigid_bodies) > 0:
        return optirx_packet.rigid_bodies[0]
    return None


def get_rigid_body_by_id(id, optirx_packet):
    if type(optirx_packet) is rx.FrameOfData and len(optirx_packet.rigid_bodies) > 0:
        for body in optirx_packet.rigid_bodies:
            if body.id == id:
                return body
    return None


def orientation2radians(orientation):
    """
    Convert from OptiTracks internal quaternion angle representation of an object's orientation to
    to euler angle representation in radians
    :param orientation: An OptiTrack object object orientation in quaternion angle representation (qx, qy, qz, qw)
    :return: orientation in euler angle representation in radians (roll, yaw, pitch)
    """
    reordered_orientation = (orientation[-1],) + orientation[:-1]  # (qx, qy, qz, qw) -> (qw, qx, qy, qz)
    return eulerangles.quat2euler(reordered_orientation)
