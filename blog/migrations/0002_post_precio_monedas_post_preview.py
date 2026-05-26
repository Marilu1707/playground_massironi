import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='precio_monedas',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Precio en monedas (0 = gratis)'),
        ),
        migrations.AddField(
            model_name='post',
            name='preview',
            field=models.TextField(blank=True, verbose_name='Preview público'),
        ),
    ]
