import math

def quadratic_bezier(t, start_point, control_point, end_point):
        """Return the (x,y) point on a quadratic bezier curve for parameter t"""
        return (
            ((1-t)**2)*start_point[0] + 2*(1-t)*t*control_point[0] + (t**2)*end_point[0],
            ((1-t)**2)*start_point[1] + 2*(1-t)*t*control_point[1] + (t**2)*end_point[1]
        )

def bezier_derivative(t, start_point, control_point, end_point):
        dx = 2*(1-t)*(control_point[0] - start_point[0]) + 2*t*(end_point[0] - control_point[0])
        dy = 2*(1-t)*(control_point[1] - start_point[1]) + 2*t*(end_point[1] - control_point[1])
        return dx, dy

def distance(start_point, end_point):
        return math.hypot(end_point[1] - start_point[0], end_point[1] - end_point[0])

def get_segment_length(track):
    from core.track.curve import CurvedTrack
    if isinstance(track, CurvedTrack):
        return track.curve_length
    else:
        x0, y0 = track.x0, track.y0
        x1, y1 = track.x1, track.y1
        return math.hypot(x1 - x0, y1 - y0)
    
def bezier_speed(t, start_point, control_point, end_point):
      """||B'(t)|| for quadratic Bezier"""
      dx = 2*(1-t)*(control_point[0] - start_point[0]) + 2*t*(end_point[0] - control_point[0])
      dy = 2*(1-t)*(control_point[1] - start_point[1]) + 2*t*(end_point[1] - control_point[1])
      return math.hypot(dx, dy)

def simpson_integral(f, a, b, n = 32):
      """Simpson's Rule for integral of f from a to b"""
      if n % 2:
            n += 1
      h = (b - a) / n
      s = f(a) + f(b)
      for i in range(1, n, 2):
            s += 4*f(a+i*h)
      for i in range(2, n-1, 2):
            s += 2*f(a+i*h)
      return s*h/3
        
