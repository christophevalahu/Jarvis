'''
    Author : Christophe Valahu and apprentice
    Last Modified : 15/04/19
    File : parameters.py
    
    Description : Parses cmd line input, contains hardware constants, pulse and state parameters
    
    Cmd args in : stepnum (INT)

'''


from states import *
import configparser
import argparse
import ast
import numpy as np
from math import sqrt, pi


#Get step number from cmd line
parser = argparse.ArgumentParser()
parser.add_argument("stepNum", help="step number", type=int)
args = parser.parse_args()
stepNum = args.stepNum

#Read config file
config = configparser.ConfigParser()
config.read('..\config\parameter_config.ini')



#--------------------------------------------------------------------------------------------------------------------#
# HARDWARE CONSTANTS
#--------------------------------------------------------------------------------------------------------------------# 

# Analog output addresses
AO1    = 0b0001
AO2    = 0b0010
AO3    = 0b0100 #RF generator for AOM, AO3 on = red detuned
AO4    = 0b1000 #Amplitude of RF signal for AOM, AO4 on = high power

TRIG1  = 0b0001

#Create Digital I/O address dictionary :
DIO = dict()
for i in range(40) :
    DIO[str(i)] = 1<<i

AOM = DIO['0']
EOM = DIO['1']
#Normally final TTL switch before MW horn (DIO2), though it broke.
#Now using switch before VSG mixing (DIO12)
UWAVE = DIO['12'] 

#TTL switches at each DDS MW output
MW1 = DIO['3']
MW2 = DIO['4']
MW3 = DIO['5']
MW4 = DIO['6']
MW5 = DIO['7']
MW6 = DIO['8']
MW7 = DIO['10']
MW8 = DIO['11']

RF1 = DIO['13']
RF2 = DIO['14']
RF3 = DIO['15']
RF4 = DIO['16']
RF5 = DIO['17'] #TTL switch for RF feeding into AOM
RF6 = DIO['18']
RF7 = DIO['20']
RF8 = DIO['21']

XM = DIO['12'] #Microwave TTL switch
XR = DIO['19'] #RF TTL switch

CAM = DIO['22'] #Camera address

AG_SWITCH = DIO['24']
AG_TRIG = DIO['25']
KEY_SWITCH = DIO['26']
KEY_TRIG = DIO['27'] #Trigger for AWG

#AWG channels
MWOUT = 2
RFOUT = 1


#--------------------------------------------------------------------------------------------------------------------#
# PULSE PARAMETERS
#--------------------------------------------------------------------------------------------------------------------#   

#State detection error parameters
ERR_PARAMS = {'err_pmt' :    {'t1' :  config['state_det_pmt'].getint('t1'), 'errm1' : ast.literal_eval(config['state_det_pmt'].get('errm1')),
                              't2' :  config['state_det_pmt'].getint('t2'), 'errm2' : ast.literal_eval(config['state_det_pmt'].get('errm2'))},
              'err_camera' : {'t1' :  config['state_det_camera'].getint('t1'), 'errm1' : ast.literal_eval(config['state_det_camera'].get('errm1')),
                              't2' :  config['state_det_camera'].getint('t2'), 'errm2' : ast.literal_eval(config['state_det_camera'].get('errm2'))}}
                        
# COOLING parameters
COOLING_DIO =  (UWAVE|AOM|RF5|KEY_SWITCH|XM) #DIOs needed for cooling: AOM/RF5 - 369 laser on, UWAVE|MW# - MWs on
OPTS_COOLING = {'dio' : COOLING_DIO, 'AO' : AO3} #AO3 - 369 red detuned
OPTS_COOLING_DDS = {'dio' : (UWAVE|AOM|RF5|MW5|MW6|MW7|MW8), 'AO' : AO3} 
COOL_TIME = config['Pulse_parameters'].getfloat('cooltime')

# PREPERATION parameters
PREP_DIO = (AOM|RF5|EOM) #DIOs need for preperation: AOM/RF5 - 369 laser on, EOM - 369 sideband on
OPTS_PREP = {'dio' : PREP_DIO, 'AO' : AO4} #AO4 - high power
PREP_TIME = config['Pulse_parameters'].getfloat('preptime')

# DETECTION PARAMETERS
DET_HARDWARE = config['Pulse_parameters'].get('dethardware')
if DET_HARDWARE == 'PMT' :
    DET_TIME = config['Pulse_parameters'].getfloat('dettimepmt')
    OPTS_DET = {'dio' : AOM|RF5} #AOM|RF5 - 369 on
elif DET_HARDWARE == 'CAMERA' :
    DET_TIME = config['Pulse_parameters'].getfloat('dettimecamera')
    OPTS_DET = {'dio' : AOM|RF5|CAM} #AOM|RF5 - 369 on, #trigger camera
 
# SIDEBAND COOLING PARAMETESR 
REPUMP_TIME = 20
#REPUMP_TIME = 30
SB_COOLING_TIMES = np.loadtxt(fname = '..\config\SB_TIMES.txt')
SB_COOLING_DIO = (UWAVE|KEY_SWITCH|XM)
OPTS_SB_COOLING = {'dio' : SB_COOLING_DIO, 'AO' : AO4}

AWG_TRIG_DELAY = 15.4 + 0.125 #Waiting time after sending trig signal to AWG
AO_DELAY_TIME = 20 
DET_DELAY_TIME = 100

OPTS_AO_DELAY = {'AO' : AO4}
OPTS_AWG_TRIG = {'dio' : KEY_TRIG}
OPTS_AWG_MW_PULSE = {'dio' : UWAVE|KEY_SWITCH|XM }
OPTS_AWG_RF_PULSE = {'dio' : UWAVE|KEY_SWITCH|XR }
OPTS_AWG_MWRF_PULSE = {'dio' : UWAVE|KEY_SWITCH|XM|XR }

OPTS_SEC_FREQ_SCAN = {'dio' : UWAVE|KEY_SWITCH|XR|AOM|RF5|XM|UWAVE, 'AO' : AO3 }

COOLING_COUNT = 1
BACKGROUND_COUNT = 2
DET_COUNT_1 = 4
DET_COUNT_2 = 8

SS_GATE_TIME = config['spinspingate'].getfloat('gatetime')

#--------------------------------------------------------------------------------------------------------------------#
# STATE PARAMETERS
#--------------------------------------------------------------------------------------------------------------------# 

probe         = State('probe', 'probe',
               config['Pulse_parameters'].getfloat('probefreq'), 
               config['Pulse_parameters'].getfloat('probetime'),
               config['Pulse_parameters'].getfloat('probeamp'))


# -------------   ION 1 -------------------

clock1         = State('clock1', 'ion_1',
               config['ion_1'].getfloat('clock1freq'), 
               config['ion_1'].getfloat('clock1time'),
               config['ion_1'].getfloat('clock1amp'))
plus1          = State('plus1', 'ion_1',
               config['ion_1'].getfloat('plus1freq'), 
               config['ion_1'].getfloat('plus1time'),
               config['ion_1'].getfloat('plus1amp'))
