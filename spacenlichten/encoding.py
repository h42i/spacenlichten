import re

def _decode_data(data):
    """
    Generate a python string from utf-8 encoded data and
    strip the http header if present.
    """
    
    dec_data = None
    
    dec_data = data.decode("utf-8")
    
    # strip http header if present
    first_line = dec_data.split("\n")[0]
    
    http_match = re.search("HTTP", first_line)
    
    if http_match:
        http_strip_match = re.search("\r?\n(\r?\n)+", dec_data, re.MULTILINE)
        
        if http_strip_match:
            dec_data = dec_data[http_strip_match.end():]
    
    return dec_data

def _encode_data(string):
    """
    Generate utf-8 encoded data from a python string.
    """
    
    return string.encode("utf-8")
