import tkinter as tk

class SimpleGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Standard Cartesian Grid")
        self.root.geometry("640x300")
        self.root.configure(bg="#121214")

        # Create a blank drawing canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=600, 
            height=250, 
            bg="#141416", 
            highlightthickness=1, 
            highlightbackground="#333"
        )
        self.canvas.pack(pady=20)

        # Draw the grid lines
        self.draw_grid_and_axes()

    def draw_grid_and_axes(self):
        w, h = 600, 250
        center_y = h / 2
        center_x = w / 2

        # 1. Draw subtle background grid lines every 40 pixels
        for x in range(0, w, 40):
            self.canvas.create_line(x, 0, x, h, fill="#252529", width=1)
        for y in range(0, h, 40):
            self.canvas.create_line(0, y, w, y, fill="#252529", width=1)

        # 2. Draw the bold Main X-Axis (Horizontal)
        self.canvas.create_line(0, center_y, w, center_y, fill="#888", width=2)
        self.canvas.create_text(w - 20, center_y - 15, text="X Axis", fill="#aaa", font=("Arial", 10, "bold"))

        # 3. Draw the bold Main Y-Axis (Vertical)
        self.canvas.create_line(center_x, 0, center_x, h, fill="#888", width=2)
        self.canvas.create_text(center_x + 30, 20, text="Y Axis", fill="#aaa", font=("Arial", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleGridApp(root)
    root.mainloop()