minus1          = State('minus1', 'ion_1',
               config['ion_1'].getfloat('minus1freq'), 
               config['ion_1'].getfloat('minus1time'),
               config['ion_1'].getfloat('minus1amp'))
dressingP1          = State('dressingP1', 'ion_1',
               plus1.freq, 
               config['ion_1'].getfloat('dressingP1time'),
               config['ion_1'].getfloat('dressingP1amp'))                
dressingM1          = State('dressingM1',  'ion_1',
               config['ion_1'].getfloat('minus1freq'), 
               config['ion_1'].getfloat('dressingM1time'),
               config['ion_1'].getfloat('dressingM1amp'))  
dressingP1.fields_on = dressingM1.fchan(freqdet = 2000)
dressingM1.fields_on = dressingP1.fchan(freqdet = -2000)
D1          = State('D1', 'ion_1',
               config['ion_1'].getfloat('D1freq'), 
               config['ion_1'].getfloat('D1time'),
               config['ion_1'].getfloat('D1amp'), 
               dressingP1.fchan() + dressingM1.fchan(),
               clock1)
       
# -------------   SIDEBAND COOLING -------------------       
               
SEC_FREQ_COM = config['sb_cooling'].getfloat('comfreq')
SEC_FREQ_STR = config['sb_cooling'].getfloat('strfreq')

pluscar1          = State('pluscar1', 'sb_cooling',
               plus1.freq, 
               config['sb_cooling'].getfloat('pluscar1time'),
               config['sb_cooling'].getfloat('pluscar1amp')) 
plusblue1          = State('plusblue1', 'sb_cooling',
               config['sb_cooling'].getfloat('plusblue1freq'), 
               config['sb_cooling'].getfloat('plusblue1time'),
               config['sb_cooling'].getfloat('plusblue1amp')) 
plusred1          = State('plusred1', 'sb_cooling',
               config['sb_cooling'].getfloat('plusred1freq'), 
               config['sb_cooling'].getfloat('plusred1time'),
               config['sb_cooling'].getfloat('plusred1amp')) 
               
Dcar1          = State('Dcar1', 'sb_cooling',
               D1.freq, 
               config['sb_cooling'].getfloat('Dcar1time'),
               config['sb_cooling'].getfloat('Dcar1amp'),
               dressingP1.fchan() + dressingM1.fchan(),
               clock1) 
Dblue1          = State('Dblue1', 'sb_cooling',
               config['sb_cooling'].getfloat('Dblue1freq'), 
               config['sb_cooling'].getfloat('Dblue1time'),
               config['sb_cooling'].getfloat('Dblue1amp'),
               dressingP1.fchan() + dressingM1.fchan(),
               clock1) 
Dred1          = State('Dred1', 'sb_cooling',
               config['sb_cooling'].getfloat('Dred1freq'), 
               config['sb_cooling'].getfloat('Dred1time'),
               config['sb_cooling'].getfloat('Dred1amp'),
               dressingP1.fchan() + dressingM1.fchan(),
               clock1) 
               
rf1          = State('RF 1', 'ion_1',
               config['ion_1'].getfloat('rf1freq'), 
               config['ion_1'].getfloat('rf1time'),
               config['ion_1'].getfloat('rf1amp'),
               dressingP1.fchan() + dressingM1.fchan(),
               clock1)        
               
# -------------   ION 2 -------------------
               
clock2         = State('clock2', 'ion_2',
               config['ion_2'].getfloat('clock2freq'), 
               config['ion_2'].getfloat('clock2time'),
               config['ion_2'].getfloat('clock2amp'))
plus2          = State('plus2', 'ion_2',
               config['ion_2'].getfloat('plus2freq'), 
               config['ion_2'].getfloat('plus2time'),
               config['ion_2'].getfloat('plus2amp'))               
minus2          = State('minus2', 'ion_2',
               config['ion_2'].getfloat('minus2freq'), 
               config['ion_2'].getfloat('minus2time'),
               config['ion_2'].getfloat('minus2amp'))               
dressingP2          = State('dressingP2',  'ion_2',
               plus2.freq,
               config['ion_2'].getfloat('dressingP2time'),
               config['ion_2'].getfloat('dressingP2amp'))
dressingM2          = State('dressingM2', 'ion_2',
               minus2.freq, 
               config['ion_2'].getfloat('dressingM2time'),
               config['ion_2'].getfloat('dressingM2amp'))     
dressingP2.fields_on = dressingM2.fchan(freqdet = 4000)
dressingM2.fields_on = dressingP2.fchan(freqdet = -4000)               
D2          = State('D2', 'ion_2',
               config['ion_2'].getfloat('D2freq'), 
               config['ion_2'].getfloat('D2time'),
               config['ion_2'].getfloat('D2amp'), 
               dressingP2.fchan() + dressingM2.fchan(),
               clock2) 
rf2          = State('RF 2', 'ion_2',
               config['ion_2'].getfloat('rf2freq'), 
               config['ion_2'].getfloat('rf2time'),
               config['ion_2'].getfloat('rf2amp'))  
               
# -------------   ION S -------------------               
               
clocks         = State('clocks', 'ion_s',
               config['ion_s'].getfloat('clocksfreq'), 
               config['ion_s'].getfloat('clockstime'),
               config['ion_s'].getfloat('clocksamp'))
pluss          = State('pluss', 'ion_s',
               config['ion_s'].getfloat('plussfreq'), 
               config['ion_s'].getfloat('plusstime'),
               config['ion_s'].getfloat('plussamp'))
minuss          = State('minuss', 'ion_s',
               config['ion_s'].getfloat('minussfreq'), 
               config['ion_s'].getfloat('minusstime'),
               config['ion_s'].getfloat('minussamp'))    
dressingPs          = State('dressingPs',  'ion_s',
               pluss.freq,
               config['ion_s'].getfloat('dressingPstime'),
               config['ion_s'].getfloat('dressingPsamp'))
dressingMs          = State('dressingMs', 'ion_s',
               minuss.freq, 
               config['ion_s'].getfloat('dressingMstime'),
               config['ion_s'].getfloat('dressingMsamp'))                    
Ds          = State('Ds', 'clock_s',
               config['ion_s'].getfloat('Dsfreq'), 
               config['ion_s'].getfloat('Dstime'),
               config['ion_s'].getfloat('Dsamp'), 
               dressingPs.fchan() + dressingMs.fchan(),
               clocks) 
 
# -------------   CDD MOLMER-SORENSEN GATE -------------------

CDD_GATE_TIME = config['cddgate'].getfloat('gatetime')
CDD_SYM_DET = config['cddgate'].getfloat('symdet')
CDD_ASYM1_DET = config['cddgate'].getfloat('asymdet1')
CDD_ASYM2_DET = config['cddgate'].getfloat('asymdet2')
CDD_PI_TIME = config['cddgate'].getfloat('pitime')
STR_FREQ = 382.757
cddplusred1  = State('cddplusred1', 'cddgate',
                     plus1.freq - STR_FREQ,
                     #config['cddgate'].getfloat('red1freq'),
                     config['cddgate'].getfloat('red1time'),
                     config['cddgate'].getfloat('red1amp')) 

