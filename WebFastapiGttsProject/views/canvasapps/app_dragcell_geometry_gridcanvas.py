import tkinter as tk

class GridCanvas(tk.Canvas):
    def __init__(self, parent, rows=15, cols=20, cell_size=40, grid_color="#E0E0E0", **kwargs):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid_color = grid_color
        
        # নাম্বারিং বা লেবেলের জন্য অফসেট (পিক্সেল মার্জিন) নির্ধারণ করা
        self.offset_x = 30  # বাম পাশে রো নম্বরের জন্য জায়গা
        self.offset_y = 30  # ওপরে কলাম নম্বরের জন্য জায়গা
        
        # ক্যানভাসের মোট সাইজ (গ্রিড সাইজ + অফসেট মার্জিন)
        width = (cols * cell_size) + self.offset_x
        height = (rows * cell_size) + self.offset_y
        
        super().__init__(parent, width=width, height=height, **kwargs)
        self.draw_grid()

    def draw_grid(self):
        # গ্রিডের মূল সীমানা হিসাব
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        # ১. উল্লম্ব (Vertical) রেখা এবং কলাম নম্বর অঙ্কন
        for col in range(self.cols + 1):
            x = self.offset_x + (col * self.cell_size)
            
            # গ্রিড লাইন টানা (অফসেট থেকে শুরু করে নিচে পর্যন্ত)
            self.create_line(x, self.offset_y, x, grid_height + self.offset_y, fill=self.grid_color, tags="grid_line")
            
            # কলাম নম্বর লেখা (শেষ লাইনের পর নম্বর যেন না বসে তাই শর্ত)
            if col < self.cols:
                label_x = x + (self.cell_size / 2)
                label_y = self.offset_y / 2  # অফসেটের ঠিক মাঝামাঝি উঁচুতে
                self.create_text(label_x, label_y, text=str(col), fill="#666666", font=("Arial", 10, "bold"), tags="label")

        # ২. অনুভূমিক (Horizontal) রেখা এবং রো নম্বর অঙ্কন
        for row in range(self.rows + 1):
            y = self.offset_y + (row * self.cell_size)
            
            # গ্রিড লাইন টানা (অফসেট থেকে শুরু করে ডানপাশ পর্যন্ত)
            self.create_line(self.offset_x, y, grid_width + self.offset_x, y, fill=self.grid_color, tags="grid_line")
            
            # রো নম্বর লেখা
            if row < self.rows:
                label_x = self.offset_x / 2  # অফসেটের ঠিক মাঝামাঝি বামে
                label_y = y + (self.cell_size / 2)
                self.create_text(label_x, label_y, text=str(row), fill="#666666", font=("Arial", 10, "bold"), tags="label")


class GeometryEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Drag & Slide Geometry Engine")
        self.root.geometry("1000x800")
        
        self.selected_item = None
        self.drag_data = {"x": 0, "y": 0}
        
        # আমাদের নতুন ক্যানভাস কম্পোনেন্ট
        self.canvas = GridCanvas(self.root, rows=32, cols=32, cell_size=24, bg="white", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20, expand=True)
        
        # অবজেক্ট তৈরি এবং ইভেন্ট বাইন্ডিং
        self.create_geometry_object(2, 2, "circle")
        self.create_geometry_object(5, 4, "square")

        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_start_drag)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_drop)

    def create_geometry_object(self, row, col, shape_type):
        size = self.canvas.cell_size
        # অফসেট বা মার্জিন যোগ করে পিক্সেল কোঅর্ডিনেট হিসাব
        x1 = self.canvas.offset_x + (col * size) + 5
        y1 = self.canvas.offset_y + (row * size) + 5
        x2 = x1 + size - 10
        y2 = y1 + size - 10
        
        if shape_type == "circle":
            self.canvas.create_oval(x1, y1, x2, y2, fill="#2196F3", outline="#0D47A1", width=2, tags="draggable")
        elif shape_type == "square":
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#F44336", outline="#B71C1C", width=2, tags="draggable")
            
        self.canvas.tag_raise("grid_line")
        self.canvas.tag_raise("label")  # লেবেলগুলোকেও শেপের ওপরে রাখা হলো

    def on_start_drag(self, event):
        self.selected_item = self.canvas.find_closest(event.x, event.y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        if not self.selected_item:
            return
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.selected_item, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drop(self, event):
        if not self.selected_item:
            return
            
        size = self.canvas.cell_size
        x1, y1, x2, y2 = self.canvas.coords(self.selected_item)
        
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # ড্রপ করার পর রো/কলাম হিসাব করার সময় অফসেট বাদ দিয়ে হিসাব করতে হবে
        target_col = int((center_x - self.canvas.offset_x) // size)
        target_row = int((center_y - self.canvas.offset_y) // size)
        
        target_col = max(0, min(target_col, self.canvas.cols - 1))
        target_row = max(0, min(target_row, self.canvas.rows - 1))
        
        # নতুন স্ন্যাপিং পজিশন (অফসেট সহ)
        new_x1 = self.canvas.offset_x + (target_col * size) + 5
        new_y1 = self.canvas.offset_y + (target_row * size) + 5
        
        self.canvas.moveto(self.selected_item, new_x1, new_y1)
        self.canvas.tag_raise("grid_line")
        self.canvas.tag_raise("label")
        self.selected_item = None

if __name__ == "__main__":
    app_root = tk.Tk()
    engine = GeometryEngine(app_root)
    app_root.mainloop()
