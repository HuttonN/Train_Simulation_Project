import json

from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack
from core.track.station import StationTrack

def load_track_layout(json_path, grid):
    with open(json_path, 'r') as file:
        data = json.load(file)

    track_objects = {}
    for track in data['tracks']:
        tid = track['id']
        if track['type'] == 'straight':
            object = StraightTrack(grid, *track['start'], *track['end'])
        elif track['type'] == 'curve':
            object = CurvedTrack(grid, *track['start'], *track['control'], *track['end'])
        elif track['type'] == 'junction':
            object = JunctionTrack(grid, *track['start'], *track['straight_end'], *track['curve_control'], *track['curve_end'])
        elif track['type'] == 'station':
            object = StationTrack(grid, *track['start'], *track['end'], track['name'])
        else:
            raise ValueError(f"Unknown track type: {track['type']}")
        if "connections" in track:
            object.connections = track["connections"]
        track_objects[tid] = object
    return track_objects