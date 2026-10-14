# ui/canvas_ui.py
import tkinter as tk
from tkinter import messagebox
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
        
        # New Feature State Variables
        self.wave_color = tk.StringVar(value="#00FF00")  # Default to Cyber Green
        self.history_records = []

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
            40, 
            text="CLASSIFIED AGENT TERMINAL", 
            fill="#00FF00",  
            font=("Courier New", 20, "bold")
        )

    def _animate_audio_wave(self):
        """Draws a fluctuating digital sound wave on the canvas with dynamic coloring."""
        if self.wave_id:
            self.canvas.delete(self.wave_id)
            self.wave_id = None

        if not self.is_speaking:
            return

        points = []
        center_y = 550  # Shifted down slightly to leave breathing room for history panels
        width = config.WINDOW_WIDTH
        
        for x in range(0, width, 5):
            relative_x = x / 40.0
            sine_value = math.sin(relative_x - self.wave_phase)
            edge_damping = math.sin((x / width) * math.pi)
            
            y = center_y + int(sine_value * 35 * edge_damping)
            points.extend([x, y])

        if len(points) >= 4:
            # Grabs color setting dynamically via self.wave_color.get()
            self.wave_id = self.canvas.create_line(
                points, fill=self.wave_color.get(), width=2, smooth=True
            )

        self.wave_phase += 0.25
        self.root.after(30, self._animate_audio_wave)

    def trigger_voice_output(self, phrase_text: str):
        """Starts background text-to-speech and links it to the canvas animation."""
        if not phrase_text.strip():
            messagebox.showwarning("Input Error", "Please type a sentence for the system to broadcast.")
            return

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
        """Displays the main terminal view equipped with custom text input fields and history arrays."""
        self._clear_screen()
        self.canvas.itemconfig(self.title_text, text="SYSTEM BROADCAST CONSOLE", fill=self.wave_color.get())
        
        # Left Panel Structure: Controls & Entry Inputs
        prompt_text = self.canvas.create_text(
            220, 110, text="Enter operational transmission below:", fill="white", font=("Arial", 11, "bold"), anchor="w"
        )
        self.active_widgets.append(prompt_text)

        self.text_entry = tk.Entry(
            self.root, width=80, font=("Arial", 12), bg="#2a2a2a", fg="white", insertbackground="white", bd=1, relief="solid"
        )
        entry_window = self.canvas.create_window(225, 150, window=self.text_entry, anchor="w")
        self.active_widgets.append(entry_window)
        self.text_entry.focus_set()
        self.text_entry.bind("<Return>", lambda event: self._process_input_submission())

        # Submit Broadcast Button
        broadcast_btn = tk.Button(
            self.root, text="⚡ Transmit Speech Wave", bg="#00FF00", fg="black", font=("Arial", 10, "bold"),
            padx=8, pady=4, activebackground="#00AA00", command=self._process_input_submission
        )
        btn_window = self.canvas.create_window(220, 200, window=broadcast_btn, anchor="w")
        self.active_widgets.append(btn_window)

        # Visual Grid Subdivider Line
        divider_line = self.canvas.create_line(430, 90, 430, 450, fill="#333333", width=1)
        self.active_widgets.append(divider_line)

        # Right Panel Structure: History Log Box
        history_title = self.canvas.create_text(
            460, 110, text="📜 Transmission Registry Logs:", fill="#888888", font=("Arial", 11, "bold"), anchor="w"
        )
        self.active_widgets.append(history_title)

        # Listbox widget to store entries
        self.history_listbox = tk.Listbox(
            self.root, width=70, height=13, font=("Courier New", 9), bg="#151515", fg="#00FF00",
            selectbackground="#222222", selectforeground="white", highlightthickness=0, bd=1, relief="solid"
        )
        listbox_window = self.canvas.create_window(460, 280, window=self.history_listbox, anchor="w")
        self.active_widgets.append(listbox_window)
        self.history_listbox.bind("<<ListboxSelect>>", self._handle_history_selection)

        # Populate history widget from states if rows exist from earlier cycles
        for record in self.history_records:
            self.history_listbox.insert(tk.END, record)

        # Bottom Left Component Area: Wave Color Configuration Panel
        color_title = self.canvas.create_text(
            220, 270, text="🎨 Frequency Color Palette:", fill="#888888", font=("Arial", 11, "bold"), anchor="w"
        )
        self.active_widgets.append(color_title)

        colors = [("Cyber Green", "#00FF00"), ("Neon Cyan", "#00AAFF"), ("Plasma Red", "#FF3333")]
        for idx, (label, hex_code) in enumerate(colors):
            radio_btn = tk.Radiobutton(
                self.root, text=label, variable=self.wave_color, value=hex_code,
                bg=config.CANVAS_BG_COLOR, fg="white", selectcolor=config.CANVAS_BG_COLOR,
                activebackground=config.CANVAS_BG_COLOR, activeforeground=hex_code,
                font=("Arial", 10), command=self._update_theme_colors
            )
            radio_window = self.canvas.create_window(220, 310 + (idx * 30), window=radio_btn, anchor="w")
            self.active_widgets.append(radio_window)

    def _update_theme_colors(self):
        """Changes the interface heading color match to mirror the frequency configuration selection."""
        self.canvas.itemconfig(self.title_text, fill=self.wave_color.get())
        self.history_listbox.config(fg=self.wave_color.get())

    def _process_input_submission(self):
        """Extracts text, updates memory arrays, and fires synthesis output loops."""
        user_sentence = self.text_entry.get().strip()
        
        if user_sentence:
            # 1. Store locally in memory array and print onto the history tracking listbox view
            self.history_records.append(user_sentence)
            self.history_listbox.insert(tk.END, f"» {user_sentence}")
            
            # 2. Trigger non-blocking sound output pipeline sequence
            self.trigger_voice_output(user_sentence)
            
            # 3. Clean up the text input field area bar cleanly
            self.text_entry.delete(0, tk.END)

    def _handle_history_selection(self, event):
        """Replays historical speech entries whenever a user clicks a row in the tracking listbox panel."""
        try:
            selection_index = self.history_listbox.curselection()
            if not selection_index:
                return
                
            raw_string = self.history_listbox.get(selection_index)
            # Remove line prefix indicator symbol cleanly before re-synthesizing
            target_phrase = raw_string.replace("» ", "", 1)
            
            self.trigger_voice_output(target_phrase)
        except Exception as error:
            print(f"[REPLAY ERROR] Failed to access selection row element context: {error}")

    def run(self):
        """Starts the main blocking UI loop."""
        self.root.mainloop()
