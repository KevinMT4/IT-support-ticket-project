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
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from .models import Usuario, Departamento, Motivo, Ticket
from .serializers import (
    UsuarioSerializer,
    UsuarioRegistroSerializer,
    DepartamentoSerializer,
    MotivoSerializer,
    TicketSerializer,
    TicketCreateSerializer
)


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
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=20
    )

    fecha_inicio = timezone.now() - timedelta(days=7)
    tickets_semana = Ticket.objects.filter(fecha_creacion__gte=fecha_inicio)
    todos_tickets = Ticket.objects.all()

    title = Paragraph("Reporte Semanal de Tickets", title_style)
    elements.append(title)

    subtitle = Paragraph(
        f"Periodo: {fecha_inicio.strftime('%d/%m/%Y')} - {timezone.now().strftime('%d/%m/%Y')}",
        styles['Normal']
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Resumen General", heading_style))
    resumen_data = [
        ['Métrica', 'Esta Semana', 'Total'],
        ['Total de Tickets', str(tickets_semana.count()), str(todos_tickets.count())],
        ['Abiertos', str(tickets_semana.filter(estado='abierto').count()), str(todos_tickets.filter(estado='abierto').count())],
        ['En Proceso', str(tickets_semana.filter(estado='en_proceso').count()), str(todos_tickets.filter(estado='en_proceso').count())],
        ['Resueltos', str(tickets_semana.filter(estado='resuelto').count()), str(todos_tickets.filter(estado='resuelto').count())],
        ['Cerrados', str(tickets_semana.filter(estado='cerrado').count()), str(todos_tickets.filter(estado='cerrado').count())],
    ]

    resumen_table = Table(resumen_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Tickets por Departamento", heading_style))
    dept_stats = todos_tickets.values('usuario__departamento__nombre').annotate(
        total=Count('id')
    ).order_by('-total')

    dept_data = [['Departamento', 'Total de Tickets']]
    for stat in dept_stats:
        dept_name = stat['usuario__departamento__nombre'] or 'Sin departamento'
        dept_data.append([dept_name, str(stat['total'])])

    dept_table = Table(dept_data, colWidths=[4 * inch, 2 * inch])
    dept_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(dept_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Top 10 Usuarios con Más Tickets", heading_style))
    user_stats = todos_tickets.values('usuario__username', 'usuario__first_name', 'usuario__last_name').annotate(
        total=Count('id')
    ).order_by('-total')[:10]

    user_data = [['Usuario', 'Total de Tickets']]
    for stat in user_stats:
        nombre_completo = f"{stat['usuario__first_name']} {stat['usuario__last_name']}".strip()
        if not nombre_completo:
            nombre_completo = stat['usuario__username']
        user_data.append([nombre_completo, str(stat['total'])])

    user_table = Table(user_data, colWidths=[4 * inch, 2 * inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(user_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Tickets por Motivo", heading_style))
    motivo_stats = todos_tickets.filter(motivo__isnull=False).values('motivo__nombre').annotate(
        total=Count('id')
    ).order_by('-total')

    motivo_data = [['Motivo', 'Total de Tickets']]
    for stat in motivo_stats:
        motivo_data.append([stat['motivo__nombre'], str(stat['total'])])

    if len(motivo_data) > 1:
        motivo_table = Table(motivo_data, colWidths=[4 * inch, 2 * inch])
        motivo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(motivo_table)
    else:
        elements.append(Paragraph("No hay tickets con motivos especificados", styles['Normal']))

    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Tickets por Prioridad", heading_style))
    prioridad_stats = todos_tickets.values('prioridad').annotate(total=Count('id')).order_by('-total')

    prioridad_nombres = {
        'baja': 'Baja',
        'media': 'Media',
        'alta': 'Alta',
        'urgente': 'Urgente'
    }

    prioridad_data = [['Prioridad', 'Total de Tickets']]
    for stat in prioridad_stats:
        prioridad_data.append([prioridad_nombres.get(stat['prioridad'], stat['prioridad']), str(stat['total'])])

    prioridad_table = Table(prioridad_data, colWidths=[4 * inch, 2 * inch])
    prioridad_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(prioridad_table)

    doc.build(elements)
    return response
