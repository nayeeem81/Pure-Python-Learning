# ui/canvas_ui.py
import tkinter as tk
import math
from config import config
from utility.audio import speak_sentence

class AgentDesktopUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Audio Wave Animation State
        self.is_speaking = False
        self.wave_phase = 0.0
        self.wave_id = None
        self.active_widgets = []

        self._create_canvas()
        self.show_dashboard_screen()

    def _create_canvas(self):
        """Builds the main background Canvas layer."""
        self.canvas = tk.Canvas(
            self.root, 
            width=config.WINDOW_WIDTH, 
            height=config.WINDOW_HEIGHT, 
            bg=config.CANVAS_BG_COLOR
        )
        self.canvas.pack(fill="both", expand=True)

        # Centered Persistent Title
        self.title_text = self.canvas.create_text(
            config.WINDOW_WIDTH // 2, 
            50, 
            text="CLASSIFIED AGENT TERMINAL", 
            fill="#00FF00",  
            font=("Courier New", 20, "bold")
        )

    def _animate_audio_wave(self):
        """Draws a fluctuating neon-green digital sound wave on the canvas."""
        if self.wave_id:
            self.canvas.delete(self.wave_id)
            self.wave_id = None

        if not self.is_speaking:
            return

        points = []
        center_y = 480  
        width = config.WINDOW_WIDTH
		       
        for x in range(0, width, 5):
            relative_x = x / 40.0
            sine_value = math.sin(relative_x - self.wave_phase)
            edge_damping = math.sin((x / width) * math.pi)
            
            y = center_y + int(sine_value * 30 * edge_damping)
            points.extend([x, y])

        if len(points) >= 4:
            self.wave_id = self.canvas.create_line(
                points, fill="#00FF00", width=2, smooth=True
            )

        self.wave_phase += 0.25
        self.root.after(30, self._animate_audio_wave)

    def trigger_voice_output(self, phrase_text: str):
        """Starts background text-to-speech and links it to the canvas animation."""
        if self.is_speaking:
            return  

        self.is_speaking = True
        self._animate_audio_wave()  

        def stop_speaking_callback():
            self.is_speaking = False

        speak_sentence(phrase_text, on_complete_callback=lambda: self.root.after(0, stop_speaking_callback))

    def _clear_screen(self):
        """Removes all dynamic canvas elements and widgets."""
        if self.wave_id:
            self.canvas.delete(self.wave_id)
            self.wave_id = None
        for item in self.active_widgets:
            self.canvas.delete(item)
        self.active_widgets.clear()

    def show_dashboard_screen(self):
        """Displays the standalone console view and fires up the voice layer."""
        self._clear_screen()
        self.canvas.itemconfig(self.title_text, text="COMMAND OVERVIEW GRIDS", fill="#00FF00")
        
        # Trigger the voice line and wave sequence automatically upon app load
        self.trigger_voice_output("System initialized. Welcome to the central command node.")

        self.active_widgets.append(self.canvas.create_text(
            config.WINDOW_WIDTH // 2, 
            160, 
            text="Core application pipeline active. Monitoring incoming data stream.", 
            fill="white", 
            font=("Arial", 16) 
        ))

        # Sample Test Button to trigger voice and wave manually again
        reboot_voice_btn = tk.Button(
            self.root, 
            text="Broadcast Test Ping", 
            bg="#222222", 
            fg="#00FF00", 
            font=("Arial", 11, "bold"),
            command=lambda: self.trigger_voice_output("Re-establishing network diagnostics handshake.")
        )
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 240, window=reboot_voice_btn))

    def run(self):
        """Starts the main blocking UI loop."""
        self.root.mainloop()
