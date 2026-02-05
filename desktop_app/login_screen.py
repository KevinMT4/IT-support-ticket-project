import customtkinter as ctk
from typing import Callable


class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, on_login_success: Callable):
        super().__init__(parent, fg_color="transparent")
        self.on_login_success = on_login_success

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        login_frame = ctk.CTkFrame(self, width=400, height=450, corner_radius=10)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            login_frame,
            text="Sistema de Tickets",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(40, 10))

        subtitle = ctk.CTkLabel(
            login_frame,
            text="Inicia sesión para continuar",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 30))

        self.username_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Usuario",
            width=300,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Contraseña",
            show="*",
            width=300,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(pady=10)

        self.error_label = ctk.CTkLabel(
            login_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        self.error_label.pack(pady=5)

        self.login_button = ctk.CTkButton(
            login_frame,
            text="Iniciar Sesión",
            command=self.handle_login,
            width=300,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_button.pack(pady=20)

        self.password_entry.bind("<Return>", lambda e: self.handle_login())

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.show_error("Por favor ingresa usuario y contraseña")
            return

        self.login_button.configure(state="disabled", text="Iniciando sesión...")
        self.error_label.configure(text="")

        self.after(100, lambda: self.on_login_success(username, password))

    def show_error(self, message: str):
        self.error_label.configure(text=message)
        self.login_button.configure(state="normal", text="Iniciar Sesión")

    def reset(self):
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
        self.login_button.configure(state="normal", text="Iniciar Sesión")
