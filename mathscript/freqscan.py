import csv
import json
import numpy
import scipy
import scipy.optimize as opt
import math
import argparse


DATA_FILE_PATH = "C:\\Users\\Christophe\\Documents\\Jarvis\\data\\"

def read_cmd_line() :

    parser = argparse.ArgumentParser()
    parser.add_argument("probs", help="JSON probs array (str)", type=str)
    args = parser.parse_args()
    json_params = json.loads(args.probs)
    probs_list = json_params['probs']
        
    return probs_list

def read_csv_probs() :

    file_path = DATA_FILE_PATH + date + "\\" + "proc_data_" + exp_num + ".csv"
    with open(file_path, newline = '') as csvfile :
        csv_data = list(csv.reader(csvfile))
    
    raw_data = csv_data[1:]
    json_params = csv_data[0][0]
    json_params = str(json_params).replace("'", '"').replace(";", ",")
    params = json.loads(json_params)
    
    return raw_data, params
    
def main() :

    probs_list = read_csv_probs()
    
    print(probs_list)
    
    return 0
    
if __name__ == "__main__":
    main()