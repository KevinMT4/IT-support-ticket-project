from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import timedelta
import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from django.conf import settings
from .models import Usuario, Departamento, Motivo, Ticket
from .serializers import (
    UsuarioSerializer,
    UsuarioRegistroSerializer,
    DepartamentoSerializer,
    MotivoSerializer,
    TicketSerializer,
    TicketCreateSerializer
)
from .email_utils import (
    send_ticket_created_email_to_user,
    send_ticket_created_email_to_admins,
    send_ticket_status_updated_email,
    send_ticket_priority_updated_email
)


class LogoHeader(Flowable):
    def __init__(self, width, height, logo_path=None):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.logo_path = logo_path

    def draw(self):
        canvas = self.canv

        if self.logo_path and os.path.exists(self.logo_path):
            logo_width = 2.5 * inch
            logo_height = 0.7 * inch
            x_position = 0.5 * inch
            y_position = self.height - logo_height - 0.2 * inch

            canvas.drawImage(
                self.logo_path,
                x_position,
                y_position,
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask='auto'
            )

            # canvas.setFillColor(colors.HexColor('#6b7280'))
            # canvas.setFont('Helvetica', 9)
            # canvas.drawString(x_position, y_position - 0.25 * inch, 'Sistema de Gestión de Tickets')
        else:
            canvas.setFillColor(colors.HexColor('#2563eb'))
            canvas.setFont('Helvetica-Bold', 24)
            canvas.drawString(0.5 * inch, self.height - 0.5 * inch, 'COFATECH')
            # canvas.setFont('Helvetica', 9)
            # canvas.setFillColor(colors.HexColor('#6b7280'))
            # canvas.drawString(0.5 * inch, self.height - 0.7 * inch, 'Sistema de Gestión de Tickets')


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Por favor proporciona email y contraseña'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user_obj = Usuario.objects.get(email=email)
        user = authenticate(username=user_obj.username, password=password)
    except Usuario.DoesNotExist:
        user = None

    if user is not None:
        if user.is_superuser and user.rol != 'superuser':
            user.rol = 'superuser'
            user.save()

        token, created = Token.objects.get_or_create(user=user)
        try:
            serialized_data = UsuarioSerializer(user).data
        except Exception as e:
            return Response({'error': f'Error al procesar datos del usuario: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'token': token.key,
            'user': serialized_data
        })
    else:
        return Response({'error': 'Credenciales inválidas'},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if hasattr(request.user, 'auth_token'):
        request.user.auth_token.delete()
    return Response({'message': 'Sesión cerrada exitosamente'})


@api_view(['POST'])
@permission_classes([AllowAny])
def registro_view(request):
    serializer = UsuarioRegistroSerializer(data=request.data)

    if serializer.is_valid():
        usuario = serializer.save()
        token, created = Token.objects.get_or_create(user=usuario)

        return Response({
            'token': token.key,
            'user': UsuarioSerializer(usuario).data,
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartamentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Departamento.objects.filter(activo=True)
    serializer_class = DepartamentoSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]


class MotivoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Motivo.objects.all()
    serializer_class = MotivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        departamento_id = self.request.query_params.get('departamento', None)
        if departamento_id:
            queryset = queryset.filter(departamento_id=departamento_id)
        return queryset


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.rol == 'superuser':
            return Ticket.objects.all()
        return Ticket.objects.filter(usuario=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        if self.request.user.rol == 'superuser':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Los administradores no pueden crear tickets')
        ticket = serializer.save(usuario=self.request.user)
        send_ticket_created_email_to_user(ticket)
        send_ticket_created_email_to_admins(ticket)

    @action(detail=True, methods=['post'])
    def update_estado(self, request, pk=None):
        ticket = self.get_object()

        if request.user.rol != 'superuser':
            return Response({'error': 'No tienes permisos para actualizar el estado'},
                            status=status.HTTP_403_FORBIDDEN)

        nuevo_estado = request.data.get('estado')
        if not nuevo_estado:
            return Response({'error': 'El estado es requerido'},
                            status=status.HTTP_400_BAD_REQUEST)

        if nuevo_estado not in dict(Ticket.ESTADO_CHOICES):
            return Response({'error': 'Estado inválido'},
                            status=status.HTTP_400_BAD_REQUEST)

        previous_estado = ticket.estado
        ticket.estado = nuevo_estado
        ticket.save()

        if previous_estado != nuevo_estado:
            send_ticket_status_updated_email(ticket, previous_estado)

        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def update_prioridad(self, request, pk=None):
        ticket = self.get_object()

        if request.user.rol != 'superuser':
            return Response({'error': 'No tienes permisos para actualizar la prioridad'},
                            status=status.HTTP_403_FORBIDDEN)

        nueva_prioridad = request.data.get('prioridad')
        if not nueva_prioridad:
            return Response({'error': 'La prioridad es requerida'},
                            status=status.HTTP_400_BAD_REQUEST)

        if nueva_prioridad not in dict(Ticket.PRIORIDAD_CHOICES):
            return Response({'error': 'Prioridad inválida'},
                            status=status.HTTP_400_BAD_REQUEST)

        previous_prioridad = ticket.prioridad
        ticket.prioridad = nueva_prioridad
        ticket.save()

        if previous_prioridad != nueva_prioridad:
            send_ticket_priority_updated_email(ticket, previous_prioridad)

        return Response(TicketSerializer(ticket).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_pdf_estadisticas(request):
    if request.user.rol != 'superuser':
        return Response({'error': 'No tienes permisos para generar reportes'},
                        status=status.HTTP_403_FORBIDDEN)

    pdf_dir = os.path.join(settings.BASE_DIR, 'reportes_pdf', 'semanales')
    os.makedirs(pdf_dir, exist_ok=True)

    filename = f"reporte_tickets_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(pdf_dir, filename)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=6,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10,
        spaceBefore=12,
        alignment=TA_CENTER
    )

    fecha_inicio = timezone.now() - timedelta(days=7)
    tickets_semana = Ticket.objects.filter(fecha_creacion__gte=fecha_inicio)
    todos_tickets = Ticket.objects.all()

    logo_path = os.path.join(settings.BASE_DIR, 'ticket_system', 'static', 'ticket_system', 'images', 'logo.png')
    logo_header = LogoHeader(7.5 * inch, 60, logo_path)
    elements.append(logo_header)
    elements.append(Spacer(1, 0.15 * inch))

    title = Paragraph("Reporte Semanal de Tickets", title_style)
    elements.append(title)

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER
    )
    subtitle = Paragraph(
        f"Periodo: {fecha_inicio.strftime('%d/%m/%Y')} - {timezone.now().strftime('%d/%m/%Y')}",
        subtitle_style
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.2 * inch))

    dept_stats = todos_tickets.values('usuario__departamento__nombre').annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    user_stats = todos_tickets.values('usuario__username', 'usuario__first_name', 'usuario__last_name').annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    motivo_stats = todos_tickets.filter(motivo__isnull=False).values('motivo__nombre').annotate(
        total=Count('id')
    ).order_by('-total')

    prioridad_stats = todos_tickets.values('prioridad').annotate(total=Count('id')).order_by('-total')
    prioridad_nombres = {
        'baja': 'Baja',
        'media': 'Media',
        'alta': 'Alta',
        'urgente': 'Urgente'
    }

    drawing_dept = Drawing(310, 210)
    if dept_stats:
        bc_dept = HorizontalBarChart()
        bc_dept.x = 100
        bc_dept.y = 30
        bc_dept.height = 150
        bc_dept.width = 190
        dept_names = [stat['usuario__departamento__nombre'] or 'Sin dept.' for stat in dept_stats]
        dept_values = [[stat['total'] for stat in dept_stats]]
        bc_dept.data = dept_values
        bc_dept.categoryAxis.categoryNames = dept_names
        bc_dept.categoryAxis.labels.fontSize = 8
        bc_dept.valueAxis.valueMin = 0
        bc_dept.valueAxis.valueMax = max(dept_values[0]) * 1.2
        bc_dept.valueAxis.labels.fontSize = 8
        bc_dept.bars[0].fillColor = colors.HexColor('#3b82f6')
        bc_dept.barWidth = 15
        drawing_dept.add(bc_dept)

    drawing_users = Drawing(310, 210)
    if user_stats:
        bc_users = HorizontalBarChart()
        bc_users.x = 100
        bc_users.y = 30
        bc_users.height = 150
        bc_users.width = 190
        user_names = []
        for stat in user_stats:
            nombre = f"{stat['usuario__first_name']} {stat['usuario__last_name']}".strip()
            if not nombre:
                nombre = stat['usuario__username']
            if len(nombre) > 15:
                nombre = nombre[:12] + '...'
            user_names.append(nombre)
        user_values = [[stat['total'] for stat in user_stats]]
        bc_users.data = user_values
        bc_users.categoryAxis.categoryNames = user_names
        bc_users.categoryAxis.labels.fontSize = 8
        bc_users.valueAxis.valueMin = 0
        bc_users.valueAxis.valueMax = max(user_values[0]) * 1.2
        bc_users.valueAxis.labels.fontSize = 8
        bc_users.bars[0].fillColor = colors.HexColor('#10b981')
        bc_users.barWidth = 15
        drawing_users.add(bc_users)

    drawing_motivos = Drawing(310, 210)
    if motivo_stats.count() > 0:
        pie_motivo = Pie()
        pie_motivo.x = 90
        pie_motivo.y = 45
        pie_motivo.width = 130
        pie_motivo.height = 130
        motivo_labels = [stat['motivo__nombre'] for stat in motivo_stats]
        motivo_values = [stat['total'] for stat in motivo_stats]
        pie_motivo.data = motivo_values
        pie_motivo.labels = motivo_labels
        pie_motivo.slices.strokeWidth = 0.5
        pie_motivo.slices.fontSize = 9
        colores = [
            colors.HexColor('#3b82f6'),
            colors.HexColor('#10b981'),
            colors.HexColor('#f59e0b'),
            colors.HexColor('#ef4444'),
            colors.HexColor('#8b5cf6'),
            colors.HexColor('#ec4899'),
        ]
        for i in range(len(motivo_values)):
            pie_motivo.slices[i].fillColor = colores[i % len(colores)]
        drawing_motivos.add(pie_motivo)

    drawing_prioridad = Drawing(310, 210)
    if prioridad_stats.count() > 0:
        pie_prioridad = Pie()
        pie_prioridad.x = 90
        pie_prioridad.y = 45
        pie_prioridad.width = 130
        pie_prioridad.height = 130
        prioridad_labels = [prioridad_nombres.get(stat['prioridad'], stat['prioridad']) for stat in prioridad_stats]
        prioridad_values = [stat['total'] for stat in prioridad_stats]
        pie_prioridad.data = prioridad_values
        pie_prioridad.labels = prioridad_labels
        pie_prioridad.slices.strokeWidth = 0.5
        pie_prioridad.slices.fontSize = 9
        prioridad_colores = {
            'Baja': colors.HexColor('#3b82f6'),
            'Media': colors.HexColor('#f59e0b'),
            'Alta': colors.HexColor('#fb923c'),
            'Urgente': colors.HexColor('#ef4444')
        }
        for i, label in enumerate(prioridad_labels):
            pie_prioridad.slices[i].fillColor = prioridad_colores.get(label, colors.gray)
        drawing_prioridad.add(pie_prioridad)

    tabla_graficas = Table([
        [Paragraph("Tickets por Motivo", heading_style), Paragraph("Tickets por Departamento", heading_style)],
        [drawing_motivos, drawing_dept],
        [Paragraph("Usuarios con Más Tickets", heading_style), Paragraph("Tickets por Prioridad", heading_style)],
        [drawing_users, drawing_prioridad],
    ], colWidths=[310, 310])

    tabla_graficas.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 2), (-1, 2), 12),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 8),
    ]))

    elements.append(tabla_graficas)

    doc.build(elements)

    pdf_content = buffer.getvalue()
    buffer.close()

    with open(pdf_path, 'wb') as f:
        f.write(pdf_content)

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_pdf_ticket(request, ticket_id):
    if request.user.rol != 'superuser':
        return Response({'error': 'No tienes permisos para generar reportes'},
                        status=status.HTTP_403_FORBIDDEN)

    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)

    pdf_dir = os.path.join(settings.BASE_DIR, 'reportes_pdf', 'tickets')
    os.makedirs(pdf_dir, exist_ok=True)

    filename = f"ticket_{ticket.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(pdf_dir, filename)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=8,
        spaceBefore=12,
        alignment=TA_LEFT
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=6
    )

    logo_path = os.path.join(settings.BASE_DIR, 'ticket_system', 'static', 'ticket_system', 'images', 'logo.png')
    logo_header = LogoHeader(7.5 * inch, 60, logo_path)
    elements.append(logo_header)
    elements.append(Spacer(1, 0.15 * inch))

    title = Paragraph(f"{ticket.asunto}", title_style)
    elements.append(title)

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6b7280')
    )
    subtitle = Paragraph(
        f"Generado el {timezone.now().strftime('%d/%m/%Y a las %H:%M')}",
        subtitle_style
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3 * inch))

    info_data = [
        ['Campo', 'Información'],
        ['Asunto', ticket.asunto],
        ['Estado', ticket.get_estado_display()],
        ['Prioridad', ticket.get_prioridad_display()],
        ['Creado por', f"{ticket.usuario.first_name} {ticket.usuario.last_name}" if ticket.usuario.first_name else ticket.usuario.username],
        ['Departamento', ticket.usuario.departamento.nombre if ticket.usuario.departamento else 'N/A'],
        ['Motivo', ticket.motivo.nombre if ticket.motivo else 'N/A'],
        ['Fecha de creación', ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')],
    ]

    if ticket.fecha_cierre:
        info_data.append(['Fecha de cierre', ticket.fecha_cierre.strftime('%d/%m/%Y %H:%M')])

    info_table = Table(info_data, colWidths=[2 * inch, 5 * inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f3f4f6')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Descripción del Ticket", heading_style))
    elements.append(Spacer(1, 0.1 * inch))

    content_style = ParagraphStyle(
        'ContentText',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=6,
        leading=14
    )

    content_text = ticket.contenido.replace('\n', '<br/>')
    content_paragraph = Paragraph(content_text, content_style)

    content_frame_data = [[content_paragraph]]
    content_table = Table(content_frame_data, colWidths=[7 * inch])
    content_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(content_table)

    doc.build(elements)

    pdf_content = buffer.getvalue()
    buffer.close()

    with open(pdf_path, 'wb') as f:
        f.write(pdf_content)

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response