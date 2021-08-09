'''
    Author : Christophe Valahu and apprentice
    Last Modified : 15/04/19
    File : pulsesequences.py
    
    Description : Hardware agnostic pulse sequences.

'''

from pulses import (innitPulseList,
                    addParam,
                    addPulse,
                    addRFShapedPulse,
                    addRFPadding,
                    makeSequence,
                    getElapsedTime,
                    resetAWGPhase)

from parameters import *
from math import pi, sqrt, floor
                    

'''
def cameratest() :
    
    innitPulseList()
    
    addPulse('Delay', 200000)
    addPulse('Camera image', 1000, 0, 1, {'dio' : AOM|RF5|CAM})
    
    addParam("steps", 1) 
    addParam("runs", 1)
    addParam("comment", "aux")
    mathparams = {"name" : "aux", "header" :'', "det" : 0, "step" : 0, "state" : '', "freq" : 0, "pitime" : 0, "amp" : 0, "steps" : 1, "runs" : 1, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", 0)
    addParam("logmsg", "Aux sequence with " + 'state')
    
    return makeSequence()
'''

#--------------------------------------------------------------------------------------------------------------------#
# INIT AND READOUT SEQUENCES
#--------------------------------------------------------------------------------------------------------------------# 


def _addReadoutPulse(count = 0) :
    
    addRFPadding(DET_DELAY_TIME + DET_TIME)
    addPulse('DET: delay', DET_DELAY_TIME)
    addPulse('DET: Detection', DET_TIME, 0, count, OPTS_DET)
	   
def _addPrepPulse(count = 0) :
    
    addRFShapedPulse('PREP: Cooling', COOL_TIME, 0, 0, MWOUT, COOLING_FCHAN)
    addRFShapedPulse('RF padding', COOL_TIME, 0, 0, RFOUT, NULL_FCHAN)    
    addPulse('PREP: Cooling', COOL_TIME, 0, count, OPTS_COOLING)
    
    addRFPadding(AO_DELAY_TIME + PREP_TIME) 
    addPulse('PREP: AO delay', AO_DELAY_TIME, 0, opts = OPTS_AO_DELAY)
    addPulse('PREP: Prep', PREP_TIME, 0, 0, OPTS_PREP)
    
