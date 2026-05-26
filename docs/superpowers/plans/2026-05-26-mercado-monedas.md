# Mercado y Monedas — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar sistema de economía interna con monedas: compra de quesos del admin, compra/venta de recetas entre usuarios, canje de puntos y manual de convivencia en el home.

**Architecture:** Nueva app `mercado` con modelos `Transaccion` y `CompraReceta`. Cambios menores en `blog` (campo `precio_monedas` + `preview` en Post) e `inventario` (campo `precio_monedas` en Queso). Todas las operaciones de monedas usan `transaction.atomic()` + `select_for_update()`.

**Tech Stack:** Django 6, PostgreSQL (Neon), django.db.transaction, function-based views con @login_required

---

## Mapa de archivos

### Crear
- `mercado/__init__.py`
- `mercado/apps.py`
- `mercado/models.py` — Transaccion, CompraReceta
- `mercado/views.py` — mercado_home, comprar_queso, comprar_receta, historial, canjear_puntos
- `mercado/urls.py`
- `mercado/forms.py` — FormularioCanje
- `mercado/admin.py`
- `mercado/templates/mercado/mercado_home.html`
- `mercado/templates/mercado/historial.html`

### Modificar
- `blog/models.py` — precio_monedas, preview en Post
- `blog/forms.py` — agregar precio_monedas
- `blog/views.py` — post_detail con lógica unlock
- `blog/templates/blog/post_detail.html` — preview + botón compra
- `inventario/models.py` — precio_monedas en Queso
- `inventario/templates/inventario/inventario_list.html` — botón comprar
- `core/templates/core/home.html` — sección manual de convivencia
- `nido_mozzarella/settings.py` — agregar 'mercado'
- `nido_mozzarella/urls.py` — include mercado.urls
- `README.md` — link de producción

---

## Task 1: App mercado — estructura base

**Files:**
- Create: `mercado/__init__.py`
- Create: `mercado/apps.py`
- Create: `mercado/models.py`
- Create: `mercado/admin.py`

- [ ] **Step 1: Crear la app**

```bash
cd /ruta/al/proyecto
python manage.py startapp mercado
```

- [ ] **Step 2: Reemplazar `mercado/apps.py`**

```python
from django.apps import AppConfig


class MercadoConfig(AppConfig):
    name = 'mercado'
    verbose_name = 'Mercado'
```

- [ ] **Step 3: Escribir `mercado/models.py`**

```python
from django.db import models
from django.contrib.auth.models import User
from blog.models import Post
from inventario.models import Queso


class Transaccion(models.Model):
    COMPRA_QUESO = 'COMPRA_QUESO'
    COMPRA_RECETA = 'COMPRA_RECETA'
    VENTA_RECETA = 'VENTA_RECETA'
    CANJE_PUNTOS = 'CANJE_PUNTOS'

    TIPO_CHOICES = [
        (COMPRA_QUESO, 'Compra de queso'),
        (COMPRA_RECETA, 'Compra de receta'),
        (VENTA_RECETA, 'Venta de receta'),
        (CANJE_PUNTOS, 'Canje de puntos'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.IntegerField()  # positivo = ganó, negativo = gastó
    descripcion = models.CharField(max_length=255)
    referencia_queso = models.ForeignKey(
        Queso, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones'
    )
    referencia_post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'

    def __str__(self):
        return f"{self.usuario.username} — {self.get_tipo_display()} ({self.monto:+d})"


class CompraReceta(models.Model):
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recetas_compradas')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='compras')
    monto_pagado = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comprador', 'post')
        ordering = ['-fecha']
        verbose_name = 'Compra de receta'
        verbose_name_plural = 'Compras de recetas'

    def __str__(self):
        return f"{self.comprador.username} desbloqueó '{self.post.titulo}'"
```

- [ ] **Step 4: Escribir `mercado/admin.py`**

```python
from django.contrib import admin
from .models import Transaccion, CompraReceta


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'monto', 'descripcion', 'fecha')
    list_filter = ('tipo',)
    readonly_fields = ('fecha',)


@admin.register(CompraReceta)
class CompraRecetaAdmin(admin.ModelAdmin):
    list_display = ('comprador', 'post', 'monto_pagado', 'fecha')
    readonly_fields = ('fecha',)
```

- [ ] **Step 5: Commit**

```bash
git add mercado/
git commit -m "feat: app mercado — modelos Transaccion y CompraReceta"
```

---

## Task 2: Modificar modelos existentes (Post + Queso)

**Files:**
- Modify: `blog/models.py`
- Modify: `inventario/models.py`

