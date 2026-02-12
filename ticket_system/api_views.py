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
        serializer.save(usuario=self.request.user)

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

        ticket.estado = nuevo_estado
        if nuevo_estado == 'cerrado':
            ticket.fecha_cierre = timezone.now()
        ticket.save()

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

        ticket.prioridad = nueva_prioridad
        ticket.save()

        return Response(TicketSerializer(ticket).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_pdf_estadisticas(request):
    if request.user.rol != 'superuser':
        return Response({'error': 'No tienes permisos para generar reportes'},
                        status=status.HTTP_403_FORBIDDEN)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_tickets_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        spaceBefore=12
    )

    fecha_inicio = timezone.now() - timedelta(days=7)
    tickets_semana = Ticket.objects.filter(fecha_creacion__gte=fecha_inicio)
    todos_tickets = Ticket.objects.all()

    logo_path = os.path.join(settings.BASE_DIR, 'ticket_system', 'static', 'ticket_system', 'images', 'logo.png')
    logo_header = LogoHeader(6.5 * inch, 80, logo_path)
    elements.append(logo_header)
    elements.append(Spacer(1, 0.15 * inch))

    title = Paragraph("Reporte Semanal de Tickets", title_style)
    elements.append(title)

    subtitle = Paragraph(
        f"Periodo: {fecha_inicio.strftime('%d/%m/%Y')} - {timezone.now().strftime('%d/%m/%Y')}",
        styles['Normal']
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Resumen General por Estado", heading_style))

    drawing = Drawing(480, 180)
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 15
    bc.height = 130
    bc.width = 380

    estados_labels = ['Abiertos', 'En Proceso', 'Resueltos', 'Cerrados']
    semana_data = [
        tickets_semana.filter(estado='abierto').count(),
        tickets_semana.filter(estado='en_proceso').count(),
        tickets_semana.filter(estado='resuelto').count(),
        tickets_semana.filter(estado='cerrado').count()
    ]
    total_data = [
        todos_tickets.filter(estado='abierto').count(),
        todos_tickets.filter(estado='en_proceso').count(),
        todos_tickets.filter(estado='resuelto').count(),
        todos_tickets.filter(estado='cerrado').count()
    ]

    bc.data = [semana_data, total_data]
    bc.categoryAxis.categoryNames = estados_labels
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = -2
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.labels.fontSize = 8
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(max(total_data), 1) * 1.2
    bc.valueAxis.labels.fontSize = 8

    bc.bars[0].fillColor = colors.HexColor('#3b82f6')
    bc.bars[1].fillColor = colors.HexColor('#10b981')
    bc.barWidth = 8
    bc.groupSpacing = 15

    legend = Legend()
    legend.x = 50
    legend.y = 155
    legend.dx = 8
    legend.dy = 8
    legend.fontName = 'Helvetica'
    legend.fontSize = 8
    legend.alignment = 'right'
    legend.columnMaximum = 2
    legend.colorNamePairs = [
        (colors.HexColor('#3b82f6'), 'Esta Semana'),
        (colors.HexColor('#10b981'), 'Total')
    ]

    drawing.add(bc)
    drawing.add(legend)
    elements.append(drawing)
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph("Tickets por Departamento", heading_style))
    dept_stats = todos_tickets.values('usuario__departamento__nombre').annotate(
        total=Count('id')
    ).order_by('-total')[:6]

    if dept_stats:
        drawing = Drawing(480, 160)
        bc = HorizontalBarChart()
        bc.x = 130
        bc.y = 15
        bc.height = 130
        bc.width = 300

        dept_names = [stat['usuario__departamento__nombre'] or 'Sin dept.' for stat in dept_stats]
        dept_values = [[stat['total'] for stat in dept_stats]]

        bc.data = dept_values
        bc.categoryAxis.categoryNames = dept_names
        bc.categoryAxis.labels.fontSize = 7
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(dept_values[0]) * 1.2
        bc.valueAxis.labels.fontSize = 7

        bc.bars[0].fillColor = colors.HexColor('#3b82f6')
        bc.barWidth = 15

        drawing.add(bc)
        elements.append(drawing)
    else:
        elements.append(Paragraph("No hay datos de departamentos", styles['Normal']))

    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph("Usuarios con Más Tickets", heading_style))
    user_stats = todos_tickets.values('usuario__username', 'usuario__first_name', 'usuario__last_name').annotate(
        total=Count('id')
    ).order_by('-total')[:6]

    if user_stats:
        drawing = Drawing(480, 160)
        bc = HorizontalBarChart()
        bc.x = 110
        bc.y = 15
        bc.height = 130
        bc.width = 320

        user_names = []
        for stat in user_stats:
            nombre = f"{stat['usuario__first_name']} {stat['usuario__last_name']}".strip()
            if not nombre:
                nombre = stat['usuario__username']
            if len(nombre) > 20:
                nombre = nombre[:17] + '...'
            user_names.append(nombre)

        user_values = [[stat['total'] for stat in user_stats]]

        bc.data = user_values
        bc.categoryAxis.categoryNames = user_names
        bc.categoryAxis.labels.fontSize = 7
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(user_values[0]) * 1.2
        bc.valueAxis.labels.fontSize = 7

        bc.bars[0].fillColor = colors.HexColor('#10b981')
        bc.barWidth = 15

        drawing.add(bc)
        elements.append(drawing)
    else:
        elements.append(Paragraph("No hay datos de usuarios", styles['Normal']))

    elements.append(Spacer(1, 0.3 * inch))

    heading_motivo = Paragraph("Tickets por Motivo", heading_style)
    heading_prioridad = Paragraph("Tickets por Prioridad", heading_style)

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

    drawing_motivo = None
    drawing_prioridad = None

    if motivo_stats.count() > 0:
        drawing_motivo = Drawing(240, 180)
        pie = Pie()
        pie.x = 40
        pie.y = 15
        pie.width = 140
        pie.height = 140

        motivo_labels = [stat['motivo__nombre'] for stat in motivo_stats]
        motivo_values = [stat['total'] for stat in motivo_stats]

        pie.data = motivo_values
        pie.labels = [f"{label}\n({value})" for label, value in zip(motivo_labels, motivo_values)]
        pie.slices.strokeWidth = 0.5
        pie.slices.fontsize = 7

        colores = [
            colors.HexColor('#3b82f6'),
            colors.HexColor('#10b981'),
            colors.HexColor('#f59e0b'),
            colors.HexColor('#ef4444'),
            colors.HexColor('#8b5cf6'),
            colors.HexColor('#ec4899'),
        ]
        for i in range(len(motivo_values)):
            pie.slices[i].fillColor = colores[i % len(colores)]

        drawing_motivo.add(pie)

    if prioridad_stats.count() > 0:
        drawing_prioridad = Drawing(240, 180)
        pie = Pie()
        pie.x = 40
        pie.y = 15
        pie.width = 140
        pie.height = 140

        prioridad_labels = [prioridad_nombres.get(stat['prioridad'], stat['prioridad']) for stat in prioridad_stats]
        prioridad_values = [stat['total'] for stat in prioridad_stats]

        pie.data = prioridad_values
        pie.labels = [f"{label}\n({value})" for label, value in zip(prioridad_labels, prioridad_values)]
        pie.slices.strokeWidth = 0.5
        pie.slices.fontsize = 7

        prioridad_colores = {
            'Baja': colors.HexColor('#3b82f6'),
            'Media': colors.HexColor('#f59e0b'),
            'Alta': colors.HexColor('#fb923c'),
            'Urgente': colors.HexColor('#ef4444')
        }
        for i, label in enumerate(prioridad_labels):
            pie.slices[i].fillColor = prioridad_colores.get(label, colors.gray)

        drawing_prioridad.add(pie)

    if drawing_motivo and drawing_prioridad:
        data = [
            [heading_motivo, heading_prioridad],
            [drawing_motivo, drawing_prioridad]
        ]
        table = Table(data, colWidths=[240, 240])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(table)
    elif drawing_motivo:
        elements.append(heading_motivo)
        elements.append(drawing_motivo)
    elif drawing_prioridad:
        elements.append(heading_prioridad)
        elements.append(drawing_prioridad)
    else:
        elements.append(Paragraph("No hay datos de motivos ni prioridades", styles['Normal']))

    doc.build(elements)
    return response
