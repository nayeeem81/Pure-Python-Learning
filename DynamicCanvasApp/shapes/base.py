# shapes/base.py
# Base Shape class
class Shape:
    """Abstract base class that all canvas shapes inherit from."""
    def __init__(self, color="blue", outline="black", width=2):
        self.color = color
        self.outline = outline
        self.width = width

    def draw(self, canvas, window_width, window_height):
        raise NotImplementedError("Subclasses must implement the draw method")

