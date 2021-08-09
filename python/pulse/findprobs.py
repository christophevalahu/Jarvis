'''
    Author : Christophe Valahu
    Last Modified : 14/04/19
    File : findprobs.py
    
    Description : Reads a CSV file containing photon counts, and outputs list of
    probabilites using the maximum likelihood method.
    
    Cmd args in : (  JSON params = {           "date"   : date    (STRING), 
                                               "expnum" : expnum  (STRING),
                                    (OPTIONAL) "filepath" : filepath (STRING), NOTE: Will trump over date and expnum
                                    (OPTIONAL) "save"   : save    (BOOL)} )
    
    Output :      ( JSON data = {"probs" : probs  (FLOAT LIST} )

'''

import csv
import json
import numpy
import scipy.optimize as opt
import math
import argparse
import os
import h5py
import numpy as np
import re

#--------------------------------------------------------------------------------------------------------------------#
# CONSTANTS
#--------------------------------------------------------------------------------------------------------------------#
this_path = os.path.abspath(os.path.dirname(__file__)) #to build relative path
DATA_FILE_PATH = os.path.join(this_path, "../../data/")
PROBS_FILE_NAME = "_PROB_"

#Smallest representable float with np
EPS = np.finfo(float).eps 
#Largest representable negative number with np
MIN_NUM = np.finfo(float).min

#--------------------------------------------------------------------------------------------------------------------#
# LOAD AND PREPARE DATA (AND SAVE)
#--------------------------------------------------------------------------------------------------------------------#
def read_cmd_line() :
    #Read json string from cmd line and return py dictionary
    parser = argparse.ArgumentParser()
    parser.add_argument("params", help="JSON params array (str)", type=str)
    args = parser.parse_args()
    cmd_params = json.loads(args.params)
    return cmd_params

def build_file_path(date, expnum) :
    return DATA_FILE_PATH + date + "\\" + expnum + "_EXP_" + date + ".h5"

def reshape_data(raw_data, runs) :
    #reshape data from a 1d array to 2d array, where every line contains counts for a run
    nchunks = len(raw_data) / runs
    reshaped_data = [];
    for i in range(int(nchunks)) :
        reshaped_data.append(raw_data[i*runs:(i+1)*runs])
        
    return reshaped_data


def save_csv_probs(probs, cmd_params, csv_params) :
    with open(DATA_FILE_PATH + cmd_params['date'] + "\\" + cmd_params['expnum'] + PROBS_FILE_NAME + cmd_params['date'] +  ".csv", 'w+', newline = '') as csvfile:
        line_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        line_writer.writerow([json.dumps(csv_params)])
        line_writer.writerow(probs['no_ion'])
        line_writer.writerow(probs['left_ion'])
        line_writer.writerow(probs['right_ion'])
        line_writer.writerow(probs['both_ion'])
        
def save_csv_pmt(prob_list, cmd_params, csv_params) :
    with open(DATA_FILE_PATH + cmd_params['date'] + "\\" + cmd_params['expnum'] + PROBS_FILE_NAME + cmd_params['date'] +  ".csv", 'w+', newline = '') as csvfile:
        line_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        line_writer.writerow([json.dumps(csv_params)])
        line_writer.writerow(prob_list)

    return 0
    
def save_csv_camera(prob_list_left, prob_list_right, params, date, expnum) :

    with open(DATA_FILE_PATH + date + "\\"  + expnum + PROBS_FILE_NAME + date +  ".csv", 'w+', newline = '') as csvfile:
        line_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        line_writer.writerow([json.dumps(params)])
        line_writer.writerow(prob_list_left)
        line_writer.writerow(prob_list_right)

    return 0
     
def read_HDF5_file(file_path) :

    f = h5py.File(file_path, 'r')
    
    det_hardware = f.attrs[u'det_hardware'].decode()
    if det_hardware == 'CAMERA':
        raw_data = f["photon_counts\counts_2"]
    elif det_hardware == 'PMT' :
        raw_data = f["photon_counts\counts_3"] #Counts_3 contains experimental data
    
    json_params = str(f.attrs[u'mathematica'].decode()).replace("'", '"').replace(";",",")
    json_params = json.loads(json_params)
    cam_dim = f.attrs[u'cam_dim']
    
    if det_hardware == 'CAMERA' :
        left_ion_weight = f["statedet\ion_left"]
        right_ion_weight = f["statedet\ion_right"]
        params_out = {'det_hardware' : det_hardware, 
                      'mathematica' : json_params,
                      'cam_dim' :cam_dim,
                      'raw_data': raw_data[:],
                      'statedet': {'t1' : f['statedet'].attrs[u't1'],
                                   't2' : f['statedet'].attrs[u't2'],
                                   'errm1' : eval(f['statedet'].attrs[u'errm1'].decode()),
                                   'errm2' :  eval(f['statedet'].attrs[u'errm2'].decode()),
                                   'left_ion_weight': left_ion_weight[:],
                                   'right_ion_weight': right_ion_weight[:]}
                      }
                      
    if det_hardware == 'PMT' :
        
        params_out = {'det_hardware' : det_hardware, 
                      'mathematica' : json_params,
                      'raw_data': reshape_data(raw_data[:], json_params['runs']),
                      'statedet': {'t1' : f['statedet'].attrs[u't1'],
                                   't2' : f['statedet'].attrs[u't2'],
                                   'errm1' : eval(f['statedet'].attrs[u'errm1'].decode()),
                                   'errm2' :  eval(f['statedet'].attrs[u'errm2'].decode()),
                                  }
                      }
    
    return params_out
    
