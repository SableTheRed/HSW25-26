import tkinter as tk
from tkinter import ttk, messagebox
import threading

from auth import login as oidc_login


class WelcomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HSW Application")
        self.geometry("500x400")
        self.configure(bg="#1a1a2e")
        self.resizable(False, False)

        self.user_info = None
        self._setup_styles()
        self._create_widgets()
        self._center_window()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Main frame style
        style.configure(
            "Main.TFrame",
            background="#1a1a2e"
        )

        # Title label style
        style.configure(
            "Title.TLabel",
            background="#1a1a2e",
            foreground="#eee",
            font=("Segoe UI", 32, "bold")
        )

        # Subtitle label style
        style.configure(
            "Subtitle.TLabel",
            background="#1a1a2e",
            foreground="#888",
            font=("Segoe UI", 12)
        )

        # Status label style
        style.configure(
            "Status.TLabel",
            background="#1a1a2e",
            foreground="#4ecca3",
            font=("Segoe UI", 11)
        )

        # Login button style
        style.configure(
            "Login.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=(30, 15)
        )
        style.map(
            "Login.TButton",
            background=[("active", "#3a86ff"), ("!active", "#4361ee")],
            foreground=[("active", "#fff"), ("!active", "#fff")]
        )

    def _create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # Logo/icon placeholder
        icon_label = tk.Label(
            main_frame,
            text="🔐",
            font=("Segoe UI Emoji", 48),
            bg="#1a1a2e"
        )
        icon_label.pack(pady=(20, 10))

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Welcome",
            style="Title.TLabel"
        )
        title_label.pack(pady=(10, 5))

        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Sign in to access your account",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(pady=(0, 30))

        # Login button
        self.login_btn = ttk.Button(
            main_frame,
            text="Sign In with SSO",
            style="Login.TButton",
            command=self._handle_login
        )
        self.login_btn.pack(pady=20)

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            style="Status.TLabel"
        )
        self.status_label.pack(pady=(20, 0))

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _handle_login(self):
        self.login_btn.configure(state="disabled")
        self.status_label.configure(text="Opening browser for sign-in...")

        # Run login in background thread to not block UI
        thread = threading.Thread(target=self._perform_login, daemon=True)
        thread.start()

    def _perform_login(self):
        try:
            sub, name, access_token, refresh_token, id_token, expires_in = oidc_login()
            self.user_info = {
                "sub": sub,
                "name": name,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "id_token": id_token,
                "expires_in": expires_in
            }
            # Update UI from main thread
            self.after(0, self._on_login_success, name)
        except ValueError as e:
            self.after(0, self._on_login_error, str(e))
        except Exception as e:
            self.after(0, self._on_login_error, f"Login failed: {e}")

    def _on_login_success(self, name):
        self.status_label.configure(
            text=f"Signed in as {name}",
            foreground="#4ecca3"
        )
        self.login_btn.configure(text="Signed In", state="disabled")
        messagebox.showinfo("Success", f"Welcome, {name}!")

    def _on_login_error(self, error_msg):
        self.status_label.configure(
            text="",
            foreground="#ff6b6b"
        )
        self.login_btn.configure(state="normal")
        messagebox.showerror("Login Error", error_msg)


def main():
    app = WelcomePage()
    app.mainloop()


if __name__ == "__main__":
    main()
