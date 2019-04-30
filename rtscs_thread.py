import threading


class RtscsThread(threading.Thread):
    def __init__(self, rtscs_controller):
        super(RtscsThread, self).__init__()
        self._rtscs_controller = rtscs_controller

    def run(self):
        #start the system
        self._rtscs_controller.start_system()

    def shutdown(self):
        #stop the system
        self._rtscs_controller.shutdown_system()
