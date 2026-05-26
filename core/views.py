from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from blog.models import Post
from .models import Mensaje
from .forms import FormularioMensaje


def home(request):
    """Vista de la página de inicio — muestra los últimos 3 posts."""
    ultimos_posts = Post.objects.order_by('-fecha')[:3]
    return render(request, 'core/home.html', {'ultimos_posts': ultimos_posts})


def about(request):
    """Vista estática 'Acerca de mí' con info de la desarrolladora."""
    return render(request, 'core/about.html')


@login_required
def messages_list(request):
    """Muestra los mensajes del usuario. El admin ve todos."""
    if request.user.is_staff:
        mensajes = Mensaje.objects.all()
    else:
        mensajes = Mensaje.objects.filter(remitente=request.user)
    return render(request, 'core/messages_list.html', {'mensajes': mensajes})


@login_required
def new_message(request):
    """Formulario para enviar un nuevo mensaje al administrador."""
    if request.method == 'POST':
        form = FormularioMensaje(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.remitente = request.user
            mensaje.save()
            messages.success(request, '¡Mensaje enviado correctamente! 📩')
            return redirect('messages_list')
    else:
        form = FormularioMensaje()
    return render(request, 'core/new_message.html', {'form': form})
