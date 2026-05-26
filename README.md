# 🧀 Nido Mozzarella

🚀 **Deploy en producción:** https://playground-massironi.vercel.app/

**Autora:** María Luján Massironi  
**Carrera:** Negocios Digitales — UADE  

---

## Descripción

Nido Mozzarella es una aplicación web desarrollada en Django con temática de pizzería kawaii. El proyecto fue trabajado, actualizado y mejorado a lo largo del curso, incorporando funcionalidades progresivamente en cada entrega.

Se utilizó IA como herramienta de ayuda e inspiración durante el desarrollo, incorporando ideas y patrones vistos en otras certificaciones previas (marketing digital, análisis de datos, desarrollo web). La combinación de estas áreas permitió tomar decisiones de diseño y arquitectura más fundamentadas.

---

## Funcionalidades

- **Blog de recetas** — cualquier usuario registrado puede publicar recetas con imagen propia. Si no se sube foto, se busca automáticamente una imagen en Unsplash por el título del post.
- **Inventario de quesos** — despensa con control de stock e indicadores visuales (verde / naranja / rojo). Gestión exclusiva para administradores.
- **Sistema de pedidos** — los usuarios pueden hacer pedidos que descuentan stock y suman puntos y monedas a su perfil.
- **Perfil de usuario** — foto de perfil, bio, nivel, puntos y monedas acumuladas. Sistema de niveles automático según puntos.
- **Juego del ratoncito 🐭** — minijuego interactivo de 60 segundos: atrapa quesos para sumar puntos, evitá la basura que resta. El ratoncito sigue tu toque o click en pantalla. Los puntos y monedas ganados se guardan en tu cuenta.
- **Autenticación completa** — registro, login, logout, edición de perfil y cambio de contraseña.
- **Mensajería** — los usuarios pueden enviar mensajes al administrador.
- **Panel de administración** — gestión completa desde `/admin/`.
- **Navbar responsivo** — menú sticky con dropdown de usuario, indicador de puntos y monedas, y menú hamburger para mobile.

---

## Tecnologías

- Python 3
- Django 6
- HTML5 / CSS3
- JavaScript (vanilla)
- SQLite (base de datos de desarrollo)
- Pillow (manejo de imágenes)
- Unsplash API (imágenes automáticas para recetas)

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone [<url-del-repo>](https://github.com/Marilu1707/playground_massironi.git)
cd nido_mozzarella

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/Scripts/activate      # Windows bash
# venv\Scripts\Activate.ps1       # Windows PowerShell

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (opcional)
cp .env.example .env
# Editá .env y agregá tu UNSPLASH_ACCESS_KEY si querés imágenes automáticas

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Levantar el servidor
python manage.py runserver
```

Abrí el navegador en `http://127.0.0.1:8000/`

---

## Rutas principales

| URL | Descripción |
|---|---|
| `/` | Inicio |
| `/about/` | Acerca de la autora |
| `/pages/` | Blog de recetas |
| `/inventario/` | Despensa de quesos |
| `/juego/jugar/` | Juego del ratoncito |
| `/juego/` | Historial de pedidos |
| `/accounts/signup/` | Registro |
| `/accounts/login/` | Login |
| `/accounts/profile/` | Perfil de usuario |
| `/admin/` | Panel de administración |

---

## Certificación

Este proyecto es la entrega final del curso **Python Flex** de Coderhouse.

| | |
|---|---|
| **Curso** | Python Flex |
| **Institución** | Coderhouse |
| **Comisión** | 56065 |
| **Duración** | 26 horas · 15 semanas |
| **Finalización** | 30 de enero de 2024 |
| **Certificado** | [Ver certificado oficial](https://pub.coderhouse.com/legacy-certificates/65e160cbc5e75f52272b3f3e?lang=es) |

---

## Notas finales

Este proyecto representa mucho más que una entrega de curso. Empezó como un ejercicio de Django y terminó siendo un espacio donde conecté todo lo que fui aprendiendo: lógica de backend, diseño de interfaces, manejo de datos y automatización.

La IA fue una compañera de trabajo real durante este proceso — no para hacer el trabajo por mí, sino para explorar ideas, entender errores, y pensar en mejores formas de implementar cada funcionalidad. Eso también es una habilidad que vale la pena desarrollar.

Gracias al curso por la estructura, y a cada iteración del proyecto por enseñarme algo nuevo. 🧀🐭

---

*Nido Mozzarella — hecho con amor y mucho queso.*
