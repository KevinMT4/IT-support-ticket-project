import os
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage


def send_ticket_created_email_to_user(ticket):
    subject = f'Nuevo Ticket Creado: {ticket.asunto}'
    # logo HTML (inline image referenced by CID)
    logo_html = '<div style="text-align:center;margin-bottom:20px;"><img src="cid:logo_image" alt="Logo" style="max-width:200px;height:auto;"></div>'

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    Nuevo Ticket Creado
                </h2>

                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
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

    # send with inline logo
    return _send_email_with_logo(subject, plain_message, logo_html + html_message, [ticket.usuario.email])


def send_ticket_created_email_to_admins(ticket):
    from .models import Usuario

    # Subject más descriptivo para Teams
    user_name = ticket.usuario.get_full_name() or ticket.usuario.username
    dept_name = ticket.usuario.departamento.nombre if ticket.usuario.departamento else 'Sin Departamento'
    subject = f'Nuevo Ticket: {ticket.asunto} - {user_name} ({dept_name})'

    logo_html = '<div style="text-align:center;margin-bottom:20px;"><img src="cid:logo_image" alt="Logo" style="max-width:200px;height:auto;"></div>'

    # HTML simplificado para mejor compatibilidad con Teams
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">

                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f3f4f6;">
                        <td style="padding: 10px; font-weight: bold; border: 1px solid #e5e7eb;">Creado por:</td>
                        <td style="padding: 10px; border: 1px solid #e5e7eb;">{user_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold; border: 1px solid #e5e7eb;">Email:</td>
                        <td style="padding: 10px; border: 1px solid #e5e7eb;">{ticket.usuario.email}</td>
                    </tr>
                    <tr style="background-color: #f3f4f6;">
                        <td style="padding: 10px; font-weight: bold; border: 1px solid #e5e7eb;">Departamento:</td>
                        <td style="padding: 10px; border: 1px solid #e5e7eb;">{dept_name}</td>
                    </tr>
                    <tr style="background-color: #f3f4f6;">
                        <td style="padding: 10px; font-weight: bold; border: 1px solid #e5e7eb;">Prioridad:</td>
                        <td style="padding: 10px; border: 1px solid #e5e7eb;">{ticket.get_prioridad_display()}</td>
                    </tr>
                    {f'<tr><td style="padding: 10px; font-weight: bold; border: 1px solid #e5e7eb;">Motivo:</td><td style="padding: 10px; border: 1px solid #e5e7eb;">{ticket.motivo.nombre}</td></tr>' if ticket.motivo else ''}
                </table>

                <div style="margin: 20px 0; padding: 15px; background-color: #fffbeb; border: 2px solid #fbbf24; border-radius: 8px;">
                    <div style="margin: 0; font-size: 14px; line-height: 1.6; word-wrap: break-word; overflow-wrap: break-word;">
                        {ticket.contenido.replace(chr(10), '<br>')}
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

    # Texto plano mejorado - MUY IMPORTANTE para Teams
    plain_message = f"""
=============================================================
NUEVO TICKET CREADO - TICKET #{ticket.id}
=============================================================

INFORMACION DEL USUARIO:
------------------------
Creado por: {user_name}
Email: {ticket.usuario.email}
Departamento: {dept_name}

DETALLES DEL TICKET:
--------------------
Prioridad: {ticket.get_prioridad_display()}
Estado: {ticket.get_estado_display()}
{f'Motivo: {ticket.motivo.nombre}' if ticket.motivo else ''}

{ticket.contenido}

=============================================================
Sistema de Gestion de Tickets - Notificacion Automatica
Por favor, ingresa al sistema para gestionar este ticket.
=============================================================
    """

    admins = Usuario.objects.filter(rol__in=['superuser', 'admin'], is_active=True)
    admin_emails = [admin.email for admin in admins if admin.email]

    if not admin_emails:
        print("No hay administradores con email configurado para notificar")
        return False

    # send with inline logo and copy hotline mailbox
    cc_list = [settings.HOTLINE_EMAIL] if getattr(settings, 'HOTLINE_EMAIL', None) else None
    success = _send_email_with_logo(subject, plain_message, logo_html + html_message, admin_emails, cc_list=cc_list)
    if success:
        print(f"Email enviado a administradores: {', '.join(admin_emails)}")
        if cc_list:
            print(f"Copia enviada a: {', '.join(cc_list)}")
    return success


def send_ticket_status_updated_email(ticket, previous_status):
    from django.utils import timezone

    subject = f'Ticket #{ticket.id} - Estado Actualizado'
    logo_html = '<div style="text-align:center;margin-bottom:20px;"><img src="cid:logo_image" alt="Logo" style="max-width:200px;height:auto;"></div>'

    # Calcular tiempo de resolución si el ticket está resuelto
    tiempo_resolucion_html = ""
    tiempo_resolucion_plain = ""
    solucion_html = ""
    solucion_plain = ""

    if ticket.estado == 'resuelto':
        tiempo_transcurrido = timezone.now() - ticket.fecha_creacion
        dias = tiempo_transcurrido.days
        horas = tiempo_transcurrido.seconds // 3600
        minutos = (tiempo_transcurrido.seconds % 3600) // 60

        if dias > 0:
            dia_word = 'días' if dias != 1 else 'día'
            hora_word = 'horas' if horas != 1 else 'hora'
            tiempo_resolucion = f"{dias} {dia_word}, {horas} {hora_word}"
        elif horas > 0:
            hora_word = 'horas' if horas != 1 else 'hora'
            minuto_word = 'minutos' if minutos != 1 else 'minuto'
            tiempo_resolucion = f"{horas} {hora_word}, {minutos} {minuto_word}"
        else:
            minuto_word = 'minutos' if minutos != 1 else 'minuto'
            tiempo_resolucion = f"{minutos} {minuto_word}"

        tiempo_resolucion_html = f'<p><strong>Tiempo de resolución:</strong> {tiempo_resolucion}</p>'
        tiempo_resolucion_plain = f"Tiempo de resolución: {tiempo_resolucion}\n"

        # Incluir detalles de la solución si están disponibles
        if ticket.solucion_texto or ticket.solucion_imagenes or ticket.cerrado_por:
            solucion_plain = "\nDetalles de la Resolución:\n"

            if ticket.cerrado_por:
                solucion_html += f"""
                <div style="margin: 20px 0;">
                    <p style="background-color: #f0fdf4; padding: 12px; border-left: 4px solid #10b981; border-radius: 4px;">
                        <strong>Cerrado por:</strong> {ticket.cerrado_por.nombre}
                    </p>
                </div>
                """
                solucion_plain += f"Cerrado por: {ticket.cerrado_por.nombre}\n"

            if ticket.solucion_texto:
                solucion_html += f"""
                <div style="margin: 20px 0;">
                    <h3 style="color: #1e40af;">Solución:</h3>
                    <p style="background-color: #f9fafb; padding: 15px; border-left: 4px solid #10b981; border-radius: 4px;">
                        {ticket.solucion_texto}
                    </p>
                </div>
                """
                solucion_plain += f"Solución:\n{ticket.solucion_texto}\n"

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    Estado del Ticket Actualizado
                </h2>

                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
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
                    {tiempo_resolucion_html}
                </div>

                {solucion_html}

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

    Asunto: {ticket.asunto}
    Estado anterior: {dict(ticket.ESTADO_CHOICES).get(previous_status, previous_status)}
    Estado actual: {ticket.get_estado_display()}
    Prioridad: {ticket.get_prioridad_display()}
    {tiempo_resolucion_plain}{solucion_plain}
    ---
    Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.
    """

    return _send_email_with_logo(subject, plain_message, logo_html + html_message, [ticket.usuario.email])


def send_ticket_priority_updated_email(ticket, previous_priority):
    subject = f'Ticket #{ticket.id} - Prioridad Actualizada'

    priority_colors = {
        'baja': '#3b82f6',
        'media': '#f59e0b',
        'alta': '#fb923c',
        'urgente': '#ef4444'
    }

    logo_html = '<div style="text-align:center;margin-bottom:20px;"><img src="cid:logo_image" alt="Logo" style="max-width:200px;height:auto;"></div>'

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    Prioridad del Ticket Actualizada
                </h2>

                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
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

    Asunto: {ticket.asunto}
    Estado: {ticket.get_estado_display()}
    Prioridad anterior: {dict(ticket.PRIORIDAD_CHOICES).get(previous_priority, previous_priority)}
    Prioridad actual: {ticket.get_prioridad_display()}

    ---
    Este correo ha sido enviado automáticamente por el Sistema de Gestión de Tickets.
    """

    return _send_email_with_logo(subject, plain_message, logo_html + html_message, [ticket.usuario.email])


def _send_email_with_logo(subject, plain_message, html_message, recipient_list, cc_list=None, bcc_list=None):
    """Send an email with HTML body and embed the project logo as an inline image (CID).
    Returns True on success, False on failure."""
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            cc=cc_list,
            bcc=bcc_list,
        )
        msg.attach_alternative(html_message, "text/html")

        # find logo path
        logo_path = os.path.join(settings.BASE_DIR, 'client', 'public', 'image.png')
        if not os.path.exists(logo_path):
            # try with .jpg
            logo_path_jpg = os.path.join(settings.BASE_DIR, 'client', 'public', 'image.jpg')
            if os.path.exists(logo_path_jpg):
                logo_path = logo_path_jpg

        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data)
                image.add_header('Content-ID', '<logo_image>')
                image.add_header('Content-Disposition', 'inline', filename=os.path.basename(logo_path))
                msg.attach(image)
        else:
            print(f"Logo not found at {logo_path}; sending email without inline logo")

        msg.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False
