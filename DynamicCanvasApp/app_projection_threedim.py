import tkinter as tk
import math

class ThreeDProjectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Perspective Canvas Simulation")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(self.root, bg="#0d1117", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        # Window dimension bounds (tracked dynamically)
        self.w = 800
        self.h = 600

        # Camera Configuration properties
        self.focal_length = 400  # Distance from the screen viewport to simulated eye

        # 3D Math Coordinates of our Circle: (X, Y, Z)
        self.circle_x = 0        # Centered horizontally in math space
        self.circle_y = 0        # Centered vertically in math space
        self.circle_z = 5.0      # Current depth distance away (Z > 0 is in front of camera)
        self.base_radius = 80    # Intrinsic mathematical size of the circle

        # Animation State Variables
        self.z_speed = 0.08      # Forward motion velocity per frame cycle step
        self.z_min = 2.0         # Closest boundary before looping back
        self.z_max = 25.0        # Furthest depth threshold limit

        # Bootstrap the persistent animation core loop pipeline execution
        self.animate_frame()

    def on_resize(self, event):
        """Captures window structural expansions cleanly."""
        self.w = event.width
        self.h = event.height

    def project_3d_to_2d(self, x, y, z):
        """Transforms 3D Cartesian coordinates into 2D Tkinter pixel space."""
        # 1. Perspective division calculation core step
        projected_x = (x * self.focal_length) / z
        projected_y = (y * self.focal_length) / z

        # 2. Shift origin framework offset from top-left (0,0) to center of canvas
        pixel_x = (self.w / 2) + projected_x
        # Invert Y to keep classical Cartesian physics intuition uniform
        pixel_y = (self.h / 2) - projected_y
        
        return pixel_x, pixel_y

    def animate_frame(self):
        """Cycles frame updates systematically to handle time-based mechanics."""
        self.canvas.delete("all")

        # Update depth over time: shape moves away down the Z-axis
        self.circle_z += self.z_speed

        # Loop the animation tracking seamlessly when it goes too deep
        if self.circle_z > self.z_max:
            self.circle_z = self.z_min

        # Calculate perspective scaling factor for the shape's visual size
        radius_projected = (self.base_radius * self.focal_length) / self.circle_z

        # Project the circle's math center point onto the 2D window space
        px, py = self.project_3d_to_2d(self.circle_x, self.circle_y, self.circle_z)

        # Draw a depth grid tunnel array visual indicator to anchor depth perception
        self.draw_tunnel_grid()

        # Render the 3D projected circle tracking bounds
        self.canvas.create_oval(
            px - radius_projected, py - radius_projected,
            px + radius_projected, py + radius_projected,
            fill="#58a6ff", outline="#1f6feb", width=3
        )

        # Add data metrics dashboard display tracking readout metrics
        self.canvas.create_text(
            20, 20, anchor=tk.NW, fill="#7d8590",
            text=f"Object Coordinate Vector Matrix Data:\n"
                 f"Math Space Coordinates: X={self.circle_x}, Y={self.circle_y}, Z={self.circle_z:.2f}\n"
                 f"Screen Viewport Pixels: px={int(px)}, py={int(py)}, Dynamic Radius={int(radius_projected)}px",
            font=("Consolas", 11)
        )

        # Schedule the next frame iteration step to execute in ~16ms (Targeting 60 FPS)
        self.root.after(16, self.animate_frame)

    def draw_tunnel_grid(self):
        """Draws background perspective lines to enforce visual immersion depth."""
        cx, cy = self.w / 2, self.h / 2
        # Project corner bounding vectors away from center to simulate structural walls
        corners = [(0, 0), (self.w, 0), (self.w, self.h), (0, self.h)]
        for ox, oy in corners:
            self.canvas.create_line(cx, cy, ox, oy, fill="#21262d", width=1)


if __name__ == "__main__":
    root = tk.Tk()
    app = ThreeDProjectionApp(root)
    root.mainloop()
