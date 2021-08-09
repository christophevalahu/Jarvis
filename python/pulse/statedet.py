'''
    Author : Christophe Valahu
    Last Modified : 29/04/19
    File : statedet.py
    
    Description : 
    
    Cmd args in : (  JSON params = {           "date"     : date      (STRING), 
                                               "expnum"   : expnum    (STRING), 
                                    (OPTIONAL) "filepath" : filepath (STRING), NOTE: Will trump over date and expnum
                                    (OPTIONAL) "update"   : update    (INT,0|1),
                                    (OPTIONAL) "genimage" : genimage  (INT,0|1)}} )
    
'''

import numpy as np
import math
import os
import argparse
import configparser
import json
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import factorial
import csv
import h5py
import warnings
import re
warnings.filterwarnings("ignore")

#--------------------------------------------------------------------------------------------------------------------#
# CONSTANTS
#--------------------------------------------------------------------------------------------------------------------#
#File constants
this_path = os.path.abspath(os.path.dirname(__file__)) #to build relative path
FILE_PATH = os.path.join(this_path, "..\\..\\data\\")
FILE_NAME_CAMERA = "kinetic_"
FILE_NAME_PMT = "test_"
FILE_EXTENSION_CAMERA = ".DAT"
FILE_EXTENSION_PMT = ".csv"
FILE_NAME_BRIGHT_WEIGHT_L = "camera_calibration_left.npy"
FILE_PATH_ION_IMAGE = os.path.join(this_path, "..\\..\\config\\")
CONFIG_FILE_PATH = os.path.join(this_path, "../../config/parameter_config.ini")

#If matplotlib isn't version 3.0, normed kwarg must be use instead of density
MATPLOTLIB_VERSION_OLD = not (matplotlib.__version__[0] == 3 and int(matplotlib.__version__[2]) >= 1) 

#dimension list indices
NRUNS = 0
NREADOUT = 1
NWIDTH = 2
NHEIGHT = 3

#img list indices
DARK = 0
BRIGHT_L = 1
BRIGHT_R = 2

#update condition
MIN_STATEDET_FID = 0.95

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
    return FILE_PATH + date + "\\" + expnum + "_SD_" + date + ".h5"
    
def read_HDF5_file(file_path) :

    f = h5py.File(file_path, 'r')
    
    det_hardware = f.attrs[u'det_hardware'].decode()
    
    json_params = str(f.attrs[u'mathematica'].decode()).replace("'", '"').replace(";",",")
    json_params = json.loads(json_params)
    cam_dim = f.attrs[u'cam_dim']
    if det_hardware == 'CAMERA' :
        no_ion_imgs = f["photon_counts\counts_1"]
        left_ion_imgs = f["photon_counts\counts_2"]
        right_ion_imgs = f["photon_counts\counts_3"]
       
        return {'det_hardware' : det_hardware,
                      'mathematica' : json_params,
                      'cam_dim' :cam_dim,
                      'no_ion': no_ion_imgs[:],
                      'left_ion': left_ion_imgs[:],
                      'right_ion' : right_ion_imgs[:]
                      }
    elif det_hardware == 'PMT' :
        no_ion_counts = f["photon_counts\counts_1"]
        one_ion_counts = f["photon_counts\counts_2"]
        two_ion_counts = f["photon_counts\counts_3"]
        
        return {'det_hardware' : det_hardware,
                      'mathematica' : json_params,
                      'cam_dim' :cam_dim,
                      'no_ion': no_ion_counts[:],
                      'one_ion': one_ion_counts[:],
                      'two_ion' : two_ion_counts[:]
                      }
            
def save_ion_weight_image(ion_weight_img, file_name) :
    #np.save(FILE_PATH_ION_IMAGE + file_name, ion_weight_img)
    np.savetxt(FILE_PATH_ION_IMAGE + file_name + ".csv", ion_weight_img, delimiter=",")
    return 0
    
def update_config(section, option, value) :
    #Overwrite value to config file
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    config.set(section, option, str(value))
    
    with open(CONFIG_FILE_PATH, "w+") as configfile :
        config.write(configfile)
        
    return 0    
    
  