cddplusblue1  = State('cddplusblue1', 'cddgate',
                     #config['cddgate'].getfloat('blue1freq'),
                     plus1.freq + STR_FREQ,
                     config['cddgate'].getfloat('blue1time'),
                     config['cddgate'].getfloat('blue1amp'))                        

cddplusred2  = State('cddplusred2', 'cddgate',
                     plus2.freq - STR_FREQ ,
                     #config['cddgate'].getfloat('red2freq'),
                     config['cddgate'].getfloat('red2time'),
                     config['cddgate'].getfloat('red2amp')) 

cddplusblue2  = State('cddplusblue2', 'cddgate',
                     plus2.freq + STR_FREQ ,
                     #config['cddgate'].getfloat('blue2freq'),
                     config['cddgate'].getfloat('blue2time'),
                     config['cddgate'].getfloat('blue2amp'))                        

cddpluscar1  = State('cddpluscar1', 'cddgate',
                     plus1.freq,
                     config['cddgate'].getfloat('car1time'),
                     config['cddgate'].getfloat('car1amp')) 

cddpluscar2  = State('cddpluscar2', 'cddgate',
                     plus2.freq,
                     config['cddgate'].getfloat('car2time'),
                     config['cddgate'].getfloat('car2amp')) 

cddplusred1.fields_on =  cddplusblue1.fchan(freqdet = +1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3) + cddpluscar1.fchan(freqdet = -1e3) + cddpluscar2.fchan(freqdet = +1e3)                    
cddplusblue1.fields_on =  cddplusred1.fchan(freqdet = -1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3) + cddpluscar1.fchan(freqdet = -1e3) + cddpluscar2.fchan(freqdet = +1e3)                    
cddplusred2.fields_on =  cddplusblue1.fchan(freqdet = +1e3) + cddplusred1.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3) + cddpluscar1.fchan(freqdet = -1e3) + cddpluscar2.fchan(freqdet = +1e3)                    
cddplusblue1.fields_on =  cddplusblue1.fchan(freqdet = +1e3) + cddplusred1.fchan(freqdet = -1e3) + cddplusred2.fchan(freqdet = -1e3) + cddpluscar1.fchan(freqdet = -1e3) + cddpluscar2.fchan(freqdet = +1e3)                    
                     
cddpluscar1.fields_on = cddplusred1.fchan(freqdet = -1e3) + cddplusblue1.fchan(freqdet = +1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3) + cddpluscar2.fchan(freqdet = +1e3)                    
#cddpluscar1.fields_on = cddpluscar2.fchan(freqdet = 5e3)
cddpluscar2.fields_on = cddplusred1.fchan(freqdet = -1e3) + cddplusblue1.fchan(freqdet = +1e3) + cddplusred2.fchan(freqdet = -1e3) + cddplusblue2.fchan(freqdet = +1e3) + cddpluscar1.fchan(freqdet = +1e3)                    
                     
cddpluspi1  = State('cddpluspi1', 'cddgate',
                     plus1.freq,
                     config['cddgate'].getfloat('pi1time'),
                     config['cddgate'].getfloat('pi1amp')) 

cddpluspi2  = State('cddpluspi2', 'cddgate',
                     plus2.freq,
                     config['cddgate'].getfloat('pi2time'),
                     config['cddgate'].getfloat('pi2amp')) 
                     
cddpluspi1.fields_on = cddpluspi2.fchan(freqdet = +2e3)
cddpluspi2.fields_on = cddpluspi1.fchan(freqdet = -2e3)
                     
# -------------   SPINSPIN GATE -------------------

SS_GATE_TIME = config['spinspingate'].getfloat('gatetime')             

dressingP1ss_map          = State('dressingP1', 'spinspingate',
               plus1.freq , 
               config['spinspingate'].getfloat('dressingP1time_map'),
               config['spinspingate'].getfloat('dressingP1amp_map'))                
dressingM1ss_map          = State('dressingM1',  'spinspingate',
               minus1.freq , 
               config['spinspingate'].getfloat('dressingM1time_map'),
               config['spinspingate'].getfloat('dressingM1amp_map')) 
dressingP2ss_map          = State('dressingP2', 'spinspingate',
               plus2.freq , 
               config['spinspingate'].getfloat('dressingP2time_map'),
               config['spinspingate'].getfloat('dressingP2amp_map'))                
dressingM2ss_map          = State('dressingM2',  'spinspingate',
               minus2.freq , 
               config['spinspingate'].getfloat('dressingM2time_map'),
               config['spinspingate'].getfloat('dressingM2amp_map'))

dressingP1ss_map.fields_on = dressingM1ss_map.fchan(freqdet = 2000) + dressingM2ss_map.fchan(freqdet = 4000) \
                         + dressingP2ss_map.fchan(freqdet = -4000)
dressingP2ss_map.fields_on = dressingM1ss_map.fchan(freqdet = 2000) + dressingM2ss_map.fchan(freqdet = 4000) \
                         + dressingP1ss_map.fchan(freqdet = -2000)
dressingM1ss_map.fields_on = dressingP1ss_map.fchan(freqdet = -2000) + dressingP2ss_map.fchan(freqdet = -4000) \
                         + dressingM2ss_map.fchan(freqdet = 4000)
dressingM2ss_map.fields_on = dressingP1ss_map.fchan(freqdet = -2000) + dressingP2ss_map.fchan(freqdet = -4000) \
                         + dressingM1ss_map.fchan(freqdet = 2000)
 
D1ss          = State('D1ss', 'spinspingate',
               D1.freq, 
               config['spinspingate'].getfloat('D1time'),
               config['spinspingate'].getfloat('D1amp'), 
               dressingP1ss_map.fchan() + dressingM1ss_map.fchan() , clock1, []) 
D2ss          = State('D2ss', 'spinspingate',
               D2.freq, 
               config['spinspingate'].getfloat('D2time'),
               config['spinspingate'].getfloat('D2amp'), 
               dressingP2ss_map.fchan() + dressingM2ss_map.fchan(), clock2, []) 
 
dressingP1ss_gate          = State('dressingP1', 'spinspingate',
               plus1.freq, 
               config['spinspingate'].getfloat('dressingP1time_gate'),
               config['spinspingate'].getfloat('dressingP1amp_gate'))                
dressingM1ss_gate          = State('dressingM1',  'spinspingate',
               minus1.freq, 
               config['spinspingate'].getfloat('dressingM1time_gate'),
               config['spinspingate'].getfloat('dressingM1amp_gate')) 
dressingP2ss_gate          = State('dressingP2', 'spinspingate',
               plus2.freq, 
               config['spinspingate'].getfloat('dressingP2time_gate'),
               config['spinspingate'].getfloat('dressingP2amp_gate'))                
