from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FormularioRegistro, FormularioEditarPerfil, FormularioCambiarPassword


def signup(request):
    """Registro de nuevo usuario."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido al nido, {user.username}! 🧀')
            return redirect('profile')
    else:
        form = FormularioRegistro()
    return render(request, 'accounts/signup.html', {'form': form})


def user_login(request):
    """Login de usuario."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'¡Hola de nuevo, {user.username}! 🍕')
            return redirect('profile')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'accounts/login.html')


def user_logout(request):
    """Logout del usuario."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Hasta la próxima 👋')
    return redirect('home')


@login_required
def profile(request):
    """Vista del perfil del usuario autenticado."""
    return render(request, 'accounts/profile.html', {'perfil': request.user.perfil})


@login_required
def edit_profile(request):
    """Edición del perfil del usuario."""
    perfil = request.user.perfil

    if request.method == 'POST':
        form = FormularioEditarPerfil(request.POST, request.FILES, instance=perfil, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name  = form.cleaned_data.get('last_name', '')
            request.user.email      = form.cleaned_data.get('email', '')
            request.user.save()

            if form.cleaned_data.get('eliminar_foto'):
                perfil.foto_perfil = None
            elif 'foto_perfil' in request.FILES:
                perfil.foto_perfil = request.FILES['foto_perfil']

            perfil.bio  = form.cleaned_data.get('bio', '')
            perfil.link = form.cleaned_data.get('link', '')
            perfil.save()

            messages.success(request, 'Perfil actualizado correctamente ✅')
            return redirect('profile')
    else:
        form = FormularioEditarPerfil(instance=perfil, user=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Cambio de contraseña del usuario."""
    if request.method == 'POST':
        form = FormularioCambiarPassword(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada con éxito 🔐')
            return redirect('profile')
    else:
        form = FormularioCambiarPassword(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
