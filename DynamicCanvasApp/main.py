# main.py
import tkinter as tk
from app_window import DynamicCanvasApp
from app_window_grid import DynamicCanvasGridApp

if __name__ == "__main__":
    # Fix High-DPI text scaling blur strictly on Windows devices
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    root = tk.Tk()
    app = DynamicCanvasGridApp(root)
    root.mainloop()