dressingM2ss_gate          = State('dressingM2',  'spinspingate',
               minus2.freq, 
               config['spinspingate'].getfloat('dressingM2time_gate'),
               config['spinspingate'].getfloat('dressingM2amp_gate'))

dressingP1ss_gate.fields_on = dressingM1ss_gate.fchan(freqdet = 2000) + dressingM2ss_gate.fchan(freqdet = 4000) \
                         + dressingP2ss_gate.fchan(freqdet = -4000)
dressingP2ss_gate.fields_on = dressingM1ss_gate.fchan(freqdet = 2000) + dressingM2ss_gate.fchan(freqdet = 4000) \
                         + dressingP1ss_gate.fchan(freqdet = -2000)
dressingM1ss_gate.fields_on = dressingP1ss_gate.fchan(freqdet = -2000) + dressingP2ss_gate.fchan(freqdet = -4000) \
                         + dressingM2ss_gate.fchan(freqdet = 4000)
dressingM2ss_gate.fields_on = dressingP1ss_gate.fchan(freqdet = -2000) + dressingP2ss_gate.fchan(freqdet = -4000) \
                         + dressingM1ss_gate.fchan(freqdet = 2000)
                         

'''
#--------------   SPANISH GATE         -------------------
if config['spanishgate'].get('freqmode') == "COM" :
    ESP_SEC_FREQ = SEC_FREQ_COM
    ETA = config['spanishgate'].getfloat('cometa')
elif config['spanishgate'].get('freqmode') == "STR" :
    ESP_SEC_FREQ =  SEC_FREQ_COM * sqrt(3)
    ETA = config['spanishgate'].getfloat('streta')
else :
    ESP_SEC_FREQ = 0
    ETA = 0
ETA = 0.00537348
ESP_SEC_FREQ = config['spanishgate'].getfloat('strfreq')
ESP_OM_RF = config['spanishgate'].getfloat('OmRF')
ESP_LOOPS = config['spanishgate'].getfloat('msloops')
ESP_THETA_OFFSET = config['spanishgate'].getfloat('theta0')
    
SYM_DET = config['spanishgate'].getfloat('symdet')
ASYM_DET_1 = config['spanishgate'].getfloat('asymdet1')
ASYM_DET_2 = config['spanishgate'].getfloat('asymdet2')
MS_GATE_TIME = config['spanishgate'].getfloat('gatetime')
MS_PULSE_SHAPING_TIME = config['spanishgate'].getfloat('pstime') #Time to ramp up for pulse shaping

clock1esp       = State('clock1esp', 'spanishgate',
               clock1.freq, 
               config['spanishgate'].getfloat('clock1time'),
               config['spanishgate'].getfloat('clock1amp'))
clock2esp       = State('clock2esp', 'spanishgate',
               clock2.freq, 
               config['spanishgate'].getfloat('clock2time'),
               config['spanishgate'].getfloat('clock2amp'))
plus1esp          = State('plus1esp', 'spanishgate',
               config['spanishgate'].getfloat('plus1freq'), 
               config['spanishgate'].getfloat('plus1time'),
               config['spanishgate'].getfloat('plus1amp'))               
plus2esp          = State('plus2esp', 'spanishgate',
               config['spanishgate'].getfloat('plus2freq'), 
               config['spanishgate'].getfloat('plus2time'),
               config['spanishgate'].getfloat('plus2amp'))               
clock1esp.fields_on = clock2esp.fchan(freqdet = 200)
clock2esp.fields_on = clock1esp.fchan(freqdet = 200)

dressingP1esp          = State('dressingP1esp', 'spanishgate',
               plus1.freq , 
               config['spanishgate'].getfloat('dressingP1time'),
               config['spanishgate'].getfloat('dressingP1amp'))                
dressingM1esp          = State('dressingM1esp',  'spanishgate',
               minus1.freq , 
               config['spanishgate'].getfloat('dressingM1time'),
               config['spanishgate'].getfloat('dressingM1amp')) 
dressingP2esp          = State('dressingP2esp', 'spanishgate',
               plus2.freq , 
               config['spanishgate'].getfloat('dressingP2time'),
               config['spanishgate'].getfloat('dressingP2amp'))                
dressingM2esp          = State('dressingM2esp',  'spanishgate',
               minus2.freq , 
               config['spanishgate'].getfloat('dressingM2time'),
               config['spanishgate'].getfloat('dressingM2amp'))
               
D1esp          = State('D1', 'ion_1',
               D1.freq, 
               config['spanishgate'].getfloat('D1time'),
               config['spanishgate'].getfloat('D1amp'), 
               dressingP1esp.fchan() + dressingM1esp.fchan() +
               dressingP2esp.fchan(freqdet = -4000) + dressingM2esp.fchan(freqdet = 4000), clock1esp, []) 
               
D2ms          = State('D2', 'ion_2',
               D2.freq, 
               config['spanishgate'].getfloat('D2time'),
               config['spanishgate'].getfloat('D2amp'), 
               dressingP1esp.fchan(freqdet = -2000) + dressingM1esp.fchan(freqdet = 2000) +
               dressingP2esp.fchan() + dressingM2esp.fchan(), clock2esp, []) 
               
D1esp.fields_on = D2esp.fchan(freqdet = -4000)
D2esp.fields_on = D1esp.fchan(freqdet = -2000)

dressingP1esp.fields_on = dressingM1esp.fchan(freqdet = 2000) + dressingM2esp.fchan(freqdet = 4000) \
                         + dressingP2esp.fchan(freqdet = -4000)
dressingP2esp.fields_on = dressingM1esp.fchan(freqdet = 2000) + dressingM2esp.fchan(freqdet = 4000) \
                         + dressingP1esp.fchan(freqdet = -2000)
dressingM1esp.fields_on = dressingP1esp.fchan(freqdet = -2000) + dressingP2esp.fchan(freqdet = -4000) \
                         + dressingM2esp.fchan(freqdet = 4000)
dressingM2esp.fields_on = dressingP1esp.fchan(freqdet = -2000) + dressingP2esp.fchan(freqdet = -4000) \
                         + dressingM1esp.fchan(freqdet = 2000)

red1esp       = State('red1esp', 'spanishgate',
               D1esp.freq - ESP_SEC_FREQ, 
               config['spanishgate'].getfloat('red1time'),
               config['spanishgate'].getfloat('red1amp'))
red2esp       = State('red2esp', 'spanishgate',
               D2esp.freq - ESP_SEC_FREQ, 
               config['spanishgate'].getfloat('red2time'),
               config['spanishgate'].getfloat('red2amp')) 
blue1esp       = State('blue1esp', 'spanishgate',
               D1esp.freq + ESP_SEC_FREQ, 
               config['spanishgate'].getfloat('blue1time'),
               config['spanishgate'].getfloat('blue1amp'))
blue2esp       = State('blue2esp', 'spanishgate',
               D2esp.freq + ESP_SEC_FREQ, 
               config['spanishgate'].getfloat('blue2time'),
               config['spanishgate'].getfloat('blue2amp'))             
                         
Dstark1esp     = State('Dstark1esp', 'spanishgate',
               D1.freq + config['spanishgate'].getfloat('asymdet1'), 
               config['spanishgate'].getfloat('Dstark1time'),
               config['spanishgate'].getfloat('Dstark1amp'), 
               dressingP1esp.fchan() + dressingM1esp.fchan() +
               dressingP2esp.fchan(freqdet = -4000) + dressingM2esp.fchan(freqdet = 4000), clock1esp, []) 
Dstark2esp     = State('Dstark2esp', 'spanishgate',
               D2.freq + config['spanishgate'].getfloat('asymdet2'), 
               config['spanishgate'].getfloat('Dstark2time'),
               config['spanishgate'].getfloat('Dstark2amp'), 
               dressingP1esp.fchan(freqdet = -2000) + dressingM1esp.fchan(freqdet = 2000) +
               dressingP2esp.fchan() + dressingM2esp.fchan(), clock2esp, []) 

Dstark1esp.fields_on = red1esp.fchan(freqdet = -15) + blue1esp.fchan(freqdet = -15) + red2esp.fchan(freqdet = -15) + blue2esp.fchan(freqdet = -15)
Dstark2esp.fields_on = red1esp.fchan(freqdet = -15) + blue1esp.fchan(freqdet = -15) + red2esp.fchan(freqdet = -15) + blue2esp.fchan(freqdet = -15)
                         
'''
# -------------   MOLMER-SORENSEN GATE -------------------

