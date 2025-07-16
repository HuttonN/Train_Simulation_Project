"""
geometry.py

Geometric utility functions for Bezier curves and point distance calculations.
Includes:
- quadratic_bezier: Compute point on a quadratic Bezier curve.
- bezier_derivative: Compute derivative of a Bezier curve at t.
- distance: Euclidean distance between two points.
- bezier_speed: Speed (norm of derivative) along Bezier curve.
"""

import math

def quadratic_bezier(t, start_point, control_point, end_point):
    """
    Return the (x, y) point on a quadratic Bezier curve for parameter t.

    Args:
        t (float): Parameter between 0 and 1.
        start_point (tuple): (x, y) start coordinates.
        control_point (tuple): (x, y) control point coordinates.
        end_point (tuple): (x, y) end coordinates.

    Returns:
        tuple: (x, y) coordinates on the curve at t.
    """
    x = (
        ((1-t) ** 2) * start_point[0]
        + 2 * (1-t) * t * control_point[0]
        + (t ** 2) * end_point[0]
    )
    y = (
        ((1-t) ** 2) * start_point[1]
        + 2 * (1-t) * t * control_point[1]
        + (t ** 2) * end_point[1]
    )
    return x, y

def bezier_derivative(t, start_point, control_point, end_point):
    """
    Return the derivative (dx, dy) of a quadratic Bezier curve at parameter t.
    """
    dx = 2*(1-t)*(control_point[0] - start_point[0]) + 2*t*(end_point[0] - control_point[0])
    dy = 2*(1-t)*(control_point[1] - start_point[1]) + 2*t*(end_point[1] - control_point[1])
    return dx, dy

def distance(p1, p2):
    """
    Return Euclidean distance between two points p1 and p2.
    """
    return math.hypot(p2[0] - p1[0], p2[1] - p1[0])
    
def bezier_speed(t, start_point, control_point, end_point):
    """
    Return ||B'(t)||, the speed along a quadratic Bezier at parameter t.
    """
    dx, dy = bezier_derivative(t, start_point, control_point, end_point)
    return math.hypot(dx, dy)

def closest_point_on_track_piece(px, py, x1, y1, x2, y2):
    """
    Returns the closest point on track piece [(x1, y1), (x2, y2)] to point (px, py).
    """
    # Vector from A to B
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return (x1, y1)  # track piece is a point
    # Vector from A to P
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))  # Clamp t to [0, 1]
    return (x1 + t * dx, y1 + t * dy)