- [ ] **Step 1: Agregar campos a `blog/models.py`**

Reemplazar la clase `Post` completa:

```python
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """Publicación del blog — recetas, lore y novedades del nido."""
    titulo = models.CharField(max_length=255)
    subtitulo = models.CharField(max_length=255, blank=True)
    cuerpo = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    imagen = models.ImageField(upload_to='posts/', null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    precio_monedas = models.IntegerField(
        default=0,
        verbose_name='Precio en monedas (0 = gratis)'
    )
    preview = models.TextField(blank=True, verbose_name='Preview público')

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        """Genera preview automático con los primeros 200 chars del cuerpo."""
        if self.precio_monedas > 0 and self.cuerpo:
            self.preview = self.cuerpo[:200]
        else:
            self.preview = ''
        super().save(*args, **kwargs)

    @property
    def es_premium(self):
        return self.precio_monedas > 0
```

- [ ] **Step 2: Agregar `precio_monedas` a `inventario/models.py`**

Agregar el campo dentro de `Queso`, después de `precio`:

```python
precio_monedas = models.IntegerField(default=10, verbose_name='Precio en monedas 🪙')
```

El modelo `Queso` completo queda:

```python
from django.db import models


class Queso(models.Model):
    """Producto del inventario del Nido Mozzarella."""
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    stock = models.IntegerField(default=0, verbose_name='Stock disponible')
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Precio ($)')
    precio_monedas = models.IntegerField(default=10, verbose_name='Precio en monedas 🪙')
    imagen = models.ImageField(upload_to='inventario/', null=True, blank=True)

    class Meta:
        verbose_name = 'Queso'
        verbose_name_plural = 'Quesos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def estado_stock(self):
        if self.stock >= 10:
            return 'green'
        elif self.stock >= 3:
            return 'orange'
        return 'red'

    def etiqueta_stock(self):
        if self.stock >= 10:
            return 'Disponible'
        elif self.stock >= 3:
            return 'Poco stock'
        return 'Sin stock'
```

- [ ] **Step 3: Commit**

```bash
git add blog/models.py inventario/models.py
git commit -m "feat: agregar precio_monedas y preview a Post y Queso"
```

---

## Task 3: Settings, URLs principales y migraciones

**Files:**
- Modify: `nido_mozzarella/settings.py`
- Modify: `nido_mozzarella/urls.py`
- Create: migrations (auto-generado)

- [ ] **Step 1: Agregar 'mercado' a INSTALLED_APPS en `settings.py`**