if config['msgate'].get('freqmode') == "COM" :
    MS_SEC_FREQ = SEC_FREQ_COM
    ETA = config['msgate'].getfloat('cometa')
elif config['msgate'].get('freqmode') == "STR" :
    MS_SEC_FREQ =  SEC_FREQ_COM * sqrt(3)
    ETA = config['msgate'].getfloat('streta')
else :
    MS_SEC_FREQ = 0
    ETA = 0
ETA = 0.00537348
#MS_SEC_FREQ = SEC_FREQ_COM * sqrt(3)
MS_SEC_FREQ = config['msgate'].getfloat('strfreq')
MS_OM_RF = config['msgate'].getfloat('OmRF')
MS_LOOPS = config['msgate'].getfloat('msloops')
MS_THETA_OFFSET = config['msgate'].getfloat('theta0')
    
SYM_DET = config['msgate'].getfloat('symdet')
ASYM_DET_1 = config['msgate'].getfloat('asymdet1')
ASYM_DET_2 = config['msgate'].getfloat('asymdet2')
MS_GATE_TIME = config['msgate'].getfloat('gatetime')
MS_PULSE_SHAPING_TIME = config['msgate'].getfloat('pstime') #Time to ramp up for pulse shaping

clock1ms       = State('clock1ms', 'msgate',
               clock1.freq, 
               config['msgate'].getfloat('clock1time'),
               config['msgate'].getfloat('clock1amp'))
clock2ms       = State('clock2ms', 'msgate',
               clock2.freq, 
               config['msgate'].getfloat('clock2time'),
               config['msgate'].getfloat('clock2amp'))
               
clock1ms.fields_on = clock2ms.fchan(freqdet = 200)
clock2ms.fields_on = clock1ms.fchan(freqdet = 200)

dressingP1ms          = State('dressingP1ms', 'msgate',
               plus1.freq , 
               config['msgate'].getfloat('dressingP1time'),
               config['msgate'].getfloat('dressingP1amp'))                
dressingM1ms          = State('dressingM1ms',  'msgate',
               minus1.freq , 
               config['msgate'].getfloat('dressingM1time'),
               config['msgate'].getfloat('dressingM1amp')) 
dressingP2ms          = State('dressingP2ms', 'msgate',
               plus2.freq , 
               config['msgate'].getfloat('dressingP2time'),
               config['msgate'].getfloat('dressingP2amp'))                
dressingM2ms          = State('dressingM2ms',  'msgate',
               minus2.freq , 
               config['msgate'].getfloat('dressingM2time'),
               config['msgate'].getfloat('dressingM2amp'))
               
D1ms          = State('D1', 'ion_1',
               D1.freq, 
               config['msgate'].getfloat('D1time'),
               config['msgate'].getfloat('D1amp'), 
               dressingP1ms.fchan() + dressingM1ms.fchan() +
               dressingP2ms.fchan(freqdet = -1e3) + dressingM2ms.fchan(freqdet = 1e3), clock1, []) 
               
D2ms          = State('D2', 'ion_2',
               D2.freq, 
               config['msgate'].getfloat('D2time'),
               config['msgate'].getfloat('D2amp'), 
               dressingP1ms.fchan(freqdet = -1e3) + dressingM1ms.fchan(freqdet = 1e3) +
               dressingP2ms.fchan() + dressingM2ms.fchan(), clock2, []) 
               
D1phase          = State('D1phase', 'ion_1',
               D1.freq, 
               config['msgate'].getfloat('Dphase1time'),
               config['msgate'].getfloat('Dphase1amp'), 
               dressingP1ms.fchan() + dressingM1ms.fchan() +
               dressingP2ms.fchan(freqdet = -1e3) + dressingM2ms.fchan(freqdet = 1e3), clock1, []) 
               
D2phase          = State('D2phase', 'ion_2',
               D2.freq, 
               config['msgate'].getfloat('Dphase2time'),
               config['msgate'].getfloat('Dphase2amp'), 
               dressingP1ms.fchan(freqdet = -1e3) + dressingM1ms.fchan(freqdet = 1e3) +
               dressingP2ms.fchan() + dressingM2ms.fchan(), clock2, []) 
               
#D1ms.fields_on = D2ms.fchan(freqdet = -4000)
#D2ms.fields_on = D1ms.fchan(freqdet = -2000)

dressingP1ms.fields_on = dressingM1ms.fchan(freqdet = 2000) + dressingM2ms.fchan(freqdet = 4000) \
                         + dressingP2ms.fchan(freqdet = -4000)
dressingP2ms.fields_on = dressingM1ms.fchan(freqdet = 2000) + dressingM2ms.fchan(freqdet = 4000) \
                         + dressingP1ms.fchan(freqdet = -2000)
dressingM1ms.fields_on = dressingP1ms.fchan(freqdet = -2000) + dressingP2ms.fchan(freqdet = -4000) \
                         + dressingM2ms.fchan(freqdet = 4000)
dressingM2ms.fields_on = dressingP1ms.fchan(freqdet = -2000) + dressingP2ms.fchan(freqdet = -4000) \
                         + dressingM1ms.fchan(freqdet = 2000)

red1ms       = State('red1ms', 'msgate',
               D1ms.freq - MS_SEC_FREQ, 
               config['msgate'].getfloat('red1time'),
               config['msgate'].getfloat('red1amp'))
