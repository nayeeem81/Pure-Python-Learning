# shapes/grid.py
 # GraphGrid with to_pixels translation math
class GraphGrid:
    def __init__(self, x_min=-10, x_max=10, y_min=-10, y_max=10):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    @property
    def width(self):
        """Returns the total width of the grid in math units."""
        return self.x_max - self.x_min
        
    @property
    def height(self):
        """Returns the total height of the grid in math units."""
        return self.y_max - self.y_min

    def to_pixels(self, math_x, math_y):
        """Converts a Cartesian math coordinate (x, y) to Tkinter screen pixels."""
        # Calculate what percentage across the graph the math coordinate is
        x_pct = (math_x - self.x_min) / (self.x_max - self.x_min)
        # Invert Y because Tkinter Y coordinates go downwards
        y_pct = (self.y_max - math_y) / (self.y_max - self.y_min)
        
        pixel_x = x_pct * self.width
        pixel_y = y_pct * self.height
        return pixel_x, pixel_y

    def draw(self, canvas):
        """Draws the X and Y axes onto the screen canvas layout."""
        # Get pixel coordinates for the origin point (0,0)
        origin_x, origin_y = self.to_pixels(0, 0)

        # Draw X-Axis line
        canvas.create_line(0, origin_y, self.x_max, origin_y, fill="#888888", width=2)
        # Draw Y-Axis line
        canvas.create_line(origin_x, 0, origin_x, self.y_max, fill="#888888", width=2)

