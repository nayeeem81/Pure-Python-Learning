 # Numerical solver finding where shapes cross
 # shapes/intersection.py
class IntersectionSolver:
    @staticmethod
    def find_circle_parabola(circle, parabola, x_min=-10, x_max=10, steps=2000):
        """Finds all true mathematical intersection coordinates between a circle and a parabola."""
        intersections = []
        step_size = (x_max - x_min) / steps
        tolerance = 0.05  # Convergence threshold limit

        # Scan across the visible X-domain space step-by-step
        for i in range(steps):
            x = x_min + (i * step_size)
            
            # 1. Get Y from Parabola: y = a*(x - h)^2 + k
            y_para = parabola.a * ((x - parabola.h) ** 2) + parabola.k
            
            # 2. Check how closely this (x, y) satisfies the Circle Equation: (x-h)^2 + (y-k)^2 - r^2 = 0
            circle_residual = ((x - circle.h) ** 2) + ((y_para - circle.k) ** 2) - (circle.r ** 2)
            
            # If the residual crosses zero, a root exists nearby
            if i > 0:
                prev_x = x - step_size
                prev_y_para = parabola.a * ((prev_x - parabola.h) ** 2) + parabola.k
                prev_residual = ((prev_x - circle.h) ** 2) + ((prev_y_para - circle.k) ** 2) - (circle.r ** 2)
                
                # Check for zero-crossing (signs match or multiply to negative)
                if prev_residual * circle_residual <= 0 or abs(circle_residual) < tolerance:
                    # Refine the point slightly to minimize numerical drift
                    if not any(abs(existing_x - x) < 0.1 for existing_x, _ in intersections):
                        intersections.append((round(x, 2), round(y_para, 2)))
                        
        return intersections