red2ms       = State('red2ms', 'msgate',
               D2ms.freq - MS_SEC_FREQ, 
               config['msgate'].getfloat('red2time'),
               config['msgate'].getfloat('red2amp')) 
blue1ms       = State('blue1ms', 'msgate',
               D1ms.freq + MS_SEC_FREQ, 
               config['msgate'].getfloat('blue1time'),
               config['msgate'].getfloat('blue1amp'))
blue2ms       = State('blue2ms', 'msgate',
               D2ms.freq + MS_SEC_FREQ, 
               config['msgate'].getfloat('blue2time'),
               config['msgate'].getfloat('blue2amp'))             
                         
Dstark1ms     = State('Dstark1ms', 'msgate',
               D1.freq + config['msgate'].getfloat('asymdet1'), 
               config['msgate'].getfloat('Dstark1time'),
               config['msgate'].getfloat('Dstark1amp'), 
               dressingP1ms.fchan() + dressingM1ms.fchan() +
               dressingP2ms.fchan(freqdet = -4000) + dressingM2ms.fchan(freqdet = 4000), clock1ms, []) 
Dstark2ms     = State('Dstark2ms', 'msgate',
               D2.freq + config['msgate'].getfloat('asymdet2'), 
               config['msgate'].getfloat('Dstark2time'),
               config['msgate'].getfloat('Dstark2amp'), 
               dressingP1ms.fchan(freqdet = -2000) + dressingM1ms.fchan(freqdet = 2000) +
               dressingP2ms.fchan() + dressingM2ms.fchan(), clock2ms, []) 

Dstark1ms.fields_on = red1ms.fchan(freqdet = -15) + blue1ms.fchan(freqdet = -15) + red2ms.fchan(freqdet = -15) + blue2ms.fchan(freqdet = -15)
Dstark2ms.fields_on = red1ms.fchan(freqdet = -15) + blue1ms.fchan(freqdet = -15) + red2ms.fchan(freqdet = -15) + blue2ms.fchan(freqdet = -15)


