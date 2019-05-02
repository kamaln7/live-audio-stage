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
        #self.make_beat()
        self._make_synths()
        self._make_synths()

    def _get_next_out(self):
        o = self._next_out
        self._next_out += 1

        return o

    def make_beat(self):
        # Builds an amplitude envelope in a linear table
        env = pyo.LinTable([(0, 0), (190, .8), (1000, .5), (4300, .1), (8191, 0)], size=8192)
        env.graph()

        # Metronome provided by Beat
        met = pyo.Beat(time=.125, taps=16, w1=90, w2=50, w3=30).play()

        # Reads the amp envelope for each trigger from Beat
        amp = pyo.TrigEnv(met, table=env, dur=met['dur'], mul=met['amp'])

        # Generates a midi note for each trigger from Beat in a pseudo-random distribution
        fr = pyo.TrigXnoiseMidi(met, dist=12, x1=1, x2=.3, scale=0, mrange=(48, 85))

        # Receives the midi note from XnoiseMidi and scale it into C harmonic minor (try others!)
        frsnap = pyo.Snap(fr, choice=[0, 2, 3, 5, 7, 8, 11], scale=1)

        # This instrument receives a frequency from Snap and molde it inside an envelop from TrigEnv
        lfo = pyo.Sine(freq=.05, mul=.05, add=.08)
        gen = pyo.SineLoop(freq=frsnap, feedback=lfo, mul=amp * .5).out(0)

        # Output the same signal with some delay in the right speaker (try a 'real' counterpoint!)
        rev = pyo.Delay(gen, delay=[.25, .5], feedback=.3, mul=.8).out(1)

        self.s.gui(locals())

    def _make_synths(self):

        s = []

        #### 1 ####
        # s.append(pyo.Sine().out(self._get_next_out()))
        # s.append(pyo.Sine(.2, mul=0.5, add=0.5).out(self._get_next_out()))
        # s.append(pyo.Sine(.2, mul=0.5, add=0.5).out(self._get_next_out()))
        # # self.synth4 = pyo.Sine(.2, mul=0.5, add=0.5).out(4)
        # s.append(pyo.SuperSaw().out(self._get_next_out()))

        #### 2 ####
        w = pyo.Sine(freq=7).out(self._get_next_out())
        l = pyo.LFO(freq=w, type=2).out(self._get_next_out())
        #sl = pyo.SineLoop(freq=w, feedback=l, mul=1).out(self._get_next_out())
        s.append(w)
        #rev = pyo.Delay(sl, delay=[.25, .5]).out(self._get_next_out())

        self.synths.append(s)

    def change_pyo(self, idx, fr, bal, mul):
        # #### 1 ####
        # # change the pyo parameters:
        # # fr = frequency
        # # mul = volume
        # fr = fr*fr/600
        # # start the first sound wave
        # self.synths[idx][0].setFreq(fr)
        # self.synths[idx][0].setMul(mul)
        # # adding more sin waves for the Y axis
        # self.synths[idx][1].setFreq(fr * 7 / 3)
        # self.synths[idx][2].setFreq(fr * 1.25)
        # self.synths[idx][3].setFreq(fr * 7 / 1.5)
        # # changing the amplitude of the waves according to position in Y axis
        # self.synths[idx][1].setMul(mul*bal)
        # self.synths[idx][2].setMul(mul*bal)
        # self.synths[idx][3].setMul(mul*bal)

        #### 2 ####
        # change the pyo parameters:
        # fr = frequency
        # mul = volume
        fr = fr*fr/600
        # start the first sound wave
        self.synths[idx][0].setFreq(fr)
        self.synths[idx][0].setMul(mul)