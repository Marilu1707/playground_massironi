from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog', '0002_post_precio_monedas_post_preview'),
        ('inventario', '0002_queso_precio_monedas'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('COMPRA_QUESO', 'Compra de queso'), ('COMPRA_RECETA', 'Compra de receta'), ('VENTA_RECETA', 'Venta de receta'), ('CANJE_PUNTOS', 'Canje de puntos')], max_length=20)),
                ('monto', models.IntegerField()),
                ('descripcion', models.CharField(max_length=255)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('referencia_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transacciones', to='blog.post')),
                ('referencia_queso', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transacciones', to='inventario.queso')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacciones', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transacción',
                'verbose_name_plural': 'Transacciones',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='CompraReceta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto_pagado', models.IntegerField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('comprador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recetas_compradas', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compras', to='blog.post')),
            ],
            options={
                'verbose_name': 'Compra de receta',
                'verbose_name_plural': 'Compras de recetas',
                'ordering': ['-fecha'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='comprareceta',
            unique_together={('comprador', 'post')},
        ),
    ]
