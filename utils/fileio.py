import json

def read_json(f):
    with open(f, encoding='utf8') as f:
        return json.load(f)