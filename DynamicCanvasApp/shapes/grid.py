# shapes/grid.py
 # GraphGrid with to_pixels translation math
class GraphGrid:
    def __init__(self, x_min=-10, x_max=10, y_min=-10, y_max=10):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def to_pixels(self, math_x, math_y, w, h):
        """Converts a Cartesian math coordinate (x, y) to Tkinter screen pixels."""
        # Calculate what percentage across the graph the math coordinate is
        x_pct = (math_x - self.x_min) / (self.x_max - self.x_min)
        # Invert Y because Tkinter Y coordinates go downwards
        y_pct = (self.y_max - math_y) / (self.y_max - self.y_min)
        
        pixel_x = x_pct * w
        pixel_y = y_pct * h
        return pixel_x, pixel_y

    def draw(self, canvas, w, h):
        """Draws the X and Y axes onto the screen canvas layout."""
        # Get pixel coordinates for the origin point (0,0)
        origin_x, origin_y = self.to_pixels(0, 0, w, h)
        
        # Draw X-Axis line
        canvas.create_line(0, origin_y, w, origin_y, fill="#888888", width=2)
        # Draw Y-Axis line
        canvas.create_line(origin_x, 0, origin_x, h, fill="#888888", width=2)