#--------------------------------------------------------------------------------------------------------------------#
# IMAGE PROCESSING
#--------------------------------------------------------------------------------------------------------------------#    
def average_img(raw_data, dim) :
    #For each readout, averages the pixels over every run
    
    average_images = np.zeros(shape=(dim[NWIDTH], dim[NHEIGHT]))
    for data in raw_data :
        average_images += data
    average_images = average_images/dim[NRUNS]
    
    return average_images
    
def normalise_img(img) :
    return np.divide(img, np.sum(img))
    
def get_weight_image(dark_img, one_ion_img, dim) :
    #Input background image and one ion image, finds average of both, subtracts background from one ion image.
    #Then normalise the resulting image so that the sum of all pixels is 1. The resuls is a 2d array where each
    #element represents the weight of a pixel, later used for state detection
    
    
    dark_img = average_img(dark_img, dim)
    one_ion_img = average_img(one_ion_img, dim)
    
    one_ion_img = one_ion_img - dark_img #Subtract Background
    pos_test = lambda x: max(x,0)
    vfunc = np.vectorize(pos_test)
    one_ion_img = vfunc(one_ion_img) #Make all negative numbers 0
    
    #Normalise bright and dark av images
    weight_img = normalise_img(one_ion_img)
    
    #plt.imshow(one_ion_img)
    #plt.show()
    
    return weight_img

    
def show_avg_img(step, file_path) :
    #For post processing, shows the average camera image of a certain step. 
    
   
    exp_data = read_HDF5_file(file_path)
    
    if exp_data['det_hardware'] != 'CAMERA' :
        return {'msg' : 'Wrong hardware', 'img' : []}
    else :
    
        av_no_ion = average_img(exp_data['no_ion'])
        av_left_ion = average_img(exp_data['left_ion'])
        av_right_ion = average_img(exp_data['right_ion'])
    
        return {'msg' : 'Success', 'img' : [1, 2, 3]}
     
        
    
#--------------------------------------------------------------------------------------------------------------------#
# STATE DET
#--------------------------------------------------------------------------------------------------------------------#       
def roundup(x):
    return int(math.ceil(x / 10.0)) * 10
    
def weighted_sum(data_img, weight_img) :
    return np.sum(np.multiply(data_img, weight_img))

def gaussian(x_list, a, b, c):
    #Function for a gaussian distribution
    return [a * math.exp(- (x - b)**2 / (2 * c**2)) for x in x_list]
    
def poisson(k, lamb):
    #Function for a poisson distribution
    return (lamb**k/factorial(k)) * np.exp(-lamb)
    
def hist_counts(t, entries) :
    #Obtain sum of counts before and after threshold t
    return [sum(entries[:t]), sum(entries[t:])]

def statedet_fid(t, dark_ent, bright_ent) :
    #Return fidelity of statedet, which is the average of the diagonal elements of the error matrix
    return ((hist_counts(t, dark_ent))[0] + (hist_counts(t, bright_ent))[1])/2
    
def hist_counts_two(t1, t2, entries) :
    return [sum(entries[:t1]), sum(entries[t1:t2]), sum(entries[t2:])]
    
def statedet_fid_two(t_dict, dark, one_bright, two_bright) :
        return ((hist_counts_two(t_dict['t1'], t_dict['t2'], dark))[0] + (hist_counts_two(t_dict['t1'], t_dict['t2'], one_bright))[1] + (hist_counts_two(t_dict['t1'], t_dict['t2'], two_bright))[2])/3


