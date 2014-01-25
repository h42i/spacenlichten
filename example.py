from spacenlichten import aliasing
from spacenlichten import node

def handler_1(json):
    data = {}
    
    data["on"] = True
    data["color"] = {
        "0": {"r": 0x10, "g": 100, "b": 100 },
        "1": {"r": 0x10, "g": 100, "b": 100 }
    }
    
    return data

def handler_2(json):
    return None

def handler_3(json):
    return None

my_node = node.Node("wlp3s0", aliasing.IFCONFIG)

my_node.register_device("10.23.42.201", 8, handler_1)
my_node.register_device("10.23.42.202", 8, handler_2)
my_node.register_device("10.23.42.203", 8, handler_3)

my_node.start()

test = input()

my_node.stop()
