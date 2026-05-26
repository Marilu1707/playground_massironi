import requests as http_requests
import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Post
from .forms import FormularioPost, FormularioBusqueda


def _fetch_unsplash_image(query):
    """Descarga una imagen de Unsplash para la receta. Retorna ContentFile o None."""
    api_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '')
    if not api_key:
        return None
    try:
        resp = http_requests.get(
            'https://api.unsplash.com/search/photos',
            params={'query': query, 'per_page': 1, 'client_id': api_key},
            timeout=5,
        )
        results = resp.json().get('results', [])
        if not results:
            return None
        image_url = results[0]['urls']['regular']
        img_resp = http_requests.get(image_url, timeout=10)
        if img_resp.status_code == 200:
            slug = hashlib.md5(query.encode()).hexdigest()[:10]
            return ContentFile(img_resp.content, name=f'unsplash_{slug}.jpg')
    except Exception:
        pass
    return None


def post_list(request):
    """Lista todos los posts. Permite búsqueda por título."""
    form_busqueda = FormularioBusqueda(request.GET)
    posts = Post.objects.all()

    if form_busqueda.is_valid():
        titulo = form_busqueda.cleaned_data.get('titulo')
        if titulo:
            posts = posts.filter(titulo__icontains=titulo)

    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'form_busqueda': form_busqueda,
    })


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


@login_required
def post_create(request):
    """Crear nueva receta — cualquier usuario registrado puede publicar."""
    if request.method == 'POST':
        form = FormularioPost(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            if not request.FILES.get('imagen'):
                imagen = _fetch_unsplash_image(post.titulo)
                if imagen:
                    post.imagen.save(imagen.name, imagen, save=False)
            post.save()
            messages.success(request, '¡Receta publicada con éxito! 🧀')
            return redirect('post_detail', pageId=post.id)
    else:
        form = FormularioPost()
    return render(request, 'blog/post_form.html', {'form': form, 'accion': 'Crear'})


@login_required
def post_edit(request, pageId):
    """Editar receta — solo el autor o un administrador."""
    post = get_object_or_404(Post, id=pageId)

    if post.autor != request.user and not request.user.is_staff:
        messages.error(request, 'Solo podés editar tus propias recetas.')
        return redirect('post_detail', pageId=post.id)

    if request.method == 'POST':
        form = FormularioPost(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Receta actualizada correctamente ✅')
            return redirect('post_detail', pageId=post.id)
    else:
        form = FormularioPost(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'post': post, 'accion': 'Editar'})


@login_required
def post_delete(request, pageId):
    """Eliminar receta — solo el autor o un administrador."""
    post = get_object_or_404(Post, id=pageId)

    if post.autor != request.user and not request.user.is_staff:
        messages.error(request, 'Solo podés eliminar tus propias recetas.')
        return redirect('post_detail', pageId=post.id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Receta eliminada.')
        return redirect('post_list')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})
