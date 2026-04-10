from django.apps import AppConfig


class TicketSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticket_system'

    def ready(self):
        from tickets.db_init import create_database_if_not_exists
        create_database_if_not_exists()
