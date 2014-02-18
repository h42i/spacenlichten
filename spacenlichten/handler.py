import yaml
from spacenlichten import reflection

class Handler:
    """
    This is the configuration structure for a devices handler.
    
    Such a file should look like the following:
    
    ip: 10.23.42.123
    script: path/to/handler.py
    """
    
    def __init__(self, path):
        with open(path, "r") as file:
            data = yaml.load(file)
            
            self.ip > data["ip"]
            
            mod_obj = _import_module(data["script"])

