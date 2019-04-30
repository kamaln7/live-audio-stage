import mido
import abc


class BaseRtscsController(object):
    """
    A base class for the system's controller - the heart of the system, which coordinates the activities of
    all of the system's components.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, param_receiver, midi_adjuster, midi_out_handler):
        self._param_receiver = param_receiver
        self._midi_adjuster = midi_adjuster
        self._midi_out_handler = midi_out_handler

    @abc.abstractmethod
    def start_system(self):
        """
        The definition of the system's flow goes here.
        """
        return

    def shutdown_system(self):
        """
        if overridden super must to be called at the end
        """
        self._param_receiver.shutdown_receiver()
