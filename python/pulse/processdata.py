'''
    Author : Christophe Valahu and apprentice
    Last Modified : 15/04/19
    File : processdata.py
    
    Description : Reads a CSV file containing probabilities, does corresponding
                  post processing, returns fit params and (OPTIONAL) saves image
    
    Cmd args in : JSON params = {              "date"     : (STRING) date, 
                                               "expnum"   : (STRING) expnum, 
                                    (OPTIONAL) "genimage" : (BOOL) save image?,
                                    (OPTIONAL) "calib"    : (BOOL) update config file? }
                                    
    Output :      JSON data =   {              "msg"      : (STRING) message used for log,
                                               "*params"  : (FLOAT) fit parameters }

'''

import csv
import json
import numpy as np
from scipy.special import factorial
from scipy.optimize import curve_fit
import math
import argparse
import configparser
import matplotlib.pyplot as plt
import os
import re
import traceback

#--------------------------------------------------------------------------------------------------------------------#
# CONSTANTS
#--------------------------------------------------------------------------------------------------------------------#
this_path = os.path.abspath(os.path.dirname(__file__)) #to build relative path
DATA_FILE_PATH = os.path.join(this_path, "../../data/")
CONFIG_FILE_PATH = os.path.join(this_path, "../../config/parameter_config.ini")

# Conditions for calibration
#MAX_FREQSCAN_ERROR = 0.1
#MAX_TIMESCAN_ERROR = 0.01
MAX_FREQSCAN_ERROR = 100000
MAX_TIMESCAN_ERROR = 0.01

#--------------------------------------------------------------------------------------------------------------------#
# LOAD AND PREPARE DATA
#--------------------------------------------------------------------------------------------------------------------#

def update_config(section, option, value) :
    #Overwrite value to config file
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    config.set(section, option, str(value))
    
    with open(CONFIG_FILE_PATH, "w+") as configfile :
        config.write(configfile)
        
    return 0
    
def build_file_path(date, expnum) :
    return DATA_FILE_PATH + date + "\\" + expnum + "_PROB_" + date + ".csv"

def read_cmd_line() :
    #Read input of cmd line
    parser = argparse.ArgumentParser()
    parser.add_argument("params", help="JSON params array (str)", type=str)
    args = parser.parse_args()
    params = json.loads(args.params)
        
    return params

def read_csv_probs(prob_file_path) :

    with open(prob_file_path, newline = '') as proccsvfile :
        proc_csv_data = list(csv.reader(proccsvfile))

    probs_zero = proc_csv_data[1:][0]
    probs_left = proc_csv_data[1:][1]
    probs_right = proc_csv_data[1:][2]
    probs_two = proc_csv_data[1:][3]
    probs_data = {'nobright' : probs_zero,    'leftbright' : probs_left,
                  'rightbright' : probs_right, 'twobright': probs_two}
    
    json_params = proc_csv_data[0][0]
    json_params = str(json_params).replace("'", '"').replace(";", ",")
    params = json.loads(json_params)
    
    return probs_data, params
    

#--------------------------------------------------------------------------------------------------------------
#
#          TIME SCAN
#
#--------------------------------------------------------------------------------------------------------------
def time_prob_up(t, Om0) :
    delta = 0 #Remove this and add delta to func args if a fit of the detuning is desired
    return [(Om0**2 /(2* (Om0**2 + delta**2)))* (1 - math.cos(t_i* math.sqrt(Om0**2 + delta**2))) for t_i in t]
    
    
