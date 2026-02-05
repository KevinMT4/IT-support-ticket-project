import customtkinter as ctk
from typing import Callable, List, Dict, Any
from datetime import datetime


class TicketsListScreen(ctk.CTkFrame):
    def __init__(self, parent, api_client, on_create_ticket: Callable, on_view_ticket: Callable, on_logout: Callable):
        super().__init__(parent, fg_color="transparent")
        self.api_client = api_client
        self.on_create_ticket = on_create_ticket
        self.on_view_ticket = on_view_ticket
        self.on_logout = on_logout
        self.tickets_data = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_tickets_list()

    def create_header(self):
        header_frame = ctk.CTkFrame(self, height=80, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="Mis Tickets",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        user_name = self.api_client.user_data.get("username", "Usuario")
        user_label = ctk.CTkLabel(
            header_frame,
            text=f"Usuario: {user_name}",
            font=ctk.CTkFont(size=12)
        )
        user_label.grid(row=0, column=1, padx=10, pady=20, sticky="e")

        refresh_btn = ctk.CTkButton(
            header_frame,
            text="↻ Actualizar",
            command=self.load_tickets,
            width=120,
            height=35
        )
        refresh_btn.grid(row=0, column=2, padx=10, pady=20)

        create_btn = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Ticket",
            command=self.on_create_ticket,
            width=140,
            height=35
        )
        create_btn.grid(row=0, column=3, padx=10, pady=20)

        logout_btn = ctk.CTkButton(
            header_frame,
            text="Cerrar Sesión",
            command=self.on_logout,
            width=120,
            height=35,
            fg_color="gray",
            hover_color="#666666"
        )
        logout_btn.grid(row=0, column=4, padx=20, pady=20)

    def create_tickets_list(self):
        list_frame = ctk.CTkFrame(self, corner_radius=10)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        headers_frame = ctk.CTkFrame(list_frame, fg_color="#2b2b2b", corner_radius=0)
        headers_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        headers_frame.grid_columnconfigure(1, weight=1)

        headers = [
            ("ID", 80),
            ("Asunto", None),
            ("Departamento", 180),
            ("Prioridad", 120),
            ("Estado", 130),
            ("Fecha", 150)
        ]

        for col, (header, width) in enumerate(headers):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            if width:
                label.grid(row=0, column=col, padx=10, pady=12, sticky="w")
            else:
                label.grid(row=0, column=col, padx=10, pady=12, sticky="ew")
                headers_frame.grid_columnconfigure(col, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent"
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

    def load_tickets(self):
        success, result = self.api_client.get_tickets()

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not success:
            error_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=f"Error: {result}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=20)
            return

        self.tickets_data = result

        if not self.tickets_data:
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No tienes tickets creados",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            empty_label.pack(pady=20)
            return

        for ticket in self.tickets_data:
            self.create_ticket_row(ticket)

    def create_ticket_row(self, ticket: Dict[str, Any]):
        row_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#2b2b2b",
            corner_radius=5,
            height=60
        )
        row_frame.pack(fill="x", padx=5, pady=3)
        row_frame.grid_columnconfigure(1, weight=1)

        btn = ctk.CTkButton(
            row_frame,
            text="",
            fg_color="transparent",
            hover_color="#3b3b3b",
            command=lambda t=ticket: self.on_view_ticket(t["id"]),
            cursor="hand2"
        )
        btn.place(relx=0, rely=0, relwidth=1, relheight=1)

        id_label = ctk.CTkLabel(
            row_frame,
            text=f"#{ticket['id']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=80
        )
        id_label.grid(row=0, column=0, padx=10, pady=15, sticky="w")

        asunto_label = ctk.CTkLabel(
            row_frame,
            text=ticket['asunto'],
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        asunto_label.grid(row=0, column=1, padx=10, pady=15, sticky="ew")

        dept_label = ctk.CTkLabel(
            row_frame,
            text=ticket.get('departamento_nombre', 'N/A'),
            font=ctk.CTkFont(size=12),
            width=180
        )
        dept_label.grid(row=0, column=2, padx=10, pady=15, sticky="w")

        prioridad_color = self.get_prioridad_color(ticket['prioridad'])
        prioridad_label = ctk.CTkLabel(
            row_frame,
            text=ticket['prioridad_display'],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=prioridad_color,
            width=120
        )
        prioridad_label.grid(row=0, column=3, padx=10, pady=15, sticky="w")

        estado_color = self.get_estado_color(ticket['estado'])
        estado_label = ctk.CTkLabel(
            row_frame,
            text=ticket['estado_display'],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=estado_color,
            width=130
        )
        estado_label.grid(row=0, column=4, padx=10, pady=15, sticky="w")

        fecha = self.format_date(ticket['fecha_creacion'])
        fecha_label = ctk.CTkLabel(
            row_frame,
            text=fecha,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            width=150
        )
        fecha_label.grid(row=0, column=5, padx=10, pady=15, sticky="w")

    def get_prioridad_color(self, prioridad: str) -> str:
        colors = {
            'baja': '#4ade80',
            'media': '#fbbf24',
            'alta': '#fb923c',
            'urgente': '#ef4444'
        }
        return colors.get(prioridad, 'white')

    def get_estado_color(self, estado: str) -> str:
        colors = {
            'abierto': '#60a5fa',
            'en_proceso': '#fbbf24',
            'resuelto': '#4ade80',
            'cerrado': '#9ca3af'
        }
        return colors.get(estado, 'white')

    def format_date(self, date_str: str) -> str:
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M')
        except Exception:
            return date_str

    def show(self):
        self.load_tickets()
