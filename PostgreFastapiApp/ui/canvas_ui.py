# ui/canvas_ui.py
import tkinter as tk
from tkinter import messagebox
import httpx
from config import config

class AgentDesktopUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Token storage on the desktop client
        self.access_token = None
        self.backend_url = f"http://{config.APP_HOST}:{config.APP_PORT}"

        self._create_canvas()
        self._build_login_form()

    def _create_canvas(self):
        """Builds and draws your primary Tkinter canvas interface."""
        self.canvas = tk.Canvas(
            self.root, 
            width=config.WINDOW_WIDTH, 
            height=config.WINDOW_HEIGHT, 
            bg=config.CANVAS_BG_COLOR
        )
        self.canvas.pack(fill="both", expand=True)

        # Main Title Header
        self.title_text = self.canvas.create_text(
            config.WINDOW_WIDTH // 2, 
            50, 
            text="CLASSIFIED AGENT TERMINAL", 
            fill="#00FF00",  # Cyber Green
            font=("Courier New", 20, "bold")
        )

    def _build_login_form(self):
        """Places Tkinter entry widgets directly onto the Canvas canvas layer."""
        # Username Field
        self.canvas.create_text(config.WINDOW_WIDTH // 2, 130, text="Username:", fill="white", font=("Arial", 12))
        self.username_entry = tk.Entry(self.root, width=25, font=("Arial", 12))
        self.username_window = self.canvas.create_window(config.WINDOW_WIDTH // 2, 160, window=self.username_entry)

        # Password Field
        self.canvas.create_text(config.WINDOW_WIDTH // 2, 210, text="Password:", fill="white", font=("Arial", 12))
        self.password_entry = tk.Entry(self.root, width=25, font=("Arial", 12), show="*")
        self.password_window = self.canvas.create_window(config.WINDOW_WIDTH // 2, 240, window=self.password_entry)

        # Login Submit Button
        self.login_button = tk.Button(
            self.root, 
            text="Authenticate", 
            command=self._handle_login, 
            bg="#00FF00", 
            fg="black", 
            font=("Arial", 11, "bold"),
            padx=10,
            pady=5
        )
        self.button_window = self.canvas.create_window(config.WINDOW_WIDTH // 2, 300, window=self.login_button)

    def _handle_login(self):
        """Extracts entries and communicates with the FastAPI /token endpoint."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please provide both an agent username and password.")
            return

        # OAuth2PasswordRequestForm expects data as form-encoded fields, not JSON
        payload = {
            "username": username,
            "password": password
        }

        try:
            # We use a context manager to execute a clean synchronous post block via httpx
            with httpx.Client() as client:
                response = client.post(f"{self.backend_url}/token", data=payload)
                
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                
                # Update UI on success
                self._clear_login_form()
                self._display_secure_dashboard()
                
            else:
                error_detail = response.json().get("detail", "Authentication Failed.")
                messagebox.showerror("Access Denied", f"Server responded: {error_detail}")

        except httpx.RequestError as exc:
            messagebox.showerror("Connection Error", f"Could not reach backend services: {exc}")

    def _clear_login_form(self):
        """Removes form elements from the active screen view."""
        self.canvas.delete(self.username_window)
        self.canvas.delete(self.password_window)
        self.canvas.delete(self.button_window)

    def _display_secure_dashboard(self):
        """Renders secure assets once the client holds the active JWT authorization."""
        self.canvas.itemconfig(self.title_text, text="ACCESS GRANTED - AGENT SESSION ACTIVE", fill="#00FF00")
        
        # Display success banner
        self.canvas.create_text(
            config.WINDOW_WIDTH // 2, 
            180, 
            text="✓ Authenticated securely via JWT token", 
            fill="#888888", 
            font=("Arial", 12, "italic")
        )

        # Create a button to fetch data from the secure API endpoint
        self.fetch_button = tk.Button(
            self.root, 
            text="Fetch Classified Payload", 
            command=self._fetch_classified_data,
            bg="#0055ff",
            fg="white",
            font=("Arial", 11, "bold")
        )
        self.canvas.create_window(config.WINDOW_WIDTH // 2, 240, window=self.fetch_button)

    def _fetch_classified_data(self):
        """Makes an authenticated call using the stored Bearer token."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.backend_url}/agent/secure-data", headers=headers)
                
            if response.status_code == 200:
                payload_data = response.json()
                secret_msg = payload_data.get("secret_payload", "No payload recovered.")
                messagebox.showinfo("Classified Intelligence Recovered", f"Payload: {secret_msg}")
            else:
                messagebox.showerror("Unauthorized", "Session expired or rejected by security server.")
        except httpx.RequestError as exc:
            messagebox.showerror("Network Fault", f"Data stream interrupted: {exc}")

    def run(self):
        """Starts the main blocking UI thread loop."""
        self.root.mainloop()
