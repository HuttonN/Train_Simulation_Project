"""
track_utils.py

Helper functions related to track piece operations.
Includes:
    - get_segment_length: Compute the geometric length of a track segment, supporting both straight and curved tracks.
"""

def get_segment_length(track, entry_ep=None, exit_ep=None):
    """
    Returns the segment length for a track (works for straight, curve, junction).
    If entry_ep/exit_ep are given, use them for JunctionTrack.
    """
    # For straight/curve: use built-in length
    if hasattr(track, "curve_length"):
        return track.curve_length
    elif hasattr(track, "x0") and hasattr(track, "y0") and hasattr(track, "x1") and hasattr(track, "y1"):
        # For StraightTrack (uses grid coords)
        dx = track.x1 - track.x0
        dy = track.y1 - track.y0
        return (dx ** 2 + dy ** 2) ** 0.5
    # For JunctionTrack
    elif hasattr(track, "get_endpoint_coords") and entry_ep is not None and exit_ep is not None:
        x0, y0 = track.get_endpoint_coords(entry_ep)
        x1, y1 = track.get_endpoint_coords(exit_ep)
        return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    else:
        raise AttributeError("Track object does not have endpoints suitable for segment length calculation.")
