import yaml
import os

class ConfigError:
    pass

class Config:
    """
    This is the general configuration structure of spacenlichten.
    
    A configuration file should look like the following:
    
    port: 2358
    interface: eth0
    aliasing: ip
    handlers: ./handlers
    """
    
    def __init__(self, path):
        with open(path, "r") as config_file:
            config = yaml.load(config_file)
            
            for field in ["port", "interface", "aliasing", "handlers"]:
                if not field in config:
                    raise ConfigError("Config field " + field +
                                      " missing in " +
                                      os.path.abspath(path))
            
            self.port = config["port"]
            self.interface = config["interface"]
            self.aliasing = config["aliasing"]
            self.handlers= config["handlers"]
