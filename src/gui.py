import tkinter as tk
from tkinter import ttk, messagebox


class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login")
        self.geometry("300x150")
        self.resizable(False, False)

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        # Username
        ttk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Password
        ttk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Login button
        ttk.Button(self, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=20)

        self.columnconfigure(1, weight=1)
        self.username_entry.focus_set()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            messagebox.showinfo("Login", f"Welcome, {username}!")
            self.destroy()
        else:
            messagebox.showwarning("Login", "Please enter both username and password.")


class WelcomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Welcome")
        self.geometry("400x300")

        # Welcome label
        welcome_label = ttk.Label(
            self,
            text="Welcome!",
            font=("Helvetica", 24, "bold")
        )
        welcome_label.pack(pady=50)

        # Description
        desc_label = ttk.Label(
            self,
            text="Please log in to continue.",
            font=("Helvetica", 12)
        )
        desc_label.pack(pady=10)

        # Login button
        login_btn = ttk.Button(
            self,
            text="Log In",
            command=self.show_login
        )
        login_btn.pack(pady=30)

    def show_login(self):
        LoginDialog(self)


def main():
    app = WelcomePage()
    app.mainloop()


if __name__ == "__main__":
    main()
