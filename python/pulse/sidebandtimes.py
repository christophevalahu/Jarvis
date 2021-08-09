# -*- coding: utf-8 -*-
"""
Created on Wed Jan  7 10:35:13 2015

@author: Andrea Rodriguez (Modified by Christophe Valahu)

Cmd args in : JSON params = {   "nlevels" : (INT)   Maximum n to calculate, 
                                "nbar"    : (FLOAT) Average motional state, 
                                "eta"     : (FLOAT) Lamb-Dicke parameters,
                                "omega"   : (FLOAT) Carrier rabi frequency in kHz (without 2 pi)
                          (OPT) "save"    : (INT}   default is 0, save to file? }
"""

#--------------------Import some libraries------------------------------------# 

import argparse
import os
import math
import numpy as np
import json
from scipy.special.basic import assoc_laguerre


#--------------------------------------------------------------------------------------------------------------------#
# CONSTANTS
#--------------------------------------------------------------------------------------------------------------------#
this_path = os.path.abspath(os.path.dirname(__file__)) #to build relative path
DATA_FILE_PATH = os.path.join(this_path, "../../config/")
SB_TIMES_FILE_NAME = "SB_TIMES"

#--------------------------------------------------------------------------------------------------------------------#
# READ PARAMETERS FROM CMD LINE
#--------------------------------------------------------------------------------------------------------------------#
def read_cmd_line() :
    #Read json string from cmd line and return py dictionary
    parser = argparse.ArgumentParser()
    parser.add_argument("params", help="JSON params array (str)", type=str)
    args = parser.parse_args()
    cmd_params = json.loads(args.params)
    return cmd_params

#--------------------------------------------------------------------------------------------------------------------#
# COMPUTE RED SIDEBAND PI TIMES
#--------------------------------------------------------------------------------------------------------------------#
'''
def create_sb_times(nlevels, nbar, eta, Om) :
    sb_times = []
    
    bsb = np.zeros(nlevels)   #Array formed by 0- nlevs elemnts [0,...,0_nlevs]
    rsb = np.zeros(nlevels+1) #Array formed by 0- nlevs+1 elemnts [0,...,0_nlevs+1]
    rsb[0] = 0;             #It makes  the RSB Rabi frequency for n=0 equal to 0.

    #Compute pre factors for blue sideband
    bsb= [abs(eta*((1.0/(i+1))**0.5) * assoc_laguerre(eta**2,i,1)) for i in range(nlevels)]
    bsblength=len(bsb)
    
    #Find rsb pre factors from bsb
    for i in range(bsblength):
        rsb[i+1]=bsb[i] 
        
    upperlimit=500 # This number limitate the Fock space and it is equal to the number
               # of pulses that we are interested in  

    rsb=rsb[1:upperlimit] #Here we are choosing the RSB factors of the RSB Rabi freq.
                           #that we compute above from 1 to the upperlimit(number of pulses)
                           #Thus rsb2 contains the same number of "pre-RSB frequencies" 
                           #than the number of pulses that we want to apply. 

    #Compute pi times from list of pre factors
    for j in rsb:
        sb_times.append((1000000*((2*math.pi)/(1000*Om*j))/2)) #times in us, round to 2 decimal places

    #Sort from shortest pi times to highest
    sb_times=sorted(sb_times)# pi-times from n=uuperlimit to n=1
    
    return sb_times
'''
def create_sb_times(nlvls, eta, Om) :

    sb_times = []

    for n in range(1, nlvls) :
    
        sb_times.append(1000000 * math.pi/(math.sqrt(n) * eta * Om))
    
    sb_times.reverse()
    
    return sb_times
    
#--------------------------------------------------------------------------------------------------------------------#
# SAVE PI TIMES TO TXT FILE
#------ --------------------------------------------------------------------------------------------------------------#
def save_times_to_file(sb_times) :
    file = open(DATA_FILE_PATH + SB_TIMES_FILE_NAME + ".txt", "w")                       
    for time in sb_times:                     # nameofthefile.txt --> user election
        file.write("%.f\n" % time)            # "w" means write in the file
    file.close()


def main() :
    cmd_params = read_cmd_line()
    sb_times = create_sb_times(cmd_params["nlevels"], cmd_params["eta"], 2*math.pi*cmd_params["omega"]*1000)
    if "save" in cmd_params and cmd_params["save"] == 1 :
        save_times_to_file(sb_times)
    print([float("%.f"%time) for time in sb_times])
    return 0
    
if __name__ == "__main__":
    main()

