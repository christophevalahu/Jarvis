from math import pi


class State:

    def __init__(self, name = 'name', header = 'header', freq=0, time=0, amp = 0, dressing_fields = [], mapping_state = '', fields_on = []):
        self.name = name
        self.header = header
        self.freq = freq                                    
        self.time = time
        self.amp = amp
        self.dressing_fields = dressing_fields
        self.fields_on = fields_on
        self.mapping_state = mapping_state
        
        
    def fchan (self, freqdet = 0, freqstep = 0, ampdet = 0, ampstep = 0, phase = 0, phasestep = 0) :
        #Returns dict for AWG channel
        return [{'freq': self.freq + freqdet, 'freq step':freqstep, 
                 'amp':self.amp + ampdet, 'amp step':ampstep, 
                 'phase':phase, 'phase step':phasestep, 
                 'channel inv':freqstep == 0 and ampstep == 0 and phasestep == 0}]
    
    def fchanGlPhase (self, freqdet = 0, freqstep = 0, ampdet = 0, ampstep = 0, phase = 0, phasestep = 0, elapsed_time = 0) :
        #Returns dict for AWG channel, compensating for a global phase
        
        gl_phase_shift = 2*pi - (elapsed_time * (self.freq + freqdet)) % (2*pi)
        
        return [{'freq': self.freq + freqdet, 'freq step':freqstep, 
                 'amp':self.amp + ampdet, 'amp step':ampstep, 
                 'phase':phase + gl_phase_shift, 'phase step':phasestep, 
                 'channel inv':freqstep == 0 and ampstep == 0 and phasestep == 0}]
    
    def cooling_fchan (self, freqstep = 0) :
        #Returns dict for AWG channel for cooling
        return [{'freq':self.freq, 'freq step':freqstep, 
                 'amp':50, 'amp step':0,
                 'phase':0, 'phase step':0, 
                 'channel inv': True}]
    
'''
from unittest import TestCase

class TestState(TestCase):
    def test_fchan(self):
        pass
    
    def test_cooling_fchan(self, cfc_exp, freqstep):
        state = State()
        cfc = state.cooling_fchan(10)
        
        exp
        
        self.assertDictEqual(cfc, 
'''


"""
class ErrorParams:
    err_pmt = Err()
    err_camera = Err()
    

@attr.ib
class Err:
    t1 = attr.ib()
    t2 = attr.ib()
    errm1 = attr.ib()
    errm2 = attr.ib()
    
ERR_PARAMS = {'err_pmt' :    {'t1' :  config['state_det_pmt'].getint('t1'), 'errm1' : ast.literal_eval(config['state_det_pmt'].get('errm1')),
                              't2' :  config['state_det_pmt'].getint('t2'), 'errm2' : ast.literal_eval(config['state_det_pmt'].get('errm2'))},
              'err_camera' : {'t1' :  config['state_det_camera'].getint('t1'), 'errm1' : ast.literal_eval(config['state_det_camera'].get('errm1')),
                              't2' :  config['state_det_camera'].getint('t2'), 'errm2' : ast.literal_eval(config['state_det_camera'].get('errm2'))}}

err_pmt = ERR(
"""