'''
# -------------   MOLMER-SORENSEN TWO TONE GATE -------------------

if config['mstwotonegate'].get('freqmode') == "COM" :
    MS_SEC_FREQ = SEC_FREQ_COM
    ETA = config['mstwotonegate'].getfloat('cometa')
elif config['mstwotonegate'].get('freqmode') == "STR" :
    MS_SEC_FREQ =  SEC_FREQ_COM * sqrt(3)
    ETA = config['mstwotonegate'].getfloat('streta')
else :
    MS_SEC_FREQ = 0
    ETA = 0
ETA = 0.00537348
#MS_SEC_FREQ = SEC_FREQ_COM * sqrt(3)
MS_SEC_FREQ = config['mstwotonegate'].getfloat('strfreq')
MS_OM_RF = config['mstwotonegate'].getfloat('OmRF')
MS_LOOPS = config['mstwotonegate'].getfloat('msloops')
MS_THETA_OFFSET = config['mstwotonegate'].getfloat('theta0')
    
SYM_DET = config['mstwotonegate'].getfloat('symdet')
ASYM_DET_1 = config['mstwotonegate'].getfloat('asymdet1')
ASYM_DET_2 = config['mstwotonegate'].getfloat('asymdet2')
MS_GATE_TIME = config['mstwotonegate'].getfloat('gatetime')
MS_PULSE_SHAPING_TIME = config['mstwotonegate'].getfloat('pstime') #Time to ramp up for pulse shaping

clock1ms       = State('clock1ms', 'mstwotonegate',
               clock1.freq, 
               config['mstwotonegate'].getfloat('clock1time'),
               config['mstwotonegate'].getfloat('clock1amp'))
clock2ms       = State('clock2ms', 'mstwotonegate',
               clock2.freq, 
               config['mstwotonegate'].getfloat('clock2time'),
               config['mstwotonegate'].getfloat('clock2amp'))
               
clock1ms.fields_on = clock2ms.fchan(freqdet = 200)
clock2ms.fields_on = clock1ms.fchan(freqdet = 200)

dressingP1ms          = State('dressingP1ms', 'mstwotonegate',
               plus1.freq , 
               config['mstwotonegate'].getfloat('dressingP1time'),
               config['mstwotonegate'].getfloat('dressingP1amp'))                
dressingM1ms          = State('dressingM1ms',  'mstwotonegate',
               minus1.freq , 
               config['mstwotonegate'].getfloat('dressingM1time'),
               config['mstwotonegate'].getfloat('dressingM1amp')) 
dressingP2ms          = State('dressingP2ms', 'mstwotonegate',
               plus2.freq , 
               config['mstwotonegate'].getfloat('dressingP2time'),
               config['mstwotonegate'].getfloat('dressingP2amp'))                
dressingM2ms          = State('dressingM2ms',  'mstwotonegate',
               minus2.freq , 
               config['mstwotonegate'].getfloat('dressingM2time'),
               config['mstwotonegate'].getfloat('dressingM2amp'))
               
D1ms          = State('D1', 'ion_1',
               D1.freq, 
               config['mstwotonegate'].getfloat('D1time'),
               config['mstwotonegate'].getfloat('D1amp'), 
               dressingP1ms.fchan() + dressingM1ms.fchan() +
               dressingP2ms.fchan(freqdet = -4000) + dressingM2ms.fchan(freqdet = 4000), clock1ms, []) 
               
D2ms          = State('D2', 'ion_2',
               D2.freq, 
               config['mstwotonegate'].getfloat('D2time'),
               config['mstwotonegate'].getfloat('D2amp'), 
               dressingP1ms.fchan(freqdet = -2000) + dressingM1ms.fchan(freqdet = 2000) +
               dressingP2ms.fchan() + dressingM2ms.fchan(), clock2ms, []) 
               
D1ms.fields_on = D2ms.fchan(freqdet = -4000)
D2ms.fields_on = D1ms.fchan(freqdet = -2000)

dressingP1ms.fields_on = dressingM1ms.fchan(freqdet = 2000) + dressingM2ms.fchan(freqdet = 4000) \
                         + dressingP2ms.fchan(freqdet = -4000)
dressingP2ms.fields_on = dressingM1ms.fchan(freqdet = 2000) + dressingM2ms.fchan(freqdet = 4000) \
                         + dressingP1ms.fchan(freqdet = -2000)
dressingM1ms.fields_on = dressingP1ms.fchan(freqdet = -2000) + dressingP2ms.fchan(freqdet = -4000) \
                         + dressingM2ms.fchan(freqdet = 4000)
dressingM2ms.fields_on = dressingP1ms.fchan(freqdet = -2000) + dressingP2ms.fchan(freqdet = -4000) \
                         + dressingM1ms.fchan(freqdet = 2000)

red11ms       = State('red11ms', 'mstwotonegate',
               D1ms.freq - MS_SEC_FREQ, 
               config['mstwotonegate'].getfloat('red11time'),
               config['mstwotonegate'].getfloat('red11amp'))
red12ms       = State('red12ms', 'mstwotonegate',
               D2ms.freq - MS_SEC_FREQ, 
               config['mstwotonegate'].getfloat('red12time'),
               config['mstwotonegate'].getfloat('red12amp')) 
blue11ms      = State('blue11ms', 'mstwotonegate',
               D1ms.freq + MS_SEC_FREQ, 
               config['mstwotonegate'].getfloat('blue11time'),
               config['mstwotonegate'].getfloat('blue11amp'))
blue12ms      = State('blue12ms', 'mstwotonegate',
               D2ms.freq + MS_SEC_FREQ, 
               config['mstwotonegate'].getfloat('blue12time'),
               config['mstwotonegate'].getfloat('blue12amp'))   
red21ms       = State('red21ms', 'mstwotonegate',
               D1ms.freq - 2*MS_SEC_FREQ, 
               config['mstwotonegate'].getfloat('red21time'),
               config['mstwotonegate'].getfloat('red21amp'))
red22ms       = State('red22ms', 'mstwotonegate',
               D2ms.freq - 2*MS_SEC_FREQ, 
               config['mstwotonegate'].getfloat('red22time'),
               config['mstwotonegate'].getfloat('red22amp')) 
blue21ms      = State('blue21ms', 'mstwotonegate',
               D1ms.freq + 2*MS_SEC_FREQ, 
               config['mstwotonegate'].getfloat('blue21time'),
               config['mstwotonegate'].getfloat('blue21amp'))
blue22ms      = State('blue22ms', 'mstwotonegate',
               D2ms.freq + 2*MS_SEC_FREQ, 
               config['mstwotonegate'].getfloat('blue22time'),
               config['mstwotonegate'].getfloat('blue22amp'))                  
                         
Dstark1ms     = State('Dstark1ms', 'mstwotonegate',
               D1.freq + config['mstwotonegate'].getfloat('asymdet1'), 
               config['mstwotonegate'].getfloat('Dstark1time'),
               config['mstwotonegate'].getfloat('Dstark1amp'), 
               dressingP1ms.fchan() + dressingM1ms.fchan() +
               dressingP2ms.fchan(freqdet = -4000) + dressingM2ms.fchan(freqdet = 4000), clock1ms, []) 
Dstark2ms     = State('Dstark2ms', 'mstwotonegate',
               D2.freq + config['mstwotonegate'].getfloat('asymdet2'), 
               config['mstwotonegate'].getfloat('Dstark2time'),
               config['mstwotonegate'].getfloat('Dstark2amp'), 
               dressingP1ms.fchan(freqdet = -2000) + dressingM1ms.fchan(freqdet = 2000) +
               dressingP2ms.fchan() + dressingM2ms.fchan(), clock2ms, []) 

Dstark1ms.fields_on = red11ms.fchan(freqdet = -15) + blue11ms.fchan(freqdet = -15) + red12ms.fchan(freqdet = -15) + blue12ms.fchan(freqdet = -15) + red21ms.fchan(freqdet = -15) + blue21ms.fchan(freqdet = -15) + red22ms.fchan(freqdet = -15) + blue22ms.fchan(freqdet = -15)
Dstark2ms.fields_on = red11ms.fchan(freqdet = -15) + blue11ms.fchan(freqdet = -15) + red12ms.fchan(freqdet = -15) + blue12ms.fchan(freqdet = -15) + red21ms.fchan(freqdet = -15) + blue21ms.fchan(freqdet = -15) + red22ms.fchan(freqdet = -15) + blue22ms.fchan(freqdet = -15)
'''
# -------------   GLOBAL LOGIC -------------------
'''
#Definitions for position 1 :
P1_clock1         = clock1
P1_D1             = D1
P1_clock2         = clock2
P1_D2             = D2

P2_clock1     = State('P2_clock1', 'globallogic',
               config['globallogic'].getfloat('P2_clock1freq'), 
               config['globallogic'].getfloat('P2_clock1time'),
               config['globallogic'].getfloat('P2_clock1amp'))
               
P2_clock2     = State('P2_clock2', 'globallogic',
               config['globallogic'].getfloat('P2_clock2freq'), 
               config['globallogic'].getfloat('P2_clock2time'),
               config['globallogic'].getfloat('P2_clock2amp'))               
               
'''
'''
#Definitions for position 2 :               

P2_plus1     = State('P2_plus1', 'globallogic',
               config['globallogic'].getfloat('P1_plus1freq'), 
               plus1.time,
               plus1.amp, 
               dressingP1.fchan() + dressingM1.fchan())
P2_minus1     = State('P2_minus1', 'globallogic',
               config['globallogic'].getfloat('P1_minus1freq'), 
               minus1.time,
               minus1.amp, 
               dressingP1.fchan() + dressingM1.fchan(),
               clock1)
P2_plus2     = State('P2_plus2', 'globallogic',
               config['globallogic'].getfloat('P2_plus2freq'), 
               plus2.time,
               plus2.amp, 
               dressingP1.fchan() + dressingM1.fchan())
P2_minus2     = State('P2_minus2', 'globallogic',
               config['globallogic'].getfloat('P2_minus2freq'), 
               minus2.time,
               minus2.amp, 
               dressingP1.fchan() + dressingM1.fchan())
               
#Four dressing fields for position 1
P1_dressingP1  = State('P1_dressingP1', 'globallogic',
               plus1.freq, 
               config['globallogic'].getfloat('P1_dressingP1time'),
               config['globallogic'].getfloat('P1_dressingP1amp'))                
P1_dressingM1  = State('P1_dressingM1',  'globallogic',
               minus1.freq, 
               config['globallogic'].getfloat('P1_dressingM1time'),
               config['globallogic'].getfloat('P1_dressingM1amp'))  
P1_dressingP2  = State('P1_dressingP2', 'globallogic',
               plus2.freq, 
               config['globallogic'].getfloat('P1_dressingP2time'),
               config['globallogic'].getfloat('P1_dressingP2amp'))                
P1_dressingM2  = State('P1_dressingM2',  'globallogic',
               minus2.freq, 
               config['globallogic'].getfloat('P1_dressingM2time'),
               config['globallogic'].getfloat('P1_dressingM2amp'))

#Four dressing fields for position 2   
P2_dressingP1  = State('P2_dressingP1', 'globallogic',
               P2_plus1.freq, 
               config['globallogic'].getfloat('P2_dressingP1time'),
               config['globallogic'].getfloat('P2_dressingP1amp'))                
P2_dressingM1  = State('P2_dressingM1',  'globallogic',
               P2_minus1.freq, 
               config['globallogic'].getfloat('P2_dressingM1time'),
               config['globallogic'].getfloat('P2_dressingM1amp'))  
P2_dressingP2  = State('P2_dressingP2', 'globallogic',
               P2_plus2.freq, 
               config['globallogic'].getfloat('P2_dressingP2time'),
               config['globallogic'].getfloat('P2_dressingP2amp'))                
P2_dressingM2  = State('P2_dressingM2',  'globallogic',
               P2_minus2.freq, 
               config['globallogic'].getfloat('P2_dressingM2time'),
               config['globallogic'].getfloat('P2_dressingM2amp'))

P1_dressingP1.fields_on = P1_dressingM1.fchan(freqdet = 2000) + \
                          P1_dressingP2.fchan(freqdet = -4000) + P1_dressingM2.fchan(freqdet = 4000) + \
                          P2_dressingP1.fchan(freqdet = -3000) + P2_dressingM1.fchan(freqdet = 3000) + \
                          P2_dressingP2.fchan(freqdet = -5000) + P2_dressingM2.fchan(freqdet = 5000)
P1_dressingM1.fields_on = P1_dressingP1.fchan(freqdet = -2000) + \
                          P1_dressingP2.fchan(freqdet = -4000) + P1_dressingM2.fchan(freqdet = 4000) + \
                          P2_dressingP1.fchan(freqdet = -3000) + P2_dressingM1.fchan(freqdet = 3000) + \
                          P2_dressingP2.fchan(freqdet = -5000) + P2_dressingM2.fchan(freqdet = 5000)
P1_dressingP2.fields_on = P1_dressingP1.fchan(freqdet = -2000) +  P1_dressingM1.fchan(freqdet = 2000) + \
                          P1_dressingM2.fchan(freqdet = 4000) + \
                          P2_dressingP1.fchan(freqdet = -3000) + P2_dressingM1.fchan(freqdet = 3000) + \
                          P2_dressingP2.fchan(freqdet = -5000) + P2_dressingM2.fchan(freqdet = 5000)
P1_dressingM2.fields_on = P1_dressingP1.fchan(freqdet = -2000) + P1_dressingP1.fchan(freqdet = -2000) + \
                          P1_dressingP2.fchan(freqdet = -4000) + \
                          P2_dressingP1.fchan(freqdet = -3000) + P2_dressingM1.fchan(freqdet = 3000) + \
                          P2_dressingP2.fchan(freqdet = -5000) + P2_dressingM2.fchan(freqdet = 5000)
P2_dressingP1.fields_on = P1_dressingP1.fchan(freqdet = -2000) + P1_dressingP1.fchan(freqdet = -2000) + \
                          P1_dressingP2.fchan(freqdet = -4000) + P1_dressingM2.fchan(freqdet = 4000) + \
                          P2_dressingM1.fchan(freqdet = 3000) + \
                          P2_dressingP2.fchan(freqdet = -5000) + P2_dressingM2.fchan(freqdet = 5000) 
P2_dressingM1.fields_on = P1_dressingP1.fchan(freqdet = -2000) + P1_dressingP1.fchan(freqdet = -2000) + \
                          P1_dressingP2.fchan(freqdet = -4000) + P1_dressingM2.fchan(freqdet = 4000) + \
                          P2_dressingP1.fchan(freqdet = -3000) + \
                          P2_dressingP2.fchan(freqdet = -5000) + P2_dressingM2.fchan(freqdet = 5000)                          
P2_dressingP2.fields_on = P1_dressingP1.fchan(freqdet = -2000) + P1_dressingP1.fchan(freqdet = -2000) + \
                          P1_dressingP2.fchan(freqdet = -4000) + P1_dressingM2.fchan(freqdet = 4000) + \
                          P2_dressingP1.fchan(freqdet = -3000) + P2_dressingM1.fchan(freqdet = 3000) + \
                          P2_dressingM2.fchan(freqdet = 5000)   
P2_dressingM2.fields_on = P1_dressingP1.fchan(freqdet = -2000) + P1_dressingP1.fchan(freqdet = -2000) + \
                          P1_dressingP2.fchan(freqdet = -4000) + P1_dressingM2.fchan(freqdet = 4000) + \
                          P2_dressingP1.fchan(freqdet = -3000) + P2_dressingM1.fchan(freqdet = 3000) + \
                          P2_dressingP2.fchan(freqdet = -5000) 

GL_DRESSING_FIELDS = P1_dressingP1.fchan() + P1_dressingM1.fchan() + P1_dressingP2.fchan() + P1_dressingM2.fchan() + \
                     P2_dressingP2.fchan() + P2_dressingM1.fchan() + P2_dressingP2.fchan() + P2_dressingM2.fchan()

#Dressing fields used to measure D freq at position 2
P2_D1_dressingP1 = dressingP1
P2_D1_dressingP1.freq = P1_plus1.freq
P2_D1_dressingM1 = dressingM1
P2_D1_dressingM1.freq = P1_minus1.freq

P2_D2_dressingP2 = dressingP2
P2_D2_dressingP2.freq = P1_plus2.freq
P2_D2_dressingM2 = dressingM2
P2_D2_dressingM2.freq = P1_minus2.freq
                       
P2_D1        = State('P2_D1', 'globallogic',
               config['globallogic'].getfloat('P2_D1freq'), 
               D1.time,
               D1.amp, 
               P2_D1_dressingP1.fchan() + P2_D1_dressingM1.fchan(), clock1)     
P2_D2        = State('P2_D2', 'globallogic',
               config['globallogic'].getfloat('P2_D2freq'), 
               D2.time,
               D2.amp, 
               P2_D2_dressingP2.fchan() + P2_D2_dressingM2.fchan(), clock1)  

GL_SHUTTLE_TIME = config['globallogic'].getfloat('shuttletime')    

GL_SHUTTLING_DIO = DIO['13'] #Need to change this DIO to the correct TTL output
OPTS_GL_SHUTTLING = {'dio' : GL_SHUTTLING_DIO}  
OPTS_AWG_MWRF_PULSE_GL_POS2 = {'dio' : UWAVE|KEY_SWITCH|XM|XR|GL_SHUTTLING_DIO }
                         
'''                  

#--------------------------------------------------------------------------------------------------------------------#
# AWG CHANNELS
#--------------------------------------------------------------------------------------------------------------------#                
NULL_FCHAN = [{'freq':0, 'freq step':0, 'amp':0, 'amp step':0, 'phase':0, 'phase step':0, 'channel inv':True}]
COOLING_FCHAN = minus1.cooling_fchan() + plus1.cooling_fchan() + minus2.cooling_fchan() + plus2.cooling_fchan() # + clock1.cooling_fchan() + clock2.cooling_fchan() 
#COOLING_FCHAN =  minus1.cooling_fchan() + plus1.cooling_fchan() + minus2.cooling_fchan() + plus2.cooling_fchan() # + clock1.cooling_fchan() + clock2.cooling_fchan() 
#COOLING_FCHAN =  pluss.cooling_fchan() + minuss.cooling_fchan() # + clocks.cooling_fchan()


#--------------------------------------------------------------------------------------------------------------------#
# RIVERLANE CIRCUITS
#--------------------------------------------------------------------------------------------------------------------#  

GS_SUBSPACE_PARAM = pi/2
GS_STATE_PARAM = 1.796361996




   