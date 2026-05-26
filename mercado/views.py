import logging

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

logger = logging.getLogger(__name__)

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
                raise ValueError('sin_stock')
            if perfil_lock.monedas < queso_lock.precio_monedas:
                raise ValueError('monedas_insuficientes')

            perfil_lock.monedas -= queso_lock.precio_monedas
            queso_lock.stock -= 1
            queso_lock.save()

            pedido = Pedido(
                usuario=request.user,
                queso=queso_lock,
                cantidad=1,
                completado=True,
            )
            pedido.puntos_ganados = pedido.calcular_puntos()
            pedido.save()

            perfil_lock.puntos += pedido.puntos_ganados
            perfil_lock.save()
            perfil_lock.actualizar_nivel()

            Transaccion.objects.create(
                usuario=request.user,
                tipo=Transaccion.COMPRA_QUESO,
                monto=-queso_lock.precio_monedas,
                descripcion=f'Compra de {queso_lock.nombre}',
                referencia_queso=queso_lock,
            )
    except ValueError as e:
        if str(e) == 'sin_stock':
            messages.error(request, 'El queso se agotó justo ahora.')
        else:
            messages.error(request, 'Monedas insuficientes.')
        return redirect('mercado_home')
    except Exception:
        logger.exception('Error en comprar_queso user=%s queso_pk=%s', request.user.pk, pk)
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
            # Ordenar locks por PK para evitar deadlock
            user_ids = sorted([request.user.pk, post.autor.pk])
            perfiles = {
                p.user_id: p
                for p in PerfilUsuario.objects.select_for_update().filter(user_id__in=user_ids)
            }
            comprador_perfil = perfiles[request.user.pk]
            autor_perfil = perfiles[post.autor.pk]

            if comprador_perfil.monedas < post.precio_monedas:
                raise ValueError('monedas_insuficientes')

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
    except ValueError:
        messages.error(request, 'Monedas insuficientes.')
        return redirect('post_detail', pageId=post.pk)
    except Exception:
        logger.exception('Error en comprar_receta user=%s post_pk=%s', request.user.pk, pk)
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
        logger.exception('Error en canjear_puntos user=%s', request.user.pk)
        messages.error(request, 'Error al procesar el canje.')
        return redirect('historial')

    messages.success(request, f'¡Canjeaste {puntos_a_gastar} puntos por {monedas_ganadas} monedas! 🪙')
    return redirect('historial')