def timescan(probs_list, params, update, genimage) :

    
    probs_list = [float(x) / 100 for x in probs_list['leftbright']]
    
    # Convert parameters to correct units
    starttime = (params['det']) * (10**(-6))
    step = params['step'] * (10**(-6))
    Omegaapprox = (2 * math.pi) /(2 * params['pitime'] * 10**(-6))
   
    #Create x-values of time:
    xdat = []
    for i in range(len(probs_list)) :
        xdat.append(starttime + i*step)
    
    xdat = np.array(xdat)
    ydat = np.array(probs_list)
    
    #Find fit parameters
    initial_guess = [Omegaapprox]
    popt, pcov = curve_fit(time_prob_up, xdat, probs_list, initial_guess)
    
    #Find error associated to the curve fitting
    perr = np.sqrt(np.diag(pcov))/(2*math.pi * 1000)
    
    Omfit = popt[0]
    pitime = (math.pi*2)/Omfit * 10**(6)/2
    
    fit_success = True if perr[0] <= MAX_TIMESCAN_ERROR else False
    
    if fit_success :
        if update :
            update_config(params['header'], params['state'] + 'time', float('%.2f'%(pitime)))
        message = "pi-time = " + '%.2f'%(pitime) + " us, Om = %.2f"%(Omfit/(2 * math.pi)/1000) + ' KHz'
    else :            
        message = "curve_fit() could not converge with good accuracy, pi-time = " + '%.2f'%(pitime) + " us, Om = %.2f"%(Omfit/(2 * math.pi)/1000) + ' KHz'
    
    if genimage :
        
        #Generate plotting data of the fit
        xdat_fit = np.arange(starttime, (starttime + len(probs_list)*step), ((len(probs_list))*step)/100)
        ydat_fit = time_prob_up(xdat_fit, Omfit)
        x_ticks = np.arange(starttime, (starttime + len(probs_list)*step), ((len(probs_list))*step)/6)
        x_ticks_label = ['%.2f' % (x*1000000) for x in x_ticks]
    
        
        plt.figure(figsize=(10.65,5)) #LabView RichTextBox aspect ratio = 2.13
        plt.plot(xdat_fit, ydat_fit, 'k', xdat, ydat, 'bo') #Plot prob data and fit data
        plt.title(message)
        plt.grid(True)
        plt.xticks(x_ticks, x_ticks_label)
        plt.axis([starttime, (starttime + len(probs_list)*step), 0, 1])
        if not os.path.exists(DATA_FILE_PATH + params['date'] + '\\_images\\') :
            os.makedirs(DATA_FILE_PATH + params['date'] + '\\_images\\')
        plt.savefig(DATA_FILE_PATH + params['date'] + '\\_images\\' + params['expnum'] + '_' + params['date']+ '.png')   
        
    output = {'msg': message, 'pitimefit': '%.2f'%(pitime), 'deltafit': (str(Omfit//(2 * math.pi * 1000))), 'fitsuccess': fit_success, 'err' : str(perr)}
    print(json.dumps(output))
    return 0


#--------------------------------------------------------------------------------------------------------------
#
#          FREQ SCAN
#
#--------------------------------------------------------------------------------------------------------------
    
def freq_prob_up(x, Omega0, om0) :
    return [(Omega0**2 / (Omega0**2 + (x_i - om0)**2))* (math.sin((math.sqrt(Omega0**2 + (x_i - om0)**2)*math.pi)/(2 *Omega0))**2) for x_i in x]
    
    
def freqscan(probs_list, params, update, genimage) :
        
    probs_list = [float(x) / 100 for x in probs_list['leftbright']]
    
    #Convert params to correct units
    startfreq = (params['freq'] + params['det']) * (2 * math.pi * 1000)
    step = params['step'] * 2 * math.pi * 1000
    Omegaapprox = (2 * math.pi) /(2 * params['pitime'] * 10**(-6))
    
    #Create x-values of frequencies:
    xdat = []
    for i in range(len(probs_list)) :
        xdat.append(startfreq + i*step)
    
    xdat = np.array(xdat)
    ydat = np.array(probs_list)
    
    #Find fit parameters
    initial_guess = [Omegaapprox, (params['freq'])* 2 * math.pi*1000]
    popt, pcov = curve_fit(freq_prob_up, xdat, probs_list, initial_guess)
    
    Omfit = popt[0]
    omfit = popt[1]
    
    #Find error associated to curve fit
    perr = np.sqrt(np.diag(pcov))/(2*math.pi * 1000)
    
    if perr[0] <= MAX_FREQSCAN_ERROR and perr[1] <= MAX_FREQSCAN_ERROR :
        if update :
            update_config(params['header'], params['state'] + 'freq', float('%.3f'%(omfit/(2 * math.pi * 1000))))
        message = "f0 = " + '%.3f'%(omfit/(2 * math.pi * 1000)) + " KHz, Rabi = " + (str(Omfit//(2 * math.pi * 1000))) + "KHz"
    else :            
        message = "curve_fit() could not converge with good accuracy, freq = " +  "%.2f" %(omfit/(2 * math.pi * 1000))
    
    if genimage :
    
        #Generate plotting data of the fit
        xdat_fit = np.arange(startfreq, (startfreq + len(probs_list)*step), ((len(probs_list))*step)/100)
        ydat_fit = freq_prob_up(xdat_fit, Omfit, omfit)
        x_ticks = np.arange(startfreq, (startfreq + len(probs_list)*step), ((len(probs_list))*step)/3)
        x_ticks_label = ['%.2f' % (x/(2*math.pi*1000)) for x in x_ticks]
    
        plt.figure(figsize=(10.65,5)) #LV aspect ratio = 2.13
        plt.plot(xdat_fit, ydat_fit, 'k', xdat, ydat, 'bo')
        plt.title(message)
        plt.grid(True)
        plt.xticks(x_ticks, x_ticks_label)
        plt.axis([startfreq, (startfreq + len(probs_list)*step), 0, 1])
        if not os.path.exists(DATA_FILE_PATH +params['date'] + '\\_images\\') :
            os.makedirs(DATA_FILE_PATH + params['date'] + '\\_images\\')
        plt.savefig(DATA_FILE_PATH + params['date'] + '\\_images\\' + params['expnum'] + '_' +  params['date']+ '.png')  
    
    output = {'msg': message, 'freqfit': '%.3f'%(omfit/(2 * math.pi * 1000)), 'Omfit': (str(Omfit//(2 * math.pi * 1000))), 'err' : str(perr)}
    print(json.dumps(output))
    return 0
    
#--------------------------------------------------------------------------------------------------------------
#
#          COHERENCE TIME
#
#--------------------------------------------------------------------------------------------------------------
def OmegaG(Om0, gamma) :
    return math.sqrt(4 * Om0**2 - gamma**2)

def time_decay_prob_up(t, Om0, G) :
    #G = gamma, Om0 = omega0
    OmG = OmegaG(Om0, G)
    return [(1 - math.exp(- G * t_i/2) *(math.cos(OmG*t_i/2) + G/OmG * math.sin(OmG*t_i/2)))/2 for t_i in t]
    
def coherencetime(probs_list, params, update, genimage) :

    probs_list = [float(x) / 100 for x in probs_list['leftbright']]
    
    # Convert parameters to correct units
    starttime = (params['det']) * (10**(-6))
    step = params['step'] * (10**(-6))
    Omegaapprox = (2 * math.pi) /(2 * params['pitime'] * 10**(-6))
    Gammaapprox = .1
    
    #Create x-values of time:
    xdat = []
    for i in range(len(probs_list)) :
        xdat.append(starttime + i*step)
    
    xdat = np.array(xdat)
    ydat = np.array(probs_list)
    '''
    #Find fit parameters
    initial_guess = [Omegaapprox, Gammaapprox]
    popt, pcov = curve_fit(time_decay_prob_up, xdat, probs_list, initial_guess)
    
    #Find error associated to the curve fitting
    perr = np.sqrt(np.diag(pcov))/(2*math.pi * 1000)
    
    Omfit = popt[0]
    Gammafit = popt[1]
    pitime = (math.pi*2)/Omfit * 10**(6)/2
    
    message = "Coherence time = " + '%.2f'%(1/Gammafit) + " s, %.2f"%(Omfit/(2 * math.pi)/1000) + ' KHz (%.2f)'%pitime + 'us)'
    
    if genimage :
        
        #Generate plotting data of the fit
        xdat_fit = np.arange(starttime, (starttime + len(probs_list)*step), ((len(probs_list))*step)/100)
        ydat_fit = time_decay_prob_up(xdat_fit, Omfit, Gammafit)
        x_ticks = np.arange(starttime, (starttime + len(probs_list)*step), ((len(probs_list))*step)/6)
        x_ticks_label = ['%.2f' % (x*1000000) for x in x_ticks]
    
        plt.figure(figsize=(10.65,5)) #LabView RichTextBox aspect ratio = 2.13
        plt.plot(xdat_fit, ydat_fit, 'k', xdat, ydat, 'bo') #Plot prob data and fit data
        plt.title(message)
        plt.grid(True)
        plt.xticks(x_ticks, x_ticks_label)
        plt.axis([starttime, (starttime + len(probs_list)*step), 0, 1])
        if not os.path.exists(DATA_FILE_PATH + params['date'] + '\\_images\\') :
            os.makedirs(DATA_FILE_PATH + params['date'] + '\\_images\\')
        plt.savefig(DATA_FILE_PATH + params['date'] + '\\_images\\' + params['expnum'] + '_' + params['date']+ '.png')   
    '''
    message = ''
    pitime =  0
    Omfit= 0
    output = {'msg': message, 'pitimefit': '%.2f'%(pitime), 'deltafit': (str(Omfit//(2 * math.pi * 1000)))}
    print(json.dumps(output))
    return 0

#--------------------------------------------------------------------------------------------------------------
#
#          Doppler temperature
#
#--------------------------------------------------------------------------------------------------------------
def prob_n(nbar, n) :
    #Equation 5.3
    return 1/(nbar + 1) * (nbar/(1 + nbar))**n
    
def OmNblue(Om0, n) :
    eta = 0.0094
    return math.sqrt(n + 1) * eta * Om0

def n_blue_prob_up(t, n, delta, Om0) :
    #Equation 5.5 joe
    tau = 0.0005
    return OmNblue(Om0, n)**2/(OmNblue(Om0, n)**2 + delta**2) * (1/2 + (math.sin(t*math.sqrt(OmNblue(Om0, n)**2 + delta**2)/2) - 0.5)*math.exp(-t/tau))

def blue_prob_up(t, nbar, delta) :
    Om0 = 2*math.pi*47400
    nmax = 300
    #Equation 5.6 of Joe Randall's thesis
    probs = []
    for t_i in t :
        prob_up = 0
        for n in range(nmax) :
            prob_up += prob_n(nbar, n) * n_blue_prob_up(t_i, n, delta, Om0)
        probs.append(prob_up)
    return probs
    
def dopplertemp(probs_list, params, update, genimage) :

    probs_list = [float(x) / 100 for x in probs_list]
    
    # Convert parameters to correct units
    starttime = (params['det']) * (10**(-6))
    step = params['step'] * (10**(-6))
    nbarapprox = 50
    deltaapprox = 100
    
    #Create x-values of time:
    xdat = []
    for i in range(len(probs_list)) :
        xdat.append(starttime + i*step)
    
    xdat = np.array(xdat)
    ydat = np.array(probs_list)
    
    #Find fit parameters
    initial_guess = [nbarapprox, deltaapprox]
    popt, pcov = curve_fit(blue_prob_up, xdat, probs_list, initial_guess)
    
    #Find error associated to the curve fitting
    perr = np.sqrt(np.diag(pcov))/(2*math.pi * 1000)
    
    nbar = popt[0]
    delta = popt[1]
    
    message = "nbar = " + '%.2f'%(nbar)
    
    if genimage :
        
        #Generate plotting data of the fit
        xdat_fit = np.arange(starttime, (starttime + len(probs_list)*step), ((len(probs_list))*step)/100)
        ydat_fit = blue_prob_up(xdat_fit, nbar, delta)
        x_ticks = np.arange(starttime, (starttime + len(probs_list)*step), ((len(probs_list))*step)/6)
        x_ticks_label = ['%.2f' % (x*1000000) for x in x_ticks]
    
        plt.figure(figsize=(10.65,5)) #LabView RichTextBox aspect ratio = 2.13
        plt.plot(xdat_fit, ydat_fit, 'k', xdat, ydat, 'bo') #Plot prob data and fit data
        plt.title(message)
        plt.grid(True)
        plt.xticks(x_ticks, x_ticks_label)
        plt.axis([starttime, (starttime + len(probs_list)*step), 0, 1])
        if not os.path.exists(DATA_FILE_PATH + params['date'] + '\\_images\\') :
            os.makedirs(DATA_FILE_PATH + params['date'] + '\\_images\\')
        plt.savefig(DATA_FILE_PATH + params['date'] + '\\_images\\' + params['expnum'] + '_' + params['date']+ '.png')   
        
    output = {'msg': message,'nbar' : nbar, 'delta': delta}
    print(json.dumps(output))
    return 0

#--------------------------------------------------------------------------------------------------------------
#
#          Molmer-Sorensen gate
#
#--------------------------------------------------------------------------------------------------------------

def ms_asym12_fitfunc(x, x0, y0) :
    return    0.00666093 \
            - 0.000105667*x \
            + 0.0000194191*x**2 \
            - 8.4225*(10**-8)*x**3 \
            - 2.74009*(10**-10)*x**4 \
            + 1.26044*(10**-12)*x**5

def ms_minasym12_fitfunc(x, x0, y0) :
    return    0.00355201 \
            + 0.0000531236 * x \
            + 0.0000132693 * x**2 \
            - 6.15207*(10**-9) * x**3 \
            - 1.3053*(10**-10) * x**4 \
            + 1.3014*(10**-13) * x**5
 
def ms_asym1_fitfunc(x, x0, y0) :
    return  - 0.000212919 \
            - 0.0000138263 * x \
            + 7.53256*(10**-6) * x**2 \
            - 2.56263*(10**-8)* x**3 \
            - 3.39344*(10**-11) * x**4 \
            + 1.78523*(10**-13) * x**5

def ms_asym1_2_fitfunc(x, A, f, x0) :
    #ASYM1 det scan at 2tgate
    return [A*math.cos((x_i - x0)*f) for x_i in x]
    
def ms_asym12_2_fitfunc(x, A, f, x0) :
    #ASYM1 det scan at 2tgate
    return [A*math.cos((x_i - x0)*f) for x_i in x]

def ms_sym_fitfunc(x, y0, m) :
    return [x_i * m + y0 for x_i in x]

def msdetscan(probs_list, params, update, genimage) :
    
    probs_list_zero = np.array([float(x) / 100 for x in probs_list['nobright']])
    probs_list_one = np.array([float(x) / 100 for x in probs_list['leftbright']])
    probs_list_two = np.array([float(x) / 100 for x in probs_list['twobright']])
    
    #Convert params to correct units
    startfreq = (params['freq'] + params['det']) * ( 1000)
    step = params['step'] * 1000

    #Create x-values of frequencies:
    xdat = []
    for i in range(len(probs_list_one)) :
        xdat.append(startfreq + i*step)
    
    xdat = np.array(xdat)
    
    #Find fit parameters
    x0_approx = params['freq']*1000
    y0_approx = 0   
    initial_guess = [x0_approx, y0_approx]
    
    if params["detmode"] == "ASYM12" :
        if params['timemult'] == 2 :
            ydat = probs_list_two
            A_approx = 1
            f_approx = 2*math.pi/200
            x0_approx = 0
            initial_guess = [A_approx, f_approx, x0_approx]
            popt, pcov = curve_fit(ms_asym12_2_fitfunc, xdat, ydat, initial_guess)
            
            A_fit = popt[0]
            f_fit = popt[1]
            asym1_offset = popt[2]
            
            message = 'detuning offset : %.2f'%asym1_offset + ' Hz'  
            output = {'msg':  message, 'det': '%.2f'%(asym1_offset)}
        
        if genimage :
            xdat_fit = np.arange(startfreq, (startfreq + len(probs_list_one)*step), ((len(probs_list_one))*step)/100)
            ydat_fit = ms_asym12_2_fitfunc(xdat_fit, A_fit, f_fit, asym1_offset)
     
            x_ticks = np.arange(startfreq, (startfreq + len(probs_list_one)*step), ((len(probs_list_one))*step)/3)
            x_ticks_label = ['%.2f' % x for x in x_ticks]
            plt.figure(figsize=(10.65,5)) #LV aspect ratio = 2.13
            plt.plot(xdat_fit, ydat_fit, 'b', xdat, ydat, 'bo')
            plt.title(message)
            plt.grid(True)
            plt.xticks(x_ticks, x_ticks_label)
            plt.axis([startfreq, (startfreq + len(probs_list_one)*step), 0, 1])
            if not os.path.exists(DATA_FILE_PATH +params['date'] + '\\_images\\') :
                os.makedirs(DATA_FILE_PATH + params['date'] + '\\_images\\')
            plt.savefig(DATA_FILE_PATH + params['date'] + '\\_images\\' + params['expnum'] + '_' +  params['date']+ '.png')  
        
    elif params["detmode"] == "ASYM1" :
        
        if params['timemult'] == 2 :
            A_approx = 1
            f_approx = 2*math.pi/200
            x0_approx = 0
            initial_guess = [A_approx, f_approx, x0_approx]
            popt, pcov = curve_fit(ms_asym1_2_fitfunc, xdat, probs_list_two, initial_guess)
            
            asym1_offset = popt[2]
            
            message = 'ASYM1 detuning offset : %.2f'%asym1_offset + ' Hz'  
            output = {'msg':  message, 'asym1det': '%.2f'%(asym1_offset)}
        
    elif params["detmode"] == "-ASYM12" :
        popt, pcov = curve_fit(ms_minasym12_fitfunc, xdat, probs_list, initial_guess)
    elif params["detmode"] == "SYM" :
        ydat_zero = np.array(probs_list_zero)
        ydat_two = np.array(probs_list_two)
        
        y0_approx = 0
        m_zero_approx = -100/0.35
        initial_guess = [y0_approx, m_zero_approx]
        popt_zero, pcov = curve_fit(ms_sym_fitfunc, xdat, ydat_zero, initial_guess)
        
        m_two_approx = 100/0.35
        initial_guess = [y0_approx, m_two_approx]
        popt_two, pcov = curve_fit(ms_sym_fitfunc, xdat, ydat_two, initial_guess)
        
        y0_zero_fit = popt_zero[0]
        m_zero_fit = popt_zero[1]
        
        y0_two_fit = popt_two[0]
        m_two_fit = popt_two[1]
        
        sym_offset = (y0_two_fit - y0_zero_fit)/(m_zero_fit- m_two_fit)
        
        message = 'Sym detuning offset : %.2f'%sym_offset + ' Hz'
    
        output = {'msg':  message, 'symdet': '%.2f'%(sym_offset)}
        
        if genimage :
            xdat_fit = np.arange(startfreq, (startfreq + len(probs_list_one)*step), ((len(probs_list_one))*step)/100)
            ydat_zero_fit = ms_sym_fitfunc(xdat_fit, y0_zero_fit, m_zero_fit)
            ydat_two_fit = ms_sym_fitfunc(xdat_fit, y0_two_fit, m_two_fit)
        
            x_ticks = np.arange(startfreq, (startfreq + len(probs_list_one)*step), ((len(probs_list_one))*step)/3)
            x_ticks_label = ['%.2f' % x for x in x_ticks]
            plt.figure(figsize=(10.65,5)) #LV aspect ratio = 2.13
            plt.plot(xdat_fit, ydat_zero_fit, 'b', xdat, ydat_zero, 'bo', xdat, ydat_two, 'go', xdat_fit, ydat_two_fit, 'g')
            plt.axvline(x = sym_offset, color = 'k', linestyle = '--')
            plt.title(message)
            plt.grid(True)
            plt.xticks(x_ticks, x_ticks_label)
            plt.axis([startfreq, (startfreq + len(probs_list_one)*step), 0, 1])
            if not os.path.exists(DATA_FILE_PATH +params['date'] + '\\_images\\') :
                os.makedirs(DATA_FILE_PATH + params['date'] + '\\_images\\')
            plt.savefig(DATA_FILE_PATH + params['date'] + '\\_images\\' + params['expnum'] + '_' +  params['date']+ '.png')  
        
    
    print(json.dumps(output))
    return 0
    
    '''
    if genimage :
        
        message = "message"
    
        xdat_fit = np.arange(startfreq, (startfreq + len(probs_list)*step), ((len(probs_list))*step)/100)
        
        if params["detmode"] == "ASYM12" :
            ydat_fit = ms_asym12_fitfunc(xdat_fit, x0, y0)
        if params["detmode"] == "ASYM1" :
            ydat_fit = ms_asym1_fitfunc(xdat_fit, x0, y0)
        if params["detmode"] == "-ASYM12" :
            ydat_fit = ms_minasym12_fitfunc(xdat_fit, x0, y0)
            
        x_ticks = np.arange(startfreq, (startfreq + len(probs_list)*step), ((len(probs_list))*step)/3)
        x_ticks_label = ['%.2f' % x for x in x_ticks]
        plt.figure(figsize=(10.65,5)) #LV aspect ratio = 2.13
        plt.plot(xdat_fit, ydat_fit, 'k', xdat, ydat, 'bo')
        plt.title(message)
        plt.grid(True)
        plt.xticks(x_ticks, x_ticks_label)
        plt.axis([startfreq, (startfreq + len(probs_list)*step), 0, 1])
        if not os.path.exists(DATA_FILE_PATH +params['date'] + '\\_images\\') :
            os.makedirs(DATA_FILE_PATH + params['date'] + '\\_images\\')
        plt.savefig(DATA_FILE_PATH + params['date'] + '\\_images\\' + params['expnum'] + '_' +  params['date']+ '.png')  

    '''

    if params["detmode"] == "SYM" :
    
        m_nobright_approx = - 0.1
        x0_nobright_approx = params['freq']*1000
        y0_nobright_approx = 0.7
        
        m_twobright_approx = + 0.1
        x0_twobright_approx = params['freq']*1000
        y0_twobright_approx = 0.2
        
        initial_guess_nobright = [m_nobright_approx, x0_nobright_approx, y0_nobright_approx]
        popt_nobright, pcov = curve_fit(ms_sym_det_func, xdat, probs_list, initial_guess_nobright)
        initial_guess_twobright = [m_twobright_approx, x0_twobright_approx, y0_twobright_approx]
        popt_twobright, pcov = curve_fit(ms_sym_det_func, xdat, probs_list, initial_guess_twobright)
    
        m_nobright  = popt_nobright[0]
        x0_nobright = popt_nobright[1]
        y0_nobright = popt_nobright[2]
        
        m_twobright  = popt_twobright[0]
        x0_twobright = popt_twobright[1]
        y0_twobright = popt_twobright[2]
        
        
        if genimage :
        
            #Generate plotting data of the fit
            xdat_fit = np.arange(startfreq, (startfreq + len(probs_list)*step), ((len(probs_list))*step)/100)
            ydat_fit = ms_sym_det(xdat_fit, m_nobright_approx, x0, y0)
            x_ticks = np.arange(startfreq, (startfreq + len(probs_list)*step), ((len(probs_list))*step)/3)
            x_ticks_label = ['%.2f' % x for x in x_ticks]
    '''    
        
        '''
#--------------------------------------------------------------------------------------------------------------
#
#          Molmer-Sorensen Parity
#
#--------------------------------------------------------------------------------------------------------------
   
def ms_parity_prob(phi, a, phi0, a0) :
    #A Cos[2 \[Phi]1 + \[Phi]off ];
    prob = []
    for phi_i in phi :
        prob.append(a0 + a * math.sin(2*phi_i + phi0))
    return prob
    
    
def msparity(probs_list, params, update, genimage) :

    
    probs_list_zero = np.array([float(x) / 100 for x in probs_list['nobright']])
    probs_list_one = np.array([float(x) / 100 for x in probs_list['leftbright']])
    probs_list_two = np.array([float(x) / 100 for x in probs_list['twobright']])
    
    parity_data = probs_list_two + probs_list_zero - probs_list_one
 
    # Get parameters
    startphi = params['det'] 
    stepphi = params['step']
    aapprox = 1
    a0approx = 0.1
    phi0approx = 0.1
    
    #Create x-values of time:
    xdat = []
    for i in range(len(probs_list_zero)) :
        xdat.append(startphi + i*stepphi)
    
    xdat = np.array(xdat)
    ydat = np.array(parity_data)
    
    print(xdat)
    print(ydat)
    
    #Find fit parameters
    initial_guess = [aapprox, phi0approx, a0approx]
    popt, pcov = curve_fit(ms_parity_prob, xdat, ydat, initial_guess)
    
    #Find error associated to the curve fitting
    perr = np.sqrt(np.diag(pcov))
    
    a_fit = popt[0] #Amplitude of sin wave
    phi0_fit = popt[1]
    a0_fit = popt[2]
    phi0_fit_err = perr[1] #fit error for phi0
        
       
    message = "amp = " + '%.2f'%(a_fit) + ", phi0 = %.2f"%(phi0_fit) 
    
    if genimage :
        
        #Generate plotting data of the fit
        xdat_fit = np.arange(startphi, (startphi + len(probs_list_one)*stepphi), ((len(probs_list_one))*stepphi)/100)
        ydat_fit = ms_parity_prob(xdat_fit, a_fit, phi0_fit, a0_fit)
        x_ticks = np.arange(startphi, (startphi + len(probs_list_one)*stepphi), ((len(probs_list_one))*stepphi)/6)
        x_ticks_label = ['%.2f' % (x) for x in x_ticks]
    
        
        plt.figure(figsize=(10.65,5)) #LabView RichTextBox aspect ratio = 2.13
        plt.plot(xdat_fit, ydat_fit, 'k', xdat, ydat, 'bo') #Plot prob data and fit data
        plt.title(message)
        plt.grid(True)
        plt.xticks(x_ticks, x_ticks_label)
        plt.axis([startphi, (startphi + len(probs_list_one)*stepphi), -1, 1])
        if not os.path.exists(DATA_FILE_PATH + params['date'] + '\\_images\\') :
            os.makedirs(DATA_FILE_PATH + params['date'] + '\\_images\\')
        plt.savefig(DATA_FILE_PATH + params['date'] + '\\_images\\' + params['expnum'] + '_' + params['date']+ '.png')   
        
    output = {'msg': message, 'afit': '%.2f'%(a_fit), 'phi0fit': '%.2f'%(phi0_fit), 'phi0err': '%.3f'%(phi0_fit_err)}
    print(json.dumps(output))
    return 0


   
   
def main() :
    cmd_params = read_cmd_line()
    
    if 'filepath' in cmd_params :
        probs_list, params = read_csv_probs(cmd_params['filepath'])       
        filename = re.search('\w+(?:\.\w+)*$', cmd_params['filepath']).group(0)
        params['expnum'] = filename[:3]
        params['date'] = filename[9:15]
    else :
        probs_list, params = read_csv_probs(build_file_path(cmd_params['date'], cmd_params['expnum']))
        params['date'] = cmd_params['date']
        params['expnum'] = cmd_params['expnum']
    
    update = 0 if 'update' not in cmd_params else cmd_params['update']
    genimage = 0 if 'genimage' not in cmd_params else cmd_params['genimage']
    func_to_call = params['name'] + '(probs_list, params, update, genimage)'
    
    #Catch error in case function isn't recognised
    try :
        eval(func_to_call)
    except Exception as e:
        output = {'msg': "Error trying to call function " + params['name'] + "."}
        print(json.dumps(output))
    
    return 0
    
if __name__ == "__main__":
    main()
    
    
    
    
    
    