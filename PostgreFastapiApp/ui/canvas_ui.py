# ui/canvas_ui.py
import tkinter as tk
from tkinter import messagebox
import httpx
import threading
from config import config

class AgentDesktopUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        # Core State
        self.access_token = None
        self.backend_url = f"http://{config.APP_HOST}:{config.APP_PORT}"
        self.active_widgets = []  # Track dynamic elements
        self.is_loading = False   # Loader flag
        self.animation_step = 0   # Track frame index
        self._create_canvas()
        self.show_login_screen()

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
        # Persistent Loader Graphic (Hidden by default via empty text)
        self.loader_text = self.canvas.create_text(
            config.WINDOW_WIDTH // 2, 
            420, 
            text="", 
            fill="#00AAFF", 
            font=("Courier New", 12, "bold"))

    def _animate_loader(self):
        """Asynchronous canvas animation loop for network activity."""
        if not self.is_loading:
            self.canvas.itemconfig(self.loader_text, text="")
            return
        # Simple cyber terminal loading bar sequence
        frames = [
            "[■□□□□□□□□□] CONNECTING VIA SECURE CORRIDOR",
            "[■■□□□□□□□□] VALIDATING AGENT CREDENTIALS",
            "[■■■■□□□□□□] EXCHANGE KEY HANDSHAKE IN PROGRESS",
            "[■■■■■■□□□□] PARSING SECURITY PRIVILEGES",
            "[■■■■■■■■□□] EXTRACTING DATA PAYLOAD PACKETS",
            "[■■■■■■■■■■] STREAM SYNCHRONIZATION COMPLETE"
        ]
        
        current_frame = frames[self.animation_step % len(frames)]
        self.canvas.itemconfig(self.loader_text, text=current_frame)
        self.animation_step += 1
        # Force a loop callback every 180ms without freezing the main app thread
        self.root.after(180, self._animate_loader)

    def start_loader(self):
        """Activates loading flag and boots canvas frame sequence."""
        self.is_loading = True
        self.animation_step = 0
        self._animate_loader()

    def stop_loader(self):
        """Signals loader system to spin down and clear."""
        self.is_loading = False

    def _clear_screen(self):
        """Removes all dynamic canvas elements and widgets to redraw the screen."""
        for item in self.active_widgets:
            self.canvas.delete(item)
        self.active_widgets.clear()

    # --- VIEW 1: LOGIN SCREEN ---
    def show_login_screen(self):
        self._clear_screen()
        self.canvas.itemconfig(self.title_text, text="AGENT AUTHENTICATION", fill="#00FF00")

        self.active_widgets.append(self.canvas.create_text(config.WINDOW_WIDTH // 2, 130, text="Username:", fill="white", font=("Arial", 11)))
        username_entry = tk.Entry(self.root, width=25, font=("Arial", 12))
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 160, window=username_entry))

        self.active_widgets.append(self.canvas.create_text(config.WINDOW_WIDTH // 2, 210, text="Password:", fill="white", font=("Arial", 11)))
        password_entry = tk.Entry(self.root, width=25, font=("Arial", 12), show="*")
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 240, window=password_entry))

        login_btn = tk.Button(
            self.root, text="Login", width=15, bg="#00FF00", fg="black", font=("Arial", 11, "bold"),
            command=lambda: self.run_network_task(self._handle_login, username_entry.get(), password_entry.get())
        )
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 300, window=login_btn))

        register_link = tk.Button(
            self.root, text="Need an account? Register here", fg="#0055ff", bg=config.CANVAS_BG_COLOR, 
            bd=0, activebackground=config.CANVAS_BG_COLOR, font=("Arial", 10, "underline"), cursor="hand2",
            command=self.show_register_screen
        )
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 350, window=register_link))

    # --- VIEW 2: REGISTRATION SCREEN ---
    def show_register_screen(self):
        self._clear_screen()
        self.canvas.itemconfig(self.title_text, text="AGENT ENROLLMENT", fill="#00AAFF")

        self.active_widgets.append(self.canvas.create_text(config.WINDOW_WIDTH // 2, 130, text="Choose Username:", fill="white", font=("Arial", 11)))
        reg_username_entry = tk.Entry(self.root, width=25, font=("Arial", 12))
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 160, window=reg_username_entry))

        self.active_widgets.append(self.canvas.create_text(config.WINDOW_WIDTH // 2, 210, text="Choose Password:", fill="white", font=("Arial", 11)))
        reg_password_entry = tk.Entry(self.root, width=25, font=("Arial", 12), show="*")
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 240, window=reg_password_entry))
        register_btn = tk.Button(
            self.root, text="Create Account", width=15, bg="#00AAFF", fg="black", font=("Arial", 11, "bold"),
            command=lambda: self.run_network_task(self._handle_registration, reg_username_entry.get(), reg_password_entry.get())
        )
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 300, window=register_btn))
        login_link = tk.Button(
            self.root, text="Already have an account? Sign in", fg="#00FF00", bg=config.CANVAS_BG_COLOR, 
            bd=0, activebackground=config.CANVAS_BG_COLOR, font=("Arial", 10, "underline"), cursor="hand2",
            command=self.show_login_screen
        )
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 350, window=login_link))

    # --- VIEW 3: SECURE DASHBOARD ---
    def show_dashboard_screen(self):
        self._clear_screen()
        self.canvas.itemconfig(self.title_text, text="ACCESS GRANTED", fill="#00FF00")
        self.active_widgets.append(self.canvas.create_text(
            config.WINDOW_WIDTH // 2, 160, 
            text="Welcome to the secure grid system.", fill="white", font=("Arial", 12)
        ))
        fetch_btn = tk.Button(
            self.root, text="Fetch Core Intelligence", bg="#5500FF", fg="white", font=("Arial", 11, "bold"),
            command=lambda: self.run_network_task(self._fetch_secure_data)
        )
        self.active_widgets.append(self.canvas.create_window(config.WINDOW_WIDTH // 2, 220, window=fetch_btn))

    # --- ASYNC MULTI-THREADING HANDLER ---
    def run_network_task(self, target_function, *args):
        """Spawns network methods in a background worker thread to keep the Canvas running smoothly."""
        if self.is_loading:
            return  # Prevent rapid duplicate clicks
        self.start_loader()

    # Wrapper to stop the animation when the network operation completes
    def worker_wrapper():
        try:
            target_function(*args)
        finally:
            self.root.after(0, self.stop_loader)
        threading.Thread(target=worker_wrapper, daemon=True).start()

    # --- BACKGROUND WORKER EXECUTIONS ---
    def _handle_login(self, username, password):
        if not username.strip() or not password.strip():
            self.stop_loader()
            messagebox.showwarning("Input Error", "Please enter both credentials.")
            return
        payload = {"username": username.strip(), "password": password.strip()}

        try:
            with httpx.Client() as client:
                response = client.post(f"{self.backend_url}/token", data=payload)
                
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                self.root.after(0, self.show_dashboard_screen)
            else:
                error_msg = response.json().get("detail", "Login failed.")
                self.root.after(0, lambda: messagebox.showerror("Access Denied", error_msg))
        except httpx.RequestError as exc:
            self.root.after(0, lambda: messagebox.showerror("Network Error", f"Server dropped link: {exc}"))

    def _handle_registration(self, username, password):
        if len(username.strip()) < 3 or len(password.strip()) < 6:
            self.stop_loader()
            messagebox.showwarning("Validation Error", "Username must be ≥ 3 chars.\nPassword must be ≥ 6 chars.")
            return
        json_payload = {"username": username.strip(), "password": password.strip()}
        try:
            with httpx.Client() as client:
                response = client.post(f"{self.backend_url}/register", json=json_payload)
                
            if response.status_code == 201:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Agent enrolled! Please login."))
                self.root.after(0, self.show_login_screen)
            else:
                error_msg = response.json().get("detail", "Registration rejected.")
                self.root.after(0, lambda: messagebox.showerror("Registration Failed", error_msg))
        except httpx.RequestError as exc:
            self.root.after(0, lambda: messagebox.showerror("Network Error", f"Server dropped link: {exc}"))

    def _fetch_secure_data(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.backend_url}/agent/secure-data", headers=headers)
            if response.status_code == 200:
                payload = response.json().get("secret_payload")
                self.root.after(0, lambda: messagebox.showinfo("Classified Feed", f"System Data Recovered:\n{payload}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Unauthorized", "Session token signature expired."))
        except httpx.RequestError as exc:
            self.root.after(0, lambda: messagebox.showerror("Network Error", f"Data stream interrupted: {exc}"))
        
    def run(self):
        self.root.mainloop()