def statedetone_pmt(dark_data, bright_data, cmd_params) :
    
    dark_data = [int(round(float(data))) for data in dark_data] #Get first column of probs data
    bright_data = [int(round(float(data))) for data in bright_data] #Get second column of probs data
    
    max_bin = max(bright_data)
    
    #dark_data = np.random.poisson(1, 1000)
    #bright_data = np.random.poisson(10, 1000)
    bins= np.linspace(0, max_bin, max_bin+1)
    
    fig = plt.figure(figsize=(10.65,5))
    ax = fig.add_subplot(111)
    
    #Create histogram from photon dark and bright photon counts
    if MATPLOTLIB_VERSION_OLD :
        entries_dark, bin_edges_dark, patches = plt.hist(dark_data, bins, range=[-0.5, max_bin + .5], normed=True, alpha = .5, histtype = 'bar', color = '#1F77B4')
        entries_bright, bin_edges_bright, patches = plt.hist(bright_data, bins, range=[-0.5, max_bin + .5], normed=True, alpha = .5, histtype = 'bar', color = '#FF7F0E')
    else :
        entries_dark, bin_edges_dark, patches = plt.hist(dark_data, bins, range=[-0.5, max_bin + .5], density=True, alpha = .5, histtype = 'bar', color = '#1F77B4')
        entries_bright, bin_edges_bright, patches = plt.hist(bright_data, bins, range=[-0.5, max_bin + .5], density=True, alpha = .5, histtype = 'bar', color = '#FF7F0E')
    
    #Center histograms
    bin_middles_dark = 0.5*(bin_edges_dark[1:] + bin_edges_dark[:-1]) - 0.5
    bin_middles_bright = 0.5*(bin_edges_bright[1:] + bin_edges_bright[:-1])
    
    #Fit poisson curve to bright and dark histogram
    parameters_dark, cov_matrix_dark = curve_fit(poisson, bin_middles_dark, entries_dark)
    parameters_bright, cov_matrix_bright = curve_fit(poisson, bin_middles_bright - 0.5, entries_bright)
    
    #Find mean of poisson fits
    mean_dark = parameters_dark[0]
    mean_bright = parameters_bright[0]
    
    #X data for fit plot
    x_plot = np.linspace(0, max_bin, 1000)
    
    #Find threshhold which gives highest fidelity
    fid_list = [statedet_fid(int(bin), entries_dark, entries_bright) for bin in bins[1:]]
    fid = max(fid_list)
    t1 = fid_list.index(fid) + 1
    
    #Find error matrix for found threshhold
    errm1 = [hist_counts(t1, entries_dark), hist_counts(t1, entries_bright)]
    
    message = "Fidelity = " + '%.2f'%(fid*100) + " %" 
    
    if 'genimage' in cmd_params and cmd_params['genimage'] == 1:
    
        txtboxstr = '\n'.join((
        r'$\mu_{dark}=%.2f$' % (mean_dark, ),
        r'$\mu_{bright}=%.2f$' % (mean_bright, ),
        r'$t1=%.2f$' % (t1, )))
        
        plt.text(.8, .8, txtboxstr, transform = ax.transAxes)
        plt.plot(x_plot, poisson(x_plot, *parameters_dark), 'r-', lw=2, color = '#1F77B4')
        plt.plot(x_plot, poisson(x_plot, *parameters_bright), 'r-', lw=2, color = '#FF7F0E')
        plt.axvline(x=t1, ls = 'dashed', color = 'black')
        plt.title('State det fidelity: %.2f'%(fid*100))
        #plt.show()
        if not os.path.exists(FILE_PATH + cmd_params['date'] + '\\_images\\') :
            os.makedirs(FILE_PATH + cmd_params['date'] + '\\_images\\')
        plt.savefig(FILE_PATH + cmd_params['date'] + '\\_images\\' + cmd_params['expnum']+ '_' + cmd_params['date']+ '.png') 
    
    if 'update' in cmd_params and cmd_params['update'] == 1 :
        if (fid > MIN_STATEDET_FID) :
            update_config('state_det_pmt', 't1', t1)
            update_config('state_det_pmt', 'errm1', str(errm1))  
        else :
            message = "Fidelity = " + '%.2f'%(fid*100) + " %, too low to update cfg!"
    
    output = {'msg': message, 't1': t1, 'errm1': str(errm1)}
    print(json.dumps(output))
    
    return 0
    
