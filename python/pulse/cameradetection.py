'''
    Author : Christophe Valahu
    Last Modified : 29/04/19
    File : cameradetection.py
    
    Description : 
    

'''

import numpy as np
import math
import os
import argparse
import json
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import factorial

#--------------------------------------------------------------------------------------------------------------------#
# CONSTANTS
#--------------------------------------------------------------------------------------------------------------------#
this_path = os.path.abspath(os.path.dirname(__file__)) #to build relative path
DATA_FILE_PATH = os.path.join(this_path, "..\\..\\data\\")
DATA_FILE_NAME = "kinetic_"

#dimension list indices
NSTEPS = 0
NRUNS = 1
NREADOUT = 2
NWIDTH = 3
NHEIGHT = 4

#img list indices
DARK = 0
BRIGHT_L = 1
BRIGHT_R = 2

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
    
    
def read_binary_file(date, expnum) :
    #Get raw data from kinetic binary file  
    #Data is a 5D array, dimensions are : nsteps, nruns, nreadouts, width, height
    
    raw_data = np.fromfile(DATA_FILE_PATH + date + "\\" + DATA_FILE_NAME + expnum + ".DAT",  dtype='>i4')
    dim = raw_data[:4] #Get first 4 elements which contain info on the dimension
    raw_data = raw_data[8:] #Discard first 8 elements
    nelems_step = np.prod(dim) #Get the number of elements contained in each step, used to find the number of steps in file
    nsteps = len(raw_data)/nelems_step #Find number of steps
    dim = np.insert(dim, 0, int(nsteps)) #Prepend dimension list with number of steps
    raw_data = raw_data.reshape(dim)
    return raw_data, dim

  
#--------------------------------------------------------------------------------------------------------------------#
# IMAGE PROCESSING
#--------------------------------------------------------------------------------------------------------------------#    
def average_img(raw_data, dim) :
    #For each readout, averages the pixels over every run
    average_images = np.zeros(shape=(dim[NREADOUT], dim[NWIDTH], dim[NHEIGHT]))
    raw_data = raw_data[0]
    
    for data in raw_data :
        average_images += data
    average_images = average_images/dim[NRUNS]
    
    return average_images
    
def normalise_img(img) :

    sum_img = np.sum(img)

    return img/sum_img
    
def process_images(raw_data, dim) :
    
    av_img = average_img(raw_data, dim)
    dark_img = av_img[DARK]
    bright_l_img = av_img[BRIGHT_L]
    
    bright_l_img = bright_l_img - dark_img #Subtract Background
    pos_test = lambda x: max(x,0)
    vfunc = np.vectorize(pos_test)
    bright_l_img = vfunc(bright_l_img) #Make all negative numbers 0
    
    #Normalise bright and dark av images
    bright_l_img = normalise_img(bright_l_img)
    
    #plt.imshow(bright_l_img)
    #plt.show()
    
    return bright_l_img
    
    
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
    
def hist_counts(t, entries) :
    #Obtain sum of counts before and after threshold t
    return [sum(entries[:t]), sum(entries[t:])]

def statedet_fid(t, dark_ent, bright_ent) :
    #Return fidelity of statedet, which is the average of the diagonal elements of the error matrix
    return ((hist_counts(t, dark_ent))[0] + (hist_counts(t, bright_ent))[1])/2
    
def statedetone(raw_data, bright_l_weight, cmd_params) :

    #get lists of weighted sum for dark and bright
    dark_data = []
    bright_data = []
    
    for data in raw_data :
        dark_data += [weighted_sum(data[DARK], bright_l_weight)]
        bright_data += [weighted_sum(data[BRIGHT_L], bright_l_weight)]
        
    min_bin = roundup(min(dark_data + bright_data) - 10)
    max_bin = roundup(max(bright_data + dark_data))
    bins = np.linspace(min_bin, max_bin, 50)
    
    fig = plt.figure(figsize=(10.65,5))  
    ax = fig.add_subplot(111)
     
    #Create histogram from photon dark and bright photon counts
    entries_dark, bin_edges_dark, patches = plt.hist(dark_data, bins,  alpha = .5, histtype = 'bar', color = '#1F77B4', normed = True)
    entries_bright, bin_edges_bright, patches = plt.hist(bright_data, bins, alpha = .5, histtype = 'bar', color = '#FF7F0E', normed = True)
    
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
    fid_list = [statedet_fid(int(bin), entries_dark, entries_bright) for bin in range(len(bin_edges_dark) - 1)] 
    fid = max(fid_list)*(bin_edges_dark[1] - bin_edges_dark[0]) #Multiply by width of one bid to get actual fidelity
    t1 = bin_edges_dark[fid_list.index(max(fid_list))]
   
    if 'genimage' in cmd_params and cmd_params['genimage'] == 1 :
        
        txtboxstr = '\n'.join((
        r'$\mu_{dark}=%.2f$' % (mean_dark, ),
        r'$\mu_{bright}=%.2f$' % (mean_bright, ),
        r'$t1=%.2f$' % (t1, )))
       
        plt.text(.8, .8, txtboxstr, transform = ax.transAxes)
        plt.plot(x_plot, gaussian(x_plot, *parameters_dark), 'r-', lw=2, color = '#1F77B4')
        plt.plot(x_plot, gaussian(x_plot, *parameters_bright), 'r-', lw=2, color = '#FF7F0E')
        ax.set_ylim([0, .05])
        plt.axvline(x=t1, ls = 'dashed', color = 'black')
        plt.title('State det fidelity: %.2f '%(fid*100))
        #plt.show()
        plt.savefig(DATA_FILE_PATH + cmd_params['date'] + '\\exp_' + cmd_params['expnum'] + '.png') 
    
    if 'update' in cmd_params and cmd_params['update'] == 1: 
        pass 
    
    message = "Fidelity = " + '%.2f'%(fid*100) + " %"   
    #output = {'msg': message, 't1': t1, 'errm1': str(errm1)}
    output = {'msg': message, 't1': t1}
    print(json.dumps(output))
    
    
def main() :

    cmd_params = read_cmd_line() 
    raw_data, dim = read_binary_file(cmd_params['date'], cmd_params['expnum'])
    bright_img = process_images(raw_data, dim)
    
    statedetone(raw_data[0], bright_img, cmd_params)
    
    return 0
    
if __name__ == "__main__":
    main()
