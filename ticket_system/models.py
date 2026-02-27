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
    # field added to hold the English translation of the reason; most
    # existing records will be populated via a data migration.
    nombre_en = models.CharField(max_length=100, blank=True, null=True)
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

    def get_nombre_por_idioma(self):
        """Return the name appropriate for the current language.

        We rely on Django's translation utilities which are driven by the
        middleware (Accept-Language header, session, etc.). When the active
        language begins with ``en`` and ``nombre_en`` is populated we return
        the English version, otherwise fall back to the original Spanish
        ``nombre``.
        """
        from django.utils import translation

        lang = translation.get_language() or ''
        if lang.startswith('en') and self.nombre_en:
            return self.nombre_en
        return self.nombre

    def __str__(self):
        # show translated name in the admin shell/representations so that
        # people immediately see the name that corresponds to the active
        # language.
        return self.get_nombre_por_idioma()


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
    solucion_texto = models.TextField(blank=True, null=True)
    solucion_imagenes = models.JSONField(blank=True, null=True)  # Lista de URLs de imágenes

    class Meta:
        db_table = 'ticket'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Ticket #{self.id} - {self.asunto}"
