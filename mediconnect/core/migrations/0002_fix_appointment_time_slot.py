from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='time_slot',
            field=models.CharField(
                max_length=20,
                null=True,
                blank=True,
                default='',
            ),
        ),
    ]