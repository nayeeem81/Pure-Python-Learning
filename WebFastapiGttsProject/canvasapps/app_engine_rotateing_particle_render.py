import tkinter as tk
import math
import random

class Particle3D:
    """Represents a single mathematical shape in a 3D coordinate space matrix."""
    def __init__(self, x, y, z, base_radius=10, color="#58a6ff"):
        self.x = x  # Math X coordinate
        self.y = y  # Math Y coordinate
        self.z = z  # Math Z coordinate (Depth)
        self.base_radius = base_radius
        self.color = color
        
        # Rotated working coordinates (recalculated per frame)
        self.rx = x
        self.ry = y
        self.rz = z
        
    def rotate_y(self, angle_rad):
        """Orbits the particle horizontally around the Y-axis."""
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Apply transformation matrix formula
        self.rx = self.x * cos_a - self.z * sin_a
        self.rz = self.x * sin_a + self.z * cos_a

    def project_and_draw(self, canvas, w, h, focal_length, z_offset):
        """Transforms 3D space points to 2D screen coordinates and renders them."""
        # Translate the object depth out of the camera's eye field
        final_z = self.rz + z_offset
        
        # Safety Guard: Skip drawing if object clips behind camera lens view plane
        if final_z <= 0.5: 
            return

        # 1. Perspective Projection Calculation Step
        proj_x = (self.rx * focal_length) / final_z
        proj_y = (self.ry * focal_length) / final_z
        
        # 2. Scale size relative to depth boundary
        radius_projected = (self.base_radius * focal_length) / final_z

        # 3. Shift origin coordinates to absolute screen canvas center
        px = (w / 2) + proj_x
        py = (h / 2) - proj_y  # Invert Y coordinates

        # Render step (Only if visible inside frame buffer boundaries)
        canvas.create_oval(
            px - radius_projected, py - radius_projected,
            px + radius_projected, py + radius_projected,
            fill=self.color, outline="", width=0
        )


class Engine3DApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced 3D Particle Rotation Engine")
        self.root.geometry("1000x750")

        self.canvas = tk.Canvas(self.root, bg="#090d16", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        # Environment Dimensions
        self.w = 1000
        self.h = 750

        # View Matrix parameters
        self.focal_length = 500
        self.z_camera_offset = 250  # Pushes 3D center away so shapes orbit out front

        # Animation state properties
        self.rotation_angle = 0.0
        self.orbit_speed = 0.015     # Angular speed step per frame increment

        # Initialize the Particle Array Engine
        self.particles = []
        self.generate_particle_field(num_particles=200)

        # Bootstrap core processing frame loop pipeline
        self.update_engine_loop()

    def generate_particle_field(self, num_particles):
        """Populates the matrix space cluster with volumetric rings/clouds."""
        colors = ["#D14009", "#FC9601", "#FFCC33", "#FFE484", "#FFFFFF"]
        
        for i in range(num_particles):
            # Generate random points distributed in a wide 3D sphere volume cluster
            radius = random.uniform(350, 360)
            theta = random.uniform(-5, 2 * math.pi)
            phi = random.uniform(-math.pi / 2, math.pi / 2)

            x = radius * math.cos(phi) * math.cos(theta)
            y = radius * math.sin(phi)
            z = radius * math.cos(phi) * math.sin(theta)
            base_radius = random.uniform(5, 12)
            
            self.particles.append(
                Particle3D(
                    x=x, y=y, z=z, 
                    base_radius=base_radius,
                    color=random.choice(colors)
                )
            )

    def on_resize(self, event):
        self.w = event.width
        self.h = event.height

    def update_engine_loop(self):
        """Processes 3D space tracking vectors and executes drawing calculations."""
        self.canvas.delete("all")

        # 1. Update global orbital timeline angular track state
        self.rotation_angle += self.orbit_speed

        # 2. Calculate the raw 3D matrix transformation changes for each entity
        for p in self.particles:
            p.rotate_y(self.rotation_angle)

        # 3. CRITICAL: Implement Painter's Depth Sorting Algorithm
        # Sort particles descending based on calculated depth rotation (Z index)
        # Objects deep down the screen grid frame stack are rendered first.
        sorted_particles = sorted(self.particles, key=lambda p: p.rz, reverse=True)

        # 4. Render the deep sorted stack layer arrays sequentially
        for p in sorted_particles:
            p.project_and_draw(self.canvas, self.w, self.h, self.focal_length, self.z_camera_offset)

        # Technical Metrics HUD Overlay text display logic
        self.canvas.create_text(
            20, 20, anchor=tk.NW, fill="#7d8590",
            text=f"3D Matrix Telemetry Readout:\n"
                 f"Active Particles Render Pipeline: {len(self.particles)}\n"
                 f"Global Axis Orbit Angle: {math.degrees(self.rotation_angle):.1f}°\n"
                 f"Z-Buffer Sort Phase Status: ACTIVE",
            font=("Consolas", 14)
        )

        # Queue next frame computation pass loop cycle execution safely (~60fps target execution)
        self.root.after(16, self.update_engine_loop)


if __name__ == "__main__":
    # Fix potential Windows layout window blur issues
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    root = tk.Tk()
    app = Engine3DApp(root)
    root.mainloop()
