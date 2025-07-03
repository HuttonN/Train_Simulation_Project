import json

def load_route(route_path, track_objects):
    with open(route_path, 'r') as file:
        data = json.load(file)
    
    route_list = [
        (track_objects[segment['track']], segment['entry'], segment['exit'])
        for segment in data['route']
    ]
    return route_list