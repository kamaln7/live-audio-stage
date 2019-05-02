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
        self._next_out = 1
        self.synths = []
        self._make_synths()
        self._make_synths()

    def _get_next_out(self):
        o = self._next_out
        self._next_out += 1

        return o

    def _make_synths(self):
        s = []
        s.append(pyo.Sine().out(self._get_next_out()))
        s.append(pyo.Sine(.2, mul=0.5, add=0.5).out(self._get_next_out()))
        s.append(pyo.Sine(.2, mul=0.5, add=0.5).out(self._get_next_out()))
        # self.synth4 = pyo.Sine(.2, mul=0.5, add=0.5).out(4)
        s.append(pyo.SuperSaw().out(self._get_next_out()))

        self.synths.append(s)

    def change_pyo(self, idx, fr, bal, mul):
        # change the pyo parameters:
        # fr = frequency
        # mul = volume
        fr = fr*fr/600
        # start the first sound wave
        self.synths[idx][0].setFreq(fr)
        self.synths[idx][0].setMul(mul)
        # adding more sin waves for the Y axis
        self.synths[idx][1].setFreq(fr * 7 / 3)
        self.synths[idx][2].setFreq(fr * 1.25)
        self.synths[idx][3].setFreq(fr * 7 / 1.5)
        # changing the amplitude of the waves according to position in Y axis
        self.synths[idx][1].setMul(mul*bal)
        self.synths[idx][2].setMul(mul*bal)
        self.synths[idx][3].setMul(mul*bal)