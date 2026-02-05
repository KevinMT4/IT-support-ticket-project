import customtkinter as ctk
from api_client import APIClient
from login_screen import LoginScreen
from tickets_list_screen import TicketsListScreen
from create_ticket_screen import CreateTicketScreen
from ticket_detail_screen import TicketDetailScreen
from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT


class TicketSystemApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.api_client = APIClient()

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.create_frames()

        self.show_frame("login")

    def create_frames(self):
        self.frames["login"] = LoginScreen(
            self.container,
            on_login_success=self.handle_login
        )

        self.frames["tickets_list"] = TicketsListScreen(
            self.container,
            self.api_client,
            on_create_ticket=lambda: self.show_frame("create_ticket"),
            on_view_ticket=self.handle_view_ticket,
            on_logout=self.handle_logout
        )

        self.frames["create_ticket"] = CreateTicketScreen(
            self.container,
            self.api_client,
            on_back=lambda: self.show_frame("tickets_list"),
            on_ticket_created=self.handle_ticket_created
        )

        self.frames["ticket_detail"] = TicketDetailScreen(
            self.container,
            self.api_client,
            on_back=lambda: self.show_frame("tickets_list")
        )

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, frame_name: str):
        frame = self.frames[frame_name]
        frame.tkraise()

        if hasattr(frame, 'show'):
            frame.show()

    def handle_login(self, username: str, password: str):
        success, message = self.api_client.login(username, password)

        if success:
            self.show_frame("tickets_list")
        else:
            self.frames["login"].show_error(message)

    def handle_logout(self):
        self.api_client.logout()
        self.frames["login"].reset()
        self.show_frame("login")

    def handle_view_ticket(self, ticket_id: int):
        self.frames["ticket_detail"].show(ticket_id)
        self.show_frame("ticket_detail")

    def handle_ticket_created(self):
        self.show_frame("tickets_list")


def main():
    app = TicketSystemApp()
    app.mainloop()


if __name__ == "__main__":
    main()
