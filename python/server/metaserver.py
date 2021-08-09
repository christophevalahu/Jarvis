#!/usr/bin/env python

import socket
import metaconstants as mc
import re
import json
import threading
from parselog import cmd2log


# Function to display hostname and 
# IP address 
def get_local_IP(): 
    try: 
        host_name = socket.gethostname() 
        return socket.gethostbyname(host_name) 
    except: 
        print("Unable to find hostname and IP")
        return None

def pre_proc() :
    
    return 0
    
def post_proc() :

    return 0

def classical_optimiser():
    
    return 0

def update_cmd():
    
    return 0
    

def TCP_pre_proc(nsteps, nruns, status) :
    
    if global_cmd != "" :
        print("Pre proc with cmd : ", global_cmd)
    else :
        print( "Pre proc with empty cmd queue, STOPPING! ")
   
    
    BUFFER_SIZE = 100  # Normally 1024, but we want fast response
    
    pre_proc()
       
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((mc.TCP_IP, mc.TCP_PORT_CONTROLLER))
    server.listen(1)
    print("PRE PROC: Waiting on listener...")
    
    conn, addr = server.accept()

    conn.send((str(status)+"\r\n").encode())
    
    if status == mc.CONT_CONTINUE :
        rec_dummy = conn.recv(BUFFER_SIZE)
        print("Recieved : ", rec_dummy)
        log_msg, params = cmd2log(global_cmd)
        params_json = json.dumps(params)
        exp_info = {"cmd": global_cmd, "params":params_json, "explog":log_msg}
        json_params_sent = json.dumps(exp_info)
        conn.send((json_params_sent + "\r\n").encode())
    
    server.close()
    
    return True

def TCP_post_proc(status) :
    
    BUFFER_SIZE = 1  
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((mc.TCP_IP, mc.TCP_PORT_CONTROLLER))
    server.listen(1)
    print("POST PROC: Waiting on listener...")
    
    conn, addr = server.accept()
    
    action_rcv = int((conn.recv(BUFFER_SIZE)).decode())
    print("POST PROC : Recieved : ", action_rcv)
    
    if action_rcv == mc.CONT_STOP :
        print("CONT SERVER : stopping current cmd")
        server.close()
        return True
    
    post_proc()
    update_cmd()
    
    json_sent = json.dumps({"dummy" : "placeholder"})
    conn.send((json_sent + "\r\n").encode())
        
    conn.send((str(status)+"\r\n").encode())
    
    server.close()
    
    return False



def parse_meta_script() :
    
    with open(mc.META_SCRIPT_FILE_PATH) as f:
        cmd_list = f.readlines()
    cmd_list = [cmd.strip() for cmd in cmd_list] 
    
    cmd_list_new = []
    
    for cmd in cmd_list :
        if cmd[0] != '#' :
            cmd_list_new.append(cmd)
    
    cmd_list = cmd_list_new
    
    return cmd_list


def get_params_from_cmd(cmd) :
        
    nstepsmatch = re.search('steps\s+=\s+(\d+)', cmd)
    if nstepsmatch:
        nsteps = nstepsmatch.group(1)
    else : 
        nsteps = 0
        
    nrunsmatch = re.search('runs\s+=\s+(\d+)', cmd)
    if nrunsmatch:
        nruns = nrunsmatch.group(1)
    else :
        nruns = 0
    
    return nsteps, nruns


def innit_compile() :

    cmd_list = parse_meta_script()
    
    nsteps, nruns = get_params_from_cmd(cmd_list)
    
    
    return cmd_list, nsteps, nruns


def save_cmd_to_temp_file(cmd) :
    
    
    temp_file = open(mc.META_TEMP_FILE_PATH,"w+")
    
    for import_line in mc.IMPORTS :
        temp_file.write(import_line + '\n')
    temp_file.write(cmd)
    temp_file.close()
    
    return 0
    
def cont_get_inni_action() :

    BUFFER_SIZE = 1  # Normally 1024, but we want fast response
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((mc.TCP_IP, mc.TCP_PORT_CONTROLLER))
    server.listen(1)
    print("CONT SERVER: Waiting on innit action listener...")
    
    conn, addr = server.accept()
    action_rcv = int((conn.recv(BUFFER_SIZE)).decode())
    print("CONT SERVER: Inni action received = ", action_rcv)
    conn.send(("\r\n").encode())
    server.close()

    return action_rcv
    

