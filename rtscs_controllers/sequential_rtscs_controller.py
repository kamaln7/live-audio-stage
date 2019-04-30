import threading
import time
from rtscs_controllers.base_rtscs_controller import BaseRtscsController
from pyo_handler import PyoHandler


class SequentialRtscsController(BaseRtscsController):
    """
    A concrete class derived form BaseRtscsController.
    Implements the general system flow suggested in BaseRtscsController in an uninterpretable manner,
    meaning it will always complete the flow, and will never break it in the middle.
    """
    def __init__(self, param_receiver,):
        super(SequentialRtscsController, self).__init__(param_receiver,
                                                        None, None)
        self._last_sustain_status = False
        self._is_shutdown_request = False
        self._shutdown_lock = threading.Lock()

    def start_system(self):
        # get an instance of PyoHandler which controls the sounds created by the system
        a = PyoHandler()
        while not self._is_shutdown_requested():
            # get rtscs params form BaseRtscsParamReceiver
            transposition, vel_shift, tempo_factor, hint, is_sustain = self._param_receiver.get_rtscs_params()
            PyoHandler.change_pyo(a, transposition, vel_shift, tempo_factor)
            # sleep for duration of msg.time between msgs
            time.sleep(0.05)



    def shutdown_system(self):
        self._shutdown_lock.acquire()
        self._is_shutdown_request = True
        self._shutdown_lock.release()
        super(SequentialRtscsController, self).shutdown_system()

    def _is_shutdown_requested(self):
        self._shutdown_lock.acquire()
        is_shutdown_requested = self._is_shutdown_request
        self._shutdown_lock.release()
        return is_shutdown_requested


