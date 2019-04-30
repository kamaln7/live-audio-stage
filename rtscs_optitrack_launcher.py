
from rtscs_param_receivers.optitrack_param_receiver.optitrack_param_receiver import OptitrackParamReceiver

from rtscs_controllers.sequential_rtscs_controller import SequentialRtscsController
from rtscs_thread import RtscsThread
from utils import display_shutdown_prompt

def main():
    # Init all system components, and start the system.
    # Receive system params from Optitrack
    # This Should be the client ip address
    pyo_parameters = OptitrackParamReceiver('127.0.0.1')
    #send the parameters to the controller and change the pyoHandler
    pyo_controller = SequentialRtscsController(pyo_parameters)
    #send the parameters from the pyoHandler to a new thread
    pyo_main_thread = RtscsThread(pyo_controller)
    #start the thread
    pyo_main_thread.start()
    display_shutdown_prompt()
    #stop the thread
    pyo_main_thread.shutdown()

if __name__ == '__main__':
    main()