def server_cont(event, lock, exit_event) :
    
    global global_cmd, global_queue
    
    global_cmd = ""
    global_queue = []
    nsteps = 0
    nruns = 0    
    
    #global_queue, nsteps_queue, nruns_queue = innit_compile()
    
    print("CONT: Event set")
    event.set()
    
    while True :
    
        inni_action = cont_get_inni_action()
    
        if inni_action == mc.CONT_INNI_STOP :
            print("CONT SERVER: Inni action exit, stopping server... ")
            return 0
        elif inni_action == mc.CONT_INNI_RUN :
            print("CONT SERVER: Inni action = run")
            pass
        else :
            print("CONT SERVER: Inni action unrecognized, stopping server!")
            return 0
    
        if exit_event.is_set() :
            return 0
                        
        
        if global_queue == [] :
            global_cmd = ""
            nruns = 0
            nsteps = 0
            TCP_pre_proc(0, 0, mc.CONT_STOP)
        
        else :
            
            lock.acquire()
            global_cmd = global_queue[0]
            del global_queue[0]
            nsteps, nruns = get_params_from_cmd(global_cmd)
            save_cmd_to_temp_file(global_cmd)
            lock.release()
            
            print("Running CONT server with nsteps = ", nsteps, " and nruns= ", nruns)
        
            start_exp = TCP_pre_proc(nsteps, nruns, mc.CONT_CONTINUE)
            
            if start_exp :
                for i in list(range(int(nsteps))) :
                    print("Post proc, index i = ", i)
                
                    stop_current_cmd = TCP_post_proc(mc.CONT_CONTINUE)
                    if stop_current_cmd :
                        global_cmd = ""
                        print("Stopping the run")
                        break;
            
            classical_optimiser()
            print("Finished run" )
    
    return 0
    
def check_cmd_valid(cmd) :

    if len(cmd) <= 1 :
        return False
    if cmd[0] == '#' :
        return False
    
    return True


def update_queue(json_queue) :
    
    queue = (json.loads(json_queue))["queue"]
    temp_queue = []
    
    for cmd in queue :
        if check_cmd_valid(cmd) == True :
            temp_queue.append(cmd)
    #print("Updated global queue : ", global_queue)
    
    return temp_queue
    
def server_queue(event, lock, exit_event) :
    
    global global_cmd, global_queue, nsteps_queue, nruns_queue 
    
    event.wait()
    event.clear()
    print("QUEUE: Event cleared")
    
    while True :
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((mc.TCP_IP, mc.TCP_PORT_QUEUE))
        server.listen(1)
        #print("SERVER QUEUE: Waiting on listener...")
        
        conn, addr = server.accept()
        
        BUFFER_SIZE_ACTION = 1
        BUFFER_SIZE_QUEUE_IN = 1000
        
        action = int((conn.recv(BUFFER_SIZE_ACTION)).decode())
        
        if action == mc.QUEUE_READ :
            #print("Action Recieved : READ")
            lock.acquire()
            json_queue = json.dumps({"cmd" : global_cmd, "queue" : global_queue})
            lock.release()
            #print("Sending queue to be read : ", global_queue)
            conn.send((json_queue + "\r\n").encode())
        elif action == mc.QUEUE_WRITE :
            #print("Action Recieved : WRITE")
            lock.acquire()
            json_queue_new = (conn.recv(BUFFER_SIZE_QUEUE_IN)).decode()
            #print("Queue server : New Queue = ", json_queue_new)
            global_queue = update_queue(json_queue_new)
            #print("Global queue from here ", global_queue)
            lock.release()
        elif action == mc.QUEUE_SHUTDOWN :
            #print("Action Recieved : SHUTDOWN")
            #print("Queue Server : Shutting down...")
            exit_event.set()
            break
        else :
            #print("Queue Server Error : Action not recognised")
            pass
            
    return 0
       
       
       
def main() :

    lock = threading.Lock()
    event = threading.Event()
    exit_event = threading.Event()
    
    t_server_cont = threading.Thread(target=server_cont, args = (event, lock, exit_event))
    t_server_queue = threading.Thread(target=server_queue, args = (event, lock, exit_event))
    t_server_cont.start()
    t_server_queue.start()

    
       

if __name__ == "__main__": 
    main()











































