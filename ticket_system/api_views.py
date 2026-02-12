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

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=4,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=4,
        spaceBefore=4
    )

    fecha_inicio = timezone.now() - timedelta(days=7)
    tickets_semana = Ticket.objects.filter(fecha_creacion__gte=fecha_inicio)
    todos_tickets = Ticket.objects.all()

    logo_path = os.path.join(settings.BASE_DIR, 'ticket_system', 'static', 'ticket_system', 'images', 'logo.png')
    logo_header = LogoHeader(6.5 * inch, 40, logo_path)
    elements.append(logo_header)
    elements.append(Spacer(1, 0.1 * inch))

    title = Paragraph("Reporte Semanal de Tickets", title_style)
    elements.append(title)

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER
    )
    subtitle = Paragraph(
        f"Periodo: {fecha_inicio.strftime('%d/%m/%Y')} - {timezone.now().strftime('%d/%m/%Y')}",
        subtitle_style
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.15 * inch))

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

    drawing_estados = Drawing(240, 140)
    bc_estados = VerticalBarChart()
    bc_estados.x = 20
    bc_estados.y = 20
    bc_estados.height = 90
    bc_estados.width = 200
    bc_estados.data = [semana_data, total_data]
    bc_estados.categoryAxis.categoryNames = estados_labels
    bc_estados.categoryAxis.labels.boxAnchor = 'ne'
    bc_estados.categoryAxis.labels.dx = -2
    bc_estados.categoryAxis.labels.dy = -2
    bc_estados.categoryAxis.labels.angle = 30
    bc_estados.categoryAxis.labels.fontSize = 6
    bc_estados.valueAxis.valueMin = 0
    bc_estados.valueAxis.valueMax = max(max(total_data), 1) * 1.2
    bc_estados.valueAxis.labels.fontSize = 6
    bc_estados.bars[0].fillColor = colors.HexColor('#3b82f6')
    bc_estados.bars[1].fillColor = colors.HexColor('#10b981')
    bc_estados.barWidth = 6
    bc_estados.groupSpacing = 10

    legend_estados = Legend()
    legend_estados.x = 30
    legend_estados.y = 120
    legend_estados.dx = 6
    legend_estados.dy = 6
    legend_estados.fontName = 'Helvetica'
    legend_estados.fontSize = 7
    legend_estados.alignment = 'right'
    legend_estados.columnMaximum = 2
    legend_estados.colorNamePairs = [
        (colors.HexColor('#3b82f6'), 'Semana'),
        (colors.HexColor('#10b981'), 'Total')
    ]
    drawing_estados.add(bc_estados)
    drawing_estados.add(legend_estados)

    drawing_dept = Drawing(240, 140)
    if dept_stats:
        bc_dept = HorizontalBarChart()
        bc_dept.x = 80
        bc_dept.y = 15
        bc_dept.height = 100
        bc_dept.width = 150
        dept_names = [stat['usuario__departamento__nombre'] or 'Sin dept.' for stat in dept_stats]
        dept_values = [[stat['total'] for stat in dept_stats]]
        bc_dept.data = dept_values
        bc_dept.categoryAxis.categoryNames = dept_names
        bc_dept.categoryAxis.labels.fontSize = 6
        bc_dept.valueAxis.valueMin = 0
        bc_dept.valueAxis.valueMax = max(dept_values[0]) * 1.2
        bc_dept.valueAxis.labels.fontSize = 6
        bc_dept.bars[0].fillColor = colors.HexColor('#3b82f6')
        bc_dept.barWidth = 10
        drawing_dept.add(bc_dept)

    drawing_users = Drawing(240, 140)
    if user_stats:
        bc_users = HorizontalBarChart()
        bc_users.x = 80
        bc_users.y = 15
        bc_users.height = 100
        bc_users.width = 150
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
        bc_users.categoryAxis.labels.fontSize = 6
        bc_users.valueAxis.valueMin = 0
        bc_users.valueAxis.valueMax = max(user_values[0]) * 1.2
        bc_users.valueAxis.labels.fontSize = 6
        bc_users.bars[0].fillColor = colors.HexColor('#10b981')
        bc_users.barWidth = 10
        drawing_users.add(bc_users)

    drawing_motivos = Drawing(240, 140)
    if motivo_stats.count() > 0:
        pie_motivo = Pie()
        pie_motivo.x = 60
        pie_motivo.y = 20
        pie_motivo.width = 90
        pie_motivo.height = 90
        motivo_labels = [stat['motivo__nombre'] for stat in motivo_stats]
        motivo_values = [stat['total'] for stat in motivo_stats]
        pie_motivo.data = motivo_values
        pie_motivo.labels = [f"{label[:10]}..." if len(label) > 10 else label for label in motivo_labels]
        pie_motivo.slices.strokeWidth = 0.5
        pie_motivo.slices.fontSize = 6
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

    drawing_prioridad = Drawing(240, 140)
    if prioridad_stats.count() > 0:
        pie_prioridad = Pie()
        pie_prioridad.x = 60
        pie_prioridad.y = 20
        pie_prioridad.width = 90
        pie_prioridad.height = 90
        prioridad_labels = [prioridad_nombres.get(stat['prioridad'], stat['prioridad']) for stat in prioridad_stats]
        prioridad_values = [stat['total'] for stat in prioridad_stats]
        pie_prioridad.data = prioridad_values
        pie_prioridad.labels = prioridad_labels
        pie_prioridad.slices.strokeWidth = 0.5
        pie_prioridad.slices.fontSize = 7
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
        [Paragraph("Resumen por Estado", heading_style), Paragraph("Tickets por Departamento", heading_style)],
        [drawing_estados, drawing_dept],
        [Spacer(1, 0.1 * inch), Spacer(1, 0.1 * inch)],
        [Paragraph("Usuarios con Más Tickets", heading_style), Paragraph("Tickets por Prioridad", heading_style)],
        [drawing_users, drawing_prioridad],
        [Spacer(1, 0.1 * inch), Spacer(1, 0.1 * inch)],
        [Paragraph("Tickets por Motivo", heading_style), ''],
        [drawing_motivos, ''],
    ], colWidths=[280, 280])

    tabla_graficas.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    elements.append(tabla_graficas)

    doc.build(elements)
    return response
