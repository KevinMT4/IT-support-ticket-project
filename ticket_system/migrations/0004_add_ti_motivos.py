from django.db import migrations


def create_ti_motivos(apps, schema_editor):
    Departamento = apps.get_model('ticket_system', 'Departamento')
    Motivo = apps.get_model('ticket_system', 'Motivo')

    ti_dept = Departamento.objects.filter(
        nombre='Tecnologias de la Informacion'
    ).first()

    if not ti_dept:
        return

    motivos = [
        {'nombre': 'Internet', 'descripcion': 'Problemas con conexión a internet'},
        {'nombre': 'Programas', 'descripcion': 'Problemas con instalación o uso de programas'},
        {'nombre': 'Contraseñas', 'descripcion': 'Cambio o recuperación de contraseñas'},
        {'nombre': 'Equipo', 'descripcion': 'Problemas con hardware o equipo de cómputo'},
    ]

    for motivo_data in motivos:
        Motivo.objects.get_or_create(
            nombre=motivo_data['nombre'],
            departamento=ti_dept,
            defaults=motivo_data
        )


class Migration(migrations.Migration):

    dependencies = [
        ('ticket_system', '0003_populate_departments'),
    ]

    operations = [
        migrations.RunPython(create_ti_motivos),
    ]
