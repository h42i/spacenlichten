import json

def encode(data):
    # no api validation at this point
    return json.dumps(data)

def decode(string):
    # no api validation at this point
    return json.loads(string)
