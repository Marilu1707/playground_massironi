import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nido_mozzarella.settings')

import django
django.setup()

from django.core.management import call_command

# Aplica migraciones pendientes (necesario para Neon en Vercel)
call_command('migrate', '--run-syncdb', verbosity=0)

# Crea superuser inicial si no existe (credenciales vía env vars en Vercel)
#   DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
_su_user = os.environ.get('DJANGO_SUPERUSER_USERNAME')
_su_pass = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if _su_user and _su_pass:
    from django.contrib.auth.models import User
    if not User.objects.filter(username=_su_user).exists():
        User.objects.create_superuser(
            username=_su_user,
            email=os.environ.get('DJANGO_SUPERUSER_EMAIL', ''),
            password=_su_pass,
        )

# Crea contenido inicial si no existe (idempotente)
try:
    call_command('seed_datos', verbosity=0)
except Exception:
    pass  # No romper el deploy si el seed falla

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
