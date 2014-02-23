import logging

log = None

def set_logger(logger):
    global log
    log = logger
