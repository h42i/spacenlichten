import json

_api_version = "0.1.23a"

RGB = 0
MONOCHROME = 1
BINARY = 2

class ApiError(Exception):
    pass

def encode(data):
    # no api validation at this point
    return json.dumps(data)

def decode(string):
    # no api validation at this point
    return json.loads(string)

def _fit_list_length(some_list, needed_length):
    if len(some_list) < needed_length:
        some_list += [ None ] * (needed_length - len(some_list))

class SpacenObject:
    def __init__(self, string=None):
        self.feedback = None
        
        if string != None:
            self.from_json(string)
    
    def _from_json_helper(self, json_dict):
        if "feedback" in json_dict:
            self.feedback = json_dict["feedback"]
    
    def from_json(self, string):
        self._from_json_helper(decode(string))
    
    def _to_json_helper(self):
        json_dict = {}
        
        json_dict["version"] = _api_version
        
        if self.feedback != None:
            json_dict["feedback"] = self.feedback
        
        return json_dict
    
    def to_json(self):
        return encode(self._to_json_helper())
    
    def merge(self, other):
        if isinstance(other, str):
            self.from_json(str)
        elif isinstance(other, SpacenObject):
            self.from_json(other.to_json())
        else:
            raise ApiError("Can't merge object of type " + str(type(other)))

class SpacenLight(SpacenObject):
    def __init__(self, mode, string=None):
        self.latch = None
        
        self._mode = mode
        
        if mode == RGB:
            self.color = None
        elif mode == MONOCHROME:
            self.intensity = None
        elif self._mode == BINARY:
            self.on = None
        else:
            raise ApiError("No such mode.")
        
        SpacenObject.__init__(self, string)
    
    def from_json(self, string):
        if self._mode == RGB:
            self._from_json_helper_rgb(decode(string))
        elif self._mode == MONOCHROME:
            self._from_json_helper_mono(decode(string))
        elif self._mode == BINARY:
            self._from_json_helper_bin(decode(string))
        else:
            raise ApiError("No such mode.")
    
    def _from_json_helper(self, json_dict):
        SpacenObject._from_json_helper(self, json_dict)
        
        if "latch" in json_dict:
            self.latch = json_dict["latch"]
    
    def _from_json_helper_rgb(self, json_dict):
        self._from_json_helper(json_dict)
    
    def _from_json_helper_mono(self, json_dict):
        self._from_json_helper(json_dict)
    
    def _from_json_helper_bin(self, json_dict):
        self._from_json_helper(json_dict)
    
    def to_json(self):
        if self._mode == RGB:
            return encode(self._to_json_helper_rgb())
        elif self._mode == MONOCHROME:
            return encode(self._to_json_helper_mono())
        elif self._mode == BINARY:
            return encode(self._to_json_helper_bin())
        else:
            raise ApiError("No such mode.")
    
    def _to_json_helper(self):
        json_dict = SpacenObject._to_json_helper(self)
        
        if self.latch != None:
            json_dict["latch"] = self.latch
        
        return json_dict
    
    def _to_json_helper_rgb(self):
        json_dict = self._to_json_helper()
        
        return json_dict
    
    def _to_json_helper_mono(self):
        json_dict = self._to_json_helper()
        
        return json_dict
    
    def _to_json_helper_bin(self):
        json_dict = self._to_json_helper()
        
        return json_dict

class SpacenPixel(SpacenLight):
    def __init__(self, mode, string=None):
        SpacenLight.__init__(self, mode, string)
    
    def _from_json_helper_rgb(self, json_dict):
        SpacenLight._from_json_helper_rgb(self, json_dict)
        
        if "color" in json_dict:
            color_dict = json_dict["color"]
            
            if "r" in color_dict and "g" in color_dict and "b" in color_dict:
                self.color = (color_dict["r"],
                              color_dict["g"],
                              color_dict["b"])
    
    def _from_json_helper_mono(self, json_dict):
        SpacenLight._from_json_helper_mono(self, json_dict)
        
        if "intensity" in json_dict:
            self.intensity = json_dict["intensity"]
    
    def _from_json_helper_bin(self, json_dict):
        SpacenLight._from_json_helper_bin(self, json_dict)
        
        if "on" in json_dict:
            self.on = json_dict["on"]
    
    def _to_json_helper_rgb(self):
        json_dict = SpacenLight._to_json_helper_rgb(self)
        
        if self.color != None and len(self.color) == 3:
            json_dict["color"] = {}
            
            color_dict = json_dict["color"]
            
            color_dict["r"] = self.color[0]
            color_dict["g"] = self.color[1]
            color_dict["b"] = self.color[2]
        
        return json_dict
    
    def _to_json_helper_mono(self):
        json_dict = SpacenLight._to_json_helper_mono(self)
        
        if self.intensity != None:
            json_dict["intensity"] = self.intensity
        
        return json_dict
    
    def _to_json_helper_bin(self):
        json_dict = SpacenLight._to_json_helper_bin(self)
        
        if self.on != None:
            json_dict["on"] = self.on
        
        return json_dict

