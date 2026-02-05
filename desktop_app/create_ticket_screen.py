import customtkinter as ctk
from typing import Callable, List, Dict, Any


class CreateTicketScreen(ctk.CTkFrame):
    def __init__(self, parent, api_client, on_back: Callable, on_ticket_created: Callable):
        super().__init__(parent, fg_color="transparent")
        self.api_client = api_client
        self.on_back = on_back
        self.on_ticket_created = on_ticket_created
        self.departamentos = []
        self.motivos = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_header()
        self.create_form()

    def create_header(self):
        header_frame = ctk.CTkFrame(self, height=80, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            header_frame,
            text="← Volver",
            command=self.on_back,
            width=100,
            height=35,
            fg_color="gray",
            hover_color="#666666"
        )
        back_btn.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        title = ctk.CTkLabel(
            header_frame,
            text="Crear Nuevo Ticket",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=1, padx=20, pady=20)

    def create_form(self):
        form_container = ctk.CTkScrollableFrame(self, corner_radius=10)
        form_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        form_container.grid_columnconfigure(0, weight=1)

        form_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=40, pady=30)
        form_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form_frame,
            text="Asunto",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.asunto_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ingresa el asunto del ticket",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.asunto_entry.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            form_frame,
            text="Departamento",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.departamento_var = ctk.StringVar(value="Selecciona un departamento")
        self.departamento_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.departamento_var,
            values=["Cargando..."],
            command=self.on_departamento_changed,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.departamento_menu.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            form_frame,
            text="Motivo (Opcional)",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=4, column=0, sticky="w", pady=(0, 5))

        self.motivo_var = ctk.StringVar(value="Selecciona un motivo")
        self.motivo_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.motivo_var,
            values=["Primero selecciona un departamento"],
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.motivo_menu.grid(row=5, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            form_frame,
            text="Prioridad",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=6, column=0, sticky="w", pady=(0, 5))

        self.prioridad_var = ctk.StringVar(value="media")
        prioridad_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        prioridad_frame.grid(row=7, column=0, sticky="ew", pady=(0, 20))

        prioridades = [
            ("Baja", "baja"),
            ("Media", "media"),
            ("Alta", "alta"),
            ("Urgente", "urgente")
        ]

        for i, (label, value) in enumerate(prioridades):
            radio = ctk.CTkRadioButton(
                prioridad_frame,
                text=label,
                variable=self.prioridad_var,
                value=value,
                font=ctk.CTkFont(size=13)
            )
            radio.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(
            form_frame,
            text="Descripción",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=8, column=0, sticky="w", pady=(0, 5))

        self.contenido_text = ctk.CTkTextbox(
            form_frame,
            height=200,
            font=ctk.CTkFont(size=13)
        )
        self.contenido_text.grid(row=9, column=0, sticky="ew", pady=(0, 20))

        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        self.error_label.grid(row=10, column=0, sticky="ew", pady=(0, 10))

        self.create_button = ctk.CTkButton(
            form_frame,
            text="Crear Ticket",
            command=self.handle_create,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.create_button.grid(row=11, column=0, sticky="ew")

    def on_departamento_changed(self, choice):
        selected_dept = next(
            (d for d in self.departamentos if d['nombre'] == choice),
            None
        )

        if selected_dept:
            self.load_motivos(selected_dept['id'])

    def load_departamentos(self):
        success, result = self.api_client.get_departamentos()

        if success:
            self.departamentos = result
            dept_names = [d['nombre'] for d in self.departamentos]
            self.departamento_menu.configure(values=dept_names)
            if dept_names:
                self.departamento_var.set(dept_names[0])
                self.on_departamento_changed(dept_names[0])
        else:
            self.departamento_menu.configure(values=["Error al cargar"])

    def load_motivos(self, departamento_id: int):
        success, result = self.api_client.get_motivos(departamento_id)

        if success:
            self.motivos = result
            if self.motivos:
                motivo_names = [m['nombre'] for m in self.motivos]
                self.motivo_menu.configure(values=["Ninguno"] + motivo_names)
                self.motivo_var.set("Ninguno")
            else:
                self.motivo_menu.configure(values=["No hay motivos disponibles"])
                self.motivo_var.set("No hay motivos disponibles")
        else:
            self.motivo_menu.configure(values=["Error al cargar"])

    def handle_create(self):
        asunto = self.asunto_entry.get().strip()
        contenido = self.contenido_text.get("1.0", "end-1c").strip()
        departamento_nombre = self.departamento_var.get()
        motivo_nombre = self.motivo_var.get()
        prioridad = self.prioridad_var.get()

        if not asunto:
            self.show_error("El asunto es requerido")
            return

        if not contenido:
            self.show_error("La descripción es requerida")
            return

        if departamento_nombre == "Selecciona un departamento":
            self.show_error("Debes seleccionar un departamento")
            return

        selected_dept = next(
            (d for d in self.departamentos if d['nombre'] == departamento_nombre),
            None
        )

        if not selected_dept:
            self.show_error("Departamento no válido")
            return

        data = {
            'asunto': asunto,
            'contenido': contenido,
            'departamento': selected_dept['id'],
            'prioridad': prioridad
        }

        if motivo_nombre != "Ninguno" and motivo_nombre != "No hay motivos disponibles":
            selected_motivo = next(
                (m for m in self.motivos if m['nombre'] == motivo_nombre),
                None
            )
            if selected_motivo:
                data['motivo'] = selected_motivo['id']

        self.create_button.configure(state="disabled", text="Creando...")
        self.error_label.configure(text="")

        success, result = self.api_client.create_ticket(data)

        if success:
            self.on_ticket_created()
        else:
            self.show_error(f"Error al crear ticket: {result}")

    def show_error(self, message: str):
        self.error_label.configure(text=message)
        self.create_button.configure(state="normal", text="Crear Ticket")

    def reset(self):
        self.asunto_entry.delete(0, "end")
        self.contenido_text.delete("1.0", "end")
        self.prioridad_var.set("media")
        self.error_label.configure(text="")
        self.create_button.configure(state="normal", text="Crear Ticket")
        self.load_departamentos()

    def show(self):
        self.reset()