#--------------------------------------------------------------------------------------------------------------------#
# FIND PROBABILITES 1 ION
#--------------------------------------------------------------------------------------------------------------------#
def find_weighted_sum_image(raw_image, weight_image) :
    return np.sum(np.multiply(raw_image, weight_image))


def gen_bright_data(raw_data, t1) :
    #Convert raw data to Dark/Bright if data is under/above threshhold
    bright_list = []
    
    for runs_data in raw_data :
        count = 0
        for result in runs_data :
            if float(result) >= t1 :
                count = count + 1
        
        bright_list.append(count)
    
    return bright_list
    
def gen_bright_data_two(raw_data, t1, t2) :
    #Convert raw data to Dark/Brightone/Brighttwo if data is under/above threshhold
    bright_list_one = []
    bright_list_two = []
    
    for runs_data in raw_data :
        count_one = 0
        count_two = 0
        for result in runs_data :
            if result >= t1 and result < t2:
                count_one = count_one + 1
            elif result >= t2 :
                count_two = count_two + 1
        
        bright_list_one.append(count_one)
        bright_list_two.append(count_two)
    
    return bright_list_one, bright_list_two

def q1_func(p1, errm) :
    PD1 = (errm)[1][0]
    PD0 = (errm)[1][1]
    return p1 * PD0 + (1-p1)*PD1
    
def maximum_likelihood(p1, nbright, runs, errm) :
    return math.log(((q1_func(p1, errm)) ** nbright) *((1 - (q1_func(p1, errm)))**(runs - nbright)))

def find_probs(bright_list, runs, errm) :
    #find probability for each step using maximum likelihood method 
    #print(bright_list)
    prob_list = []
    for nbright in bright_list :
        max_p = opt.fminbound(lambda p1: -maximum_likelihood(p1, nbright, runs, errm), 0, 1)
        prob_list.append(max_p*100)
        
    prob_list = np.array([float('%.3f'%x) for x in (numpy.transpose(prob_list))])
    
    return {'no_ion' : (100 - prob_list).tolist(),
            'left_ion' : prob_list.tolist(),
            'right_ion' : prob_list.tolist(),
            'both_ion' : np.zeros(prob_list.size).tolist()}

#--------------------------------------------------------------------------------------------------------------------#
# FIND PROBABILITES 2 IONS
#--------------------------------------------------------------------------------------------------------------------#
 
def q1_func2(p1, p2, errm2) :
    #Take elements of the error matrix, note that p0 = 1 - p1 - p2
    PB1_00 = errm2[1][0]
    PB1_01 = errm2[1][1]
    PB1_11 = errm2[1][2]
    return (1 - p1 - p2) * PB1_00 + p1 * PB1_01 + p2 * PB1_11
    
def q2_func2(p1, p2, errm2) :
    #Take elements of the error matrix, note that p0 = 1 - p1 - p2
    PB2_00 = errm2[2][0]
    PB2_01 = errm2[2][1]
    PB2_11 = errm2[2][2]
    
    return (1 -p1-p2) * PB2_00 + p1 * PB2_01 + p2 * PB2_11

def ml_func_two(p, errm2, k1, k2, runs) :
    val1 = q1_func2(p[0], p[1], errm2)**k1
    val2 = q2_func2(p[0], p[1], errm2)**k2
    val3 = ( 1 - q1_func2(p[0], p[1], errm2) - q2_func2(p[0], p[1], errm2))**(runs - k1 - k2)
    
    val1 = MIN_NUM if val1 == 0 else math.log(val1)
    val2 = MIN_NUM if val2 == 0 else math.log(val2)
    val3 = MIN_NUM if val3 == 0 else math.log(val3)
    
    return -(val1 + val2 + val3)
    
