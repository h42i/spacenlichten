from spacenlichten import aliasing
from spacenlichten import node
from spacenlichten import api

import RPi.GPIO as gpio

bulb_pins = [ 21, 22, 23, 24 ]
bulb_states = [ api.SpacenBulb() ] * 4

# use P1 header pin numbering convention
gpio.setmode(gpio.BOARD)

# set up gpio pins for output
for pin in bulb_pins:
    gpio.setup(pin, gpio.OUT)
    gpio.output(pin, gpio.HIGH)


def bulb_handler(json, index):
    """
    Handles 4 relais to control lights.
    LOW switches the relais 'on',
    HIGH switches it 'off'.
    """
    
    change = api.SpacenBulb(json)
    
    if change.on:
        gpio.output(bulb_pins[index], gpio.LOW)
    elif not change.on:
        gpio.output(bulb_pins[index], gpio.HIGH)
    
    bulb_states[index].merge(change)
    
    if bulb_states[index].feedback:
        return bulb_states[index].to_json()

def bulb_handler_0(json):
    return bulb_handler(json, 0)

def bulb_handler_1(json):
    return bulb_handler(json, 1)

def bulb_handler_2(json):
    return bulb_handler(json, 2)

def bulb_handler_3(json):
    return bulb_handler(json, 3)

bulb_node = node.Node("eth0", aliasing.IP)

bulb_node.register_device("10.23.42.201", 8, bulb_handler_0)
bulb_node.register_device("10.23.42.202", 8, bulb_handler_1)
bulb_node.register_device("10.23.42.203", 8, bulb_handler_2)
bulb_node.register_device("10.23.42.204", 8, bulb_handler_3)

bulb_node.start()

try:
    wait = input()
except:
    pass

bulb_node.stop()