def _addLineTrigPulse() :
    
    addRFShapedPulse('Line trig set', 10, 0, 0, MWOUT, COOLING_FCHAN)
    addRFShapedPulse('RF padding', 10, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Line trig set', 10, 0, opts = OPTS_COOLING)
       
def _addSbCoolingPulse(det = 0, step = 0) :
    #On the first SB cooling, do all N motional states.
    #On the rest, do just the first 50, since the nbar shouldn't be higher than 2
    
    cooling_times = SB_COOLING_TIMES
    
    for sb_time in cooling_times:
        addRFShapedPulse('SB COOL : RSB pulse', sb_time, 0, 0, MWOUT, plusred1.fchan(freqdet = det, freqstep = step, ampdet = 0, ampstep = 0))
        addRFShapedPulse('SB COOL : RF padding', sb_time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('SB COOL : ', sb_time, 0, opts = OPTS_SB_COOLING)
        
        addRFPadding(REPUMP_TIME)
        addPulse("SB COOl repump", REPUMP_TIME, 0, opts = OPTS_PREP)
     
    return 0
   
def  auxsequence1(runs = 0, sb_cooling = False) :
    
    innitPulseList()
    
    state = probe
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    if sb_cooling :
        _addSbCoolingPulse()
    
    addRFShapedPulse('Aux pi pulse ' + state.name, state.time, 0, 0, MWOUT, state.fchan())
    addPulse('Aux pi pulse ' + state.name, state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", 1) 
    addParam("runs", runs)
    addParam("comment", "aux")
    mathparams = {"name" : "aux", "header" : state.header, "det" : 0, "step" : 0, "state" : state.name, "freq" : state.freq, 
                  "pitime" : state.time, "amp" : state.amp, "steps" : 1, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", 0)
    addParam("logmsg", "Aux sequence with " + state.name)
    
    return makeSequence()
      
def auxsequence(runs = 0, sb_cooling = False) :

    state = probe
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    addRFShapedPulse('Pi pulse' + state.name, state.time, 0, 0, MWOUT, state.fchan())  
    addPulse('Pi pulse ' + state.name, state.time, 0, opts = OPTS_AWG_MW_PULSE)    

    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", 1) 
    addParam("runs", runs)
    addParam("comment", "aux")
    mathparams = {"name" : "aux", "header" : state.header, "det" : 0, "step" : 0, "state" : state.name, "freq" : state.freq, 
                  "pitime" : state.time, "amp" : state.amp, "steps" : 1, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", 0)
    addParam("logmsg", "Aux sequence with " + state.name)
    
    
    return makeSequence()
    
def addDelayPulse(time = 0) :
        addRFPadding(time)
        addPulse('Delay', time, 0)

#--------------------------------------------------------------------------------------------------------------------#
# CALIBRATION PULSE SEQUENCES
#--------------------------------------------------------------------------------------------------------------------#  
    
def statedetone(state = "", steps = 0, runs = 0, calib = 0) :
    
    state = eval(state)
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = 1)
    _addPrepPulse()
    
    addRFShapedPulse('Pi pulse on ' + state.name, state.time, 0, 0, MWOUT, state.fchan())
    addPulse('Statedet', state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(count = 2)
    
    
    addParam("steps", 1) 
    addParam("runs", runs)
    addParam("comment", "statedetone")
    mathparams = {"name" : "statedetone", "det" : 0, "step" : 0, "state" : 'state', "freq" : 0, "pitime" : 0, "amp" : 0, 
                  "steps" : 1, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "State det one ion, runs = " + str(runs))
    
    return makeSequence()
       
def statedettwo(steps = 0, runs = 0, sb_cool = False, calib = 0) :

    state1 = clock1
    state2 = clock2
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = 1)
    _addPrepPulse()
    
    if sb_cool:
        _addSbCoolingPulse()
    
    addRFShapedPulse('Pi pulse on ' + state1.name, state1.time, 0, 0, MWOUT, state1.fchan())
    addPulse('Pi pulse ion 1', state1.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(count = 2)
    _addPrepPulse()
    
    addRFShapedPulse('Pi pulse ion 1 and 2', state1.time, 0, 0, MWOUT, state1.fchan())
    addRFShapedPulse('Pi pulse ion 1 and 2', state2.time, 0, 0, MWOUT, state2.fchan())
    addPulse('Pi pulse ion 1 and 2', state1.time + state2.time, 0, opts = OPTS_AWG_MW_PULSE)
    _addReadoutPulse(count = 4)
    
    addParam("steps", 1) 
    addParam("runs", runs)
    addParam("comment", "statedettwo")
    mathparams = {"name" : "statedettwo",  "det" : 0, "step" : 0, "state" : 'state', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : 1, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "State det two ions, runs = " + str(runs))
    
    return makeSequence()
          
def msstatedettwo(steps = 0, runs = 0, sb_cool = False, calib = 0) :

    state1 = clock1
    state2 = clock2
    
    dressing_fields = dressingP1ms.fchan() + dressingP2ms.fchan() \
                    + dressingM1.fchan() + dressingM2.fchan()
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = 1)
    _addPrepPulse()
    
    if sb_cool:
        _addSbCoolingPulse()
    
    #Clock ion 1
    addRFShapedPulse('Pi pulse on ' + state1.name, state1.time, 0, 0, MWOUT, state1.fchan())
    addRFShapedPulse('Padding', state1.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi pulse ion 1', state1.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Pi D1
    addRFShapedPulse('Pi on D1', D1.time, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('Pi on D1', D1.time, 0, 0, RFOUT, D1.fchan())
    addPulse('Pi on D1', D1.time, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    _addReadoutPulse(count = 2)
    _addPrepPulse()
    
    #Clocks 1 and 2
    addRFShapedPulse('Pi pulse ion 1 and 2', state1.time, 0, 0, MWOUT, state1.fchan())
    addRFShapedPulse('Pi pulse ion 1 and 2', state2.time, 0, 0, MWOUT, state2.fchan())
    addRFShapedPulse('Padding', state1.time + state2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi pulse ion 1 and 2', state1.time + state2.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Pi D1 and D2
    addRFShapedPulse('Pi on D1 and D2', D1.time + D2.time, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('Pi on D1', D1.time, 0, 0, RFOUT, D1.fchan())
    addRFShapedPulse('Pi on D2', D2.time, 0, 0, RFOUT, D2.fchan())
    addPulse('Pi on D1 and D2', D1.time + D2.time, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    _addReadoutPulse(count = 4)
    
    addParam("steps", 1) 
    addParam("runs", runs)
    addParam("comment", "statedettwo")
    mathparams = {"name" : "statedettwo",  "det" : 0, "step" : 0, "state" : 'state', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : 1, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "State det two ions, runs = " + str(runs))
    
    return makeSequence()

def statedetmatch(steps = 0, runs = 0) :
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    addRFShapedPulse('Pi pulse on ' + clock1.name, clock1.time, 0, 0, MWOUT, clock1.fchan())
    addPulse('Statedet', clock1.time, 0, opts = OPTS_AWG_MW_PULSE)
    _addReadoutPulse(count = 1)
    
    _addPrepPulse()
    addRFShapedPulse('Pi pulse on ' + clock2.name, clock2.time, 0, 0, MWOUT, clock2.fchan())
    addPulse('Statedet', clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    _addReadoutPulse(count = 2)
    
    addParam("steps", steps) 
    addParam("runs", runs)
    addParam("comment", "statedetmatch")
    mathparams = {"name" : "statedetmatch", "det" : 0, "step" : 0, "state" : '', "freq" : 0, "pitime" : 0, "amp" : 0, 
                  "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("logmsg", "Matching statedet brightness, runs = " + str(runs))
    
    return makeSequence()
  
def freqscan(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0, sb_cool = False, delay = 0) :
        
    state = eval(state)
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
  
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    if sb_cool :
        _addSbCoolingPulse()
    
    if delay != 0 :
        addRFPadding(delay)
        addPulse('delay', delay)
    
    if state.dressing_fields != [] :
        state.dressing_fields = dressingP1.fchan() + dressingM1.fchan()
        #Pi pulse from 0 to clock
        addRFShapedPulse('Pi Clock', state.mapping_state.time, 0, 0, MWOUT, state.mapping_state.fchan() + 
                                                                               state.mapping_state.fields_on)
        addRFShapedPulse('RF padding', state.mapping_state.time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Pi clock', state.mapping_state.time, 0, opts = OPTS_AWG_MW_PULSE)
        
        #Freq scan on dressed state with dressing fields on
        addRFShapedPulse('Freq scan ' + state.name, state.time, 0, 0, MWOUT, state.dressing_fields)
        addRFShapedPulse('Freq scan ' + state.name, state.time, 0, 0, RFOUT, state.fchan(freqdet = det, freqstep = step) + 
                                                                                state.fields_on)
        addPulse('Freq scan ' + state.name, state.time, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #Pi pulse from 0 to clock
        addRFShapedPulse('Pi Clock', state.mapping_state.time, 0, 0, MWOUT, state.mapping_state.fchan() + 
                                                                               state.mapping_state.fields_on)
        addRFShapedPulse('RF padding', state.mapping_state.time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Pi clock', state.mapping_state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    else :
        addRFShapedPulse('Freq scan ' + state.name, state.time, 0, 0, MWOUT, state.fchan(freqdet = det, freqstep = step) + 
                                                                                state.fields_on)  
        addPulse('Freq scan ' + state.name, state.time, 0, opts = OPTS_AWG_MW_PULSE)    
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps) 
    addParam("runs", runs)
    addParam("comment", "freqscan")
    mathparams = {"name" : "freqscan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    if sb_cool :
        addParam("logmsg", "Frequency scan (COLD) on " + state.name + ", det = " + str(det) + ", step = " + str(step))
    else :
        addParam("logmsg", "Frequency scan on " + state.name + ", det = " + str(det) + ", step = " + str(step))
    return makeSequence()
 
def optimizeSBcooling(det = 0, step = 0, steps = 0, runs = 0) :
        
    state = Dblue1
    innitPulseList()
    calib = 0
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    _addSbCoolingPulse(det, step)
    
    #Pi pulse from 0 to clock
    addRFShapedPulse('Pi Clock', state.mapping_state.time, 0, 0, MWOUT, state.mapping_state.fchan() + 
                                                                           state.mapping_state.fields_on)
    addRFShapedPulse('RF padding', state.mapping_state.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', state.mapping_state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Time scan on dressed state with dressing fields on
    addRFShapedPulse('Freq scan ' + state.name, state.time, 0, 0, MWOUT, state.dressing_fields)
    addRFShapedPulse('Freq scan ' + state.name, state.time, 0, 0, RFOUT, state.fchan() + state.fields_on)
    addPulse('Freq scan ' + state.name, state.time, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse from 0 to clock
    addRFShapedPulse('Pi Clock', state.mapping_state.time, 0, 0, MWOUT, state.mapping_state.fchan() + 
                                                                           state.mapping_state.fields_on)
    addRFShapedPulse('RF padding', state.mapping_state.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', state.mapping_state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
   
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps) 
    addParam("runs", runs)
    addParam("comment", "freqscan")
    mathparams = {"name" : "freqscan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "SB cooling optimisation, det = " + str(det) + ", step = " + str(step))
    return makeSequence()
        
def timescan(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0, sb_cool = False) :
        
    if det < 0 :
        det = 0
    
    state = eval(state)
    innitPulseList()
   
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    
    WARMUP_TIME = 50
    addRFShapedPulse('Warm up amplifiers', WARMUP_TIME, 0, 0, MWOUT, state.fchan(freqdet = -1e3) + state.fields_on)  
    addPulse('Warm up amplifiers', WARMUP_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
    
    if sb_cool :
        _addSbCoolingPulse()
    
    if state.dressing_fields != [] :
        #Pi pulse from 0 to clock
        addRFShapedPulse('Pi Clock', state.mapping_state.time, 0, 0, MWOUT, state.mapping_state.fchan() + 
                                                                               state.mapping_state.fields_on)
        addRFShapedPulse('RF padding', state.mapping_state.time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Pi clock', state.mapping_state.time, 0, opts = OPTS_AWG_MW_PULSE)
        
        #Time scan on dressed state with dressing fields on
        addRFShapedPulse('Time scan ' + state.name, det, step, 0, MWOUT, state.dressing_fields)
        addRFShapedPulse('Time scan ' + state.name, det, step, 0, RFOUT, state.fchan() + state.fields_on)
        addPulse('Time scan ' + state.name, det, step, opts = OPTS_AWG_MWRF_PULSE)
        
        #Pi pulse from 0 to clock
        addRFShapedPulse('Pi Clock', state.mapping_state.time, 0, 0, MWOUT, state.mapping_state.fchan() + 
                                                                               state.mapping_state.fields_on)
        addRFShapedPulse('RF padding', state.mapping_state.time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Pi clock', state.mapping_state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    else :
        addRFShapedPulse('Time scan ' + state.name, det, step, 0, MWOUT, state.fchan() + state.fields_on)  
        addPulse('Time scan ' + state.name, det, step, opts = OPTS_AWG_MW_PULSE)
        
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    if sb_cool :
        addParam("logmsg", "Time scan (COLD) on " + state.name + ", step = " + str(step))
    elif det != 0 :
        addParam("logmsg", "Time scan on " + state.name + ", step = " + str(step) + ', detuning = ' + str(det))
    else :
        addParam("logmsg", "Time scan on " + state.name + ", step = " + str(step))
    return makeSequence()
    
def lifetime(state = "", det = 0, step = 0, steps = 0, runs = 0, delay = 0, calib = 0) :
    
    if det < 0 :
        det = 0
    
    state = eval(state)
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    dressing_fields = dressingP1.fchan() + dressingM1.fchan()
    
    if state.dressing_fields != [] :
        #0 -> 0'
        addRFShapedPulse('Pi Clock', state.mapping_state.time, 0, 0, MWOUT, state.mapping_state.fchan() + 
                                                                               state.mapping_state.fields_on)
        addRFShapedPulse('RF padding', state.mapping_state.time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Pi clock', state.mapping_state.time, 0, opts = OPTS_AWG_MW_PULSE)
        
        #0' -> D
        addRFShapedPulse('Pi Clock', state.time, 0, 0, MWOUT, dressing_fields)
        addRFShapedPulse('RF padding', state.time, 0, 0, RFOUT, state.fchan())
        addPulse('Pi to D', state.time, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #Delay
        addRFShapedPulse('T1 delay ', det, step, 0, MWOUT, dressing_fields)
        addRFShapedPulse('T1 delay ', det, step, 0, RFOUT, NULL_FCHAN)
        addPulse('T1 Delay ', det, step, opts = OPTS_AWG_MWRF_PULSE)
        
        #D - > 0'
        addRFShapedPulse('Pi Clock', state.time, 0, 0, MWOUT, dressing_fields)
        addRFShapedPulse('RF padding', state.time, 0, 0, RFOUT, state.fchan())
        addPulse('Pi from D', state.time, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #0' -> 0
        addRFShapedPulse('Pi Clock', state.mapping_state.time, 0, 0, MWOUT, state.mapping_state.fchan() + 
                                                                               state.mapping_state.fields_on)
        addRFShapedPulse('RF padding', state.mapping_state.time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Pi clock', state.mapping_state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    else :
        #0' -> State
        addRFShapedPulse('Pi state', state.time, 0, 0, MWOUT, state.fchan())
        addRFShapedPulse('RF padding', state.time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Pi state', state.time, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #Delay
        addRFShapedPulse('T1 delay ', det, step, 0, MWOUT, NULL_FCHAN)
        addRFShapedPulse('T1 delay ', det, step, 0, RFOUT, NULL_FCHAN)
        addPulse('T1 Delay ', det, step, opts = OPTS_AWG_MWRF_PULSE)
        
        #State - > 0'
        addRFShapedPulse('Pi state', state.time, 0, 0, MWOUT, state.fchan())
        addRFShapedPulse('RF padding', state.time, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Pi state', state.time, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "coherencetime")
    mathparams = {"name" : "coherencetime", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Lifetime on " + state.name + ", delay = " + str(det))
    
    return makeSequence()   
    
def coherencetime(state = "", det = 0, step = 0, steps = 0, runs = 0, delay = 0, calib = 0) :
    
    if det < 0 :
        det = 0
    
    state = eval(state)
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
   
    if state.dressing_fields != [] :
        state.dressing_fields = dressingP1.fchan() + dressingM1.fchan(ampdet =-1, ampstep = .2)
        
        #Pi pulse from 0 to clock
        addRFShapedPulse('Padding ', clock1.time, 0, 0, RFOUT, NULL_FCHAN)
        addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
        addPulse('Pi clock', clock1.time, 0, opts = OPTS_AWG_MW_PULSE)
        
        #0' -> D/2
        addRFShapedPulse('Pi Clock', state.time/2, 0, 0, MWOUT, state.dressing_fields)
        addRFShapedPulse('RF padding', state.time/2, 0, 0, RFOUT, state.fchan())
        addPulse('PI/2 D', state.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #Delay/2
        addRFShapedPulse('T1 delay ', delay/2, 0, 0, MWOUT, state.dressing_fields)
        addRFShapedPulse('T1 delay ', delay/2, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('T1 Delay ', delay/2, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #Spin echo
        addRFShapedPulse('Pi Clock', state.time, 0, 0, MWOUT, state.dressing_fields)
        addRFShapedPulse('RF padding', state.time, 0, 0, RFOUT, state.fchan())
        addPulse('Spin echo', state.time, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #Delay/2
        addRFShapedPulse('T1 delay ', delay/2, 0, 0, MWOUT, state.dressing_fields)
        addRFShapedPulse('T1 delay ', delay/2, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('T1 Delay ', delay/2, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #0' -> D/2
        addRFShapedPulse('Pi Clock', state.time/2, 0, 0, MWOUT, state.dressing_fields)
        addRFShapedPulse('RF padding', state.time/2, 0, 0, RFOUT, state.fchan(phase = det, phasestep = step))
        addPulse('PI/2 D', state.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
        
        #Pi pulse from 0 to clock
        addRFShapedPulse('Padding ', clock1.time, 0, 0, RFOUT, NULL_FCHAN)
        addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
        addPulse('Pi clock', clock1.time, 0, opts = OPTS_AWG_MW_PULSE)
        
  
   
    else :
    
        # Pi/2 Pulse
        addRFShapedPulse('RF Padding', state.time/2, 0, 0, RFOUT, NULL_FCHAN)
        addRFShapedPulse('Pi/2 Pulse', state.time/2, 0, 0, MWOUT, state.fchan() + state.fields_on)  
        addPulse('Pi/2 pulse', state.time/2, 0, opts = OPTS_AWG_MW_PULSE)
        
        # Delay/2 
        addRFShapedPulse('Padding', delay/2, 0, 0, MWOUT, NULL_FCHAN)
        addPulse('Padding', delay/2)
        
        
        # Spin echo pi pulse
        addRFShapedPulse('RF Padding', state.time, 0, 0, RFOUT, NULL_FCHAN)
        addRFShapedPulse('Spin echo pi Pulse', state.time, 0, 0, MWOUT, state.fchan() + state.fields_on)  
        addPulse('Spin echo pi pulse', state.time, 0, opts = OPTS_AWG_MW_PULSE)
        
        
        # Delay/2
        addRFShapedPulse('Padding', delay/2, 0, 0, MWOUT, NULL_FCHAN)
        addPulse('Padding', delay/2)
        
        # Pi/2 pulse
        addRFShapedPulse('RF Padding', state.time/2, 0, 0, RFOUT, NULL_FCHAN)
        addRFShapedPulse('Pi/2 Pulse', state.time/2, 0, 0, MWOUT, state.fchan(phase = det, phasestep = step) + state.fields_on)  
        addPulse('Pi/2 pulse', state.time/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "coherencetime")
    mathparams = {"name" : "coherencetime", "delay" : delay, "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Time scan (coherence) on " + state.name + ", step = " + str(step) + ', delay = ' + str(delay) + ' us')
    
    return makeSequence()   

def dopplertemp(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    if det < 0 :
        det = 0
    
    state = eval(state)
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    addRFShapedPulse('Time scan ' + state.name, det, step, 0, MWOUT, state.fchan() + state.fields_on)  
    addPulse('Time scan ' + state.name, det, step, opts = OPTS_AWG_MW_PULSE)

    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "dopplertemp")
    mathparams = {"name" : "dopplertemp", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Doppler temp on " + state.name + ", step = " + str(step))
    
    return makeSequence()     

def secfreq(mode = "COM", det = 0, step = 0, steps = 0, runs = 0, amp = 0) :
 
    if mode == "COM" :
        sec_freq = SEC_FREQ_COM
    elif mode == "STR" :
        sec_freq = SEC_FREQ_STR
 
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    addRFShapedPulse('PREP: Cooling', COOL_TIME, 0, 0, MWOUT, COOLING_FCHAN)
    addRFShapedPulse('RF padding', COOL_TIME, 0, 0, RFOUT, State(freq = sec_freq, amp = amp).fchan(freqdet = det, freqstep = step))    
    addPulse('PREP: Cooling', COOL_TIME, 0, COOLING_COUNT, OPTS_SEC_FREQ_SCAN)
    
    _addLineTrigPulse()
    
    addParam("steps", steps) 
    addParam("runs", runs)
    addParam("comment", "secfreq")
    mathparams = {"name" : "secfreq", "header" : "", "det" : det, "step" : step, "state" : "sideband", "freq" : 0, 
                  "pitime" : 20, "amp" : 5, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", 0)
    addParam("logmsg", "Sec freq scan, det = " + str(det) + ", step = " + str(step))
    
    return makeSequence()

   
#--------------------------------------------------------------------------------------------------------------------#
#  MOLMER SORENSEN CDD GATE PULSE SEQUENCES
#--------------------------------------------------------------------------------------------------------------------# 
 
def cddsbfreq(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0, sb_cool = False) :

    state = cddplusblue2
    innitPulseList()
   
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    if sb_cool :
        _addSbCoolingPulse()
 
    WARMUP_FIELDS = cddplusred1.fchan(freqdet = -1e3) + cddplusblue1.fchan(freqdet = +1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3) + cddpluscar1.fchan(freqdet = -1e3) + cddpluscar2.fchan(freqdet = +1e3)                    
    WARMUP_TIME = 50
    addRFShapedPulse('Warm up amplifiers', WARMUP_TIME, 0, 0, MWOUT, WARMUP_FIELDS)  
    addPulse('Warm up amplifiers', WARMUP_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
    def fields_car(phase) :
        return cddpluscar1.fchan(phase = phase, freqdet = -1e3) + cddpluscar2.fchan(phase = phase, freqdet = 0)
     
    r1 = -1e3
    b1 = 1e3
    r2 = -1e3
    b2 = 0
    
    timestep = 0
    timedet = 3109.9 #-15
    
    current_time = stepNum * timestep + timedet
    T_PERIOD = 2*cddpluscar1.time
    N_PERIODS = floor(current_time/T_PERIOD)
    NEW_DET = current_time - T_PERIOD*N_PERIODS
    
     
    def fields_sb(phase = 0) :
        return cddplusred1.fchan(freqdet = r1 , freqstep = 0, phase = phase) + \
               cddplusblue1.fchan(freqdet = b1,  freqstep = 0, phase = phase) + \
               cddplusred2.fchan(freqdet =r2 , freqstep = 0, phase = phase) + \
               cddplusblue2.fchan(freqdet = b2 + det, freqstep = step, phase = phase)                   
        
    for i in range(N_PERIODS) :
        
        myphase = np.pi*((-1)**i + 1)/2
        addRFShapedPulse('2pi pulse with pf' , T_PERIOD, 0, 0, MWOUT, fields_sb() + fields_car(myphase))  
        addPulse('2pi pulse with pf', T_PERIOD, 0, opts = OPTS_AWG_MW_PULSE)
        
    myphase = np.pi*((-1)**(N_PERIODS) + 1)/2
    addRFShapedPulse('Time scan ', NEW_DET, 0, 0, MWOUT, fields_sb() + fields_car(myphase))
    addPulse('Time scan ', NEW_DET, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps) 
    addParam("runs", runs)
    addParam("comment", "freqscan")
    mathparams = {"name" : "freqscan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    if sb_cool :
        addParam("logmsg", "Frequency scan (COLD) on " + state.name + ", det = " + str(det) + ", step = " + str(step))
    else :
        addParam("logmsg", "Frequency scan on " + state.name + ", det = " + str(det) + ", step = " + str(step))
    return makeSequence()
    
def cddgate(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0, sb_cool = False) :
    state = cddplusred1
    innitPulseList()
   
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    if sb_cool :
        _addSbCoolingPulse()
   
    WARMUP_FIELDS = cddplusred1.fchan(freqdet = -1e3) + cddplusblue1.fchan(freqdet = +1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3) + cddpluscar1.fchan(freqdet = -1e3) + cddpluscar2.fchan(freqdet = +1e3)                    
    WARMUP_TIME = 50
    addRFShapedPulse('Warm up amplifiers', WARMUP_TIME, 0, 0, MWOUT, WARMUP_FIELDS)  
    addPulse('Warm up amplifiers', WARMUP_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
    TWO_IONS = True
    PF = True
    
    delta0 = 0.322
    
    sym_det = 0#-2#-2*delta0#1e3
    sym_step = 0#0.2#delta0/5
    
    asym1_det = -2e3
    asym1_step = 0
    
    asym2_det = -0.5
    asym2_step = 0.1
    
    timestep =  0*cddpluscar1.time * 20
    timedet = 3109.9 #(3109.9/2 - cddpluscar1.time)
    
    car1det = -2e3
    car2det = 0
    
    current_time = stepNum * timestep + timedet
    T_PERIOD = 2*cddpluscar1.time
    N_PERIODS = floor(current_time/T_PERIOD)
    NEW_DET = current_time - T_PERIOD*N_PERIODS
    
    def fields_car(phase) :
        return cddpluscar1.fchan(phase = phase, freqdet = car1det) + cddpluscar2.fchan(phase = phase, freqdet = car2det)
     
    def fields_sb(phase = 0) :
        return cddplusred1.fchan(freqdet = -sym_det +asym1_det, freqstep = -sym_step + asym1_step , phase = phase) + \
               cddplusblue1.fchan(freqdet = sym_det + asym1_det,  freqstep = sym_step + asym1_step, phase = phase) + \
               cddplusred2.fchan(freqdet =  2e3-sym_det +asym2_det, freqstep = -sym_step + asym2_step,phase = phase) + \
               cddplusblue2.fchan(freqdet = sym_det + asym2_det , freqstep = sym_step +asym2_step, phase = phase)                   
        
   
    for i in range(N_PERIODS) :
        
        myphase = np.pi*((-1)**i + 1)/2
        addRFShapedPulse('2pi pulse with pf' , T_PERIOD, 0, 0, MWOUT, fields_sb() + fields_car(myphase))  
        addPulse('2pi pulse with pf', T_PERIOD, 0, opts = OPTS_AWG_MW_PULSE)
    myphase = np.pi*((-1)**(N_PERIODS) + 1)/2
    addRFShapedPulse('Time scan ', NEW_DET, 0, 0, MWOUT, fields_sb() + fields_car(myphase))
    addPulse('Time scan ', NEW_DET, 0, opts = OPTS_AWG_MW_PULSE)

    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    if sb_cool :
        addParam("logmsg", "CDD Gate " + state.name + ", step = " + str(step))
    elif det != 0 :
        addParam("logmsg", "CDD Gate")
    else :
        addParam("logmsg", "CDD Gate")
    return makeSequence()

 
def cddcartimescan(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0, sb_cool = False) :
    
    state = eval(state)
    
    if det < 0 :
        det = 0
    
    innitPulseList()
   
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    
    WARMUP_TIME = 50
    addRFShapedPulse('Warm up amplifiers', WARMUP_TIME, 0, 0, MWOUT, state.fchan(freqdet = -1e3) + state.fields_on)  
    addPulse('Warm up amplifiers', WARMUP_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
    T_POWER = 29.9
    T_PERIOD = 1/T_POWER*1e3
    N_FLOPS = 93
    GATE_TIME = N_FLOPS*T_PERIOD
    curr_time = 0
    for i in range(N_FLOPS) :
        addRFShapedPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, 0, MWOUT, state.fchan(phase = np.pi*((-1)**i + 1)/2, ampdet = det, ampstep = step) + state.fields_on)  
        addPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, opts = OPTS_AWG_MW_PULSE)
   
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Matching CDD drive powers, ampdet = " + str(det) + ', ampstep = ' + str(step))
    return makeSequence()

 
def timescan_pf(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0, sb_cool = False) :
        
    if det < 0 :
        det = 0
    
    state = eval(state)
    innitPulseList()
   
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    WARMUP_TIME = 50
    addRFShapedPulse('Warm up amplifiers', WARMUP_TIME, 0, 0, MWOUT, state.fchan(freqdet = -1e3) + state.fields_on)  
    addPulse('Warm up amplifiers', WARMUP_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
    TWO_IONS = True
    PF = False
    
    current_time = stepNum * step + det
    T_PERIOD = 2*cddpluscar1.time
    N_PERIODS = floor(current_time/T_PERIOD)
    NEW_DET = current_time - T_PERIOD*N_PERIODS
    
    if TWO_IONS : 
    
        FIELDS_SB = cddplusred1.fchan(freqdet = -1e3) + cddplusblue1.fchan(freqdet = +1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3)                   
        def fields_car(phase) :
            return cddpluscar1.fchan(phase = phase) + cddpluscar2.fchan(phase = phase)
        
        for i in range(N_PERIODS) :
            if PF :
                addRFShapedPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, 0, MWOUT, FIELDS_SB + fields_car(np.pi*((-1)**i + 1)/2))  
            else :
                addRFShapedPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, 0, MWOUT, FIELDS_SB + fields_car(np.pi*((-1)**i + 1)/2))  
            addPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, opts = OPTS_AWG_MW_PULSE)
        if PF :
            current_phase = np.pi*((-1)**(N_PERIODS) + 1)/2
        else :
            current_phase = 0
        addRFShapedPulse('Time scan ' + state.name, NEW_DET, 0, 0, MWOUT, FIELDS_SB + fields_car(current_phase))
        addPulse('Time scan ' + state.name, NEW_DET, 0, opts = OPTS_AWG_MW_PULSE)
        
    else :
        for i in range(N_PERIODS) :
            if PF :
                addRFShapedPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, 0, MWOUT, state.fchan(phase = np.pi*((-1)**i + 1)/2) + state.fields_on)  
            else :
                addRFShapedPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, 0, MWOUT, state.fchan() + state.fields_on)  
            addPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, opts = OPTS_AWG_MW_PULSE)
        if PF :
            current_phase = np.pi*((-1)**(N_PERIODS) + 1)/2
        else :
            current_phase = 0
        addRFShapedPulse('Time scan ' + state.name, NEW_DET, 0, 0, MWOUT, state.fchan(phase = current_phase) + state.fields_on)
        addPulse('Time scan ' + state.name, NEW_DET, 0, opts = OPTS_AWG_MW_PULSE)
        
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    if sb_cool :
        addParam("logmsg", "Time scan (COLD) on " + state.name + ", step = " + str(step))
    elif det != 0 :
        addParam("logmsg", "Time scan on " + state.name + ", step = " + str(step) + ', detuning = ' + str(det))
    else :
        addParam("logmsg", "Time scan on " + state.name + ", step = " + str(step))
    return makeSequence()


def cddgatepop(det = 0, step = 0, steps = 0, runs = 0, sb_cool = False, pi_pulse = False) :

    if det < 0 :
        det = 0 
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    # Sidebands and Drives during first half
    cdd_drives_1 = cddpluscar1.fchan() + cddpluscar2.fchan()
    cdd_sb_1 = cddplusred1.fchan() + cddplusblue1.fchan() + cddplusred2.fchan() + cddplusblue2.fchan()
    
    # Sidebands and Drives during second half
    cdd_drives_2 = cddpluscar1.fchan() + cddpluscar2.fchan()
    cdd_sb_2 = cddplusred1.fchan() + cddplusblue1.fchan() + cddplusred2.fchan() + cddplusblue2.fchan()
    
    # Refocussing pi pulse
    cdd_pi_chan = cddpluspi1.fchan(phase = pi/2) + cddpluspi2.fchan(phase = pi/2)
    
    def drive_fields(phase) :
        return cddpluscar1.fchan() + cddpluscar2.fchan()
    
    def sideband_fields(phase) :
        return cddplusred1.fchan() + cddplusblue1.fchan() + cddplusred2.fchan() + cddplusblue2.fchan()
    
    if sb_cool :
        _addSbCoolingPulse()
    
    WARMUP_TIME = 50
    addRFShapedPulse('Warm up amplifiers', WARMUP_TIME, 0, 0, MWOUT, state.fchan(freqdet = -1e3) + state.fields_on)  
    addPulse('Warm up amplifiers', WARMUP_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
    T_POWER = 29.9
    T_PERIOD = 1/T_POWER*1e3
    N_FLOPS = 93
    GATE_TIME = N_FLOPS*T_PERIOD
    curr_time = 0
    
    for i in range(N_FLOPS) :
        phase = np.pi*((-1)**i + 1)/2
        addRFShapedPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, 0, MWOUT, drive_fields(phase = phase) + sideband_fields(phase= phase))
        addPulse('2pi pulse with pf' + state.name, T_PERIOD, 0, opts = OPTS_AWG_MW_PULSE)
   
    
    '''
    # Sidebands and carrier for plus of both ions
    addRFShapedPulse('MS CDD Gate : MW sb + car', CDD_GATE_TIME/2, 0, 0, MWOUT, cdd_drives_1 + cdd_sb_1)
    addRFShapedPulse('MS CDD Gate : RF padding', CDD_GATE_TIME/2, 0, 0, RFOUT, NULL_FCHAN )
    addPulse('MS CDD Gate, first half', CDD_GATE_TIME/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    if pi_pulse :
        #Add refocussing pi pulse midway with pi/2 phase shift
        addRFShapedPulse('Refocussing pi pulse', CDD_PI_TIME, 0, 0, MWOUT, cdd_pi_chan)
        addRFShapedPulse('RF Padding', CDD_PI_TIME, 0, 0, RFOUT, NULL_FCHAN)
        addPulse('Refocussing pi pulse', CDD_PI_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
        # Sidebands and carrier for plus of both ions
        addRFShapedPulse('MS CDD Gate : MW sb + car', CDD_GATE_TIME/2 + det, step, 0, MWOUT, cdd_drives_2 + cdd_sb_2)
        addRFShapedPulse('MS CDD Gate : RF padding', CDD_GATE_TIME/2 + det, step, 0, RFOUT, NULL_FCHAN )
        addPulse('MS CDD Gate, first half', CDD_GATE_TIME/2 + det, step, opts = OPTS_AWG_MW_PULSE)
    
    else : 
        
        # Sidebands and carrier for plus of both ions
        addRFShapedPulse('MS CDD Gate : MW sb + car', CDD_GATE_TIME/2, 0, 0, MWOUT, cdd_drives_1 + cdd_sb_1)
        addRFShapedPulse('MS CDD Gate : RF padding', CDD_GATE_TIME/2, 0, 0, RFOUT, NULL_FCHAN )
        addPulse('MS CDD Gate, first half', CDD_GATE_TIME/2, 0, opts = OPTS_AWG_MW_PULSE)                                                                       
    '''
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "cddgate")
    mathparams = {"name" : "cddgate", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "CDD gate, det = " + str(det) + ", step = " + str(step))
    
    return makeSequence()

def cddgatecar(det = 0, step = 0, steps = 0, runs = 0, ion = 'both') :

    state = cddpluscar1

    if det < 0 :
        det = 0 
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    # Sidebands and cars during first half
    
    cdd_cars = NULL_FCHAN
    
    if ion is '1' :
        cdd_cars = cddpluscar1.fchan(ampdet = det, ampstep = step) + cddpluscar2.fchan(freqdet = +1e3)
    elif ion is '2' : 
        cdd_cars = cddpluscar1.fchan(freqdet = +1e3) + cddpluscar2.fchan(ampdet = det, ampstep = step)
    elif ion is 'both' :
        cdd_cars = cddpluscar1.fchan(ampdet = det, ampstep = step) + cddpluscar2.fchan(ampdet = det, ampstep = step)
        
        
    cdd_sb = cddplusred1.fchan(freqdet = -1e3) + cddplusblue1.fchan(freqdet = +1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3)
    
    # Sidebands and carrier for plus of both ions
    addRFShapedPulse('MS CDD Gate : MW sb + car', CDD_GATE_TIME, 0, 0, MWOUT, cdd_cars)
    addRFShapedPulse('MS CDD Gate : RF padding', CDD_GATE_TIME, 0, 0, RFOUT, NULL_FCHAN )
    addPulse('MS CDD Gate, first half', CDD_GATE_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", 0)
    addParam("logmsg", "Time scan on " + state.name + ", step = " + str(step))
    
    return makeSequence()


def cddgatefreq( mode = 'sym', det = 0, step = 0, steps = 0, runs = 0, sb_cool = False, pi_pulse = False) :

    calib = 0
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    # Sidebands and Drives during first half
    cdd_drives_1 = cddpluscar1.fchan() + cddpluscar2.fchan()
    cdd_sb_1 = cddplusred1.fchan() + cddplusblue1.fchan() + cddplusred2.fchan() + cddplusblue2.fchan()
    
    # Sidebands and Drives during second half
    cdd_drives_2 = cddpluscar1.fchan() + cddpluscar2.fchan()
    cdd_sb_2 = cddplusred1.fchan() + cddplusblue1.fchan() + cddplusred2.fchan() + cddplusblue2.fchan()
    
    # Refocussing pi pulse
    cdd_pi_chan = cddpluspi1.fchan(phase = pi/2) + cddpluspi2.fchan(phase = pi/2)
    
    def drive_fields(phase) :
        return cddpluscar1.fchan(phase = phase) + cddpluscar2.fchan(phase = phase)
    
    def sideband_fields(phase) :
        if mode is 'sym' :
        
            return cddplusred1.fchan(freqdet = CDD_SYM_DET + det - 1e3, freqstep = step, phase = phase) + \
                   cddplusblue1.fchan(freqdet = -CDD_SYM_DET -det + 1e3, freqstep = -step, phase = phase) + \
                   cddplusred2.fchan(freqdet = CDD_SYM_DET+det - 1e3, freqstep = step, phase = phase) + \
                   cddplusblue2.fchan(freqdet = -CDD_SYM_DET-det +1e3, freqstep = -step, phase = phase)  
        else: 
            return 0
            '''cddplusred1.fchan(freqdet = CDD_SYM_DET+det, step = step) + \
                   cddplusblue1.fchan(freqdet = -CDD_SYM_DET-det, step = -step) + \ 
                   cddplusred2.fchan(freqdet =CDD_SYM_DET+ det, step = step) + \
                   cddplusblue2.fchan(freqdet = -CDD_SYM_DET-det, step = -step)  '''
    if sb_cool :
        _addSbCoolingPulse()
    
    WARMUP_TIME = 50
    WARMUP_FIELDS = cddplusred1.fchan(freqdet = -1e3) + cddplusblue1.fchan(freqdet = +1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3) + cddpluscar1.fchan(freqdet = -1e3) + cddpluscar2.fchan(freqdet = +1e3)                    
    addRFShapedPulse('Warm up amplifiers', WARMUP_TIME, 0, 0, MWOUT, WARMUP_FIELDS)  
    addPulse('Warm up amplifiers', WARMUP_TIME, 0, opts = OPTS_AWG_MW_PULSE)
    
    T_POWER = 29.9
    T_PERIOD = 1/T_POWER*1e3
    N_FLOPS = 93
    GATE_TIME = N_FLOPS*T_PERIOD
    GATE_TIME = 3110
    T_PERIOD = 3110/N_FLOPS
    T_PERIOD = 2*cddpluscar1.time
    curr_time = 0
    
    for i in range(N_FLOPS) :
        phase = np.pi*((-1)**i + 1)/2
        addRFShapedPulse('2pi pulse with pf', T_PERIOD, 0, 0, MWOUT, drive_fields(phase = phase) + sideband_fields(phase= phase))
        addPulse('2pi pulse with pf', T_PERIOD, 0, opts = OPTS_AWG_MW_PULSE)
   
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "cddgate")
    mathparams = {"name" : "cddgate", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "CDD gate, det = " + str(det) + ", step = " + str(step))
    
    return makeSequence()

 
#--------------------------------------------------------------------------------------------------------------------#
#  SPIN SPIN GATE PULSE SEQUENCES
#--------------------------------------------------------------------------------------------------------------------# 
    
def spinspingate(det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    if det < 0 :
        det = 0
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    #Pi pulse from 0 to 0' for both ions
    addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
    addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT, clock2.fchan())
    addRFShapedPulse('RF padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1.time + clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Pi pulse from 0' to D for both ions
    Dtime = (D1ss.time + D2ss.time)/2 #Ideally both times are equal
    addRFShapedPulse('Mapping dressing fields', Dtime, 0, 0, MWOUT, D1ss.dressing_fields + D2ss.dressing_fields)
    addRFShapedPulse('Pi pulse D1 and D2', Dtime, 0, 0, RFOUT, D1ss.fchan() + D2ss.fchan())
    addPulse('Pi pulse D1 and D2', Dtime, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Spin spin gate
    addRFShapedPulse('Gate dressing fields', det, step, 0, MWOUT, dressingP1ss_gate.fchan() + dressingM1ss_gate.fchan() + 
                                                                     dressingP2ss_gate.fchan() + dressingM2ss_gate.fchan())
    addRFShapedPulse('RF padding', det, step, 0, RFOUT, NULL_FCHAN)
    addPulse('Spin spin gate', det, step, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Pi pulse from 0' to D for both ions
    Dtime = (D1ss.time + D2ss.time)/2 #Ideally both times are equal
    addRFShapedPulse('Mapping dressing fields', Dtime, 0, 0, MWOUT, D1ss.dressing_fields + D2ss.dressing_fields)
    addRFShapedPulse('Pi pulse D1 and D2', Dtime, 0, 0, RFOUT, D1ss.fchan() + D2ss.fchan())
    addPulse('Pi pulse D1 and D2', Dtime, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse from 0 to 0' for both ions   
    addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
    addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT,  clock2.fchan())
    addRFShapedPulse('RF padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1.time + clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Spin spin gate, step = " + str(step))
    
    return makeSequence()

def spinspinparity(det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    #Pi pulse from 0 to 0' for both ions
    addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
    addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT, clock2.fchan())
    addRFShapedPulse('RF padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1.time + clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Pi/2 pulse from 0' to D for both ions
    #Doing both pulses separately 
    addRFShapedPulse('Mapping to D ion 1', D1ss.time/2, 0, 0, MWOUT, dressingP1ss_map.fchan() + dresingM1ss_map.fchan())
    addRFShapedPulse('Mapping to D ion 1', D1ss.time/2, 0, 0, RFOUT, D1ss.fchan())
    addRFShapedPulse('Mapping to D ion 2', D2ss.time/2, 0, 0, MWOUT, dressingP2ss_map.fchan() + dresingM2ss_map.fchan())
    addRFShapedPulse('Mapping to D ion 2', D2ss.time/2, 0, 0, RFOUT, D2ss.fchan())
    addPulse('Pi pulse D1 and D2', D1ss.time/2 + D2ss.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Spin spin gate
    #0'0' + DD -> 0'0' + i DD
    addRFShapedPulse('Gate dressing fields', SS_GATE_TIME, 0, 0, MWOUT, dressingP1ss_gate.fchan() + dressingM1ss_gate.fchan() + 
                                                                     dressingP2ss_gate.fchan() + dressingM2ss_gate.fchan())
    addRFShapedPulse('RF padding', SS_GATE_TIME, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Spin spin gate', SS_GATE_TIME, 0, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Parity pi/2 pulse on 0' -> D for both ions with variable phase
    addRFShapedPulse('Mapping to D ion 1', D1ss.time/2, 0, 0, MWOUT, dressingP1ss_map.fchan() + dresingM1ss_map.fchan())
    addRFShapedPulse('Mapping to D ion 1', D1ss.time/2, 0, 0, RFOUT, D1ss.fchan(phase = det, phasestep = step))
    addRFShapedPulse('Mapping to D ion 2', D2ss.time/2, 0, 0, MWOUT, dressingP2ss_map.fchan() + dresingM2ss_map.fchan())
    addRFShapedPulse('Mapping to D ion 2', D2ss.time/2, 0, 0, RFOUT, D2ss.fchan(phase = det, phasestep = step))
    addPulse('Pi pulse D1 and D2', D1ss.time/2 + D2ss.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)    
        
    #Pi pulse from 0 to 0' for both ions   
    addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
    addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT,  clock2.fchan())
    addRFShapedPulse('RF padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1.time + clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Spin spin gate, step = " + str(step))
    
    return makeSequence()

def spinspintime(state = "", mode = "",det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    state = D1
    if det < 0 :
        det = 0
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
   
    #Pi pulse from 0 to clock
    if mode == "ion1" :
        addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
        addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT, clock2.fchan())
    elif mode == "ion2":
        addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
        addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT, clock2.fchan())
    elif mode == "both":
        addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
        addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT, clock2.fchan())

    addRFShapedPulse('RF padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1.time + clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Time scan on dressed state with dressing fields on
    if mode == "ion1" :
        addRFShapedPulse('Time scan ' , det, step, 0, MWOUT, dressingP1_map.fchan() + dressingM1_map.fchan() + 
                                                                dressingP2_map.fchan(freqdet = -4000) + dressingM2_map.fchan(freqdet = 4000))
        addRFShapedPulse('Time scan ' , det, step, 0, RFOUT, D1ss.fchan() + D2ss.fchan(freqdet = 1000))
    if mode == "ion2" :
        addRFShapedPulse('Time scan ' , det, step, 0, MWOUT, dressingP1_map.fchan(freqdet = -2000) + dressingM1_map.fchan(freqdet = 2000) + 
                                                                dressingP2_map.fchan() + dressingM2_map.fchan())
        addRFShapedPulse('Time scan ' , det, step, 0, RFOUT, D1ss.fchan(freqdet = 1000) + D2ss.fchan())
    elif mode == "both" :
        addRFShapedPulse('Time scan ' , det, step, 0, MWOUT, dressingP1_map.fchan() + dressingM1_map.fchan() + 
                                                                dressingP2_map.fchan() + dressingM2_map.fchan())
        addRFShapedPulse('Time scan ' , det, step, 0, RFOUT, D1ss.fchan() + D2ss.fchan())
    addPulse('Time scan ', det, step, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse from 0 to clock
    if mode == "ion1" :
        addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
        addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT, clock2.fchan())
    elif mode == "ion2":
        addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
        addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT, clock2.fchan())
    elif mode == "both":
        addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
        addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT,  clock2.fchan())
    addRFShapedPulse('RF padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1.time + clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
  
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Time scan on " + state.name + ", step = " + str(step))
    
    return makeSequence()
    
def spinspinfreq(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    state = D1
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)

    #Pi pulse from 0 to clock
    addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
    addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT, clock2.fchan())
    addRFShapedPulse('RF padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1.time + clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Time scan on dressed state with dressing fields on
    Dtime = (D1ss.time + D2ss.time)/2
    addRFShapedPulse('Time scan ' , Dtime, 0, 0, MWOUT, dressingP1_map.fchan() + dressingM1_map.fchan() + 
                                                           dressingP2_map.fchan(freqdet = -4000)  +dressingM2_map.fchan(freqdet = 4000))
    addRFShapedPulse('Time scan ' , Dtime, 0, 0, RFOUT, D1ss.fchan(freqdet = det, freqstep = step) + D2ss.fchan(freqdet = 200))
    addPulse('Time scan ', Dtime, 0, opts = OPTS_AWG_MWRF_PULSE)
   
    addRFShapedPulse('Pi Clock', clock1.time, 0, 0, MWOUT, clock1.fchan())
    addRFShapedPulse('Pi Clock', clock2.time, 0, 0, MWOUT,  clock2.fchan())
    addRFShapedPulse('RF padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1.time + clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
   
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Time scan on " + state.name + ", step = " + str(step))
    
    return makeSequence()
    
 
#--------------------------------------------------------------------------------------------------------------------#
#  MOLMER SORENSEN GATE PULSE SEQUENCES
#--------------------------------------------------------------------------------------------------------------------# 


def catfreqscan(det = 0, step = 0, steps = 0, runs = 0, sb_cool = False) :

    cat_time = 1000/(ETA * MS_OM_RF/sqrt(2))
    
    #Get the detuning from each sideband transitions
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    if sb_cool:
        _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' ion 1
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Red and blue sidebands for both ions
    addRFShapedPulse('MS GATE: mw dressing fields', cat_time, 0, MS_PULSE_SHAPING_TIME, MWOUT, dressingP1ms.fchan() + dressingM1ms.fchan() 
                                                                    + dressingP2ms.fchan(-4000) + dressingM2ms.fchan(4000))
    addRFShapedPulse('MS Gate: rf red and blue sb', cat_time, 0, MS_PULSE_SHAPING_TIME, RFOUT, red1ms.fchan(freqdet = det , freqstep = step) 
                                                                       + blue1ms.fchan(freqdet = det  , freqstep = step) 
                                                                       + red2ms.fchan(freqdet = 2000)  
                                                                       + blue2ms.fchan(freqdet = 2000))
    addPulse('MS GATE', cat_time, 0, opts = OPTS_AWG_MWRF_PULSE)

    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msgate")
    mathparams = {"name" : "msgate", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, 
                  "pitime" : 0, "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", 0)
    addParam("logmsg", "Cat freq scan, det = " + str(det) + ", step = " + str(step) )
    
    return makeSequence()

def cattimescan(det = 0, step = 0, steps = 0, runs = 0, sb_cool = False) :

    if det < 0 :
        det = 0 
        
    #Get the detuning from each sideband transitions
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    if sb_cool:
        _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' ion 1
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Red and blue sidebands for both ions
    addRFShapedPulse('MS GATE: mw dressing fields', det, step, MS_PULSE_SHAPING_TIME, MWOUT, dressingP1ms.fchan() + dressingM1ms.fchan() 
                                                                    + dressingP2ms.fchan(-4000) + dressingM2ms.fchan(4000))
    addRFShapedPulse('MS Gate: rf red and blue sb', det, step, MS_PULSE_SHAPING_TIME, RFOUT, red1ms.fchan() 
                                                                       + blue1ms.fchan( ) 
                                                                       + red2ms.fchan(freqdet = 2000)  
                                                                       + blue2ms.fchan(freqdet = 2000))
    addPulse('MS GATE', det, step, opts = OPTS_AWG_MWRF_PULSE)

    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msgate")
    mathparams = {"name" : "msgate", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", 0)
    addParam("logmsg", "Cat time scan, step = " + str(step))
    
    return makeSequence()    
      
def msgate(det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    if det < 0 :
        det = 0 
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Red and blue sideband for both ions
    addRFShapedPulse('MS GATE: mw dressing fields', det, step, MS_PULSE_SHAPING_TIME, MWOUT, dressingP1ms.fchan() + dressingM1ms.fchan() 
                                                                    + dressingP2ms.fchan() + dressingM2ms.fchan())
    addRFShapedPulse('MS Gate: rf red and blue sb', det, step, MS_PULSE_SHAPING_TIME, RFOUT, red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1) 
                                                                                           + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1) 
                                                                                           + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2)  
                                                                                           + blue2ms.fchan(freqdet =  SYM_DET + ASYM_DET_2))
    addPulse('MS GATE', det, step,  opts = OPTS_AWG_MWRF_PULSE)

    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msgate")
    mathparams = {"name" : "msgate", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MS gate, step = " + str(step))
    
    return makeSequence()
   
def mstwotonegate(det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    if det < 0 :
        det = 0 
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Two red and blue sidebands for both ions
    addRFShapedPulse('MS TWO TONE GATE: mw dressing fields', det, step, MS_PULSE_SHAPING_TIME, MWOUT, dressingP1ms.fchan() + dressingM1ms.fchan() 
                                                                    + dressingP2ms.fchan() + dressingM2ms.fchan())
    addRFShapedPulse('MS TWO TONE Gate: rf red and blue sb', det, step, MS_PULSE_SHAPING_TIME, RFOUT, red11ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1) 
                                                                                           + blue11ms.fchan(freqdet = SYM_DET + ASYM_DET_1) 
                                                                                           + red12ms.fchan(freqdet = - SYM_DET + ASYM_DET_2)  
                                                                                           + blue12ms.fchan(freqdet =  SYM_DET + ASYM_DET_2)
                                                                                           + red21ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1) 
                                                                                           + blue21ms.fchan(freqdet = SYM_DET + ASYM_DET_1) 
                                                                                           + red22ms.fchan(freqdet = - SYM_DET + ASYM_DET_2)  
                                                                                           + blue22ms.fchan(freqdet =  SYM_DET + ASYM_DET_2))
    addPulse('MS TWO TONE GATE', det, step,  opts = OPTS_AWG_MWRF_PULSE)

    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "mstwotonegate")
    mathparams = {"name" : "mstwotonegate", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MS TWO TONE gate, step = " + str(step))
    
    return makeSequence()   
   
def RLtest(det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    if det < 0 :
        det = 0 
    
    dressing_fields = dressingP1ms.fchan() + dressingM1ms.fchan() + dressingP2ms.fchan() + dressingM2ms.fchan()
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger                                                                                                                                                                                                                                                                    
    
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
        
    resetAWGPhase()
    
    '''
    Ry(state_param, 0)
    UMS()
    Rx(pi/2, 0)
    Rx(-pi/2, 1)
    Ry(subspace_param, 1)
    '''
    #1.796361996
    
    YspTime = 1.796361996 * D1.time/pi #606.7 us
    
    #Ry(state_param, 0)
    addRFShapedPulse('Ry(state_param, 0)', YspTime, 0, 0, RFOUT, D1.fchan(phase = pi/2))
    addRFShapedPulse('Ry(state_param, 0)', YspTime, 0, 0, MWOUT, dressing_fields)
    addPulse('Ry(state_param, 0)', YspTime, 0, opts = OPTS_AWG_MWRF_PULSE)
        
    dasym1 = 231
    dasym2 = 397
        
    phi1 = - dasym1 * (YspTime / 1000000) * 2 * pi
    phi2 = - dasym2 * (YspTime / 1000000) * 2 * pi
    phi1 = 0
    phi2 = 0
    '''
    #MS gate
    addRFShapedPulse('MS GATE: mw dressing fields', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, MWOUT, dressing_fields)
    
    addRFShapedPulse('MS Gate: rf red and blue sb', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, RFOUT, 
                                            red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1, phase = phi1) 
                                          + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1, phase = phi1) 
                                          + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2, phase = phi2)  
                                          + blue2ms.fchan(freqdet =  SYM_DET + ASYM_DET_2, phase = phi2))
                                         
    addPulse(str(phi1), MS_GATE_TIME , 0,  opts = OPTS_AWG_MWRF_PULSE)
    '''
    
    phi3 = -1.174 + phi1
    phi4 = -0.396 + phi2
    phi3 = 0
    phi4 = 0
    
    #Rx(pi/2, 0)
    addRFShapedPulse('Rx(pi/2, 0)', D1.time/2, 0, 0, RFOUT, D1.fchan(phase =  phi3))
    addRFShapedPulse('Rx(pi/2, 0)', D1.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('Rx(pi/2, 0)', D1.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Rx(-pi/2, 1)
    addRFShapedPulse('Parity pi/2', D2.time/2, 0, 0, RFOUT, D2.fchan(phase = -pi + phi4 ))
    addRFShapedPulse('Parity dressing fields', D2.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('Rx(-pi/2, 1)', D2.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Ry(subspace_param, 1), subspace_param = pi/2
    addRFShapedPulse('Parity pi/2', D2.time/2, 0, 0, RFOUT, D2.fchan(phase = pi/2 + phi4 ))
    addRFShapedPulse('Parity dressing fields', D2.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('Ry(subspace_param, 1)', D2.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msparity")
    mathparams = {"name" : "msparity", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MS parity, step = " + str(step))
    
    return makeSequence()
   

def msparity(det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    if det < 0 :
        det = 0 
    
    dressing_fields = dressingP1ms.fchan() + dressingM1ms.fchan() + dressingP2ms.fchan() + dressingM2ms.fchan()
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger                                                                                                                                                                                                                                                                    
    
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
        
    resetAWGPhase()
    
    '''
    tau = 0
    #Time delay
    addRFShapedPulse('Dressing fields', tau, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('RF padding', tau, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Time delay', tau, 0, opts = OPTS_AWG_MWRF_PULSE)
    '''
    
    #Molmer-Sorensen gate
    #Red and blue sidebands for both ions  
    addRFShapedPulse('MS GATE: mw dressing fields', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, MWOUT, dressing_fields)
    
    addRFShapedPulse('MS Gate: rf red and blue sb', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, RFOUT, 
                                            red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1) 
                                          + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1) 
                                          + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2)  
                                          + blue2ms.fchan(freqdet =  SYM_DET + ASYM_DET_2))
                                         
    addPulse('MS GATE', MS_GATE_TIME , 0,  opts = OPTS_AWG_MWRF_PULSE)
        
    phi3 = 0
    phi4 = 0
    
    #Parity pi/2 pulse 
    addRFShapedPulse('Parity pi/2', D1.time/2, 0, 0, RFOUT, D1.fchan(phase = det + phi3, phasestep = step) 
                                                          + D2.fchan(phase = det + phi4, phasestep = step))
    addRFShapedPulse('Parity dressing fields', D1.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('Parity pi/2', D1.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msparity")
    mathparams = {"name" : "msparity", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MS parity, step = " + str(step))
    
    return makeSequence()
   
def msparity01(det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    if det < 0 :
        det = 0 
    
    dressing_fields = dressingP1ms.fchan() + dressingM1ms.fchan() + dressingP2ms.fchan() + dressingM2ms.fchan()
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger                                                                                                                                                                                                                                                                    
    
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
        
    resetAWGPhase()
    
    '''
    tau = 0
    #Time delay
    addRFShapedPulse('Dressing fields', tau, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('RF padding', tau, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Time delay', tau, 0, opts = OPTS_AWG_MWRF_PULSE)
    '''
    
    # X Pi pulse ion 1 
    addRFShapedPulse('Pi ion 1', D1.time, 0, 0, RFOUT, D1.fchan())
    addRFShapedPulse('dressing fields', D1.time, 0, 0, MWOUT, dressing_fields)
    addPulse('Pi ion 1', D1.time, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    phi1 = 0
    phi2 = 0
        
    #Molmer-Sorensen gate
    #Red and blue sidebands for both ions  
    addRFShapedPulse('MS GATE: mw dressing fields', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, MWOUT, dressing_fields)
    
    addRFShapedPulse('MS Gate: rf red and blue sb', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, RFOUT, 
                                            red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1, phase = phi1) 
                                          + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1, phase = phi1) 
                                          + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2, phase = phi2)  
                                          + blue2ms.fchan(freqdet =  SYM_DET + ASYM_DET_2, phase = phi2))
                                         
    addPulse('MS GATE', MS_GATE_TIME , 0,  opts = OPTS_AWG_MWRF_PULSE)
    
    phi3 = 0
    phi4 = 0 
    
    #Parity pi/2 pulse 
    addRFShapedPulse('Parity pi/2', D1.time/2, 0, 0, RFOUT, D1.fchan(phase = det + phi3, phasestep = step) 
                                                         + D2.fchan(phase = det + phi4, phasestep = -step))
    addRFShapedPulse('Parity dressing fields', D1.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('Parity pi/2', D1.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msparity")
    mathparams = {"name" : "msparity", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MS parity, step = " + str(step))
    
    
    return makeSequence()
   
def msparitybackup(det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    
    if det < 0 :
        det = 0 
    
    dressing_fields = dressingP1ms.fchan() + dressingM1ms.fchan() + dressingP2ms.fchan() + dressingM2ms.fchan()
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    '''
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    '''
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Red and blue sidebands for both ions    
    T_PHASE = getElapsedTime()
    
    addRFShapedPulse('MS GATE: mw dressing fields', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, MWOUT, dressing_fields)
                              
    '''
    addRFShapedPulse('MS Gate: rf red and blue sb', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, RFOUT, 
                                            red1ms.fchanGlPhase(freqdet =  - SYM_DET + ASYM_DET_1, elapsed_time = T_PHASE) 
                                          + blue1ms.fchanGlPhase(freqdet = SYM_DET + ASYM_DET_1, elapsed_time = T_PHASE) 
                                          + red2ms.fchanGlPhase(freqdet = - SYM_DET + ASYM_DET_2, elapsed_time = T_PHASE)  
                                          + blue2ms.fchanGlPhase(freqdet =  SYM_DET + ASYM_DET_2, elapsed_time = T_PHASE))
    '''
    addRFShapedPulse('MS Gate: rf red and blue sb', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, RFOUT, 
                                            red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1) 
                                          + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1) 
                                          + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2)  
                                          + blue2ms.fchan(freqdet =  SYM_DET + ASYM_DET_2))
    addPulse('MS GATE', MS_GATE_TIME , 0,  opts = OPTS_AWG_MWRF_PULSE)
    
    #Parity pi/2 pulse 
    addRFShapedPulse('Parity pi/2', D1.time/2, 0, 0, RFOUT, D1.fchan(phase = det, phasestep = step) + D2.fchan(phase = det, phasestep = step))
    addRFShapedPulse('Parity dressing fields', D1.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('Parity pi/2', D1.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msparity")
    mathparams = {"name" : "msparity", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MS parity, step = " + str(step))
    
    return makeSequence()

def msRFpower(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0) :

    if det < 0 :
        det = 0
    
    state = eval(state)
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    #_addSbCoolingPulse()
   
    rf_state = state
    clock_state = clock1
    if state == red1ms or state == blue1ms :
        clock_state = clock1
        rf_state.freq = (plus1.freq - minus1.freq)/2
        #rf_state.freq = D1.freq
    elif state == red2ms or state == blue2ms :
        clock_state = clock2
        rf_state.freq = (plus2.freq - minus2.freq )/2
        #rf_state.freq = D2.freq
    
    #Pi pulse from 0 to 0'
    addRFShapedPulse('Pi Clock', clock_state.time, 0, 0, MWOUT, clock_state.fchan() + clock_state.fields_on)
    addRFShapedPulse('RF padding', clock_state.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock_state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #RF scan at (om+ + om-)/2, dressing fields off
    addRFShapedPulse('Time scan ' + state.name, det, step, 0, MWOUT, NULL_FCHAN)
    
    if state == red1ms :
        addRFShapedPulse('Time scan ' + state.name, det, step, 0, RFOUT, rf_state.fchan() + blue1ms.fchan(freqdet = +100) + 
                                                             red2ms.fchan(freqdet = -100) + blue2ms.fchan(freqdet = +100))
    '''if state == blue1ms :
        addRFShapedPulse('Time scan ' + state.name, det, step, 0, RFOUT, rf_state.fchan() + red1ms.fchan(freqdet = +4000) + red2ms.fchan(freqdet = +4000) + blue2ms.fchan(freqdet = +4000))
    '''
    if state == blue1ms :
        addRFShapedPulse('Time scan ' + state.name, det, step, 0, RFOUT, blue1ms.fchan() + red1ms.fchan(freqdet = -100) +  
                                                               red2ms.fchan(freqdet = -100) + blue2ms.fchan(freqdet = +100))
    if state == red2ms :
        addRFShapedPulse('Time scan ' + state.name, det, step, 0, RFOUT, rf_state.fchan() + blue1ms.fchan(freqdet = +100) +  
                                                             red1ms.fchan(freqdet = -100) + blue2ms.fchan(freqdet = +100))
    if state == blue2ms :
        addRFShapedPulse('Time scan ' + state.name, det, step, 0, RFOUT, rf_state.fchan() + blue1ms.fchan(freqdet = +4000) + 
                                                            red2ms.fchan(freqdet = +4000) + red1ms.fchan(freqdet = +4000))
    addPulse('Time scan ' + state.name, det, step, opts = OPTS_AWG_RF_PULSE)
    
    #Pi pulse from 0 to clock
    addRFShapedPulse('Pi Clock', clock_state.time, 0, 0, MWOUT, clock_state.fchan())
    addRFShapedPulse('RF padding', clock_state.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock_state.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "timescan")
    mathparams = {"name" : "timescan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, "freq" : state.freq, 
                  "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "Matching RF power on " + state.name + ", step = " + str(step))
    
    return makeSequence()

def msdetscan(mode = "", timemult=1, det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    #Asymmetric and symmetric detuning scans of MS gate
    #Scan modes can be ASYM1, ASYM2, SYM
 
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    '''
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    '''
    
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    if mode == "ASYM1" :
        rf_fields = red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + blue1ms.fchan(freqdet =  SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + red2ms.fchan(freqdet =  - SYM_DET + ASYM_DET_2)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2)
        gate_time = MS_GATE_TIME 
    elif mode == "ASYM2" :
        rf_fields = red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1) \
                   + red2ms.fchan(freqdet =  - SYM_DET + ASYM_DET_2 + det, freqstep = step)  \
                   + blue2ms.fchan(freqdet =  SYM_DET + ASYM_DET_2 + det, freqstep = step)         
        gate_time = MS_GATE_TIME 
    elif mode == "ASYM12" :
        rf_fields = red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1 + det, freqstep  = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2 + det, freqstep = step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2 + det, freqstep = step)         
        gate_time =  2*MS_GATE_TIME 
    elif mode == "-ASYM12" :
        rf_fields = red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1 + det, freqstep  = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2 - det, freqstep = -step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2 - det, freqstep = -step)         
        gate_time =  2*MS_GATE_TIME 
    elif mode == "SYM" :
        rf_fields = red1ms.fchan(freqdet = - SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1 - det, freqstep = -step) \
                   + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2 + det, freqstep = step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2 - det, freqstep = -step)
        gate_time =  MS_GATE_TIME 
    elif mode == "POW1" :
        rf_fields = red1ms.fchan(freqdet =- SYM_DET + ASYM_DET_1 , ampdet = det, ampstep = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1, ampdet = det, ampstep = step) \
                   + red2ms.fchan(freqdet = -SYM_DET + ASYM_DET_2)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2 )
        gate_time =  MS_GATE_TIME 
    elif mode == "POW2" :
        rf_fields = red1ms.fchan(freqdet = -SYM_DET + ASYM_DET_1 ) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1) \
                   + red2ms.fchan(freqdet = -SYM_DET + ASYM_DET_2, ampdet = det, ampstep = step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2, ampdet = det, ampstep = step)
        gate_time = MS_GATE_TIME 
    elif mode == "POW12" :
        rf_fields = red1ms.fchan(freqdet = -SYM_DET + ASYM_DET_1, ampdet = det, ampstep = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1, ampdet = det, ampstep = step) \
                   + red2ms.fchan(freqdet = -SYM_DET + ASYM_DET_2, ampdet = det, ampstep = step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2, ampdet = det, ampstep = step)
        gate_time =  MS_GATE_TIME 
    
    gate_time = timemult*MS_GATE_TIME
    
    #Red and blue sidebands for both ions
    addRFShapedPulse('MS GATE: mw dressing fields', gate_time , 0, MS_PULSE_SHAPING_TIME, MWOUT, dressingP1ms.fchan() + dressingM1ms.fchan() \
                                                                    + dressingP2ms.fchan() + dressingM2ms.fchan())
    addRFShapedPulse('MS Gate: rf red and blue sb', gate_time, 0, MS_PULSE_SHAPING_TIME, RFOUT,  rf_fields)
    addPulse('MS GATE', gate_time,0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msdetscan")
    mathparams = {"name" : "msdetscan", "detmode" : mode, "timemult" : timemult, "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, \
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MS gate det scan " + mode + ", det = " + str(det) + ", step = " + str(step))
    
    return makeSequence()

def msparitydetscan(mode = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    #Asymmetric and symmetric detuning scans of MS gate
    #Scan modes can be ASYM1, ASYM2, SYM
 
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    if mode == "ASYM1" :
        rf_fields = red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + blue1ms.fchan(freqdet =  SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + red2ms.fchan(freqdet =  - SYM_DET + ASYM_DET_2)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2)
        gate_time = MS_GATE_TIME 
    elif mode == "ASYM2" :
        rf_fields = red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1) \
                   + red2ms.fchan(freqdet =  - SYM_DET + ASYM_DET_2 + det, freqstep = step)  \
                   + blue2ms.fchan(freqdet =  SYM_DET + ASYM_DET_2 + det, freqstep = step)         
        gate_time = MS_GATE_TIME 
    elif mode == "ASYM12" :
        rf_fields = red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1 + det, freqstep  = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2 + det, freqstep = step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2 + det, freqstep = step)         
        gate_time =  MS_GATE_TIME 
    elif mode == "SYM" :
        rf_fields = red1ms.fchan(freqdet = - SYM_DET + ASYM_DET_1 + det, freqstep = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1 - det, freqstep = -step) \
                   + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2 + det, freqstep = step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2 - det, freqstep = -step)
        gate_time =  MS_GATE_TIME 
    elif mode == "POW1" :
        rf_fields = red1ms.fchan(freqdet =- SYM_DET + ASYM_DET_1 , ampdet = det, ampstep = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1, ampdet = det, ampstep = step) \
                   + red2ms.fchan(freqdet = -SYM_DET + ASYM_DET_2)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2 )
        gate_time =  MS_GATE_TIME 
    elif mode == "POW2" :
        rf_fields = red1ms.fchan(freqdet = -SYM_DET + ASYM_DET_1 ) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1) \
                   + red2ms.fchan(freqdet = -SYM_DET + ASYM_DET_2, ampdet = det, ampstep = step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2, ampdet = det, ampstep = step)
        gate_time = MS_GATE_TIME 
    elif mode == "POW12" :
        rf_fields = red1ms.fchan(freqdet = -SYM_DET + ASYM_DET_1, ampdet = det, ampstep = step) \
                   + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1, ampdet = det, ampstep = step) \
                   + red2ms.fchan(freqdet = -SYM_DET + ASYM_DET_2, ampdet = det, ampstep = step)  \
                   + blue2ms.fchan(freqdet = SYM_DET + ASYM_DET_2, ampdet = det, ampstep = step)
        gate_time =  MS_GATE_TIME 
    
    #Red and blue sidebands for both ions
    addRFShapedPulse('MS GATE: mw dressing fields', gate_time, 0, 0, MWOUT, dressingP1ms.fchan() + dressingM1ms.fchan() \
                                                                          + dressingP2ms.fchan() + dressingM2ms.fchan())
    addRFShapedPulse('MS Gate: rf red and blue sb', gate_time, 0, 0, RFOUT,  rf_fields)
    addPulse('MS GATE', gate_time, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Parity pi/2 pulse 
    addRFShapedPulse('Parity pi/2', D1.time/2, 0, 0, RFOUT, D1.fchan(phase = pi/2) + D2.fchan(phase = pi/2))
    addRFShapedPulse('Parity dressing fields', D1.time/2, 0, 0, MWOUT, dressingP1ms.fchan() + dressingM1ms.fchan() \
                                                                     + dressingP2ms.fchan() + dressingM2ms.fchan())
    addPulse('Parity pi/2', D1.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', clock1ms.time, 0, 0, MWOUT, clock1ms.fchan())
    addRFShapedPulse('Pi Clock', clock2ms.time, 0, 0, MWOUT,  clock2ms.fchan())
    addRFShapedPulse('RF padding', clock1ms.time + clock2ms.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1ms.time + clock2ms.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msgate")
    mathparams = {"name" : "msgate", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, \
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MS parity det scan " + mode + ", det = " + str(det) + ", step = " + str(step))
    
    return makeSequence()
  
def msMWpowermatch(state = "", det = 0, step = 0, steps = 0, runs = 0, delay = 0, calib = 0) :
    #Match powers of MS dressing fields with a Ramsey type experiment
    
    state = eval(state)
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    
    '''
    if state == D1 :
        dressing_fields = dressingP1ms.fchan() + dressingM1.fchan() \
                        + dressingP2ms.fchan(freqdet = -4000) + dressingM2ms.fchan(freqdet = 4000)
    elif state == D2 :
        dressing_fields = dressingP1ms.fchan(freqdet = -2000) + dressingM1.fchan(freqdet = 2000) \
                        + dressingP2ms.fchan() + dressingM2ms.fchan()
    '''
    
    dressing_fields = dressingP1ms.fchan() + dressingM1.fchan() \
                    + dressingP2ms.fchan() + dressingM2ms.fchan()
    
    #Pi pulse from 0 to clock for both ions, using states clock1 and clock2
    #00 -> 0'0'
    ramseyclock1 = clock1
    ramseyclock2 = clock2
    addRFShapedPulse('Pi Clock ion 1', ramseyclock1.time, 0, 0, MWOUT, ramseyclock1)
    addRFShapedPulse('Pi Clock ion 2', ramseyclock2.time, 0, 0, MWOUT, ramseyclcok2)
    addRFShapedPulse('RF padding', ramseyclock1.time + ramseyclock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', ramseyclock1.time + ramseyclock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Pi/2 pulse both ions
    #0'0' -> (0'0' + D'D')/sqrt(2)
    addRFShapedPulse('Pi/2 pulse on D', D1.time/2 + D2.time/2, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('Pi/2 pulse on D' , D1.time/2, 0, 0, RFOUT, D1.fchan())
    addRFShapedPulse('Pi/2 pulse on D' , D2.time/2, 0, 0, RFOUT, D2.fchan())
    addPulse('Pi/2 pulse on D', delay, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Padding for frist delay/2 
    addRFShapedPulse('Spin echo delay', delay/2, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('RF Padding', delay/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Spin echo delay', delay/2, 0, OPTS_AWG_MW_PULSE)
    
    #Pi pulse for spin echo 
    addRFShapedPulse('Pi pulse (spin echo)', D1.time + D2.time, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('Pi pulse (spin echo)', D1.time, 0, 0, RFOUT, D1.fchan())
    addRFShapedPulse('Pi pulse (spin echo)', D2.time, 0, 0, RFOUT, D2.fchan())
    addPulse('Pi pulse (spin echo)', D1.time + D2.time, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Padding for second delay/2
    addRFShapedPulse('Spin echo delay', delay/2, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('RF Padding', delay/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Spin echo delay', delay/2, 0, OPTS_AWG_MW_PULSE)
        
    #Pi pulse on clocks from 0'0' -> 00
    addRFShapedPulse('Pi Clock ion 1', ramseyclock1.time, 0, 0, MWOUT, ramseyclock1)
    addRFShapedPulse('Pi Clock ion 2', ramseyclock2.time, 0, 0, MWOUT, ramseyclcok2)
    addRFShapedPulse('RF padding', ramseyclock1.time + ramseyclock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', ramseyclock1.time + ramseyclock2.time, 0, opts = OPTS_AWG_MW_PULSE)
        
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps) 
    addParam("runs", runs)
    addParam("comment", "ramsey")
    mathparams = {"name" : "freqscan", "header" : state.header, "det" : det, "step" : step, "state" : state.name, 
                  "freq" : state.freq, "pitime" : state.time, "amp" : state.amp, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "MW power matching" + state.name + ", det = " + str(det) + ", step = " + str(step))
    
    return makeSequence()
  
def CNOTphase(steps = 0, runs = 0) :
    
    dressing_fields = dressingP1ms.fchan() + dressingM1ms.fchan() + dressingP2ms.fchan() + dressingM2ms.fchan()
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger                                                                                                                                                                                                                                                                    
    
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
        
    resetAWGPhase()
    
    
    #Y pi/2 ion 1
    addRFShapedPulse('Parity pi/2', D1.time/2, 0, 0, RFOUT, D1.fchan(phase = pi/2))
    addRFShapedPulse('Parity dressing fields', D1.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('Y pi/2 1', D1.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    phi1 = -1.556
    phi2 = -2.675
    
    #XX(pi/4) gate
    addRFShapedPulse('MS GATE: mw dressing fields', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, MWOUT, dressing_fields)
    
    addRFShapedPulse('MS Gate: rf red and blue sb', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, RFOUT, 
                                            red1ms.fchan(freqdet =  - SYM_DET + ASYM_DET_1, phase = phi1) 
                                          + blue1ms.fchan(freqdet = SYM_DET + ASYM_DET_1, phase = phi1) 
                                          + red2ms.fchan(freqdet = - SYM_DET + ASYM_DET_2, phase = phi2)  
                                          + blue2ms.fchan(freqdet =  SYM_DET + ASYM_DET_2, phase = phi2))
                                         
    addPulse('XX pi/4', MS_GATE_TIME , 0,  opts = OPTS_AWG_MWRF_PULSE)
        
        
    phi3 = -1.174 + phi1
    phi4 = -0.396 + phi2 
    
    #X -pi/2 ion 1
    addRFShapedPulse('Parity pi/2', 3* D1.time/2, 0, 0, RFOUT, D1.fchan(phase = phi3))
    addRFShapedPulse('Parity dressing fields', 3* D1.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('X -pi/2 1', 3* D1.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #X -pi/2 ion 2
    addRFShapedPulse('Parity pi/2', 3* D2.time/2, 0, 0, RFOUT, D2.fchan(phase = phi4))
    addRFShapedPulse('Parity dressing fields', 3* D2.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('X - pi/2 2', 3*D2.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Y -pi/2 ion 1
    addRFShapedPulse('Parity pi/2', 3*D1.time/2, 0, 0, RFOUT, D1.fchan(phase =  phi3))
    addRFShapedPulse('Parity dressing fields', 3*D1.time/2, 0, 0, MWOUT, dressing_fields)
    addPulse('Y - pi/2 1', 3*D1.time/2, 0, opts = OPTS_AWG_MWRF_PULSE)
    
    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "msparity")
    mathparams = {"name" : "msparity", "header" : '', "det" : 0, "step" : 0, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", 0)
    addParam("logmsg", "CNOT phase")
    
    return makeSequence()

'''         
def spanishgate(det = 0, step = 0, steps = 0, runs = 0, calib = 0):
   if det < 0 :
        det = 0 
    
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    _addSbCoolingPulse()
    
    #Pi pulse 0 -> 0' both ions
    addRFShapedPulse('Pi Clock', clock1esp.time, 0, 0, MWOUT, clock1esp.fchan())
    addRFShapedPulse('Pi Clock', clock2esp.time, 0, 0, MWOUT,  clock2esp.fchan())
    addRFShapedPulse('RF padding', clock1esp.time + clock2esp.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1esp.time + clock2esp.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Red sideband, blue sideband and carrier transitions for both ions 
    addRFShapedPulse('SPANISH GATE: mw carrier fields', det, step, ESP_PULSE_SHAPING_TIME, MWOUT, plus1esp.fchan() + plus2esp.fchan())
    addRFShapedPulse('SPANISH GATE: mw dressing fields', det, step, ESP_PULSE_SHAPING_TIME, MWOUT, dressingP1esp.fchan() + dressingM1esp.fchan() 
                                                                    + dressingP2esp.fchan() + dressingM2esp.fchan())
    addRFShapedPulse('SPANISH Gate: rf red and blue sb', det, step, ESP_PULSE_SHAPING_TIME, RFOUT, red1esp.fchan(freqdet =  - SYM_DET + ASYM_DET_1) 
                                                                                           + blue1esp.fchan(freqdet = SYM_DET + ASYM_DET_1) 
                                                                                           + red2esp.fchan(freqdet = - SYM_DET + ASYM_DET_2)  
                                                                                           + blue2esp.fchan(freqdet =  SYM_DET + ASYM_DET_2))
    addPulse('SPANISH GATE', det, step,  opts = OPTS_AWG_MWRF_PULSE)

    #Pi pulse 0' -> 0 both ions
    addRFShapedPulse('Pi Clock', clock1esp.time, 0, 0, MWOUT, clock1esp.fchan())
    addRFShapedPulse('Pi Clock', clock2esp.time, 0, 0, MWOUT,  clock2esp.fchan())
    addRFShapedPulse('RF padding', clock1esp.time + clock2esp.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Pi clock', clock1esp.time + clock2esp.time, 0, opts = OPTS_AWG_MW_PULSE)
    
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()
    
    addParam("steps", steps)
    addParam("runs", runs)
    addParam("comment", "spanishgate")
    mathparams = {"name" : "spanishgate", "header" : '', "det" : det, "step" : step, "state" : '', "freq" : 0, "pitime" : 0, 
                  "amp" : 0, "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    addParam("calib", calib)
    addParam("logmsg", "SPANISH gate, step = " + str(step))
    
    return makeSequence()
 '''  
#--------------------------------------------------------------------------------------------------------------------#
# QUANTUM CIRCUIT TOOLBOX
#--------------------------------------------------------------------------------------------------------------------#    

def InitQubits(sbcool = False) :
    #Assuming working in {0', D} basis, initialize qubits to 0'
    #Using states clock1 and clock2, might need to change in future
    _addPrepPulse()
    _addReadoutPulse(count = BACKGROUND_COUNT)
    _addPrepPulse(count = COOLING_COUNT)
    if sbcool == True :
        _addSbCoolingPulse()
    
    '''
    addRFShapedPulse('0->0\' qubit 1 and 2', clock1.time, 0, 0, MWOUT, clock1.fchan())
    addRFShapedPulse('0->0\' qubit 1 and 2', clock2.time, 0, 0, MWOUT, clock2.fchan())
    addRFShapedPulse('RF Padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Init Qubit 1', clock1.time, 0, opts = OPTS_AWG_MW_PULSE)
    addPulse('Init Qubit 2', clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    '''
    addRFShapedPulse('0->0\' qubit 1 and 2', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF Padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Init Qubit 1 and 2', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)

def Measure() :
    #Map back to 0/0'
    '''
    addRFShapedPulse('0->0\' qubit 1 and 2', clock1.time, 0, 0, MWOUT, clock1.fchan())
    addRFShapedPulse('0->0\' qubit 1 and 2', clock2.time, 0, 0, MWOUT, clock2.fchan())
    addRFShapedPulse('RF Padding', clock1.time + clock2.time, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Map Qubit 1', clock1.time, 0, opts = OPTS_AWG_MW_PULSE)
    addPulse('Map Qubit 2', clock2.time, 0, opts = OPTS_AWG_MW_PULSE)
    '''
    addRFShapedPulse('0->0\' qubit 1 and 2', (clock1ms.time + clock2ms.time)/2, 0, 0, MWOUT, clock1ms.fchan() + clock2ms.fchan())
    addRFShapedPulse('RF Padding', (clock1ms.time + clock2ms.time)/2, 0, 0, RFOUT, NULL_FCHAN)
    addPulse('Measure Qubits 1 and 2', (clock1ms.time + clock2ms.time)/2, 0, opts = OPTS_AWG_MW_PULSE)
    
    #Measure
    _addReadoutPulse(DET_COUNT_1)
    _addLineTrigPulse()

def Rx(theta, qubit) :
    #Apply x rotation with angle theta, phi = 0
    #Qubit = 0 -> ion 1 
    #Qubit = 1 -> ion 2
    pulse_name = 'RX, theta = %.2f'%theta + ', ion ' + str(qubit)
    
    if qubit == 0 : 
        state = D1
    elif qubit == 1:
        state= D2
        
    if theta < 0 :
        theta = -theta
        phi = - pi
    else :
        phi = 0
        
    tgate = state.time * theta/(pi)
    
    dressing_fields =  dressingP1ms.fchan() + dressingM1ms.fchan() + dressingP2ms.fchan() + dressingM2ms.fchan()
    addRFShapedPulse('X gate on ' + state.name, tgate, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('X gate on ' + state.name, tgate, 0, 0, RFOUT, state.fchan(phase = phi))
    addPulse(pulse_name, tgate, 0, opts = OPTS_AWG_MWRF_PULSE)
    
def Ry(theta, qubit) :
    #Apply y rotation with angle theta, phi = pi/2
    #Qubit = 0 -> ion 1 
    #Qubit = 1 -> ion 2
    pulse_name = 'RY, theta = %.2f'%theta + ', ion ' + str(qubit)
    
    if qubit == 0 : 
        state = D1
    elif qubit == 1:
        state= D2

    if theta < 0 :
        theta = - theta
        phi = 3 * pi /2
    else :
        phi = pi/2
    
    tgate = state.time * theta/(pi)
    
    dressing_fields =  dressingP1ms.fchan() + dressingM1ms.fchan() + dressingP2ms.fchan() + dressingM2ms.fchan()
    addRFShapedPulse('Y gate on ' + state.name, tgate, 0, 0, MWOUT, dressing_fields)
    addRFShapedPulse('Y gate on ' + state.name, tgate, 0, 0, RFOUT, state.fchan(phase = phi))
    addPulse(pulse_name, tgate, 0, opts = OPTS_AWG_MWRF_PULSE)

def CZ() : 
    #Apply cnot gate using spinspin coupling, only requires four microwave gate fields on
    addRFShapedPulse('CNOT', SS_GATE_TIME, 0, 0, MWOUT, dressingP1_gate.fchan() + dressingM1_gate.fchan() +
    dressingP2_gate.fchan() + dressingM2_gate.fchan())
    #addRFShapedPulse('RF padding' + state.name, state.time * theta/(pi), 0, 0, RFOUT, NULL_FCHAN)

def UMS(phistep = 0) :
    #Molmer-Sorensen Gate
    
    PHI0 = -1.884
    DELTA_PHI = 5.942
    PHI0 = 0
    DELTA_PHI = 3.14
    #Red and blue sidebands for both ions
    addRFShapedPulse('MS GATE: mw dressing fields', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, MWOUT, 
                                                    dressingP1ms.fchan() + dressingM1ms.fchan() 
                                                  + dressingP2ms.fchan() + dressingM2ms.fchan())
                                                  
    addRFShapedPulse('MS Gate: rf red and blue sb', MS_GATE_TIME, 0, MS_PULSE_SHAPING_TIME, RFOUT, 
                                                    red1ms.fchan(freqdet  = - SYM_DET + ASYM_DET_1, phase = PHI0, phasestep = phistep) 
                                                  + blue1ms.fchan(freqdet =   SYM_DET + ASYM_DET_1, phase = PHI0, phasestep = phistep) 
                                                  + red2ms.fchan(freqdet  = - SYM_DET + ASYM_DET_2, phase = PHI0 + DELTA_PHI, phasestep = phistep)  
                                                  + blue2ms.fchan(freqdet =   SYM_DET + ASYM_DET_2, phase = PHI0 + DELTA_PHI, phasestep = phistep))
    addPulse('MS GATE', MS_GATE_TIME, 0,  opts = OPTS_AWG_MWRF_PULSE)
    
    return 0 

def CNOT(phasestep = 0) :

    Ry(-pi/2, 0)
    Rx(-pi/2, 0)
    Rx(-pi/2, 1)
    UMS(phasestep)
    Ry(pi/2, 0)

def Mapping() :
    return 0


#--------------------------------------------------------------------------------------------------------------------#
# RIVERLANE CIRCUITS
#--------------------------------------------------------------------------------------------------------------------#    

#Initialisation circuits 

def Z0Z1() :
    return 0
    
def X0X1() :
    #Innit for X0X1
    Ry(-pi/2, 0)
    Ry(-pi/2, 1)   


def CNOTphase1(phasestep = 0, steps = 0, runs = 0) :
    
    #Innit Pulse sequence
    innitPulseList()
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    InitQubits(sbcool = True)
    
    resetAWGPhase()
    
    Rx(pi/2, 0)
    Rx(pi/2, 1)
    CNOT(phasestep)
    
    Measure()
    
    addParam('steps', steps)
    addParam('runs', runs)
    addParam('logmsg', 'CNOT phase scan, step = ' + str(phasestep))
    mathparams = {"name" : "calibcircuit", "det" : 0, "step" : 0, "state" : '', "freq" : 0, "pitime" : 0, "amp" : 0, 
                  "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    return makeSequence()
   

def RLcircuitZ0(state_param, subspace_param, steps = 0, runs = 0) :
    
    #Innit Pulse sequence
    innitPulseList()
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    InitQubits(sbcool = True)
    '''
    Ry(state_param, 0)
    UMS()
    Ry(- pi/2, 0)
    Rx(-pi/2, 0)
    Ry(-pi/2, 0)
    Rx(subspace_param, 1)
    UMS()
    Ry(pi/2, 1)
    '''
    CNOT()
    
    Measure()
    
    addParam('steps', steps)
    addParam('runs', runs)
    addParam('logmsg', 'RL: Calibcircuit, steps = ' + str(steps) + ', runs = ' + str(runs))
    mathparams = {"name" : "calibcircuit", "det" : 0, "step" : 0, "state" : '', "freq" : 0, "pitime" : 0, "amp" : 0, 
                  "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    return makeSequence()
    
def RLcircuitX0X1(state_param, subspace_param, steps = 0, runs = 0) :
    
    #Innit Pulse sequence
    innitPulseList()
    
    addPulse('AWG Trig delay', AWG_TRIG_DELAY, 0, opts = OPTS_AWG_TRIG) #Innit AWG Trigger
    
    InitQubits(sbcool = True)
    
    resetAWGPhase()
    
    Ry(state_param, 0)
    #UMS()
    Rx(pi/2, 0)
    Rx(-pi/2, 1)
    Ry(subspace_param, 1)
 
    Measure()
    
    addParam('steps', steps)
    addParam('runs', runs)
    addParam('logmsg', 'RL: Calibcircuit, steps = ' + str(steps) + ', runs = ' + str(runs))
    mathparams = {"name" : "calibcircuit", "det" : 0, "step" : 0, "state" : '', "freq" : 0, "pitime" : 0, "amp" : 0, 
                  "steps" : steps, "runs" : runs, 'err' : ERR_PARAMS}
    addParam("mathematica", str(mathparams))
    return makeSequence()
    
    
#--------------------------------------------------------------------------------------------------------------------#
# GLOBAL LOGIC 
#--------------------------------------------------------------------------------------------------------------------#   
'''

#def gl_rotation(phi = 0, theta = 0, pos = 0, qubit = 0):

    if pos == 1 and qubit == 1:
        state = P1_D1
    elif pos == 1 and qubit == 2:
        state = P1_D2
    elif pos == 2 and qubit == 1:
        state = P2_D1
    elif pos == 2 and qubit == 2:
        state = P2_D2
    
    tgate = theta/(2*pi) * (2 * state.time)
    
    addRFShapedPulse('Single Qubit Gate',  tgate, 0, 0, RFOUT, state.fchan(phase = phi))
    addRFShapedPulse('MW Dressing Fields', tgate, 0, 0, MWOUT, GL_DRESSING_FIELDS)    

    return tgate

def gl_1Q_gates(pos = 0) :
    
    pulse_time = 0
    
    pulse_time += gl_single_qubit_gate(phi = pi/2, theta = pi/2, pos = 1, qubit = 1)
    pulse_time += gl_single_qubit_gate(phi = pi, theta = pi/2, pos = 2, qubit = 1)
    pulse_time += gl_single_qubit_gate(phi = pi, theta = pi/2, pos = 2, qubit = 2)
    pulse_time += gl_single_qubit_gate(phi = -pi/2, theta = pi/2, pos = 2, qubit = 1)
    
    if pos == 1 :
        addPulse('SQgates, pos ' + str(pos), pulse_time, 0, OPTS_AWG_MWRF_PULSE)
    if pos == 2 :
        addPulse('SQgates, pos ' + str(pos), pulse_time, 0, OPTS_AWG_MWRF_PULSE_GL_POS2)
    
def gl_2Q_gate() :
    
    return 0
    
def gl_shuttle(pos = 0) :
    
    addRFPadding(GL_SHUTTLING_TIME)
    
    if pos == 1:
        addPulse('Shuttling pos ' + str(pos), GL_SHUTTLING_TIME)
    if pos == 2:
        addPulse('Shuttling pos ' + str(pos), GL_SHUTTLING_TIME, 0, opts = OPTS_GL_SHUTTLING)
    
    return 0


#def gl_sequence(det, step, steps, runs):

    innitPulseList()
    
    InitQubits() #Initialize qubits to |0'0'>
    
    #Do a first round of single qubit gates with ions in pos 1
    gl_1Q_gates()
    
    #Two qubit gate at pos 1
    gl_2Q_gates()
    
    #Shuttle ions to pos 2
    gl_shuttle(pos = 2)
    
    #Second round of single qubit gates with ions in pos 2
    gl_1Q_gates()
    
    return 0












'''

