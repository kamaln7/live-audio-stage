import abc


class BaseRtscsParamReceiver(object):
    """
    A base class which defines an interface for getting the system's internal params
    from a human interface device (be it hardware or software).
    Driving classes should be able to take the input from a human interface device, interpret it as they wish
    and convert it to the defined internal system params as defined below in get_rtscs_params().
    The type of the human interface device doesn't matter as long as input data can be collected from it,
    it could be a camera, mouse, joystick or a GUI, or anything else.
    Depending on the scenario, it might be advisable that the derived class would utilize a separate thread/process
    to continuously collect the input data.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_rtscs_params(self):
        """
        Reads the input from the human interface device, converts it to internal rtscs_params and returns it.
        The internal rtscs_params are as follows:
        * frequency
        * amplitude
        * number of sine waves
        :return: (frequency, amplitude, number of sine waves)
        """
        return

    @abc.abstractmethod
    def shutdown_receiver(self):
        """
        Free all threads / other resources used by param receiver.
        If no such resources are used can be implemented as an empty method.
        """
        return
