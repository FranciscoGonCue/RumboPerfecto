from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0002_alter_itemplan_tipo_delete_tiposervicio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemplan',
            name='api_provider_id',
        ),
        migrations.RemoveField(
            model_name='itemplan',
            name='datos_json',
        ),
    ]