Localizar `INSTALLED_APPS` y agregar `'mercado'` al final de la lista:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'accounts',
    'blog',
    'inventario',
    'juego',
    'mercado',
]
```

- [ ] **Step 2: Agregar URLs de mercado en `nido_mozzarella/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('pages/', include('blog.urls')),
    path('inventario/', include('inventario.urls')),
    path('juego/', include('juego.urls')),
    path('mercado/', include('mercado.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 3: Generar y aplicar migraciones**

```bash
python manage.py makemigrations mercado
python manage.py makemigrations blog
python manage.py makemigrations inventario
python manage.py migrate
```

Expected output: sin errores, nuevas tablas creadas.

- [ ] **Step 4: Commit**

```bash
git add nido_mozzarella/settings.py nido_mozzarella/urls.py mercado/migrations/ blog/migrations/ inventario/migrations/
git commit -m "feat: registrar app mercado, URLs y migraciones"
```

---

## Task 4: Vistas y URLs del mercado

**Files:**
- Create: `mercado/views.py`
- Create: `mercado/urls.py`
- Create: `mercado/forms.py`

- [ ] **Step 1: Escribir `mercado/forms.py`**

```python
from django import forms


class FormularioCanje(forms.Form):
    """Confirmación del canje de puntos por monedas."""
    confirmar = forms.BooleanField(
        required=True,
        label='Confirmo el canje de todos mis puntos disponibles (10 puntos = 5 monedas)',
    )
```

- [ ] **Step 2: Escribir `mercado/views.py`**

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction

from blog.models import Post
from inventario.models import Queso
from juego.models import Pedido
from accounts.models import PerfilUsuario
from .models import Transaccion, CompraReceta
from .forms import FormularioCanje

RATIO_PUNTOS = 10   # puntos necesarios por lote
RATIO_MONEDAS = 5   # monedas ganadas por lote


def mercado_home(request):
    """Listado público del mercado: quesos con stock y recetas premium."""
    quesos = Queso.objects.filter(stock__gt=0, precio_monedas__gt=0)
    recetas_premium = Post.objects.filter(precio_monedas__gt=0).select_related('autor')

    compras_usuario = set()
    if request.user.is_authenticated:
        compras_usuario = set(
            CompraReceta.objects.filter(comprador=request.user)
            .values_list('post_id', flat=True)
        )

    return render(request, 'mercado/mercado_home.html', {
        'quesos': quesos,
        'recetas_premium': recetas_premium,
        'compras_usuario': compras_usuario,
    })


@login_required
@require_POST
def comprar_queso(request, pk):
    """Compra un queso del inventario usando monedas."""
    queso = get_object_or_404(Queso, pk=pk)
    perfil = request.user.perfil

    if queso.stock <= 0:
        messages.error(request, 'No hay stock disponible.')
        return redirect('mercado_home')

    if perfil.monedas < queso.precio_monedas:
        messages.error(request, f'No tenés suficientes monedas. Necesitás {queso.precio_monedas} 🪙')
        return redirect('mercado_home')

    try:
        with transaction.atomic():
            perfil_lock = PerfilUsuario.objects.select_for_update().get(user=request.user)
            queso_lock = Queso.objects.select_for_update().get(pk=pk)

            if queso_lock.stock <= 0:
                messages.error(request, 'El queso se agotó justo ahora.')
                return redirect('mercado_home')
            if perfil_lock.monedas < queso_lock.precio_monedas:
                messages.error(request, 'Monedas insuficientes.')
                return redirect('mercado_home')

            perfil_lock.monedas -= queso_lock.precio_monedas
            queso_lock.stock -= 1
            queso_lock.save()

            pedido = Pedido.objects.create(
                usuario=request.user,
                queso=queso_lock,
                cantidad=1,
                completado=True,
                puntos_ganados=5,
            )
            perfil_lock.puntos += pedido.puntos_ganados
            perfil_lock.actualizar_nivel()  # llama a save() internamente

            Transaccion.objects.create(
                usuario=request.user,
                tipo=Transaccion.COMPRA_QUESO,
                monto=-queso_lock.precio_monedas,
                descripcion=f'Compra de {queso_lock.nombre}',
                referencia_queso=queso_lock,
            )
    except Exception:
        messages.error(request, 'Ocurrió un error al procesar la compra.')
        return redirect('mercado_home')

    messages.success(request, f'¡Compraste {queso.nombre} por {queso.precio_monedas} monedas! 🧀')
    return redirect('mercado_home')


@login_required
@require_POST
def comprar_receta(request, pk):
    """Desbloquea una receta premium pagando monedas al autor."""
    post = get_object_or_404(Post, pk=pk, precio_monedas__gt=0)

    if post.autor == request.user or request.user.is_staff:
        messages.info(request, 'Ya tenés acceso completo a esta receta.')
        return redirect('post_detail', pageId=post.pk)

    if CompraReceta.objects.filter(comprador=request.user, post=post).exists():
        messages.info(request, 'Ya desbloqueaste esta receta.')
        return redirect('post_detail', pageId=post.pk)

    perfil = request.user.perfil
    if perfil.monedas < post.precio_monedas:
        messages.error(request, f'No tenés suficientes monedas. Necesitás {post.precio_monedas} 🪙')
        return redirect('post_detail', pageId=post.pk)

    try:
        with transaction.atomic():
            comprador_perfil = PerfilUsuario.objects.select_for_update().get(user=request.user)
            autor_perfil = PerfilUsuario.objects.select_for_update().get(user=post.autor)

            if comprador_perfil.monedas < post.precio_monedas:
                messages.error(request, 'Monedas insuficientes.')
                return redirect('post_detail', pageId=post.pk)

            comprador_perfil.monedas -= post.precio_monedas
            autor_perfil.monedas += post.precio_monedas
            comprador_perfil.save()
            autor_perfil.save()

            CompraReceta.objects.create(
                comprador=request.user,
                post=post,
                monto_pagado=post.precio_monedas,
            )

            Transaccion.objects.create(
                usuario=request.user,
                tipo=Transaccion.COMPRA_RECETA,
                monto=-post.precio_monedas,
                descripcion=f'Desbloqueó receta: {post.titulo}',
                referencia_post=post,
            )
            Transaccion.objects.create(
                usuario=post.autor,
                tipo=Transaccion.VENTA_RECETA,
                monto=post.precio_monedas,
                descripcion=f'Venta de receta: {post.titulo}',
                referencia_post=post,
            )
    except Exception:
        messages.error(request, 'Ocurrió un error al procesar la compra.')
        return redirect('post_detail', pageId=post.pk)

    messages.success(request, f'¡Receta desbloqueada por {post.precio_monedas} monedas! 📖')
    return redirect('post_detail', pageId=post.pk)


@login_required
def historial(request):
    """Muestra todas las transacciones del usuario y el formulario de canje."""
    transacciones = Transaccion.objects.filter(usuario=request.user)
    form_canje = FormularioCanje()
    return render(request, 'mercado/historial.html', {
        'transacciones': transacciones,
        'form_canje': form_canje,
        'ratio_puntos': RATIO_PUNTOS,
        'ratio_monedas': RATIO_MONEDAS,
    })


@login_required
@require_POST
def canjear_puntos(request):
    """Convierte todos los puntos disponibles en monedas (10 pts = 5 monedas)."""
    perfil = request.user.perfil

    if perfil.puntos < RATIO_PUNTOS:
        messages.error(request, f'Necesitás al menos {RATIO_PUNTOS} puntos para canjear.')
        return redirect('historial')

    form = FormularioCanje(request.POST)
    if not form.is_valid():
        messages.error(request, 'Confirmá el canje antes de continuar.')
        return redirect('historial')

    try:
        with transaction.atomic():
            perfil_lock = PerfilUsuario.objects.select_for_update().get(user=request.user)
            lotes = perfil_lock.puntos // RATIO_PUNTOS
            puntos_a_gastar = lotes * RATIO_PUNTOS
            monedas_ganadas = lotes * RATIO_MONEDAS

            perfil_lock.puntos -= puntos_a_gastar
            perfil_lock.monedas += monedas_ganadas
            perfil_lock.save()

            Transaccion.objects.create(
                usuario=request.user,
                tipo=Transaccion.CANJE_PUNTOS,
                monto=monedas_ganadas,
                descripcion=f'Canjeó {puntos_a_gastar} puntos por {monedas_ganadas} monedas',
            )
    except Exception:
        messages.error(request, 'Error al procesar el canje.')
        return redirect('historial')

    messages.success(request, f'¡Canjeaste {puntos_a_gastar} puntos por {monedas_ganadas} monedas! 🪙')
    return redirect('historial')
```

- [ ] **Step 3: Escribir `mercado/urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.mercado_home, name='mercado_home'),
    path('comprar/queso/<int:pk>/', views.comprar_queso, name='comprar_queso'),
    path('comprar/receta/<int:pk>/', views.comprar_receta, name='comprar_receta'),
    path('historial/', views.historial, name='historial'),
    path('canjear/', views.canjear_puntos, name='canjear_puntos'),
]
```

- [ ] **Step 4: Commit**

```bash
git add mercado/views.py mercado/urls.py mercado/forms.py
git commit -m "feat: vistas y URLs del mercado"
```

---

## Task 5: Templates del mercado

**Files:**
- Create: `mercado/templates/mercado/mercado_home.html`
- Create: `mercado/templates/mercado/historial.html`

- [ ] **Step 1: Crear directorio**

```bash
mkdir -p mercado/templates/mercado
```

- [ ] **Step 2: Escribir `mercado/templates/mercado/mercado_home.html`**

```html
{% extends "base/base.html" %}