class SpacenStrip(SpacenLight):
    def __init__(self, mode, string=None):
        SpacenLight.__init__(self, mode, string)
    
    def _from_json_helper_rgb(self, json_dict):
        SpacenLight._from_json_helper_rgb(self, json_dict)
        
        if "color" in json_dict:
            color_dict = json_dict["color"]
            
            needed_length = max(int(i_0_key) for i_0_key in color_dict) + 1
            
            if self.color == None:
                self.color = []
            
            _fit_list_length(self.color, needed_length)
            
            for i_0_key in color_dict:
                inner_color_dict_0 = color_dict[i_0_key]
                
                if "r" in inner_color_dict_0 and "g" in inner_color_dict_0 and "b" in inner_color_dict_0:
                    self.color[int(i_0_key)] = (inner_color_dict_0["r"],
                                                inner_color_dict_0["g"],
                                                inner_color_dict_0["b"])
    
    def _from_json_helper_mono(self, json_dict):
        SpacenLight._from_json_helper_mono(self, json_dict)
        
        if "intensity" in json_dict:
            intensity_dict = json_dict["intensity"]
            
            needed_length = max(int(i_0_key) for i_0_key in intensity_dict) + 1
            
            if self.intensity == None:
                self.intensity = []
            
            _fit_list_length(self.intensity, needed_length)
            
            for i_0_key in intensity_dict:
                self.intensity[int(i_0_key)] = intensity_dict[i_0_key]
    
    def _from_json_helper_bin(self, json_dict):
        SpacenLight._from_json_helper_bin(self, json_dict)
        
        if "on" in json_dict:
            on_dict = json_dict["on"]
            
            needed_length = max(int(i_0_key) for i_0_key in on_dict) + 1
            
            if self.on == None:
                self.on = []
            
            _fit_list_length(self.on, needed_length)
            
            for i_0_key in on_dict:
                self.on[int(i_0_key)] = on_dict[i_0_key]
    
    def _to_json_helper_rgb(self):
        json_dict = SpacenLight._to_json_helper_rgb(self)
        
        if self.color != None:
            json_dict["color"] = {}
            
            color_dict = json_dict["color"]
            
            for i_0 in range(len(self.color)):
                if self.color[i_0] != None and len(self.color[i_0]) == 3:
                    color_dict[str(i_0)] = {}
                    
                    inner_color_dict_0 = color_dict[str(i_0)]
                    
                    inner_color_dict_0["r"] = self.color[i_0][0]
                    inner_color_dict_0["g"] = self.color[i_0][1]
                    inner_color_dict_0["b"] = self.color[i_0][2]
        
        return json_dict
    
    def _to_json_helper_mono(self):
        json_dict = SpacenLight._to_json_helper_mono(self)
        
        if self.intensity != None:
            json_dict["intensity"] = {}
            
            intensity_dict = json_dict["intensity"]
            
            for i_0 in range(len(self.intensity)):
                if self.intensity[i_0] != None:
                    intensity_dict[str(i_0)] = self.intensity[i_0]
        
        return json_dict
    
    def _to_json_helper_bin(self):
        json_dict = SpacenLight._to_json_helper_bin(self)
        
        if self.on != None:
            json_dict["on"] = {}
            
            on_dict = json_dict["on"]
            
            for i_0 in range(len(self.on)):
                if self.on[i_0] != None:
                   on_dict[str(i_0)] = self.on[i_0]
        
        return json_dict

class SpacenBulb(SpacenPixel):
    def __init__(self, string=None):
        SpacenLight.__init__(self, BINARY, string)
