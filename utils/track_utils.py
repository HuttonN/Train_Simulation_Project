"""
track_utils.py

Helper functions related to track piece operations.
Includes:
    - get_segment_length: Compute the geometric length of a track segment, supporting both straight and curved tracks.
"""

import math

def get_segment_length(track):
    """
    Returns the geometric length of a track piece.

    Arguments:
        track: Track object (expects x0, y0, x1, y1 or a curve_length attribute).

    Returns:
        float: Length of the track piece.
    """
    from core.track.curve import CurvedTrack
    if isinstance(track, CurvedTrack):
        return track.curve_length
    else:
        x0, y0 = track.x0, track.y0
        x1, y1 = track.x1, track.y1
        return math.hypot(x1 - x0, y1 - y0)
    