{% block title %}Mercado — Nido Mozzarella{% endblock %}

{% block content %}

<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem; margin-bottom:0.5rem;">
    <div>
        <h1 class="section-title">🏪 El Mercado</h1>
        <p class="section-subtitle">Comprá quesos y desbloqueá recetas con tus monedas</p>
    </div>
    {% if user.is_authenticated %}
        <div style="text-align:right;">
            <span style="font-size:1.1rem; font-weight:700;">🪙 {{ user.perfil.monedas }} monedas</span><br>
            <a href="{% url 'historial' %}" style="font-size:0.85rem; color:var(--accent);">Ver historial →</a>
        </div>
    {% endif %}
</div>

<!-- QUESOS -->
<section style="margin-bottom:2.5rem;">
    <h2 class="section-title" style="font-size:1.3rem;">🧀 Quesos disponibles</h2>
    {% if quesos %}
        <div class="cards-grid">
            {% for queso in quesos %}
            <div class="card">
                {% if queso.imagen %}
                    <img src="{{ queso.imagen.url }}" alt="{{ queso.nombre }}" class="card-img">
                {% else %}
                    <div style="height:140px; background:var(--accent); display:flex; align-items:center; justify-content:center; font-size:3rem;">🧀</div>
                {% endif %}
                <div class="card-body">
                    <p class="card-title">{{ queso.nombre }}</p>
                    <p class="card-text">{{ queso.descripcion|truncatewords:10 }}</p>
                    <p style="font-size:0.85rem; color:#888; margin-bottom:0.5rem;">Stock: {{ queso.stock }}</p>
                    {% if user.is_authenticated %}
                        <form method="post" action="{% url 'comprar_queso' queso.pk %}">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-primary"
                                {% if user.perfil.monedas < queso.precio_monedas %}disabled title="No tenés suficientes monedas"{% endif %}>
                                Comprar 🪙{{ queso.precio_monedas }}
                            </button>
                        </form>
                    {% else %}
                        <a href="{% url 'login' %}" class="btn btn-secondary">Ingresá para comprar</a>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    {% else %}
        <div class="empty-state"><p>🧀 No hay quesos disponibles en este momento.</p></div>
    {% endif %}
