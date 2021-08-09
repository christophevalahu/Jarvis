'''
    Author : Christophe Valahu and apprentice
    Last Modified : 15/04/19
    File : pulses.py
    
    Description : Builds a pulse sequence. Adds pulses to a global list and adds experiment parameters.
                  Converts low lvl pulse sequence to hardware.
    
    Output : JSON = {   "PulseSeq" : List of JSON pulse  = {  "enabled" (BOOL),
                                                              "string"  (STRING),
                                                              "time"    (FLOAT),
                                                              "step"    (INT),
                                                              "dio"     (bINT),
                                                              "count"   (bINT),
                                                              "trigger" (bINT),
                                                              "AO"      (bINT) }
                        "RFPulseSeq" : (STRING) sent to AWG
                        
                        "Params" : List of JSON params 

'''

import json
from RFparser import makeRFPulseString
import parameters as pm

def innitPulseList() :
    #Initialise global pulse variables
    global PulseSequence
    global PulseList
    global RFPulseList
    global ParamsList 
    
    PulseSequence = dict.fromkeys(('PulseSeq', 'RFPulseSeq', 'Params'))
    PulseList = []
    RFPulseList = []
    
    ParamsList= dict.fromkeys(('steps', 'runs', 'comment', 'mathematica', 'calib', 'logmsg', 'ndets'))
    ParamsList['ndets'] = 0
    ParamsList['steps'] = 0
    ParamsList['runs']  = 0
    ParamsList['comment'] = 'default'
    ParamsList['calib'] = 0
    ParamsList['logmsg'] = 'Default log msg'
    ParamsList['mathematica'] = "{'dummy':''}"
    
def getElapsedTime() :
    
    time = 0
    
    for pulse in PulseList :
        time = time + pulse['time'] + 0.125
        
    return time

def addParam(key, value):
	ParamsList[key] = value

def addPulse(name='name', time=0, step=0, count = 0, opts = {}):

    if time > 0.125 : 
        time = time  - 0.125 #125ns corresponds to the 5 cycles of the FPGA.
                             #Add this offset to compensate.

    enabled = True

    dio     = opts['dio']     if 'dio'     in opts else 0 
    trigger = opts['trigger'] if 'trigger' in opts else 0
    AO      = opts['AO']      if 'AO'      in opts else 0
    
    if count != 0 : ParamsList['ndets'] += 1
    
    newPulse = {'enabled':enabled, 'string':name, 'time':time, 'step':step, 'dio':dio,  'count':count, 'trigger':trigger, 'AO':AO}
    PulseList.append(newPulse)


def addRFShapedPulse(name='name', time=0, step=0, timeps=0, IQ=0, channels=[pm.NULL_FCHAN]):
    channelsInv = True
    for chan in channels:
        channelsInv = channelsInv and chan['channel inv'] # If any of the channel are variant, make inv false
    newRfPulse = {'type':'shapedPulse', 'string':name, 'time':time, 'step':step, 'timeps':timeps, 'IQ':IQ, 'chans':channels, 'pulse inv':step == 0 and channelsInv}
    RFPulseList.append(newRfPulse)

def resetAWGPhase() :
    newRfPulse = {'type':'resetPhase', 'string':'resetPhase', 'time':0, 'step':0, 'timeps':0, 'IQ':0, 'chans':[pm.NULL_FCHAN], 'pulse inv':True}
    RFPulseList.append(newRfPulse)

def addRFPadding(time ) :
    addRFShapedPulse('MW Padding', time, 0, 0, pm.MWOUT, pm.NULL_FCHAN)
    addRFShapedPulse('RF Padding', time, 0, 0, pm.RFOUT, pm.NULL_FCHAN)
    
def makeSequence():
    
    PulseSequence['PulseSeq'] = PulseList
    PulseSequence['RFPulseSeq'] = '== RF pulses ==\n' + makeRFPulseString(RFPulseList)
    PulseSequence['Params'] = ParamsList
    
    print(json.dumps(PulseSequence))
    
    
    
    
    
    
    