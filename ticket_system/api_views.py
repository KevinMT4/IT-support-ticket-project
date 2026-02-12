from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
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