</section>

<!-- RECETAS PREMIUM -->
<section>
    <h2 class="section-title" style="font-size:1.3rem;">📖 Recetas premium</h2>
    {% if recetas_premium %}
        <div class="cards-grid">
            {% for post in recetas_premium %}
            <div class="card">
                {% if post.imagen %}
                    <img src="{{ post.imagen.url }}" alt="{{ post.titulo }}" class="card-img">
                {% else %}
                    <div style="height:140px; background:var(--accent); display:flex; align-items:center; justify-content:center; font-size:3rem;">📖</div>
                {% endif %}
                <div class="card-body">
                    <p class="card-title">{{ post.titulo }}</p>
                    <p style="font-size:0.8rem; color:#9B7B3A; margin-bottom:0.3rem;">
                        ✍️ {{ post.autor.get_full_name|default:post.autor.username }}
                    </p>
                    <p class="card-text">{{ post.preview|default:post.cuerpo|truncatewords:15 }}</p>
                    {% if user.is_authenticated %}
                        {% if post.id in compras_usuario or user == post.autor or user.is_staff %}
                            <a href="{% url 'post_detail' post.id %}" class="btn btn-secondary">✅ Ya desbloqueada</a>
                        {% else %}
                            <a href="{% url 'post_detail' post.id %}" class="btn btn-primary">
                                Desbloquear 🪙{{ post.precio_monedas }}
                            </a>
                        {% endif %}
                    {% else %}
                        <a href="{% url 'login' %}" class="btn btn-secondary">Ingresá para desbloquear</a>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    {% else %}
        <div class="empty-state"><p>📖 No hay recetas premium publicadas todavía.</p></div>
    {% endif %}
</section>

{% endblock %}
```

- [ ] **Step 3: Escribir `mercado/templates/mercado/historial.html`**

```html
{% extends "base/base.html" %}

{% block title %}Historial de monedas — Nido Mozzarella{% endblock %}

{% block content %}

<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem; margin-bottom:1.5rem;">
    <div>
        <h1 class="section-title">🪙 Mis monedas</h1>
        <p class="section-subtitle">Historial de transacciones</p>
    </div>
    <div style="text-align:right;">
        <p style="font-size:1.3rem; font-weight:900;">🪙 {{ user.perfil.monedas }}</p>
        <p style="font-size:0.9rem; color:#888;">⭐ {{ user.perfil.puntos }} puntos</p>
    </div>
</div>

<!-- CANJEAR PUNTOS -->
{% if user.perfil.puntos >= ratio_puntos %}
<div style="background:var(--card-bg); border:2px solid var(--accent); border-radius:12px; padding:1.2rem; margin-bottom:2rem;">
    <h3 style="margin-bottom:0.5rem;">🔄 Canjear puntos por monedas</h3>
    <p style="font-size:0.9rem; margin-bottom:0.8rem;">
        Tenés <strong>{{ user.perfil.puntos }} puntos</strong>. 
        Podés canjear <strong>{{ user.perfil.puntos|divisibleby:ratio_puntos|yesno:"sí,no" }}</strong> lotes de {{ ratio_puntos }} puntos
        → ganás <strong>{{ user.perfil.puntos|add:0 }}</strong> monedas aprox.
    </p>
    <form method="post" action="{% url 'canjear_puntos' %}">
        {% csrf_token %}
        <label style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem; cursor:pointer;">
            {{ form_canje.confirmar }}
            <span style="font-size:0.9rem;">{{ form_canje.confirmar.label }}</span>
        </label>
        <button type="submit" class="btn btn-primary">Canjear ahora</button>
    </form>
</div>
{% else %}
<div style="background:var(--card-bg); border:1px solid var(--border); border-radius:12px; padding:1.2rem; margin-bottom:2rem; color:#888;">
    <p>Necesitás al menos <strong>{{ ratio_puntos }} puntos</strong> para canjear. Tenés {{ user.perfil.puntos }}.</p>
</div>
{% endif %}

