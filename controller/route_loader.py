import json

def load_route(route_path, track_objects):
    with open(route_path, 'r') as file:
        data = json.load(file)
    route_list = []
    for track_piece in data['route']:
        track_obj = track_objects[track_piece['track']]
        route_list.append({
            "track_obj": track_obj,
            "track_id": track_obj.track_id,
            "entry": track_piece["entry"],
            "exit": track_piece["exit"],
            # Include all other metadata (like "stop?"), if present:
            **{k: v for k, v in track_piece.items() if k not in ("track", "entry", "exit")}
        })
    return route_list
