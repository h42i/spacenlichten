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
                    raise ConfigError("Configuration field port is missing in " + os.path.abspath(path))
            
            self.port = config["port"]
            self.interface = config["interface"]
            self.interface_tool = config["aliasing"]
            self.handlers_directory = config["handlers"]
