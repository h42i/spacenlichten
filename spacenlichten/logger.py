import datetime
import time

def log(string):
    now_string = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
    
    print("[" + now_string + "] spacenlichten> " + string)
