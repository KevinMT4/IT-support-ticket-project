from django.db import migrations


def create_departments(apps, schema_editor):
    Departamento = apps.get_model('ticket_system', 'Departamento')

    departments = [
        {
            'nombre': 'Calidad',
            'gerente': 'Gerente de Calidad',
            'email': 'calidad@cofat.com',
            'descripcion': 'Departamento de Control de Calidad',
            'activo': True
        },
        {
            'nombre': 'Finanzas',
            'gerente': 'Gerente de Finanzas',
            'email': 'finanzas@cofat.com',
            'descripcion': 'Departamento de Finanzas',
            'activo': True
        },
        {
            'nombre': 'Compras',
            'gerente': 'Gerente de Compras',
            'email': 'compras@cofat.com',
            'descripcion': 'Departamento de Compras',
            'activo': True
        },
        {
            'nombre': 'Ventas',
            'gerente': 'Gerente de Ventas',
            'email': 'ventas@cofat.com',
            'descripcion': 'Departamento de Ventas',
            'activo': True
        },
        {
            'nombre': 'Ingenieria',
            'gerente': 'Gerente de Ingenieria',
            'email': 'ingenieria@cofat.com',
            'descripcion': 'Departamento de Ingenieria',
            'activo': True
        },
        {
            'nombre': 'Logistica',
            'gerente': 'Gerente de Logistica',
            'email': 'logistica@cofat.com',
            'descripcion': 'Departamento de Logistica',
            'activo': True
        },
        {
            'nombre': 'Recursos Humanos',
            'gerente': 'Gerente de Recursos Humanos',
            'email': 'rrhh@cofat.com',
            'descripcion': 'Departamento de Recursos Humanos',
            'activo': True
        },
        {
            'nombre': 'Tecnologias de la Informacion',
            'gerente': 'Gerente de TI',
            'email': 'ti@cofat.com',
            'descripcion': 'Departamento de Tecnologias de la Informacion',
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
        ('ticket_system', '0002_departamento_usuario'),
    ]

    operations = [
        migrations.RunPython(create_departments),
    ]
