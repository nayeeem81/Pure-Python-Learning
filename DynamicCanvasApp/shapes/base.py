# shapes/base.py
# Base Shape class
class Shape:
    """Abstract base class that all canvas shapes inherit from."""
    def __init__(self, color="blue", outline="black", width=0, height=0, x=0, y=0, r=0, a_semi=0, b_semi=0, start=0, end=0, curve=0, linewidth=1):
        self.width = linewidth
        self.color = color
        self.outline = outline
        self.width = width
        self.height = height
        self.mx = x          # X-center
        self.my = y          # Y-center
        self.r = r           # Radius (for circles)
        self.a_semi = a_semi
        self.b_semi = b_semi
        self.curve = curve          # Vertical shift factor (for parabolas)
        self.start = start   # Start X coordinate for parabolas
        self.end = end     # End X coordinate for parabolas
        self.mathcoordinates = []  # List to store math coordinates for drawing
        self.pixelcoordinates = []  # List to store pixel coordinates for drawing

    def draw(self, canvas, window_width, window_height):
        raise NotImplementedError("Subclasses must implement the draw method")

