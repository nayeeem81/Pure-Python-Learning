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
        self.grid = GraphGrid(x_min=-32, x_max=32, y_min=-32, y_max=32)
        
        # Initialize primary shapes
        self.rectangle = MathRectangle(mx=-10, my=-10, width=10, height=6, color="#e3f2fd", outline="#2196f3")
        
        self.circle    = MathCircle(mx=-10, my=10, r=10, color="#e3f2fd", outline="#4caf50")
        
        self.ellipse   = MathEllipse(mx=-5, my=5, a_semi=7, b_semi=7, color="#e3f2fd", outline="#9c27b0")
        
        self.parabola  = MathParabola(start=0.1, end=32, curve=0, mx=0, my=0, color="#e3f2fd", outline="#f44336")
        
        # Layer stack arrangement
        self.shapes = [self.rectangle, self.circle, self.ellipse, self.parabola]
        
        # Interactive States Tracking
        self.mouse_math_x = 0.0
        self.mouse_math_y = 0.0
        self.selected_shape = None
        self.clear_shape = False
        self.reset_shape = False
       
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
        # ----------------------------------------------------
        # NEW TRAY 1: BUTTON SELECTION SYSTEM (Directly under Canvas)
        # ----------------------------------------------------
        self.button_tray = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=8, bd=1, relief=tk.RAISED)
        self.button_tray.pack(fill=tk.X, side=tk.TOP) # Stack below canvas, fill horizontally
        
        # Add the requested Rectangle and Circle action buttons
        # Rectangle button (Add rectangle)
        self.btn_rect = tk.Button(self.button_tray, text="Rectangle Tool", width=15, 
                                  font=("Arial", 14, "bold"), bg="#2196f3", fg="white")
        self.btn_rect.pack(side=tk.LEFT, padx=10)
        
        # Circle button (Add circle)
        self.btn_circle = tk.Button(self.button_tray, text="ADD CIRCLE", width=15, 
                                    font=("Arial", 14, "bold"), bg="#4caf50", fg="white")
        self.btn_circle.pack(side=tk.LEFT, padx=10)

        # Reset button (Add Reset Canvas)
        self.btn_reset = tk.Button(self.button_tray, text="RESET", width=15, 
                                   command=self.reset_canvas, font=("Arial", 14, "bold"), bg="#4caf50", fg="white")
        self.btn_reset.pack(side=tk.LEFT, padx=10)
        
        # Clear button (Add Clear Canvas)
        self.btn_clear = tk.Button(self.button_tray, text="CLEAR", width=15, 
                                   command=self.clear_canvas, font=("Arial", 14, "bold"), bg="#f44336", fg="white")
        self.btn_clear.pack(side=tk.LEFT, padx=10)


        """Generates slider rows across the bottom panel tray."""
        # --- COLUMN 0 & 1: Circle Controls ---
        tk.Label(self.control_frame, text="[ CIRCLE CONFIG ]", bg="#f5f5f5", font=("Arial", 14, "bold"), fg="#4caf50").grid(row=0, column=0, columnspan=2)
        
        #  Circle Radius Slider
        tk.Label(self.control_frame, text="Radius (r):", bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W)
        
        self.slider_cr = tk.Scale(self.control_frame, from_=0.5, to=16, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_cr.set(self.circle.r)
        
        self.slider_cr.grid(row=1, column=1, padx=5, pady=2)
        

        #  Circle X-Center Slider
        tk.Label(self.control_frame, text="Center X:", bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W)
        
        self.slider_cx = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_cx.set(self.circle.mx)
        
        self.slider_cx.grid(row=2, column=1, padx=5, pady=2)
        

        #  Circle Y-Center Slider
        tk.Label(self.control_frame, text="Center Y (y):", bg="#f5f5f5").grid(row=3, column=0, sticky=tk.W)

        self.slider_cy = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_cy.set(self.circle.my)
        
        self.slider_cy.grid(row=3, column=1, padx=5, pady=2)



        # --- COLUMN 2 & 3: Rectangle Controls ---
        tk.Label(self.control_frame, text="[ RECTANGLE ]", bg="#f5f5f5", font=("Arial", 14, "bold"), fg="#2196f3").grid(row=0, column=2, columnspan=2)
        
        #  Rectangle Width Slider
        tk.Label(self.control_frame, text="Width (w):", bg="#f5f5f5").grid(row=1, column=2, sticky=tk.W)
        
        self.slider_rw = tk.Scale(self.control_frame, from_=1.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_rw.set(self.rectangle.width)
        
        self.slider_rw.grid(row=2, column=3, padx=5, pady=2)

        #  Rectangle Height Slider
        tk.Label(self.control_frame, text="Height (h):", bg="#f5f5f5").grid(row=3, column=2, sticky=tk.W)
        
        self.slider_rh = tk.Scale(self.control_frame, from_=1.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_rh.set(self.rectangle.height)
        
        self.slider_rh.grid(row=4, column=3, padx=5, pady=2)

        # Rectangle Vertex Y Slider
        tk.Label(self.control_frame, text="Vertex Y:", bg="#f5f5f5").grid(row=5, column=3, sticky=tk.W)
        
        self.slider_ry = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_ry.set(self.rectangle.my)

        self.slider_ry.grid(row=5, column=4, padx=5, pady=2)

        # Rectangle  (X) Sliders

        tk.Label(self.control_frame, text="Vertex X:", bg="#f5f5f5").grid(row=6, column=3, sticky=tk.W)
        
        self.slider_rx = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_rx.set(self.rectangle.mx)
        
        self.slider_rx.grid(row=6, column=4, padx=4, pady=2)

        # --- COLUMN 4 & 5: Ellipse Controls ---
        tk.Label(self.control_frame, text="[ ELLIPSE ]", bg="#f5f5f5", font=("Arial", 14, "bold"), fg="#9c27b0").grid(row=0, column=4, columnspan=2)

        # Ellipse Semi  (a) Sliders
        tk.Label(self.control_frame, text="Semi (a):", bg="#f5f5f5").grid(row=1, column=4, sticky=tk.W)
        
        self.slider_ea = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)

        self.slider_ea.set(self.ellipse.a_semi)

        self.slider_ea.grid(row=2, column=5, padx=5, pady=2)
        
        # Ellipse Semi (b) Sliders
        tk.Label(self.control_frame, text="Semi Y (b):", bg="#f5f5f5").grid(row=3, column=4, sticky=tk.W)
        
        self.slider_eb = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)

        self.slider_eb.set(self.ellipse.b_semi)

        self.slider_eb.grid(row=4, column=5, padx=5, pady=2)

         # Ellipse  (Y) Sliders
        tk.Label(self.control_frame, text="Vertex Y (y):", bg="#f5f5f5").grid(row=5, column=4, sticky=tk.W)
        
        self.slider_ey = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_ey.set(self.ellipse.my)

        self.slider_ey.grid(row=6, column=5, padx=5, pady=2)

        # Ellipse  (X) Sliders
        tk.Label(self.control_frame, text="Vertex X (x):", bg="#f5f5f5").grid(row=7, column=4, sticky=tk.W)
        
        self.slider_ex = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_ex.set(self.ellipse.mx)
        
        self.slider_ex.grid(row=8, column=5, padx=5, pady=2)


        # --- COLUMN 6 & 7: Parabola Controls ---
        tk.Label(self.control_frame, text="[ PARABOLA ]", bg="#f5f5f5", font=("Arial", 14, "bold"), fg="#f44336").grid(row=0, column=6, columnspan=2)

        # Parabola Curve (a) Sliders
        tk.Label(self.control_frame, text="Curve (a):", bg="#f5f5f5").grid(row=1, column=6, sticky=tk.W)
        
        self.slider_pa = tk.Scale(self.control_frame, from_=-1.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_pa.set(self.parabola.curve)
        
        self.slider_pa.grid(row=1, column=7, padx=5, pady=2)
        
        # Parabola (Y) Sliders
        tk.Label(self.control_frame, text="Vertex Y (y):", bg="#f5f5f5").grid(row=2, column=6, sticky=tk.W)
        
        self.slider_py = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_py.set(self.parabola.my)

        self.slider_py.grid(row=2, column=7, padx=5, pady=2)

        # Parabola (X) Sliders
        tk.Label(self.control_frame, text="Vertex X (x):", bg="#f5f5f5").grid(row=3, column=6, sticky=tk.W)
        
        self.slider_px = tk.Scale(self.control_frame, from_=-32.0, to=32.0, resolution=0.1, orient=tk.HORIZONTAL, length=120, command=self.on_ui_modify)
        
        self.slider_px.set(self.parabola.mx)
        
        self.slider_px.grid(row=3, column=7, padx=5, pady=2)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.clear_shape = True

    def reset_canvas(self):
        self.render_scene()
        self.reset_shape = True

    def on_ui_modify(self, val):
        """Fires when user interacts via Sliders directly."""
        if not self.selected_shape:
            self.circle.r = float(self.slider_cr.get())
            self.circle.mx = float(self.slider_cx.get())
            self.circle.my = float(self.slider_cy.get())
            self.rectangle.width = float(self.slider_rw.get())
            self.rectangle.height = float(self.slider_rh.get())
            self.rectangle.mx = float(self.slider_rx.get())
            self.rectangle.my = float(self.slider_ry.get())
            self.ellipse.a_semi = float(self.slider_ea.get())
            self.ellipse.b_semi = float(self.slider_eb.get())   
            self.ellipse.mx = float(self.slider_ex.get())
            self.ellipse.my = float(self.slider_ey.get())
            self.parabola.curve = float(self.slider_pa.get())
            self.parabola.mx = float(self.slider_px.get())
            self.parabola.my = float(self.slider_py.get())
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
        self.clear_shape = False

        for shape in self.shapes:
            if hasattr(shape, 'contains_math_point') and shape.contains_math_point(click_mx, click_my):
                self.selected_shape = shape
                self.drag_offset_x = click_mx - shape.mx
                self.drag_offset_y = click_my - shape.my
                break
            if hasattr(shape, 'contains_math_point_circle') and shape.contains_math_point_circle(click_mx, click_my, shape.r, self.grid):
                self.selected_shape = shape
                self.drag_offset_x = click_mx - shape.mx
                self.drag_offset_y = click_my - shape.my
                break

    def on_mouse_drag(self, event):
        """Fires continuously while dragging the cursor."""
        if self.selected_shape:
            current_mx, current_my = self.pixel_to_math(event.x, event.y)
            new_h = current_mx - self.drag_offset_x
            new_k = current_my - self.drag_offset_y

            self.clear_shape = False
            
            # --- SYNCHRONIZE EACH SHAPE'S  MATCHING SLIDERS ---
            if self.selected_shape == self.circle:
                self.selected_shape.h = round(new_h, 2)
                self.selected_shape.k = round(new_k, 2)
                self.render_scene()
               
            elif self.selected_shape == self.rectangle:
                # Rectangle lacks h/k sliders in your layout, but updates internally
                self.selected_shape.h = round(new_h, 2)
                self.selected_shape.k = round(new_k, 2)
                self.render_scene()

            elif self.selected_shape == self.ellipse:
                # If you add center h/k sliders for the ellipse later, sync them here
                self.selected_shape.h = round(new_h, 2)
                self.selected_shape.k = round(new_k, 2)
                self.render_scene()
               

    def on_mouse_release(self, event):
        self.clear_shape = False

        current_mx, current_my = self.pixel_to_math(event.x, event.y)
        new_h = current_mx - self.drag_offset_x
        new_k = current_my - self.drag_offset_y

        self.selected_shape.h = new_h
        self.selected_shape.k = new_k
        self.render_scene()
        self.selected_shape = None

    def track_mouse_movement(self, event):
        self.mouse_math_x, self.mouse_math_y = self.pixel_to_math(event.x, event.y)
        

    def render_scene(self, event=None):
        if(self.clear_shape and self.reset_shape == False):
            return
        
        if(self.reset_shape):
            self.clear_shape = False
            self.reset_shape = False

        w = self.canvas.winfo_width() if event is None else event.width
        h = self.canvas.winfo_height() if event is None else event.height
        if w > 32 and h > 32:
            self.grid.draw(self.canvas)

            for shape in self.shapes:
                shape.draw(self.canvas, w, h, self.grid)
            
        mx_pixel, my_pixel = self.grid.to_pixels(self.mouse_math_x, self.mouse_math_y)
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
