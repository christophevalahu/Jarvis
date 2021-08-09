def statedetone(state = "", steps = 0, runs = 0, calib = 0) :
    log_msg = "State det one ion on " + state + ", runs = " + str(runs)
    params = {"mathematica" : "statedetone", "state" : '', "det" : 0, "step" : 0, "steps" : steps, "runs" : runs, "calib" : calib}
    return log_msg, params
    
def statedettwo(steps = 0, runs = 0, calib = 0) :
    log_msg = "State det two ions, runs = " + str(runs)
    params = {"mathematica" : "statedettwo", "state" : '', "det" : 0, "step" : 0, "steps" : steps, "runs" : runs, "calib" : calib}
    return log_msg, params

def secfreq(mode = "", det = 0, step = 0, steps = 0, runs = 0, amp = 0) :
    log_msg = "Secfreq scan, det = " + str(det)+ ", step = " + str(step) + ", amp = " + str(amp) 
    params = {"mathematica" : "secfreq", "mode" : mode, "det" : det, "step" : step, "steps" : steps, "runs" : runs, "amp": amp}
    return log_msg, params
    
def freqscan(state = "", det = 0, step = 0, steps = 0, runs = 0, calib = 0, sb_cool = False, delay = 0) :
    log_msg = "Frequency scan on " + state + ", det = " + str(det) + ", step = " + str(step)
    params = {"mathematica" : "freqscan", "state" : state, "det" : det, "step" : step, "steps" : steps, "runs" : runs, "calib" : calib}
    return log_msg, params
    
def timescan(state, det = 0, step = 0, steps = 0, runs = 0, sb_cool = False, calib = 0) :
    log_msg = "Time scan on " + state + ", step = " + str(step)
    params = {"mathematica" : "timescan", "state" : state, "det" : det, "step" : step, "steps" : steps, "runs" : runs, "calib" : calib}
    return log_msg, params

def msRFpower(state = "", det = 0, step = 0, steps = 0, runs = 0) :
    log_msg = "RF power match on " + state + ", step = " + str(step) + ", det = " + str(det)
    params = {"mathematica" : "timescan", "state" : state, "det" : det, "step" : step, "steps" : steps, "runs" : runs, "calib" : 0}
    return log_msg, params
    
def msdetscan(mode = "", timemult = 0, det = 0, step = 0, steps = 0, runs = 0, calib = 0) :
    log_msg = "MS gate " + mode + " scan, step = " + str(step) + ", det = " + str(det)
    params = {"mathematica" : "msdetscan", "detmode" : mode, "timemult" : timemult, "state" : "", "det" : det, "step" : step, "steps" : steps, "runs" : runs, "calib" : 0}
    return log_msg, params
    
def optimizeSBcooling(det = 0, step = 0, steps = 0, runs = 0) :
    log_msg = "Optimize SB cooling, step = " + str(step) + ", det = " + str(det)
    params = {"mathematica" : "", "state" : "", "det" : det, "step" : step, "steps" : steps, "runs" : runs, "calib" : 0}
    return log_msg, params

def cmd2log(cmd) :
    
    try :
        log_msg, params = eval(cmd)
    except Exception as e :
        
        log_msg = "parselog.py Error: Unrecognized function: " + cmd + " \n Catched error : " + str(e)
        params = {"mathematica" : "", "state" : '', "det" : 0, "step" : 0, "steps" : 0, "runs" : 0, "calib" : 0}
    
    return log_msg, params
    