def statedettwo_pmt(dark_data, one_bright_data, two_bright_data, cmd_params) :
    
    dark_data = [int(round(float(data))) for data in dark_data] #Get first column of probs data
    one_bright_data = [int(round(float(data))) for data in one_bright_data] #Get second column of probs data
    two_bright_data = [int(round(float(data))) for data in two_bright_data] #Get second column of probs data
    
    max_bin = max([max(one_bright_data), max(two_bright_data)])
    
    #dark_data = np.random.poisson(1, 1000)
    #bright_data = np.random.poisson(10, 1000)
    bins= np.linspace(0, max_bin, max_bin+1)
    
    fig = plt.figure(figsize=(10.65,5))
    ax = fig.add_subplot(111)
    
    #Create histogram from photon dark and bright photon counts
    if MATPLOTLIB_VERSION_OLD :
        entries_dark, bin_edges_dark, patches = plt.hist(dark_data, bins, range=[-0.5, max_bin + .5], normed=True, alpha = .5, histtype = 'bar', color = '#1F77B4')
        entries_one_bright, bin_edges_one_bright, patches = plt.hist(one_bright_data, bins, range=[-0.5, max_bin + .5], normed=True, alpha = .5, histtype = 'bar', color = '#FF7F0E')
        entries_two_bright, bin_edges_two_bright, patches = plt.hist(two_bright_data, bins, range=[-0.5, max_bin + .5], normed=True, alpha = .5, histtype = 'bar', color = '#6EC175')
    else :
        entries_dark, bin_edges_dark, patches = plt.hist(dark_data, bins, range=[-0.5, max_bin + .5], density=True, alpha = .5, histtype = 'bar', color = '#1F77B4')
        entries_one_bright, bin_edges_one_bright, patches = plt.hist(one_bright_data, bins, range=[-0.5, max_bin + .5], density=True, alpha = .5, histtype = 'bar', color = '#FF7F0E')
        entries_two_bright, bin_edges_two_bright, patches = plt.hist(two_bright_data, bins, range=[-0.5, max_bin + .5], density=True, alpha = .5, histtype = 'bar', color = '#6EC175')
           
    #Center histograms
    #bin_middles_dark = 0.5*(bin_edges_dark[1:] + bin_edges_dark[:-1])
    bin_middles_dark = 0.5*(bin_edges_dark[1:] + bin_edges_dark[:-1]) - 0.5
    bin_middles_one_bright = 0.5*(bin_edges_one_bright[1:] + bin_edges_one_bright[:-1])
    bin_middles_two_bright = 0.5*(bin_edges_two_bright[1:] + bin_edges_two_bright[:-1])
    
    #Fit poisson curve to bright and dark histogram
    parameters_dark, cov_matrix_dark = curve_fit(poisson, bin_middles_dark, entries_dark)
    parameters_one_bright, cov_matrix_one_bright = curve_fit(poisson, bin_middles_one_bright - 0.5, entries_one_bright)
    parameters_two_bright, cov_matrix_two_bright = curve_fit(poisson, bin_middles_two_bright - 0.5, entries_two_bright)
    
    #Find mean of poisson fits
    mean_dark = parameters_dark[0]
    mean_one_bright = parameters_one_bright[0]
    mean_two_bright = parameters_two_bright[0]
   
    #X data for fit plot
    x_plot = np.linspace(0, max_bin, 1000)
    
    #Find threshhold which gives highest fidelity
    thresh_list = []
    for t2 in range(1, max_bin) :
        for t1 in range(t2) :
            thresh_list += [{'t1' : t1, 't2' : t2}]
    fid_list = [statedet_fid_two(thresh, entries_dark, entries_one_bright, entries_two_bright) for thresh in thresh_list]
    fid = max(fid_list)
    t_opt_dict = thresh_list[fid_list.index(fid)]
    t1 = t_opt_dict['t1']
    t2 = t_opt_dict['t2']
       
    #Find error matrix for found threshhold
    errm2 = [hist_counts_two(t_opt_dict['t1'], t_opt_dict['t2'], entries_dark), 
             hist_counts_two(t_opt_dict['t1'], t_opt_dict['t2'], entries_one_bright), 
             hist_counts_two(t_opt_dict['t1'], t_opt_dict['t2'], entries_two_bright)]
        
    message = "Fidelity = " + '%.2f'%(fid*100) + " %" 
    
    if 'genimage' in cmd_params and cmd_params['genimage'] == 1:
        
        txtboxstr = '\n'.join((
        r'$\mu_{dark}=%.2f$' % (mean_dark, ),
        r'$\mu_{one_bright}=%.2f$' % (mean_one_bright, ),
        r'$\mu_{two_bright}=%.2f$' % (mean_two_bright, ),
        r'$t1=%.2f$' % (t1, ),
        r'$t2=%.2f$' % (t2, )))
        
        plt.text(.8, .7, txtboxstr, transform = ax.transAxes)
        plt.plot(x_plot, poisson(x_plot, *parameters_dark), 'r-', lw=2, color = '#1F77B4')
        plt.plot(x_plot, poisson(x_plot, *parameters_one_bright), 'r-', lw=2, color = '#FF7F0E')
        plt.plot(x_plot, poisson(x_plot, *parameters_two_bright), 'r-', lw=2, color = '#6EC175')
        plt.axvline(x=t1, ls = 'dashed', color = 'black')
        plt.axvline(x=t2, ls = 'dashed', color = 'black')
        plt.title('State det fidelity: %.2f'%(fid*100))
        #plt.show()
        if not os.path.exists(FILE_PATH + cmd_params['date'] + '\\_images\\') :
            os.makedirs(FILE_PATH + cmd_params['date'] + '\\_images\\')
        plt.savefig(FILE_PATH + cmd_params['date'] + '\\_images\\' + cmd_params['expnum']+ '_' + cmd_params['date']+ '.png') 
    '''
    if 'update' in cmd_params and cmd_params['update'] == 1 :
        if (fid > MIN_STATEDET_FID) :
            update_config('state_det_pmt', 't1', t1)
            update_config('state_det_pmt', 'errm2', str(errm2))  
        else :
            message = "Fidelity = " + '%.2f'%(fid*100) + " %, too low to update cfg!"
    '''
    output = {'msg': message, 't1': t1, 't2': t2, 'errm2': str(errm2)}
    print(json.dumps(output))
    
    return 0
    
