import struct
import tkinter as tk

cyh = 350
cxk = 350
r = 200

circlepoints = [{}] 

XMaxNeg = cyh - r
XMaxPos = cyh + r

YMaxNeg = cxk - r
YMaxPos = cxk + r

root = tk.Tk()
root.title("Python: Circle Equation Chart")

window_width = 600
window_height = 600
canvas = tk.Canvas(root, width=window_width, height=window_height, bg="#1e1e1e")
canvas.pack()

# Chart layout math constants
chart_width = 600
chart_height = 600
margin_left = 50

# Draw baseline center lines
canvas.create_line(0, 350, 600, 350, fill="#555555", dash=(4, 2))

# Draw backgrounds & Title text elements
canvas.create_text(400, 20, text="CIRCLE DRAW", fill="#ffffff", font=("Arial", 14, "bold"))

def draw_point(canvas, x, y, radius=3, color="black"):
    return canvas.create_oval(x, y, x, y, fill=color, outline="")


for y in range(YMaxNeg, YMaxPos, 1):
    for x in range(XMaxNeg, XMaxPos, 1):
        ok = (x - cyh) ** 2 + (y - cxk) ** 2
        if(ok < r ** 2):
            circlepoints.append({'x': x, 'y': y})
            draw_point(canvas, x, y, radius=4, color="#FF5733")

print(f"Points: {len(circlepoints)}")
print("Displaying chart rendering window...")

root.mainloop()