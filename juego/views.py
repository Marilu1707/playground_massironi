import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from .models import Pedido
from .forms import FormularioPedido

MONEDAS_POR_PEDIDO = 10  # monedas fijas que da cada pedido manual


@login_required
def juego_list(request):
    """Historial de pedidos del usuario autenticado."""
    pedidos = Pedido.objects.filter(usuario=request.user)
    total_puntos = sum(p.puntos_ganados for p in pedidos)
    return render(request, 'juego/juego_list.html', {
        'pedidos': pedidos,
        'total_puntos': total_puntos,
    })


@login_required
def juego_create(request):
    """Crear un nuevo pedido desde el formulario clásico."""
    if request.method == 'POST':
        form = FormularioPedido(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.usuario = request.user
            queso = pedido.queso

            if queso.stock < pedido.cantidad:
                messages.error(request, f'No hay suficiente stock de {queso.nombre}. Stock actual: {queso.stock}')
                return render(request, 'juego/juego_form.html', {'form': form})

            with transaction.atomic():
                from inventario.models import Queso as QuesoModel
                from accounts.models import PerfilUsuario
                from mercado.models import Transaccion

                queso_lock  = QuesoModel.objects.select_for_update().get(pk=queso.pk)
                perfil_lock = PerfilUsuario.objects.select_for_update().get(user=request.user)

                if queso_lock.stock < pedido.cantidad:
                    messages.error(request, f'Stock insuficiente de {queso.nombre}.')
                    return render(request, 'juego/juego_form.html', {'form': form})

                queso_lock.stock -= pedido.cantidad
                queso_lock.save()

                pedido.puntos_ganados = pedido.calcular_puntos()
                pedido.completado = True
                pedido.save()

                perfil_lock.puntos  += pedido.puntos_ganados
                perfil_lock.monedas += MONEDAS_POR_PEDIDO
                perfil_lock.save()
                perfil_lock.actualizar_nivel()

                Transaccion.objects.create(
                    usuario=request.user,
                    tipo=Transaccion.JUEGO,
                    monto=MONEDAS_POR_PEDIDO,
                    descripcion=f'Pedido manual: {pedido.cantidad}x {queso_lock.nombre}',
                    referencia_queso=queso_lock,
                )

            messages.success(request, f'¡Pedido completado! Ganaste {pedido.puntos_ganados} puntos y {MONEDAS_POR_PEDIDO} monedas 🎉')
            return redirect('juego_list')
    else:
        form = FormularioPedido()
    return render(request, 'juego/juego_form.html', {'form': form})


@login_required
def juego_game(request):
    """Vista del juego interactivo del ratoncito."""
    return render(request, 'juego/juego_game.html')


@login_required
@require_POST
def puntuar(request):
    """Endpoint AJAX: recibe { puntos, monedas } y actualiza el perfil del usuario."""
    try:
        data    = json.loads(request.body)
        puntos  = max(0, int(data.get('puntos', 0)))
        monedas = max(0, int(data.get('monedas', 0)))
    except (ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Datos inválidos'}, status=400)

    from accounts.models import PerfilUsuario
    from mercado.models import Transaccion

    with transaction.atomic():
        perfil = PerfilUsuario.objects.select_for_update().get(user=request.user)
        perfil.puntos  += puntos
        perfil.monedas += monedas
        perfil.save()
        perfil.actualizar_nivel()

        if monedas > 0:
            Transaccion.objects.create(
                usuario=request.user,
                tipo=Transaccion.JUEGO,
                monto=monedas,
                descripcion=f'Partida: +{puntos} pts, +{monedas} 🪙',
            )

    return JsonResponse({
        'ok':      True,
        'puntos':  perfil.puntos,
        'monedas': perfil.monedas,
        'nivel':   perfil.nivel,
    })