def statedetone_camera(dark_imgs, ion_imgs, ion_weight, cmd_params) :

    #get lists of weighted sum for dark and bright
    dark_data = []
    bright_data = []
    
    for dark_img in dark_imgs :
        dark_data += [weighted_sum(dark_img, ion_weight)]
    
    for ion_img in ion_imgs :
        bright_data += [weighted_sum(ion_img, ion_weight)]
        
    min_bin = roundup(min(dark_data + bright_data) - 10)
    max_bin = roundup(max(bright_data + dark_data))
    bins = np.linspace(min_bin, max_bin, 50)
    
    fig = plt.figure(figsize=(10.65,5))  
    ax = fig.add_subplot(111)
     
    #Create histogram from photon dark and bright photon counts
    if MATPLOTLIB_VERSION_OLD :
        entries_dark, bin_edges_dark, patches = plt.hist(dark_data, bins,  alpha = .5, histtype = 'bar', color = '#1F77B4', normed = True)
        entries_bright, bin_edges_bright, patches = plt.hist(bright_data, bins, alpha = .5, histtype = 'bar', color = '#FF7F0E', normed = True)
    else:
        entries_dark, bin_edges_dark, patches = plt.hist(dark_data, bins,  alpha = .5, histtype = 'bar', color = '#1F77B4', density = True)
        entries_bright, bin_edges_bright, patches = plt.hist(bright_data, bins, alpha = .5, histtype = 'bar', color = '#FF7F0E', density = True)


    #Fit poisson curve to bright and dark histogram
    initial_guess_dark = [.015, 500, 100]
    initial_guess_bright = [.015, 900, 100]
    parameters_dark, cov_matrix_dark = curve_fit(gaussian, bin_edges_dark[:-1], entries_dark, initial_guess_dark)
    parameters_bright, cov_matrix_bright = curve_fit(gaussian, bin_edges_bright[:-1], entries_bright, initial_guess_bright)
    
    #Find mean of poisson fits
    mean_dark = parameters_dark[1]
    mean_bright = parameters_bright[1]
        
    #X data for fit plot
    x_plot = np.linspace(min_bin, max_bin, 1000)
    
    #Find threshhold which gives highest fidelity
    bin_width = (bin_edges_dark[1] - bin_edges_dark[0])
    fid_list = [statedet_fid(int(bin), entries_dark, entries_bright) for bin in range(len(bin_edges_dark) - 1)] 
    fid = max(fid_list)*bin_width #Multiply by width of one bid to get actual fidelity
    max_bin = fid_list.index(max(fid_list))
    t1 = int(bin_edges_dark[fid_list.index(max(fid_list))])
   
    #Find error matrix for found threshhold
    errm1 = np.dot([hist_counts(max_bin, entries_dark), hist_counts(max_bin, entries_bright)], bin_width).tolist()
   
    message = "Fidelity = " + '%.2f'%(fid*100) + " %"  
   
    if 'genimage' in cmd_params and cmd_params['genimage'] == 1 :
        
        txtboxstr = '\n'.join((
        r'$\mu_{dark}=%.2f$' % (mean_dark, ),
        r'$\mu_{bright}=%.2f$' % (mean_bright, ),
        r'$t1=%.2f$' % (t1, )))
       
        plt.text(.8, .8, txtboxstr, transform = ax.transAxes)
        plt.plot(x_plot, gaussian(x_plot, *parameters_dark), 'r-', lw=2, color = '#1F77B4')
        plt.plot(x_plot, gaussian(x_plot, *parameters_bright), 'r-', lw=2, color = '#FF7F0E')
        ax.set_ylim([0, 0.05])
        plt.axvline(x=t1, ls = 'dashed', color = 'black')
        plt.title('State det fidelity: %.2f '%(fid*100))
        #plt.imshow(ion_weight, extent=[700, 1000, 0,0.05], aspect = 300/0.015 / (10.65/5))
        #fig.figimage(ion_weight, 0, 1)
        newax = fig.add_axes([0.17, 0.42, 0.2, 0.4], anchor='NE', zorder=1)
        newax.imshow(ion_weight.transpose())
        newax.axis('off')
        #plt.show()
        if not os.path.exists(FILE_PATH + cmd_params['date'] + '\\_images\\') :
            os.makedirs(FILE_PATH + cmd_params['date'] + '\\_images\\')
        plt.savefig(FILE_PATH + cmd_params['date'] + '\\_images\\' + cmd_params['expnum'] + '_' +  cmd_params['date']+ '.png') 
    
    if 'update' in cmd_params and cmd_params['update'] == 1: 
        if (fid > MIN_STATEDET_FID) :
            update_config('state_det_camera', 't1', t1)
            update_config('state_det_camera', 'errm1', str(errm1))
            save_ion_weight_image(left_ion_weight, "left_ion_weight")
        else :
            message = "Fidelity = " + '%.2f'%(fid*100) + " %, too low to update cfg!"
             
    output = {'msg': message, 't1': t1, 'errm1': str(errm1)}
    
    print(json.dumps(output))
   