<!-- HISTORIAL -->
{% if transacciones %}
    <table class="data-table">
        <thead>
            <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Descripción</th>
                <th>Monedas</th>
            </tr>
        </thead>
        <tbody>
            {% for t in transacciones %}
            <tr>
                <td style="font-size:0.85rem; color:#888;">{{ t.fecha|date:"d/m/Y H:i" }}</td>
                <td><span class="badge badge-{% if t.monto > 0 %}green{% else %}orange{% endif %}">{{ t.get_tipo_display }}</span></td>
                <td>{{ t.descripcion }}</td>
                <td style="font-weight:700; color:{% if t.monto > 0 %}green{% else %}#c0392b{% endif %};">
                    {{ t.monto|stringformat:"+d" }} 🪙
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
{% else %}
    <div class="empty-state"><p>🪙 Todavía no tenés transacciones.</p></div>
{% endif %}

<div style="margin-top:1.5rem;">
    <a href="{% url 'mercado_home' %}" class="btn btn-secondary">← Volver al mercado</a>
</div>

{% endblock %}
```

- [ ] **Step 4: Commit**

```bash
git add mercado/templates/
git commit -m "feat: templates del mercado (home e historial)"
```

---

## Task 6: Actualizar blog — unlock de recetas premium

**Files:**
- Modify: `blog/views.py`
- Modify: `blog/forms.py`
- Modify: `blog/templates/blog/post_detail.html`

- [ ] **Step 1: Actualizar `post_detail` en `blog/views.py`**

Reemplazar la función `post_detail` existente:

```python
def post_detail(request, pageId):
    """Detalle de un post. Si es premium y el usuario no lo compró, muestra el preview."""
    post = get_object_or_404(Post, pk=pageId)

    desbloqueado = True  # por defecto (post gratuito)
    if post.es_premium:
        if not request.user.is_authenticated:
            desbloqueado = False
        elif request.user == post.autor or request.user.is_staff:
            desbloqueado = True
        else:
            from mercado.models import CompraReceta
            desbloqueado = CompraReceta.objects.filter(
                comprador=request.user, post=post
            ).exists()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'desbloqueado': desbloqueado,
    })
```

- [ ] **Step 2: Agregar `precio_monedas` a `blog/forms.py`**

```python
from django import forms
from .models import Post


class FormularioPost(forms.ModelForm):
    """Formulario para crear y editar posts del blog."""

    class Meta:
        model = Post
        fields = ['titulo', 'subtitulo', 'cuerpo', 'imagen', 'precio_monedas']
        labels = {
            'titulo': 'Título',
            'subtitulo': 'Subtítulo',
            'cuerpo': 'Contenido',
            'imagen': 'Imagen',
            'precio_monedas': 'Precio en monedas (0 = gratis)',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Título de la receta o publicación'}),
            'subtitulo': forms.TextInput(attrs={'placeholder': 'Subtítulo opcional'}),
            'cuerpo': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Escribí el contenido aquí...'}),
            'precio_monedas': forms.NumberInput(attrs={'min': 0, 'placeholder': '0'}),
        }


class FormularioBusqueda(forms.Form):
    """Formulario de búsqueda de posts por título."""
    titulo = forms.CharField(
        max_length=255,
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': '🔍 Buscar recetas...'}),
    )
```

- [ ] **Step 3: Actualizar `blog/templates/blog/post_detail.html`**

```html
{% extends "base/base.html" %}

{% block title %}{{ post.titulo }} — Nido Mozzarella{% endblock %}

{% block content %}

