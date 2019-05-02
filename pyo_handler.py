import pyo

"""
This class is responsible for creating a PYO server
and manipulating the PYO commands that actually create the sound
"""


class PyoHandler:
    def __init__(self):
        # start the pyo server with the following parameters
        self.s = pyo.Server(sr=48000, nchnls=2, buffersize=512, duplex=0, winhost="asio").boot()
        self.s.start()
        # each synth is a sin sound wave
        #self.synth = pyo.SuperSaw()
        self.synth = pyo.Sine()
        self.synth2 = pyo.Sine(.2, mul=0.5, add=0.5).out(2)
        self.synth3 = pyo.Sine(.2, mul=0.5, add=0.5).out(3)
        #self.synth4 = pyo.Sine(.2, mul=0.5, add=0.5).out(4)
        self.synth4 = pyo.SuperSaw()

    def change_pyo(self, fr, bal, mul):
        # change the pyo parameters:
        # fr = frequency
        # mul = volume
        fr = fr*fr/600
        # start the first sound wave
        self.synth.out(1)
        self.synth.setFreq(fr)
        self.synth.setMul(mul)
        # adding more sin waves for the Y axis
        self.synth2.setFreq(fr * 15 / 3)
        self.synth3.setFreq(fr * 1.25)
        self.synth4.setFreq(fr * 7 / 2)
        # changing the amplitude of the waves according to position in Y axis
        self.synth2.setMul(mul*bal)
        self.synth3.setMul(mul*bal)
        self.synth4.setMul(mul*bal)