def statedettwo_camera(dark_imgs, ion_left_imgs, ion_right_imgs, ion_left_weight, ion_right_weight, cmd_params) :

    #get lists of weighted sum for dark and bright
    dark_left_data = []
    bright_left_data = []
    dark_right_data = []
    bright_right_data = []
    
    for dark_img in dark_imgs :
        dark_left_data += [weighted_sum(dark_img, ion_left_weight)]
        dark_right_data += [weighted_sum(dark_img, ion_right_weight)]
        
    for ion_left_img in ion_left_imgs :
        bright_left_data += [weighted_sum(ion_left_img, ion_left_weight)]
        
    for ion_right_img in ion_right_imgs :
        bright_right_data += [weighted_sum(ion_right_img, ion_right_weight)]
        
    min_bin = roundup(min(dark_left_data + bright_left_data) - 10)
    max_bin_left = roundup(max(bright_left_data + dark_left_data))
    max_bin_right = roundup(max(bright_right_data + dark_right_data))
    max_bin = max([max_bin_left, max_bin_right])
    bins = np.linspace(min_bin, max_bin, 50)
    
    fig = plt.figure(figsize=(10.65,5))  
    ax = fig.add_subplot(111)
     
    #Create histogram from photon dark and bright photon counts
    if MATPLOTLIB_VERSION_OLD :
        entries_left_dark, bin_edges_left_dark, patches = plt.hist(dark_left_data, bins,  alpha = .5, histtype = 'bar', color = '#1F77B4', normed = True)
        entries_left_bright, bin_edges_left_bright, patches = plt.hist(bright_left_data, bins, alpha = .5, histtype = 'bar', color = '#FF7F0E', normed = True)
        entries_right_dark, bin_edges_right_dark, patches = plt.hist(dark_right_data, bins,  alpha = .5, histtype = 'bar', color = '#8D5E9E', normed = True)
        entries_right_bright, bin_edges_right_bright, patches = plt.hist(bright_right_data, bins, alpha = .5, histtype = 'bar', color = '#5EA068', normed = True)
    else:
        entries_left_dark, bin_edges_left_dark, patches = plt.hist(dark_left_data, bins,  alpha = .5, histtype = 'bar', color = '#1F77B4', density = True)
        entries_left_bright, bin_edges_left_bright, patches = plt.hist(bright_left_data, bins, alpha = .5, histtype = 'bar', color = '#FF7F0E', density = True)
        entries_right_dark, bin_edges_right_dark, patches = plt.hist(dark_right_data, bins,  alpha = .5, histtype = 'bar', color = '#8D5E9E', density = True)
        entries_right_bright, bin_edges_right_bright, patches = plt.hist(bright_right_data, bins, alpha = .5, histtype = 'bar', color = '#5EA068', density = True)


    #Fit poisson curve to bright and dark histogram
    initial_guess_left_dark = [.015, 500, 100]
    initial_guess_left_bright = [.015, 900, 100]
    initial_guess_right_dark = [.015, 500, 100]
    initial_guess_right_bright = [.015, 900, 100]
    parameters_left_dark, cov_matrix_left_dark = curve_fit(gaussian, bin_edges_left_dark[:-1], entries_left_dark, initial_guess_left_dark)
    parameters_left_bright, cov_matrix_left_bright = curve_fit(gaussian, bin_edges_left_bright[:-1], entries_left_bright, initial_guess_left_bright)
    parameters_right_dark, cov_matrix_right_dark = curve_fit(gaussian, bin_edges_right_dark[:-1], entries_right_dark, initial_guess_right_dark)
    parameters_right_bright, cov_matrix_right_bright = curve_fit(gaussian, bin_edges_right_bright[:-1], entries_right_bright, initial_guess_right_bright)
    
    #Find mean of poisson fits
    mean_left_dark = parameters_left_dark[1]
    mean_left_bright = parameters_left_bright[1]
    mean_right_dark = parameters_right_dark[1]
    mean_right_bright = parameters_right_bright[1]
        
    #X data for fit plot
    x_plot = np.linspace(min_bin, max_bin, 1000)
    
    #Find threshhold which gives highest fidelity
    bin_width = (bin_edges_left_dark[1] - bin_edges_left_dark[0])
    
    fid_list_left = [statedet_fid(int(bin), entries_left_dark, entries_left_bright) for bin in range(len(bin_edges_left_dark) - 1)] 
    fid_left = max(fid_list_left)*bin_width #Multiply by width of one bid to get actual fidelity
    max_bin = fid_list_left.index(max(fid_list_left))
    t1 = int(bin_edges_left_dark[fid_list_left.index(max(fid_list_left))])
    
    fid_list_right = [statedet_fid(int(bin), entries_right_dark, entries_right_bright) for bin in range(len(bin_edges_right_dark) - 1)] 
    fid_right = max(fid_list_right)*bin_width #Multiply by width of one bid to get actual fidelity
    max_bin = fid_list_right.index(max(fid_list_right))
    t2 = int(bin_edges_right_dark[fid_list_right.index(max(fid_list_right))])
   
    #Find error matrix for found threshhold
    errm1 = np.dot([hist_counts(max_bin, entries_left_dark), hist_counts(max_bin, entries_left_bright)], bin_width).tolist()
    errm1 = np.dot([hist_counts(max_bin, entries_right_dark), hist_counts(max_bin, entries_right_bright)], bin_width).tolist()
   
    message = "Fid left ion = " + '%.2f'%(fid_left*100) + " %, Fid right ion = " + '%.2f'%(fid_right*100) + " %"  
   
    if 'genimage' in cmd_params and cmd_params['genimage'] == 1 :
        
        txtboxstr = '\n'.join((
        r'$\mu_{dark_left}=%.2f$' % (mean_left_dark, ),
        r'$\mu_{bright_left}=%.2f$' % (mean_left_bright, ),
        r'$\mu_{dark_right}=%.2f$' % (mean_right_dark, ),
        r'$\mu_{bright_right}=%.2f$' % (mean_right_bright, ),
        r'$t1=%.2f$' % (t1, ),
        r'$t2=%.2f$' % (t2, )))
       
        plt.text(.8, .6, txtboxstr, transform = ax.transAxes)
        plt.plot(x_plot, gaussian(x_plot, *parameters_left_dark), 'r-', lw=2, color = '#1F77B4')
        plt.plot(x_plot, gaussian(x_plot, *parameters_left_bright), 'r-', lw=2, color = '#FF7F0E')
        plt.plot(x_plot, gaussian(x_plot, *parameters_right_dark), 'r-', lw=2, color = '#8D5E9E')
        plt.plot(x_plot, gaussian(x_plot, *parameters_right_bright), 'r-', lw=2, color = '#5EA068')
        ax.set_ylim([0, 0.05])
        plt.axvline(x=t1, ls = 'dashed', color = 'black')
        plt.title('Fidelity left ion: %.2f '%(fid_left*100) + ', fidelity right ion: %.2f '%(fid_right*100))
        #plt.imshow(ion_weight, extent=[700, 1000, 0,0.05], aspect = 300/0.015 / (10.65/5))
        #fig.figimage(ion_weight, 0, 1)
        newax_left = fig.add_axes([0.17, 0.45, 0.2, 0.4], anchor='NE', zorder=1)
        newax_left.imshow(ion_left_weight.transpose())
        newax_left.axis('off')
        newax_right = fig.add_axes([0.17, 0.20, 0.2, 0.4], anchor='NE', zorder=1)
        newax_right.imshow(ion_right_weight.transpose())
        newax_right.axis('off')
        #plt.show()
        if not os.path.exists(FILE_PATH + cmd_params['date'] + '\\_images\\') :
            os.makedirs(FILE_PATH + cmd_params['date'] + '\\_images\\')
        plt.savefig(FILE_PATH + cmd_params['date'] + '\\_images\\' + cmd_params['expnum'] + '_' +  cmd_params['date']+ '.png') 
    
    if 'update' in cmd_params and cmd_params['update'] == 1: 
        if (fid > MIN_STATEDET_FID) :
            update_config('state_det_camera', 't1', t1)
            update_config('state_det_camera', 'errm1', str(errm1))
            update_config('state_det_camera', 't2', t2)
            update_config('state_det_camera', 'errm2', str(errm2))
            save_ion_weight_image(left_ion_weight, "left_ion_weight")
            save_ion_weight_image(right_ion_weight, "right_ion_weight")
        
        else :
            message = "Fidelity = " + '%.2f'%(fid*100) + " %, too low to update cfg!"
             
    output = {'msg': message, 't1': t1, 'errm1': str(errm1)}
    
    print(json.dumps(output))
      
    
