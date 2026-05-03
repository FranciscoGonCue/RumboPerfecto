from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="actividad",
            field=models.JSONField(blank=True, default=list, help_text="Lista de servicios de actividad"),
        ),
        migrations.AddField(
            model_name="customuser",
            name="alojamiento",
            field=models.JSONField(blank=True, default=list, help_text="Lista de servicios de alojamiento"),
        ),
        migrations.AddField(
            model_name="customuser",
            name="restaurante",
            field=models.JSONField(blank=True, default=list, help_text="Lista de servicios de restaurante"),
        ),
    ]