def format_probs_output(prob_list):
    return np.array([float('%.3f'%x) for x in (numpy.transpose(prob_list))])
    
def find_probs_two(bright_list_one, bright_list_two, runs, errm2) :
    
    MAX_LIKELIHOOD_METHOD = False
    
    if MAX_LIKELIHOOD_METHOD : 
    
        prob_list = []
        for k1, k2 in zip(bright_list_one, bright_list_two) :  
            max_p = opt.minimize( ml_func_two, [0.5, 0.5], args = (errm2, k1, k2, runs), method = 'SLSQP', bounds = [[0,1],[0,1]])
            prob_list.append(np.flip(max_p.x*100))
    else :        
        
        errm2inv = np.transpose(np.linalg.inv(errm2))
        prob_list = []
        for nbrightone, nbrighttwo in zip(bright_list_one, bright_list_two) :   
            nbrightnone = runs - nbrightone  - nbrighttwo    
         
            bright_list = (np.asarray([[nbrightnone/runs], [nbrightone/runs], [nbrighttwo/runs]]))
            prob_matrix = np.matmul(errm2inv, bright_list)        
            prob_list.append(prob_matrix*100)
            
    prob_list = np.transpose(prob_list)[0]
    
    probs_one_ion = format_probs_output(prob_list[1])
    probs_two_ion = format_probs_output(prob_list[0])
    probs_no_ion = format_probs_output(100 - prob_list[0] - prob_list[1])
    
    return {'no_ion' : probs_no_ion.tolist(),
            'left_ion' : probs_one_ion.tolist(),
            'right_ion' : probs_one_ion.tolist(),
            'both_ion' : probs_two_ion.tolist()}
    
   
   
def main() :

    cmd_params = read_cmd_line() 
    if 'filepath' in cmd_params :
        exp_params = read_HDF5_file(cmd_params['filepath'])
        filename = re.search('\w+(?:\.\w+)*$', cmd_params['filepath']).group(0)
      
        cmd_params['expnum'] = filename[:3]
        cmd_params['date'] = filename[8:14]
        
    else :
        exp_params = read_HDF5_file(build_file_path(cmd_params['date'], cmd_params['expnum']))
    
    if exp_params['det_hardware'] == 'CAMERA' :    
        photon_counts_left_ion = [find_weighted_sum_image(raw_img, exp_params['statedet']['left_ion_weight']) for raw_img in exp_params['raw_data']]
        photon_counts_right_ion = [find_weighted_sum_image(raw_img, exp_params['statedet']['right_ion_weight']) for raw_img in exp_params['raw_data']]
    
        photon_counts_left_ion = reshape_data(photon_counts_left_ion, exp_params['mathematica']['runs'])
        photon_counts_right_ion = reshape_data(photon_counts_right_ion, exp_params['mathematica']['runs'])
        
        left_ion_bright_list = gen_bright_data(photon_counts_left_ion, exp_params['statedet']['t1'])
        right_ion_bright_list = gen_bright_data(photon_counts_right_ion, exp_params['statedet']['t2'])
        
        left_ion_probs_list = find_probs(left_ion_bright_list, exp_params['mathematica']['runs'], exp_params['statedet']['errm1'])
        right_ion_probs_list = find_probs(right_ion_bright_list, exp_params['mathematica']['runs'], exp_params['statedet']['errm2'])
        
        print(json.dumps({"probs":left_ion_probs_list}))
        
        if 'save' in cmd_params and cmd_params['save'] == 1 :
            save_csv_camera(left_ion_probs_list, right_ion_probs_list, exp_params['mathematica'], cmd_params['date'], cmd_params['expnum'])
        
    elif exp_params['det_hardware']  == 'PMT' :
        if 'num_ions' in cmd_params and cmd_params['num_ions'] == 2 :
            bright_list_one, bright_list_two = gen_bright_data_two(exp_params['raw_data'], exp_params['statedet']['t1'], exp_params['statedet']['t2'])
            probs_list = find_probs_two(bright_list_one, bright_list_two, exp_params['mathematica']['runs'], exp_params['statedet']['errm2'])
        else :
            bright_list = gen_bright_data(exp_params['raw_data'], exp_params['statedet']['t1'])
            probs_list = find_probs(bright_list, exp_params['mathematica']['runs'], exp_params['statedet']['errm1'])
        
        print(json.dumps(probs_list))
        
        if 'save' in cmd_params and cmd_params['save'] == 1 :
            #save_csv_pmt(probs_list, cmd_params, exp_params['mathematica'])
            save_csv_probs(probs_list, cmd_params, exp_params['mathematica'])

    return 0
    
if __name__ == "__main__":
    main()
    
    
    
    