def main() :
    
    cmd_params = read_cmd_line() 
    if 'filepath' in cmd_params :
        exp_params = read_HDF5_file(cmd_params['filepath'])
        filename = re.search('\w+(?:\.\w+)*$', cmd_params['filepath']).group(0)
        cmd_params['expnum'] = filename[:3]
        cmd_params['date'] = filename[7:13]
    else :
        exp_params = read_HDF5_file(build_file_path(cmd_params['date'], cmd_params['expnum']))
    
    func_name = exp_params['mathematica']['name']
    
    if exp_params['det_hardware'] == 'CAMERA' :
        left_ion_weight = get_weight_image(exp_params['no_ion'], exp_params['left_ion'], exp_params['cam_dim'])
        
        if func_name == 'statedetone' :
            statedetone_camera(exp_params['no_ion'], exp_params['left_ion'], left_ion_weight, cmd_params)
        elif func_name == 'statedettwo' :
            right_ion_weight = get_weight_image(exp_params['no_ion'], exp_params['right_ion'], exp_params['cam_dim'])
            statedettwo_camera(exp_params['no_ion'], exp_params['left_ion'], exp_params['right_ion'], left_ion_weight, right_ion_weight, cmd_params)
        
    elif exp_params['det_hardware'] == 'PMT' :
        if func_name == 'statedetone' :
            statedetone_pmt(exp_params['no_ion'], exp_params['one_ion'], cmd_params)
        elif func_name == 'statedettwo' :
            statedettwo_pmt(exp_params['no_ion'], exp_params['one_ion'], exp_params['two_ion'], cmd_params)
  
    return 0
    
if __name__ == "__main__":
    main()
