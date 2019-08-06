import threading
#from eventlet.green import threading
import optirx as rx

DEFAULT_MULTICAST_ADDRESS = '239.255.42.99'
DEFAULT_DATA_PORT = 1511
DEFAULT_NATNETSDK_VERSION = (2, 8, 0, 0)


class OptitrackPacketReceiver(threading.Thread):
    """
    Responsible for constantly receiving UDP packets form the OptiTrack system, parsing them to optirx objects,
    and storing them locally to make them available when needed.
    The OptitrackPacketReceiver is a separate thread, so it continues receiving UDP packets regardless of the
    activity of the rest of the system.
    """
    def __init__(self, server_ip_addr, natnetsdk_version=DEFAULT_NATNETSDK_VERSION,
                 multicast_addr=DEFAULT_MULTICAST_ADDRESS, data_port=DEFAULT_DATA_PORT):
        super(OptitrackPacketReceiver, self).__init__()
        self._natnetsdk_version = natnetsdk_version
        self._last_packet = None
        self._is_shutdown_request = False
        # open UDP port to Optitrack server
        self._dsock = rx.mkdatasock(ip_address=server_ip_addr, multicast_address=multicast_addr, port=data_port)

    def run(self):
        while not self._is_shutdown_requested():
            # receive UDP data packet from Optitrack server
            data = self._dsock.recv(rx.MAX_PACKETSIZE)
            # parse packet and store it locally
            self._last_packet = rx.unpack(data, self._natnetsdk_version)
            # update natnet sdk version to what Optitrack software says it is
            if type(self._last_packet) is rx.SenderData:
                self._natnetsdk_version = self._last_packet.natnet_version

    def get_last_packet(self):
        """
        Returns the last packet recieved from the OptiTrack system as a optirx object
        """
        last_packet = self._last_packet
        return last_packet

    def _is_shutdown_requested(self):
        is_shutdown_request = self._is_shutdown_request
        return is_shutdown_request

    def shutdown(self):
        self._is_shutdown_request = True
