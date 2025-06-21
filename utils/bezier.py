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