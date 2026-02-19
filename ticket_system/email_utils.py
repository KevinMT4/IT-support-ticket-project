from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_ticket_created_email_to_user(ticket):
    subject = f'Nuevo Ticket Creado #{ticket.id}: {ticket.asunto}'

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    Nuevo Ticket Creado
                </h2>

                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Número de Ticket:</strong> #{ticket.id}</p>
                    <p><strong>Asunto:</strong> {ticket.asunto}</p>
                    <p><strong>Prioridad:</strong> {ticket.get_prioridad_display()}</p>
                    <p><strong>Estado:</strong> {ticket.get_estado_display()}</p>
                    <p><strong>Departamento:</strong> {ticket.departamento.nombre}</p>
                    {f'<p><strong>Motivo:</strong> {ticket.motivo.nombre}</p>' if ticket.motivo else ''}
                </div>

                <div style="margin: 20px 0;">
                    <h3 style="color: #1e40af;">Descripción:</h3>
                    <p style="background-color: #f9fafb; padding: 15px; border-left: 4px solid #2563eb; border-radius: 4px;">
                        {ticket.contenido}
                    </p>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 0.875rem; color: #6b7280;">
                    <p>Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.</p>
                    <p>Por favor, no responda a este correo.</p>
                </div>
            </div>
        </body>
    </html>
    """

    plain_message = f"""
    Nuevo Ticket Creado

    Número de Ticket: #{ticket.id}
    Asunto: {ticket.asunto}
    Prioridad: {ticket.get_prioridad_display()}
    Estado: {ticket.get_estado_display()}
    Departamento: {ticket.departamento.nombre}
    {f'Motivo: {ticket.motivo.nombre}' if ticket.motivo else ''}

    Descripción:
    {ticket.contenido}

    ---
    Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ticket.usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