<div class="post-detail">
    {% if post.imagen %}
        <img src="{{ post.imagen.url }}" alt="{{ post.titulo }}">
    {% endif %}

    <h1 style="font-size:2rem; font-weight:900; margin-bottom:0.3rem;">{{ post.titulo }}</h1>
    {% if post.subtitulo %}
        <p style="font-size:1.1rem; color:#9B7B3A; margin-bottom:0.8rem;">{{ post.subtitulo }}</p>
    {% endif %}

    <p class="post-meta">
        ✍️ {{ post.autor.get_full_name|default:post.autor.username }}
        &nbsp;·&nbsp;
        📅 {{ post.fecha|date:"d \d\e F \d\e Y" }}
        {% if post.es_premium %}
            &nbsp;·&nbsp; <span class="badge badge-orange">🪙 Premium · {{ post.precio_monedas }} monedas</span>
        {% endif %}
    </p>

    <hr style="border:none; border-top:2px solid var(--border); margin:1rem 0;">

    {% if desbloqueado %}
        <div style="line-height:1.8; font-size:1rem;">
            {{ post.cuerpo|linebreaks }}
        </div>
    {% else %}
        <!-- PREVIEW + PAYWALL -->
        <div style="line-height:1.8; font-size:1rem; position:relative;">
            <div style="max-height:120px; overflow:hidden; mask-image:linear-gradient(to bottom, black 40%, transparent 100%);">
                {{ post.preview|linebreaks }}
            </div>
        </div>
        <div style="text-align:center; margin:2rem 0; padding:1.5rem; background:var(--card-bg); border:2px dashed var(--accent); border-radius:12px;">
            <p style="font-size:1.1rem; font-weight:700; margin-bottom:0.5rem;">🔒 Receta premium</p>
            <p style="color:#888; margin-bottom:1rem;">Desbloqueá la receta completa por <strong>{{ post.precio_monedas }} monedas</strong></p>
            {% if user.is_authenticated %}
                <p style="font-size:0.9rem; margin-bottom:1rem;">Tenés <strong>🪙 {{ user.perfil.monedas }}</strong> monedas</p>
                <form method="post" action="{% url 'comprar_receta' post.id %}">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-primary"
                        {% if user.perfil.monedas < post.precio_monedas %}disabled{% endif %}>
                        {% if user.perfil.monedas < post.precio_monedas %}
                            Monedas insuficientes
                        {% else %}
                            Desbloquear por 🪙{{ post.precio_monedas }}
                        {% endif %}
                    </button>
                </form>
            {% else %}
                <a href="{% url 'login' %}" class="btn btn-primary">Iniciá sesión para desbloquear</a>
            {% endif %}
        </div>
    {% endif %}

    <div style="margin-top:2rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
        <a href="{% url 'post_list' %}" class="btn btn-secondary">← Volver a recetas</a>
        {% if user == post.autor or user.is_staff %}
            <a href="{% url 'post_edit' post.id %}" class="btn btn-primary">Editar</a>
            <a href="{% url 'post_delete' post.id %}" class="btn btn-danger">Eliminar</a>
        {% endif %}
    </div>
</div>

{% endblock %}
```

- [ ] **Step 4: Commit**

```bash
git add blog/views.py blog/forms.py blog/templates/
git commit -m "feat: recetas premium — paywall y unlock en post_detail"
```

---

## Task 7: Actualizar inventario — botón comprar con monedas

**Files:**
- Modify: `inventario/templates/inventario/inventario_list.html`

- [ ] **Step 1: Actualizar `inventario/templates/inventario/inventario_list.html`**

Reemplazar la columna "Precio" y agregar botón en la tabla. El template completo:

```html
{% extends "base/base.html" %}

{% block title %}Inventario — Nido Mozzarella{% endblock %}

{% block content %}

<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem; margin-bottom:0.5rem;">
    <div>
        <h1 class="section-title">🧀 La Despensa</h1>
        <p class="section-subtitle">Stock actual de quesos del nido</p>
    </div>
    {% if user.is_staff %}
        <a href="{% url 'inventario_create' %}" class="btn btn-primary">+ Agregar queso</a>
    {% endif %}
</div>

<!-- BÚSQUEDA -->
<form method="get" style="margin-bottom:1.5rem; display:flex; gap:0.5rem;">
    <div style="flex:1;">{{ form_busqueda.nombre }}</div>
    <button type="submit" class="btn btn-primary">Buscar</button>
    {% if request.GET.nombre %}
        <a href="{% url 'inventario_list' %}" class="btn btn-secondary">Limpiar</a>
    {% endif %}
</form>

