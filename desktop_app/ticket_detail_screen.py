import customtkinter as ctk
from typing import Callable, Dict, Any
from datetime import datetime


class TicketDetailScreen(ctk.CTkFrame):
    def __init__(self, parent, api_client, on_back: Callable):
        super().__init__(parent, fg_color="transparent")
        self.api_client = api_client
        self.on_back = on_back
        self.ticket_id = None
        self.ticket_data = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_detail_view()

    def create_header(self):
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            self.header_frame,
            text="← Volver",
            command=self.on_back,
            width=100,
            height=35,
            fg_color="gray",
            hover_color="#666666"
        )
        back_btn.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Detalles del Ticket",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=1, padx=20, pady=20)

    def create_detail_view(self):
        self.detail_container = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.detail_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.detail_container.grid_columnconfigure(0, weight=1)

    def load_ticket(self, ticket_id: int):
        self.ticket_id = ticket_id

        for widget in self.detail_container.winfo_children():
            widget.destroy()

        success, result = self.api_client.get_ticket(ticket_id)

        if not success:
            error_label = ctk.CTkLabel(
                self.detail_container,
                text=f"Error: {result}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=20)
            return

        self.ticket_data = result
        self.display_ticket()

    def display_ticket(self):
        ticket = self.ticket_data

        self.title_label.configure(text=f"Ticket #{ticket['id']}")

        main_frame = ctk.CTkFrame(self.detail_container, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)
        main_frame.grid_columnconfigure(0, weight=1)

        info_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        info_frame.grid_columnconfigure(1, weight=1)

        labels_data = [
            ("ID:", f"#{ticket['id']}"),
            ("Asunto:", ticket['asunto']),
            ("Usuario:", ticket['usuario_nombre']),
            ("Departamento:", ticket['departamento_nombre']),
            ("Motivo:", ticket.get('motivo_nombre', 'N/A')),
            ("Fecha Creación:", self.format_date(ticket['fecha_creacion'])),
        ]

        for i, (label, value) in enumerate(labels_data):
            label_widget = ctk.CTkLabel(
                info_frame,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            label_widget.grid(row=i, column=0, padx=20, pady=10, sticky="w")

            value_widget = ctk.CTkLabel(
                info_frame,
                text=value,
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            value_widget.grid(row=i, column=1, padx=20, pady=10, sticky="ew")

        status_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        status_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_columnconfigure(1, weight=1)

        prioridad_label = ctk.CTkLabel(
            status_frame,
            text="Prioridad",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        prioridad_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        prioridad_color = self.get_prioridad_color(ticket['prioridad'])
        prioridad_value = ctk.CTkLabel(
            status_frame,
            text=ticket['prioridad_display'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=prioridad_color
        )
        prioridad_value.grid(row=1, column=0, padx=20, pady=(0, 20))

        estado_label = ctk.CTkLabel(
            status_frame,
            text="Estado",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        estado_label.grid(row=0, column=1, padx=20, pady=(20, 5))

        estado_color = self.get_estado_color(ticket['estado'])
        self.estado_value = ctk.CTkLabel(
            status_frame,
            text=ticket['estado_display'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=estado_color
        )
        self.estado_value.grid(row=1, column=1, padx=20, pady=(0, 20))

        content_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        content_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        content_title = ctk.CTkLabel(
            content_frame,
            text="Descripción",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        content_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        content_text = ctk.CTkTextbox(
            content_frame,
            height=250,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        content_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        content_text.insert("1.0", ticket['contenido'])
        content_text.configure(state="disabled")

        if self.api_client.is_superuser():
            self.create_admin_controls(main_frame, ticket['estado'])

    def create_admin_controls(self, parent, current_estado: str):
        admin_frame = ctk.CTkFrame(parent, corner_radius=10)
        admin_frame.grid(row=3, column=0, sticky="ew")
        admin_frame.grid_columnconfigure(0, weight=1)

        admin_title = ctk.CTkLabel(
            admin_frame,
            text="Actualizar Estado",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        admin_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.estado_var = ctk.StringVar(value=current_estado)

        estados = [
            ("Abierto", "abierto"),
            ("En Proceso", "en_proceso"),
            ("Resuelto", "resuelto"),
            ("Cerrado", "cerrado")
        ]

        buttons_frame = ctk.CTkFrame(admin_frame, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        for i, (label, value) in enumerate(estados):
            radio = ctk.CTkRadioButton(
                buttons_frame,
                text=label,
                variable=self.estado_var,
                value=value,
                font=ctk.CTkFont(size=13)
            )
            radio.pack(side="left", padx=(0, 20))

        self.update_button = ctk.CTkButton(
            admin_frame,
            text="Actualizar Estado",
            command=self.handle_update_estado,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.update_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.message_label = ctk.CTkLabel(
            admin_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.message_label.grid(row=3, column=0, padx=20, pady=(0, 20))

    def handle_update_estado(self):
        nuevo_estado = self.estado_var.get()

        self.update_button.configure(state="disabled", text="Actualizando...")
        self.message_label.configure(text="")

        success, result = self.api_client.update_ticket_estado(
            self.ticket_id,
            nuevo_estado
        )

        if success:
            self.ticket_data = result
            estado_color = self.get_estado_color(result['estado'])
            self.estado_value.configure(
                text=result['estado_display'],
                text_color=estado_color
            )
            self.message_label.configure(
                text="Estado actualizado exitosamente",
                text_color="green"
            )
        else:
            self.message_label.configure(
                text=f"Error: {result}",
                text_color="red"
            )

        self.update_button.configure(state="normal", text="Actualizar Estado")

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

    def show(self, ticket_id: int):
        self.load_ticket(ticket_id)
