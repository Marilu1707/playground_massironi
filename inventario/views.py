from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Queso
from .forms import FormularioQueso, FormularioBusquedaQueso


def inventario_list(request):
    """Lista todos los quesos del inventario. Permite búsqueda por nombre."""
    form_busqueda = FormularioBusquedaQueso(request.GET)
    quesos = Queso.objects.all()

    if form_busqueda.is_valid():
        nombre = form_busqueda.cleaned_data.get('nombre')
        if nombre:
            quesos = quesos.filter(nombre__icontains=nombre)

    return render(request, 'inventario/inventario_list.html', {
        'quesos': quesos,
        'form_busqueda': form_busqueda,
    })


@staff_member_required
def inventario_create(request):
    """Agregar nuevo queso al inventario — solo administradores."""
    if request.method == 'POST':
        form = FormularioQueso(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Queso agregado al inventario! 🧀')
            return redirect('inventario_list')
    else:
        form = FormularioQueso()
    return render(request, 'inventario/inventario_form.html', {'form': form, 'accion': 'Agregar'})


@staff_member_required
def inventario_edit(request, pk):
    """Editar queso existente — solo administradores."""
    queso = get_object_or_404(Queso, pk=pk)
    if request.method == 'POST':
        form = FormularioQueso(request.POST, request.FILES, instance=queso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Queso actualizado correctamente ✅')
            return redirect('inventario_list')
    else:
        form = FormularioQueso(instance=queso)
    return render(request, 'inventario/inventario_form.html', {'form': form, 'queso': queso, 'accion': 'Editar'})


@staff_member_required
def inventario_delete(request, pk):
    """Eliminar queso — solo administradores."""
    queso = get_object_or_404(Queso, pk=pk)
    if request.method == 'POST':
        queso.delete()
        messages.success(request, 'Queso eliminado del inventario.')
        return redirect('inventario_list')
    return render(request, 'inventario/inventario_confirm_delete.html', {'queso': queso})