def send_ticket_created_email_to_admins(ticket):
    from .models import Usuario

    subject = f'Nuevo Ticket Creado #{ticket.id}: {ticket.asunto}'

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    Nuevo Ticket Creado - Notificación para Administrador
                </h2>

                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Número de Ticket:</strong> #{ticket.id}</p>
                    <p><strong>Creado por:</strong> {ticket.usuario.get_full_name() or ticket.usuario.username}</p>
                    <p><strong>Email del usuario:</strong> {ticket.usuario.email}</p>
                    <p><strong>Departamento del usuario:</strong> {ticket.usuario.departamento.nombre if ticket.usuario.departamento else 'N/A'}</p>
                    <hr style="margin: 15px 0; border: none; border-top: 1px solid #d1d5db;">
                    <p><strong>Asunto:</strong> {ticket.asunto}</p>
                    <p><strong>Prioridad:</strong> {ticket.get_prioridad_display()}</p>
                    <p><strong>Estado:</strong> {ticket.get_estado_display()}</p>
                    <p><strong>Departamento destino:</strong> {ticket.departamento.nombre}</p>
                    {f'<p><strong>Motivo:</strong> {ticket.motivo.nombre}</p>' if ticket.motivo else ''}
                </div>

                <div style="margin: 20px 0;">
                    <h3 style="color: #1e40af;">Descripción del Problema:</h3>
                    <p style="background-color: #f9fafb; padding: 15px; border-left: 4px solid #2563eb; border-radius: 4px;">
                        {ticket.contenido}
                    </p>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 0.875rem; color: #6b7280;">
                    <p>Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.</p>
                    <p>Por favor, ingresa al sistema para gestionar este ticket.</p>
                </div>
            </div>
        </body>
    </html>
    """

    plain_message = f"""
    Nuevo Ticket Creado - Notificación para Administrador

    Número de Ticket: #{ticket.id}
    Creado por: {ticket.usuario.get_full_name() or ticket.usuario.username}
    Email del usuario: {ticket.usuario.email}
    Departamento del usuario: {ticket.usuario.departamento.nombre if ticket.usuario.departamento else 'N/A'}

    Asunto: {ticket.asunto}
    Prioridad: {ticket.get_prioridad_display()}
    Estado: {ticket.get_estado_display()}
    Departamento destino: {ticket.departamento.nombre}
    {f'Motivo: {ticket.motivo.nombre}' if ticket.motivo else ''}

    Descripción del Problema:
    {ticket.contenido}

    ---
    Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.
    Por favor, ingresa al sistema para gestionar este ticket.
    """

    admins = Usuario.objects.filter(rol__in=['superuser', 'admin'], is_active=True)
    admin_emails = [admin.email for admin in admins if admin.email]

    if not admin_emails:
        print("No hay administradores con email configurado para notificar")
        return False

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Email enviado a administradores: {', '.join(admin_emails)}")
        return True
    except Exception as e:
        print(f"Error enviando email a administradores: {e}")
        return False


def send_ticket_status_updated_email(ticket, previous_status):
    subject = f'Ticket #{ticket.id} - Estado Actualizado'

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    Estado del Ticket Actualizado
                </h2>

                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Número de Ticket:</strong> #{ticket.id}</p>
                    <p><strong>Asunto:</strong> {ticket.asunto}</p>
                    <p style="margin: 15px 0;">
                        <strong>Estado anterior:</strong>
                        <span style="background-color: #e5e7eb; padding: 4px 12px; border-radius: 16px;">
                            {dict(ticket.ESTADO_CHOICES).get(previous_status, previous_status)}
                        </span>
                    </p>
                    <p style="margin: 15px 0;">
                        <strong>Estado actual:</strong>
                        <span style="background-color: #10b981; color: white; padding: 4px 12px; border-radius: 16px;">
                            {ticket.get_estado_display()}
                        </span>
                    </p>
                    <p><strong>Prioridad:</strong> {ticket.get_prioridad_display()}</p>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 0.875rem; color: #6b7280;">
                    <p>Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.</p>
                    <p>Por favor, no responda a este correo.</p>
                </div>
            </div>
        </body>
    </html>
    """

    plain_message = f"""
    Estado del Ticket Actualizado

    Número de Ticket: #{ticket.id}
    Asunto: {ticket.asunto}
    Estado anterior: {dict(ticket.ESTADO_CHOICES).get(previous_status, previous_status)}
    Estado actual: {ticket.get_estado_display()}
    Prioridad: {ticket.get_prioridad_display()}

    ---
    Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ticket.usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


def send_ticket_priority_updated_email(ticket, previous_priority):
    subject = f'Ticket #{ticket.id} - Prioridad Actualizada'

    priority_colors = {
        'baja': '#3b82f6',
        'media': '#f59e0b',
        'alta': '#fb923c',
        'urgente': '#ef4444'
    }

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    Prioridad del Ticket Actualizada
                </h2>

                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Número de Ticket:</strong> #{ticket.id}</p>
                    <p><strong>Asunto:</strong> {ticket.asunto}</p>
                    <p><strong>Estado:</strong> {ticket.get_estado_display()}</p>
                    <p style="margin: 15px 0;">
                        <strong>Prioridad anterior:</strong>
                        <span style="background-color: {priority_colors.get(previous_priority, '#6b7280')}; color: white; padding: 4px 12px; border-radius: 16px;">
                            {dict(ticket.PRIORIDAD_CHOICES).get(previous_priority, previous_priority)}
                        </span>
                    </p>
                    <p style="margin: 15px 0;">
                        <strong>Prioridad actual:</strong>
                        <span style="background-color: {priority_colors.get(ticket.prioridad, '#6b7280')}; color: white; padding: 4px 12px; border-radius: 16px; font-weight: bold;">
                            {ticket.get_prioridad_display()}
                        </span>
                    </p>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 0.875rem; color: #6b7280;">
                    <p>Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.</p>
                    <p>Por favor, no responda a este correo.</p>
                </div>
            </div>
        </body>
    </html>
    """

    plain_message = f"""
    Prioridad del Ticket Actualizada

    Número de Ticket: #{ticket.id}
    Asunto: {ticket.asunto}
    Estado: {ticket.get_estado_display()}
    Prioridad anterior: {dict(ticket.PRIORIDAD_CHOICES).get(previous_priority, previous_priority)}
    Prioridad actual: {ticket.get_prioridad_display()}

    ---
    Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ticket.usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False
