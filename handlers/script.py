my_broadcast = None

def initialize(broadcast):
    global my_broadcast 
    
    my_broadcast = broadcast

def receive(json_string, send):
    my_broadcast("test")

def run():
    pass
