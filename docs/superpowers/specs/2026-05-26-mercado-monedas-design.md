# Diseño: Sistema de Mercado y Monedas — Nido Mozzarella

**Fecha:** 2026-05-26
**Estado:** Aprobado

---

## Resumen

Agregar un sistema de economía interna basado en monedas que permita:
- Comprar quesos del inventario (admin → usuario)
- Comprar recetas premium entre usuarios (usuario → usuario)
- Ganar monedas vendiendo recetas y canjeando puntos

---

## 1. Modelos de datos

### App nueva: `mercado`

**`Transaccion`**
```
usuario         → ForeignKey(User)
tipo            → CharField(choices: COMPRA_QUESO, COMPRA_RECETA, VENTA_RECETA, CANJE_PUNTOS)
monto           → IntegerField (positivo = ganó, negativo = gastó)
descripcion     → CharField(max_length=255)
referencia_queso → ForeignKey(Queso, null=True, blank=True)
referencia_post  → ForeignKey(Post, null=True, blank=True)
fecha           → DateTimeField(auto_now_add=True)
```

**`CompraReceta`**
```
comprador    → ForeignKey(User)
post         → ForeignKey(Post)
monto_pagado → IntegerField
fecha        → DateTimeField(auto_now_add=True)
unique_together: (comprador, post)
```

### Cambios en modelos existentes

**`Post` (blog):**
- `precio_monedas` → IntegerField(default=0) — 0 = gratis, >0 = premium
- `preview` → TextField(blank=True) — primeros ~200 chars del cuerpo, se genera al guardar

**`Queso` (inventario):**
- `precio_monedas` → IntegerField(default=10) — separado del precio en $ real

---

## 2. Vistas y URLs

### App `mercado`
```
/mercado/                    → listado de quesos + recetas premium disponibles
/mercado/comprar/queso/<id>/ → POST — compra queso con monedas
/mercado/comprar/receta/<id>/→ POST — desbloquea receta premium
/mercado/historial/          → mis transacciones (requiere login)
/mercado/canjear/            → POST — convertir puntos en monedas
```

### Cambios en `blog`
- `post_detail`: si `precio_monedas > 0` y el usuario no tiene `CompraReceta`, muestra `preview` + botón "Desbloquear por X monedas"
- `post_create` / `post_edit`: agrega campo `precio_monedas`

### Cambios en `inventario`
- `inventario_list`: muestra precio en monedas en cada queso + botón "Comprar con monedas"

### Cambios en `core`
- `home`: sección fija "Cómo funciona el Nido 🧀" siempre visible con 4 ítems explicativos

### README
- Agregar link de producción: `https://playground-massironi.vercel.app/`

---

## 3. Lógica de negocio

### Comprar queso
1. Verificar monedas suficientes (`perfil.monedas >= queso.precio_monedas`)
2. Verificar stock disponible (`queso.stock > 0`)
3. Descontar monedas del perfil
4. Reducir `queso.stock` en 1
5. Crear `Pedido` (flujo existente — da puntos)
6. Registrar `Transaccion(tipo=COMPRA_QUESO, monto=-precio_monedas)`
7. Todo en `transaction.atomic()` — rollback si cualquier paso falla

### Comprar receta
1. Verificar que no existe `CompraReceta(comprador=request.user, post=post)`
2. Verificar monedas suficientes
3. Descontar monedas al comprador
4. Sumar monedas al autor (`post.autor.perfil.monedas`)
5. Crear `CompraReceta`
6. Registrar `Transaccion(tipo=COMPRA_RECETA, monto=-monto)` para comprador
7. Registrar `Transaccion(tipo=VENTA_RECETA, monto=+monto)` para autor
8. Todo en `transaction.atomic()`

### Canjear puntos → monedas
- Ratio: 10 puntos = 5 monedas
- Mínimo para canjear: 10 puntos
- Restar puntos del perfil, sumar monedas
- Registrar `Transaccion(tipo=CANJE_PUNTOS, monto=+monedas_ganadas)`

---

## 4. Manual de convivencia (home)

Sección fija en `core/home.html`, siempre visible, con 4 ítems:
1. **Qué son las monedas** — la moneda interna del nido, empezás con 100
2. **Cómo ganarlas** — vendiendo recetas + canjeando puntos (10 pts = 5 monedas)
3. **Cómo gastarlas** — comprando quesos del inventario o recetas premium de otros
4. **El mercado** — link directo a `/mercado/`

---

## 5. Archivos a crear / modificar

### Crear
- `mercado/__init__.py`
- `mercado/apps.py`
- `mercado/models.py` — Transaccion, CompraReceta
- `mercado/views.py` — 4 vistas
- `mercado/urls.py`
- `mercado/forms.py` — FormularioCanje
- `mercado/templates/mercado/mercado_home.html`
- `mercado/templates/mercado/historial.html`
- `mercado/migrations/0001_initial.py`

### Modificar
- `blog/models.py` — agregar precio_monedas, preview a Post
- `blog/views.py` — lógica de unlock en post_detail
- `blog/forms.py` — agregar precio_monedas
- `blog/templates/blog/post_detail.html` — preview + botón compra
- `inventario/models.py` — agregar precio_monedas a Queso
- `inventario/templates/inventario/inventario_list.html` — botón comprar
- `core/templates/core/home.html` — sección manual de convivencia
- `nido_mozzarella/settings.py` — agregar 'mercado' a INSTALLED_APPS
- `nido_mozzarella/urls.py` — include mercado.urls
- `README.md` — agregar link de producción

---

## 6. Consideraciones

- Todas las operaciones de monedas usan `select_for_update()` para evitar race conditions
- El campo `preview` se genera automáticamente en `Post.save()` si `precio_monedas > 0`
- Usuarios no autenticados ven el preview de recetas premium sin botón de compra
- El admin puede editar `precio_monedas` de quesos desde el panel de Django Admin
