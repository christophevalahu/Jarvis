# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 10:59:36 2019

@author: cv222
"""

# STATES
#Temp examples
CONT_IDLE = 0
CONT_CONTINUE = 1
CONT_STOP = 2

# CONTROLLER INNIT ACTIONS
CONT_INNI_RUN = 0
CONT_INNI_STOP = 1


# QUEUE COMMANDS
QUEUE_WRITE = 0
QUEUE_READ = 1
QUEUE_SHUTDOWN = 2

# PORTS
TCP_PORT_CONTROLLER = 8095
TCP_PORT_QUEUE = 8093
TCP_IP = 'localhost'

META_SCRIPT_FILE_PATH = '..\pulse\scriptmeta.txt'
META_TEMP_FILE_PATH = '..\pulse\_metatemp.py'
IMPORTS = ['from pulsesequences import *','from states import *']
