from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_customuser_service_lists'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='alojamiento',
            new_name='alojamientos',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='actividad',
            new_name='actividades',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='restaurante',
            new_name='restaurantes',
        ),
    ]
