from django.db import migrations


def create_new_departments(apps, schema_editor):
    Departamento = apps.get_model('ticket_system', 'Departamento')

    departments = [
        {
            'nombre': 'Mantenimiento',
            'gerente': 'Gerente de Mantenimiento',
            'email': 'mantenimiento@empresa.com',
            'descripcion': 'Departamento de Mantenimiento',
            'activo': True
        },
        {
            'nombre': 'Produccion',
            'gerente': 'Gerente de Produccion',
            'email': 'produccion@empresa.com',
            'descripcion': 'Departamento de Produccion',
            'activo': True
        },
    ]

    for dept_data in departments:
        Departamento.objects.get_or_create(
            nombre=dept_data['nombre'],
            defaults=dept_data
        )


class Migration(migrations.Migration):

    dependencies = [
        ('ticket_system', '0006_ticket_solucion_imagenes_ticket_solucion_texto'),
    ]

    operations = [
        migrations.RunPython(create_new_departments),
    ]
