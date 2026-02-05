from rest_framework import serializers
from .models import Usuario, Departamento, Motivo, Ticket


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'gerente', 'email', 'descripcion', 'activo']


class UsuarioSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'departamento', 'departamento_nombre', 'rol']
        read_only_fields = ['id']


class MotivoSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)

    class Meta:
        model = Motivo
        fields = ['id', 'nombre', 'descripcion', 'departamento', 'departamento_nombre']

class TicketSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    motivo_nombre = serializers.CharField(source='motivo.nombre', read_only=True, allow_null=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'usuario', 'usuario_nombre', 'departamento', 'departamento_nombre',
                  'motivo', 'motivo_nombre', 'asunto', 'contenido', 'prioridad',
                  'prioridad_display', 'estado', 'estado_display', 'fecha_creacion',
                  'fecha_cierre']
        read_only_fields = ['id', 'fecha_creacion', 'usuario']

    def get_usuario_nombre(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}" if obj.usuario.first_name else obj.usuario.username

class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['departamento', 'motivo', 'asunto', 'contenido', 'prioridad']