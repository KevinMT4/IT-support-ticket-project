from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Departamento, Motivo, Ticket


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'gerente', 'email', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'gerente', 'email']
    ordering = ['nombre']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'departamento', 'rol', 'is_active']
    list_filter = ['rol', 'departamento', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('departamento', 'rol')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('departamento', 'rol')}),
    )


@admin.register(Motivo)
class MotivoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'departamento', 'descripcion']
    list_filter = ['departamento']
    search_fields = ['nombre', 'descripcion']
    ordering = ['departamento', 'nombre']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'asunto', 'usuario', 'departamento', 'prioridad', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'prioridad', 'departamento', 'fecha_creacion']
    search_fields = ['asunto', 'contenido', 'usuario__username', 'usuario__email']
    ordering = ['-fecha_creacion']
    readonly_fields = ['fecha_creacion']

    fieldsets = (
        ('Información del Ticket', {
            'fields': ('usuario', 'departamento', 'motivo', 'asunto', 'contenido')
        }),
        ('Estado y Prioridad', {
            'fields': ('estado', 'prioridad')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_cierre')
        }),
    )
