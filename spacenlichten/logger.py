import datetime
import time
import os

verbose = False
log_path = None

def log(string):
    now_string = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
    
    if log_path != None:
        with open(log_path, "a") as log_file:
            log_file.write("[" + now_string + "] " + string + os.linesep)
    
    if verbose:
        print("spacenlichten> [" + now_string + "] " + string)
