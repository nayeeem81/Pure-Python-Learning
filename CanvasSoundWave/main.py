# main.py
import sys
from config import config
from ui.canvas_ui import AgentDesktopUI

def main():
    """Application entry point that initializes and boots the standalone Desktop console."""
    try:
        # 1. Initialize the modular desktop interface asset framework
        desktop_app = AgentDesktopUI()
        
        # 2. Launch your Tkinter main event thread loop
        desktop_app.run()
        
    except Exception as error:
        print(f"[FATAL LAUNCH ERROR] Failed to initialize desktop console: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
