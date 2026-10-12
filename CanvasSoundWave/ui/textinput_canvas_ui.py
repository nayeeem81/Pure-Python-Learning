# ui/textinput_canvas_ui.py
import tkinter as tk
from tkinter import messagebox
import math
from config import config
from utility.audio import speak_sentence  # Ensure this points to your audio file folder path

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
        center_y = 480  # Positioned lower down on the screen layout
        width = config.WINDOW_WIDTH
        
        for x in range(0, width, 5):
            relative_x = x / 40.0
            sine_value = math.sin(relative_x - self.wave_phase)
            edge_damping = math.sin((x / width) * math.pi)
            
            y = center_y + int(sine_value * 35 * edge_damping) # Slightly taller wave height
            points.extend([x, y])

        if len(points) >= 4:
            self.wave_id = self.canvas.create_line(
                points, fill="#00FF00", width=2, smooth=True
            )

        self.wave_phase += 0.25
        self.root.after(30, self._animate_audio_wave)

    def trigger_voice_output(self, phrase_text: str):
        """Starts background text-to-speech and links it to the canvas animation."""
        if not phrase_text.strip():
            messagebox.showwarning("Input Error", "Please type a sentence for the system to broadcast.")
            return

        if self.is_speaking:
            return  # Prevent overlapping voice outputs

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
        """Displays the main terminal view equipped with the custom text input fields."""
        self._clear_screen()
        self.canvas.itemconfig(self.title_text, text="SYSTEM BROADCAST CONSOLE", fill="#00FF00")
        
        # Initial greeting line
        self.trigger_voice_output("Console ready. Enter your operational transmission below.")

        # 1. Canvas Prompt Label
        prompt_text = self.canvas.create_text(
            config.WINDOW_WIDTH // 2, 
            150, 
            text="Enter custom sentence to synthesize:", 
            fill="white", 
            font=("Arial", 11)
        )
        self.active_widgets.append(prompt_text)

        # 2. Main Entry Widget (The input box)
        self.text_entry = tk.Entry(
            self.root, 
            width=40, 
            font=("Arial", 12), 
            bg="#2a2a2a", 
            fg="white", 
            insertbackground="white", # White blinking cursor text indicator
            bd=1,
            relief="solid"
        )
        entry_window = self.canvas.create_window(
            config.WINDOW_WIDTH // 2, 
            190, 
            window=self.text_entry
        )
        self.active_widgets.append(entry_window)
        
        # Focus keyboard cursor into the text input box automatically on load
        self.text_entry.focus_set()

        # Bind the keyboard 'Enter' key directly to trigger the audio execution
        self.text_entry.bind("<Return>", lambda event: self._process_input_submission())

        # 3. Trigger Submission Button
        broadcast_btn = tk.Button(
            self.root, 
            text="⚡ Transmit Speech Wave", 
            bg="#00FF00", 
            fg="black", 
            font=("Arial", 11, "bold"),
            padx=10,
            pady=5,
            activebackground="#00AA00",
            command=self._process_input_submission
        )
        btn_window = self.canvas.create_window(
            config.WINDOW_WIDTH // 2, 
            250, 
            window=broadcast_btn
        )
        self.active_widgets.append(btn_window)

    def _process_input_submission(self):
        """Extracts the entry box text and resets the input bar cleanly."""
        user_sentence = self.text_entry.get()
        
        if user_sentence.strip():
            # Pass text to background streaming thread
            self.trigger_voice_output(user_sentence)
            # Clear text field for next entry run
            self.text_entry.delete(0, tk.END)

    def run(self):
        """Starts the main blocking UI loop."""
        self.root.mainloop()

