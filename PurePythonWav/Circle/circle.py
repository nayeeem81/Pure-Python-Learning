import struct
import tkinter as tk

h = 500
k = 0
r = 500

circlepoints = [{}] 

XMaxNeg = h - 500
XMaxPos = h + 500

YMaxNeg = k - 500
YMaxPos = k + 500


root = tk.Tk()
root.title("Pure Python Stereo Waveform Chart (2-Channel)")

window_width = 800
window_height = 800
canvas = tk.Canvas(root, width=window_width, height=window_height, bg="#1e1e1e")
canvas.pack()

# Draw baseline center lines
canvas.create_line(50, 50, 1100, 0, fill="#555555", dash=(4, 2))

# Draw backgrounds & Title text elements
canvas.create_text(400, 20, text="CIRCLE DRAW", fill="#ffffff", font=("Arial", 14, "bold"))


# Chart layout math constants
chart_width = 700
chart_height = 700
margin_left = 50

# Center lines (silence anchors) for both plots
left_center_y = 0
right_center_y = 500

# Draw backgrounds & Title text elements
canvas.create_text(400, 20, text="CIRCLE DRAW", fill="#ffffff", font=("Arial", 14, "bold"))


def draw_point(canvas, x, y, radius=3, color="black"):
    return canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="")


for y in range(0, 500, 1):
    for x in range(500, 0, -1):
        if (x - h) ** 2 + (y - k) ** 2 <= r ** 2:
            circlepoints.append({'x': x, 'y': y})
            draw_point(canvas, x, y, radius=4, color="#FF5733")
        
print(f"Points: {len(circlepoints)}")


print("Displaying chart rendering window...")

root.mainloop()