import json

from core.track.straight import StraightTrack
from core.track.curve import CurvedTrack
from core.track.junction import JunctionTrack
from core.track.station import StationTrack
from core.track.double_curve_junction import DoubleCurveJunctionTrack

def load_track_layout(json_path, grid):
    with open(json_path, 'r') as file:
        data = json.load(file)

    track_objects = {}
    for track in data['tracks']:
        tid = track['id']
        ttype = track['type']
        if ttype == 'straight':
            track_object = StraightTrack(grid, *track['start'], *track['end'], tid, ttype)
        elif ttype == 'curve':
            track_object = CurvedTrack(grid, *track['start'], *track['control'], *track['end'], tid, ttype)
        elif ttype == 'junction':
            track_object = JunctionTrack(grid, *track['start'], *track['straight_end'], *track['curve_control'], *track['curve_end'], tid, ttype)
        elif ttype == 'station':
            track_object = StationTrack(grid, *track['start'], *track['end'], track['name'], tid, ttype)
        elif ttype == 'double_curve_junction':
            track_object = DoubleCurveJunctionTrack(grid, *track['start'], *track['right_curve_control'], *track['left_curve_control'], *track['right_curve_end'], *track['left_curve_end'], tid, ttype)
        else:
            raise ValueError(f"Unknown track type: {ttype}")
        track_object.connections = track["connections"]
        track_objects[tid] = track_object
    return track_objects