{% if quesos %}
    <table class="data-table">
        <thead>
            <tr>
                <th>Queso</th>
                <th>Descripción</th>
                <th>Precio $</th>
                <th>Precio 🪙</th>
                <th>Stock</th>
                <th>Estado</th>
                <th>Acción</th>
                {% if user.is_staff %}<th>Admin</th>{% endif %}
            </tr>
        </thead>
        <tbody>
            {% for queso in quesos %}
            <tr>
                <td>
                    {% if queso.imagen %}
                        <img src="{{ queso.imagen.url }}" alt="{{ queso.nombre }}"
                             style="width:40px; height:40px; object-fit:cover; border-radius:8px; vertical-align:middle; margin-right:0.5rem;">
                    {% else %}
                        <span style="font-size:1.5rem; margin-right:0.5rem;">🧀</span>
                    {% endif %}
                    <strong>{{ queso.nombre }}</strong>
                </td>
                <td>{{ queso.descripcion|truncatewords:10 }}</td>
                <td>${{ queso.precio }}</td>
                <td>🪙{{ queso.precio_monedas }}</td>
                <td>{{ queso.stock }}</td>
                <td>
                    <span class="badge badge-{{ queso.estado_stock }}">{{ queso.etiqueta_stock }}</span>
                </td>
                <td>
                    {% if user.is_authenticated and queso.stock > 0 %}
                        <form method="post" action="{% url 'comprar_queso' queso.pk %}">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-primary"
                                style="font-size:0.8rem; padding:0.3rem 0.6rem;"
                                {% if user.perfil.monedas < queso.precio_monedas %}disabled{% endif %}>
                                Comprar 🪙
                            </button>
                        </form>
                    {% elif queso.stock == 0 %}
                        <span style="font-size:0.8rem; color:#888;">Sin stock</span>
                    {% else %}
                        <a href="{% url 'login' %}" class="btn btn-secondary" style="font-size:0.8rem; padding:0.3rem 0.6rem;">Login</a>
                    {% endif %}
                </td>
                {% if user.is_staff %}
                <td>
                    <a href="{% url 'inventario_edit' queso.pk %}" class="btn btn-secondary" style="font-size:0.8rem; padding:0.3rem 0.6rem;">Editar</a>
                    <a href="{% url 'inventario_delete' queso.pk %}" class="btn btn-danger" style="font-size:0.8rem; padding:0.3rem 0.6rem;">Eliminar</a>
                </td>
                {% endif %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
{% else %}
    <div class="empty-state">
        <p>🧀 La despensa está vacía. ¡Pronto habrá quesos!</p>
    </div>
{% endif %}

{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add inventario/templates/
git commit -m "feat: botón comprar con monedas en inventario"
```

---

## Task 8: Manual de convivencia en el home + README

**Files:**
- Modify: `core/templates/core/home.html`
- Modify: `README.md`

- [ ] **Step 1: Agregar sección en `core/templates/core/home.html`**

Agregar ANTES del bloque `{% endblock %}` final, después de la sección de últimas recetas:

```html
<!-- MANUAL DE CONVIVENCIA -->
<section style="margin-top:3rem;">
    <h2 class="section-title">📋 Cómo funciona el Nido</h2>
    <p class="section-subtitle">Todo lo que necesitás saber para vivir en el nido</p>
    <div class="cards-grid" style="grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));">

        <div class="card" style="text-align:center; padding:1.5rem;">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">🪙</div>
            <p class="card-title">Qué son las monedas</p>
            <p class="card-text">La moneda interna del nido. Empezás con 100 al registrarte. Úsalas para comprar y desbloquear contenido.</p>
        </div>

        <div class="card" style="text-align:center; padding:1.5rem;">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">⬆️</div>
            <p class="card-title">Cómo ganar monedas</p>
            <p class="card-text">Vendé tus recetas premium a otros usuarios. También podés canjear tus puntos: 10 puntos = 5 monedas.</p>
        </div>

        <div class="card" style="text-align:center; padding:1.5rem;">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">🛒</div>
            <p class="card-title">Cómo gastarlas</p>
            <p class="card-text">Comprá quesos del inventario o desbloqueá recetas premium publicadas por otros habitantes del nido.</p>
        </div>

        <div class="card" style="text-align:center; padding:1.5rem;">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">🏪</div>
            <p class="card-title">El Mercado</p>
            <p class="card-text">El lugar donde todo sucede. Explorá quesos y recetas disponibles.</p>
            <a href="{% url 'mercado_home' %}" class="btn btn-primary" style="margin-top:0.5rem;">Ir al mercado</a>
        </div>

    </div>
</section>
```

- [ ] **Step 2: Actualizar `README.md`**

Agregar al inicio del README, después del título principal:

```markdown
🚀 **Deploy en producción:** https://playground-massironi.vercel.app/
```

- [ ] **Step 3: Commit**

```bash
git add core/templates/core/home.html README.md
git commit -m "feat: manual de convivencia en home + link Vercel en README"
```

---

## Task 9: Deploy final

- [ ] **Step 1: Verificar que todas las migraciones están generadas**

```bash
python manage.py makemigrations --check
```

Expected: "No changes detected"

- [ ] **Step 2: Push a master para triggerear deploy en Vercel**

```bash
git push origin master
```

- [ ] **Step 3: Verificar en Vercel**

- Build log debe mostrar `migrate` sin errores
- Entrar a https://playground-massironi.vercel.app/ y verificar sección "Cómo funciona el Nido"
- Entrar a https://playground-massironi.vercel.app/mercado/ y verificar que carga

- [ ] **Step 4: Commit final si hay ajustes menores**

```bash
git add .
git commit -m "fix: ajustes post-deploy"
git push origin master
```
