from spacenlichten import aliasing
from spacenlichten import node
from spacenlichten import api

state = api.SpacenStrip(api.BINARY)

def handler_1(json):
    state.feedback = True
    state.on = [ True ]
    
    other = api.SpacenStrip(api.BINARY)
    
    other.on = [ None, False, True ]
    
    state.merge(other)
    
    if state.feedback:
        return state.to_json()

def handler_2(json):
    return None

def handler_3(json):
    return None

my_node = node.Node("wlp3s0", aliasing.IP)

#my_node.register_device("172.16.200.204", 8, handler_1)

br = my_node.register_device("10.23.42.201", 8, handler_1)
my_node.register_device("10.23.42.202", 8, handler_2)
my_node.register_device("10.23.42.203", 8, handler_3)

my_node.start()

test = input()

print('TEST')
br("TEEEEEEEEST")

test = input()

print('TEST')
br("TEEEEEEEEST")

test = input()

print('TEST')
br("TEEEEEEEEST")

test = input()

my_node.stop()
