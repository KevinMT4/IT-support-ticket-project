from django.db import migrations, models


def add_nombre_en(apps, schema_editor):
    Motivo = apps.get_model('ticket_system', 'Motivo')
    # some simple manual translations for the initial seed data
    translation_map = {
        'Internet': 'Internet',
        'Programas': 'Software',
        'Contraseñas': 'Passwords',
        'Equipo': 'Hardware',
        # additional entries can be added later by hand if new motivos are
        # introduced via migrations or the admin UI.
    }
    for motivo in Motivo.objects.all():
        english = translation_map.get(motivo.nombre)
        if english:
            motivo.nombre_en = english
            motivo.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ticket_system', '0007_add_mantenimiento_produccion'),
    ]

    operations = [
        migrations.AddField(
            model_name='motivo',
            name='nombre_en',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.RunPython(add_nombre_en, reverse_code=migrations.RunPython.noop),
    ]
