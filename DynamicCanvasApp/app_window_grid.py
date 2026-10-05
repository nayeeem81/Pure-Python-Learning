# app_window_grid.py
import tkinter as tk
from shapes.grid import GraphGrid
from shapes.primitives import MathCircle, MathRectangle, MathEllipse, MathParabola

class DynamicCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Drag & Slide Geometry Engine")
        self.root.geometry("1000x800")
        
        # 1. MAIN CANVAS AREA
        self.canvas = tk.Canvas(self.root, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        # 2. CONTROL DASHBOARD FRAME PANEL
        self.control_frame = tk.Frame(self.root, bg="#f5f5f5", padx=12, pady=12, bd=1, relief=tk.SUNKEN)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 3. MATHEMATICAL GRID ENVIRONMENT
        self.grid = GraphGrid(x_min=-10, x_max=10, y_min=-10, y_max=10)
        
        # Initialize primary shapes
        self.rectangle = MathRectangle(h=3, k=-2, w_math=4, h_math=3, color="#e3f2fd", outline="#2196f3", width=2)
        self.circle    = MathCircle(h=-3, k=4, r=2.5, color="", outline="#4caf50", width=2)
        self.ellipse   = MathEllipse(h=4, k=4, a_semi=3.5, b_semi=1.5, color="", outline="#9c27b0", width=2)
        self.parabola  = MathParabola(a=0.2, h=4, k=-5, color="", outline="#f44336", width=2)
        
        # Layer stack arrangement
        self.shapes = [self.rectangle, self.circle, self.ellipse, self.parabola]
        
        # Interactive States Tracking
        self.mouse_math_x = 0.0
        self.mouse_math_y = 0.0
        self.selected_shape = None
        self.drag_offset_x = 0.0
        self.drag_offset_y = 0.0
        
        # 4. DEPLOY COMPREHENSIVE SLIDERS
        self.build_ui_layout()
        
        # 5. CORE EVENT BINDINGS
        self.canvas.bind("<Configure>", self.render_scene)
        self.canvas.bind("<Motion>", self.track_mouse_movement)
        
        # Bindings for Click and Drag Engine
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
    def build_ui_layout(self):
        """Generates slider rows across the bottom panel tray."""
        # --- COLUMN 0 & 1: Circle Controls ---
        tk.Label(self.control_frame, text="[ CIRCLE CONFIG ]", bg="#f5f5f5", font=("Arial", 9, "bold"), fg="#4caf50").grid(row=0, column=0, columnspan=2)
        
        tk.Label(self.control_frame, text="Radius (r):", bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W)
        self.slider_cr = tk.Scale(self.control_frame, from_=0.5, to=6.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        self.slider_cr.set(self.circle.r)
        self.slider_cr.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Label(self.control_frame, text="Center X (h):", bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W)
        self.slider_ch = tk.Scale(self.control_frame, from_=-8.0, to=8.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        self.slider_ch.set(self.circle.h)
        self.slider_ch.grid(row=2, column=1, padx=5, pady=2)
        
        tk.Label(self.control_frame, text="Center Y (k):", bg="#f5f5f5").grid(row=3, column=0, sticky=tk.W)
        self.slider_ck = tk.Scale(self.control_frame, from_=-8.0, to=8.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        self.slider_ck.set(self.circle.k)
        self.slider_ck.grid(row=3, column=1, padx=5, pady=2)

        # --- COLUMN 2 & 3: Rectangle Controls ---
        tk.Label(self.control_frame, text="[ RECTANGLE ]", bg="#f5f5f5", font=("Arial", 9, "bold"), fg="#2196f3").grid(row=0, column=2, columnspan=2)
        tk.Label(self.control_frame, text="Width (w):", bg="#f5f5f5").grid(row=1, column=2, sticky=tk.W)
        self.slider_rw = tk.Scale(self.control_frame, from_=1.0, to=8.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        self.slider_rw.set(self.rectangle.w_math)
        self.slider_rw.grid(row=1, column=3, padx=5, pady=2)

        # --- COLUMN 4 & 5: Ellipse Controls ---
        tk.Label(self.control_frame, text="[ ELLIPSE ]", bg="#f5f5f5", font=("Arial", 9, "bold"), fg="#9c27b0").grid(row=0, column=4, columnspan=2)
        tk.Label(self.control_frame, text="Semi X (a):", bg="#f5f5f5").grid(row=1, column=4, sticky=tk.W)
        self.slider_ea = tk.Scale(self.control_frame, from_=0.5, to=6.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        self.slider_ea.set(self.ellipse.a_semi)
        self.slider_ea.grid(row=1, column=5, padx=5, pady=2)
        
        tk.Label(self.control_frame, text="Semi Y (b):", bg="#f5f5f5").grid(row=2, column=4, sticky=tk.W)
        self.slider_eb = tk.Scale(self.control_frame, from_=0.5, to=6.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        self.slider_eb.set(self.ellipse.b_semi)
        self.slider_eb.grid(row=2, column=5, padx=5, pady=2)

        # --- COLUMN 6 & 7: Parabola Controls ---
        tk.Label(self.control_frame, text="[ PARABOLA ]", bg="#f5f5f5", font=("Arial", 9, "bold"), fg="#f44336").grid(row=0, column=6, columnspan=2)
        tk.Label(self.control_frame, text="Curve (a):", bg="#f5f5f5").grid(row=1, column=6, sticky=tk.W)
        self.slider_pa = tk.Scale(self.control_frame, from_=-1.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        self.slider_pa.set(self.parabola.a)
        self.slider_pa.grid(row=1, column=7, padx=5, pady=2)
        
        tk.Label(self.control_frame, text="Vertex Y (k):", bg="#f5f5f5").grid(row=2, column=6, sticky=tk.W)
        self.slider_pk = tk.Scale(self.control_frame, from_=-8.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        self.slider_pk.set(self.parabola.k)
        self.slider_pk.grid(row=2, column=7, padx=5, pady=2)

    def on_ui_modify(self, val):
        """Fires when user interacts via Sliders directly."""
        if not self.selected_shape:
            self.circle.r = float(self.slider_cr.get())
            self.circle.h = float(self.slider_ch.get())
            self.circle.k = float(self.slider_ck.get())
            
            self.rectangle.w_math = float(self.slider_rw.get())
            self.ellipse.a_semi = float(self.slider_ea.get())
            self.ellipse.b_semi = float(self.slider_eb.get())
            self.parabola.a = float(self.slider_pa.get())
            self.parabola.k = float(self.slider_pk.get())
            self.render_scene()

    def pixel_to_math(self, px, py):
        """Translates screen pixel inputs into math units."""
        w = max(10, self.canvas.winfo_width())
        h = max(10, self.canvas.winfo_height())
        mx = self.grid.x_min + (px / w) * (self.grid.x_max - self.grid.x_min)
        my = self.grid.y_max - (py / h) * (self.grid.y_max - self.grid.y_min)
        return mx, my

    def on_mouse_click(self, event):
        """Fires the instant click down occurs over the canvas."""
        click_mx, click_my = self.pixel_to_math(event.x, event.y)
        
        for shape in reversed(self.shapes):
            if hasattr(shape, 'contains_math_point') and shape.contains_math_point(click_mx, click_my):
                self.selected_shape = shape
                self.drag_offset_x = click_mx - shape.h
                self.drag_offset_y = click_my - shape.k
                break

    def on_mouse_drag(self, event):
        """Fires continuously while dragging the cursor."""
        if self.selected_shape:
            current_mx, current_my = self.pixel_to_math(event.x, event.y)
            
            new_h = current_mx - self.drag_offset_x
            new_k = current_my - self.drag_offset_y
            
            self.selected_shape.h = round(new_h, 2)
            self.selected_shape.k = round(new_k, 2)
            
            if self.selected_shape == self.circle:
                self.slider_ch.set(self.selected_shape.h)
                self.slider_ck.set(self.selected_shape.k)
                
            self.render_scene()

    def on_mouse_release(self, event):
        self.selected_shape = None

    def track_mouse_movement(self, event):
        self.mouse_math_x, self.mouse_math_y = self.pixel_to_math(event.x, event.y)
        self.render_scene()

    def render_scene(self, event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() if event is None else event.width
        h = self.canvas.winfo_height() if event is None else event.height
        if w < 10 or h < 10: return

        self.grid.draw(self.canvas, w, h)
        
        for shape in self.shapes:
            shape.draw(self.canvas, w, h, self.grid)
            
        mx_pixel, my_pixel = self.grid.to_pixels(self.mouse_math_x, self.mouse_math_y, w, h)
        display_text = f"Matrix: ({self.mouse_math_x:.2f}, {self.mouse_math_y:.2f})"
        
        text_id = self.canvas.create_text(
            mx_pixel + 15, my_pixel + 15, anchor=tk.NW, 
            text=display_text, font=("Consolas", 9, "bold"), fill="#222222"
        )
        
        x1, y1, x2, y2 = self.canvas.bbox(text_id)
        
        bg_rect_id = self.canvas.create_rectangle(
            x1 - 3, y1 - 3, x2 + 3, y2 + 3, 
            fill="#ffffff", outline="#dddddd", width=1
        )
        
        self.canvas.tag_lower(bg_rect_id, text_id)
