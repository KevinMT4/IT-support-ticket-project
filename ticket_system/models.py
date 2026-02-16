from django.db import models
from django.contrib.auth.models import AbstractUser


class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    gerente = models.CharField(max_length=100)
    email = models.EmailField()
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    usuario = models.OneToOneField(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departamento_asignado'
    )

    class Meta:
        db_table = 'departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('user', 'Usuario'),
        ('admin', 'Administrador'),
        ('superuser', 'Super Usuario'),
    ]

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='user')

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"


class Motivo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='motivos'
    )

    class Meta:
        db_table = 'motivo'
        verbose_name = 'Motivo'
        verbose_name_plural = 'Motivos'

    def __str__(self):
        return self.nombre


class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tickets_creados'
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    motivo = models.ForeignKey(
        Motivo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    asunto = models.CharField(max_length=200)
    contenido = models.TextField()
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ticket'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Ticket #{self.id} - {self.asunto}"
