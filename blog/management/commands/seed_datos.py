"""
Management command: seed_datos
Crea contenido inicial del nido (idempotente — usa get_or_create).
Pensado para ejecutarse en cada cold start de Vercel vía api/index.py.
"""

import requests
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.conf import settings
from blog.models import Post
from inventario.models import Queso


# ── Receta 1: Pizza Margherita ───────────────────────────────────────────────

PIZZA_CUERPO = """\
Hay pizzas y hay pizza. La Margherita es la original, la que define todo lo demás.
Tres ingredientes sobre masa: tomate, mozzarella, albahaca. Nada más necesita.

🍕 INGREDIENTES (2 pizzas medianas)

Masa:
- 500 g harina 000
- 325 ml agua tibia
- 7 g levadura seca
- 10 g sal
- 1 cdita azúcar
- 2 cdas aceite de oliva

Salsa:
- 400 g tomates perita maduros (o en lata, al natural)
- 1 diente de ajo
- Sal, pimienta negra
- Orégano seco a gusto

Para armar:
- 300 g mozzarella fresca
- Albahaca fresca
- Aceite de oliva extra virgen


📋 CÓMO SE HACE

1. LA MASA
Disolvé la levadura con el azúcar en el agua tibia. Esperá 5 minutos: tiene que espumar.
En un bowl grande mezclá la harina con la sal, hacé un hueco en el centro y volcá el agua con levadura más el aceite.
Integrá todo y amasá sobre la mesada durante unos 10 minutos, hasta que la masa quede lisa, elástica y no se pegue.
Formá un bollo, pasalo a un bowl aceitado, cubrilo con film o un repasador húmedo y dejalo leudar 90 minutos en un lugar tibio hasta que duplique su tamaño.

2. LA SALSA
Procesá o pisá los tomates con el ajo hasta obtener una salsa rústica, sin cocinar.
Condimentá con sal, pimienta y orégano. La salsa se cocina en el horno, así conserva frescura.

3. EL ARMADO
Precalentá el horno al máximo posible, mínimo 250 °C, con la bandeja o piedra adentro.
Dividí la masa en dos bollos y estirálos con las manos sobre una superficie enharinada — círculos de unos 30 cm, finos en el centro y con el borde un poco más alto.
Extendé la salsa dejando 2 cm sin cubrir en los bordes.
Distribuí la mozzarella cortada en rodajas o desmenuzada de manera irregular.

4. EL HORNEADO
Colocá la pizza sobre la bandeja caliente y horneá 8 a 10 minutos, hasta que los bordes estén dorados y la mozzarella burbujee con manchas doradas.
Al sacarla del horno: albahaca fresca, un hilo de aceite de oliva y, si querés, sal en escamas.
Comela de inmediato.


⚡ CLAVES PARA QUE QUEDE BIEN

- La bandeja tiene que estar caliente antes de poner la pizza. Es lo que hace que la base quede crocante.
- No pongas demasiada salsa ni demasiado queso — la pizza napolitana es generosa en bordes y discreta en el relleno.
- Estirá con las manos, no con palote: preservás el aire de la masa y los bordes quedan más esponjosos.
- Si la masa se retrae al estirar, dejala descansar 5 minutos tapada y volvé a intentar.
- La mozzarella de búfala tiene mucha agua: si la usás, secala sobre papel antes de ponerla.


🔥 VARIACIONES

- Con parmesano: dos cucharadas de parmesano rallado sobre la mozzarella antes de hornear
- Marinara (sin queso): solo salsa, ajo en láminas y orégano — la pizza más antigua de todas
- Cuatro quesos: mozzarella + provolone + gorgonzola + parmesano
"""

PIZZA_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/"
    "Eq_it-na_pizza-margherita_sep2005_sml.jpg/1280px-Eq_it-na_pizza-margherita_sep2005_sml.jpg"
)


# ── Receta 2: Pasta Alfredo ──────────────────────────────────────────────────

ALFREDO_CUERPO = """\
Pocos platos son tan satisfactorios como un buen Alfredo. Solo necesitás cuatro ingredientes
y veinte minutos. El truco está en la técnica, no en los ingredientes.

🍝 INGREDIENTES (2 porciones)

- 280 g spaghetti o fettuccine
- 4 cdas manteca sin sal
- 1 diente de ajo grande
- 1 taza y media de crema de leche (crema doble)
- 80 g parmesano recién rallado, más extra para servir
- Sal y pimienta blanca a gusto
- Perejil fresco picado para decorar


📋 CÓMO SE HACE

1. HERVIR LA PASTA
Poné agua abundante a hervir con bastante sal (tiene que saber a mar).
Cocinás la pasta según el paquete, un minuto menos del tiempo indicado para que quede al dente.
Antes de escurrir, reservá media taza del agua de cocción: tiene almidón y va a ayudar a ligar la salsa.

2. LA SALSA
Mientras hierve la pasta, derretí la manteca en una sartén grande a fuego medio-bajo.
Agregá el ajo finamente picado o rallado y cocinalo 2 o 3 minutos sin que se dore demasiado — tiene que perfumar, no amargar.
Volcá la crema y dejá reducir a fuego medio durante 10 a 12 minutos, revolviendo cada tanto. La salsa tiene que espesar y burbujear suavemente. Sabés que está lista cuando al pasar una cuchara de madera deja un rastro limpio.
Salpimentá.

3. UNIR TODO
Pasá la pasta directamente desde la olla a la sartén con la salsa, usando pinzas o directamente con la pasta chorreando un poco de agua.
Bajá el fuego al mínimo. Agregá el parmesano de a poco, mezclando continuamente con pinzas o un tenedor, para que se funda de manera pareja sin hacerse grumos.
Si la salsa queda muy espesa, agregá de a cucharadas el agua de cocción reservada hasta que la pasta esté cremosa y bien napada.
Probá y ajustá sal.

4. SERVIR
Serví de inmediato en platos calientes. Decorá con perejil picado, más parmesano rallado y un giro de pimienta negra.
El Alfredo no espera — se come en el momento.


⚡ CLAVES PARA QUE QUEDE BIEN

- Rallá el parmesano al momento. El pre-rallado lleva celulosa antiaglomerante que impide que funda bien.
- Nunca fuego alto con la crema. La paciencia de esos 10 minutos es lo que hace la diferencia.
- Agregá el queso de a poco y mezclá sin parar: ese es el secreto para una salsa sedosa.
- Usá platos precalentados o la pasta se enfría antes de llegar a la mesa.
- Si sobra, calentala con un chorrito de crema a fuego muy suave, revolviendo.


🔥 VARIACIONES

- Con pollo grillado: pechugas condimentadas con páprika y ajo, cortadas en tiras, encima de la pasta
- Con champiñones: saltear 200 g de hongos con el ajo antes de agregar la crema
- Versión con limón: una cdita de ralladura de limón al final, cambia todo
- Fettuccine Alfredo: la versión clásica romana, con fettuccine en lugar de spaghetti
"""

ALFREDO_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/"
    "Fettucine_Alfredo_%284%29.jpg/1280px-Fettucine_Alfredo_%284%29.jpg"
)


# ── Receta 3: Cheesecake ─────────────────────────────────────────────────────

CHEESECAKE_CUERPO = """\
Una tarta de queso que vale la pena hacer. Base crocante de galleta, relleno cremoso y aireado,
y ese momento perfecto cuando la sacás del horno con el centro todavía tembloroso.

🧀 INGREDIENTES (molde de 20 cm, 8 porciones)

Base:
- 200 g galletas María (o cualquier galleta dulce seca)
- 90 g manteca derretida

Relleno:
- 500 g queso crema a temperatura ambiente
- 200 ml crema de leche
- 4 huevos grandes
- 120 g azúcar
- 1 cda harina o maicena
- 1 cdita esencia de vainilla


📋 CÓMO SE HACE

1. LA BASE
Procesá las galletas hasta que queden como arena fina. Si no tenés procesadora, metelas en una bolsa y aplastálas con un palo de amasar.
Mezclá el polvo de galleta con la manteca derretida hasta que todo quede húmedo y se una.
Volcá en un molde desmontable de 20 cm forrado con papel manteca. Presioná con el fondo de un vaso para compactar bien, subiendo un poco por los bordes.
Llevá a la heladera mientras preparás el relleno.

2. EL RELLENO
En un bowl grande batí el queso crema con el azúcar y la vainilla, solo hasta integrar — no hace falta batir mucho.
Agregá los huevos de a uno, mezclando suavemente después de cada uno. La clave es no incorporar aire: batido lento, movimientos envolventes.
Sumá la crema y la maicena, integrá hasta que todo quede liso y sin grumos.

3. HORNEAR
Precalentá el horno a 175 °C.
Sacá la base de la heladera y volcá el relleno encima.
Horneá 35 a 40 minutos. La tarta está lista cuando los bordes están firmes pero el centro todavía tiembla un poco — como una gelatina. Eso es lo que querés.

4. EL ENFRIADO (la parte más importante)
Apagá el horno, dejá la puerta entreabierta con la ayuda de una cuchara de madera y dejá la tarta dentro 15 minutos más.
Sacala del horno y dejá que llegue a temperatura ambiente en la mesada, sin apuro.
Cubrí con film y metela en la heladera al menos 4 horas. De un día para el otro queda mucho mejor.
Desmoldá fría.


⚡ CLAVES PARA QUE QUEDE BIEN

- El queso crema tiene que estar a temperatura ambiente o va a quedar con grumos. Sacalo de la heladera una hora antes.
- No batas demasiado — el aire en el relleno hace que se agriete en el horno.
- El centro tembloroso no es falta de cocción: es lo que le da esa textura cremosa que distingue una buena cheesecake.
- El enfriado gradual dentro del horno evita el "crack" clásico en la superficie.
- Cortála con un cuchillo pasado por agua caliente para cortes limpios.


🔥 VARIACIONES

- Con frutillas: cubrí con 200 g de frutillas salteadas con 2 cdas de azúcar y jugo de limón
- Con dulce de leche: una capa fina de dulce de leche sobre la base antes del relleno
- Cheesecake japonesa: reemplazá la mitad del queso crema por ricotta y los huevos batí las claras a nieve — queda más suave y esponjosa
- Sin horno: reemplazá los huevos por 10 g de gelatina sin sabor disuelta en crema caliente; refrigerá 6 horas
"""

CHEESECAKE_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/"
    "NY_Cheesecake.jpg/1280px-NY_Cheesecake.jpg"
)
CHEESECAKE_IMAGE_FALLBACK = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/"
    "Cheesecake_with_blueberry_sauce.jpg/1280px-Cheesecake_with_blueberry_sauce.jpg"
)


# ── Helpers ──────────────────────────────────────────────────────────────────

SYSTEM_USERNAME = 'nido_sistema'


def _load_image(filename, remote_url, fallback_url=None, timeout=10):
    """
    Carga una imagen: primero busca en static/img/ (archivo commiteado),
    si no existe descarga desde remote_url o fallback_url.
    Retorna (ContentFile, source_label) o (None, None).
    """
    static_path = Path(settings.BASE_DIR) / 'static' / 'img' / filename
    if static_path.exists():
        return ContentFile(static_path.read_bytes()), 'static'

    for url in filter(None, [remote_url, fallback_url]):
        try:
            resp = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200 and resp.content:
                return ContentFile(resp.content), url
        except Exception:
            pass
    return None, None


def _create_post_with_image(post, filename, image_url, fallback_url, stdout, style):
    """Guarda la imagen en el post y reporta el resultado."""
    content, source = _load_image(filename, image_url, fallback_url)
    if content:
        post.imagen.save(filename, content, save=True)
        label = 'static/img' if source == 'static' else 'descarga'
        stdout.write(style.SUCCESS(f"  ✅ imagen desde {label}"))
    else:
        post.save()
        stdout.write(style.WARNING(f"  ⚠️  sin imagen (no encontrada)"))


# ── Recetas a sembrar ────────────────────────────────────────────────────────

RECETAS = [
    {
        'titulo':           'Pizza Margherita 🍕',
        'subtitulo':        'Masa, tomate, mozzarella, albahaca — y nada más',
        'cuerpo':           PIZZA_CUERPO,
        'imagen_url':       PIZZA_IMAGE_URL,
        'imagen_fallback':  None,
        'imagen_filename':  'pizza_margherita.jpg',
        'precio_monedas':   0,
    },
    {
        'titulo':           'Pasta Alfredo 🍝',
        'subtitulo':        'Manteca, crema y parmesano — lista en 20 minutos',
        'cuerpo':           ALFREDO_CUERPO,
        'imagen_url':       ALFREDO_IMAGE_URL,
        'imagen_fallback':  None,
        'imagen_filename':  'pasta_alfredo.jpg',
        'precio_monedas':   0,
    },
    {
        'titulo':           'Cheesecake Clásica 🧀',
        'subtitulo':        'Base crocante, relleno cremoso, centro tembloroso',
        'cuerpo':           CHEESECAKE_CUERPO,
        'imagen_url':       CHEESECAKE_IMAGE_URL,
        'imagen_fallback':  CHEESECAKE_IMAGE_FALLBACK,
        'imagen_filename':  'cheesecake.jpg',
        'precio_monedas':   50,  # receta premium
    },
]

# ── Quesos a sembrar ─────────────────────────────────────────────────────────

QUESOS = [
    {
        'nombre':          'Mozzarella Fresca 🧀',
        'descripcion':     'Suave y cremosa. Imprescindible para pizzas, ensaladas caprese y cualquier cosa que merezca derretirse.',
        'stock':           20,
        'precio':          '1200.00',
        'precio_monedas':  15,
    },
    {
        'nombre':          'Parmesano Reggiano 🫙',
        'descripcion':     'Curado 24 meses. Granulado, intenso, salado. Rallado sobre pasta o en láminas sobre cualquier cosa.',
        'stock':           15,
        'precio':          '2800.00',
        'precio_monedas':  25,
    },
    {
        'nombre':          'Ricotta Fresca 🥣',
        'descripcion':     'Liviana y suave. Perfecta para rellenos, postres, tostadas y como base de salsas cremosas.',
        'stock':           25,
        'precio':          '900.00',
        'precio_monedas':  10,
    },
    {
        'nombre':          'Gorgonzola 💙',
        'descripcion':     'Azul, fuerte y cremoso. Para quienes saben lo que quieren: riesgo, sabor y carácter.',
        'stock':           10,
        'precio':          '3200.00',
        'precio_monedas':  30,
    },
    {
        'nombre':          'Provolone Ahumado 🔥',
        'descripcion':     'Semiduro, elástico y con ese toque ahumado que lo distingue. Ideal para sandwich, tabla y gratinar.',
        'stock':           18,
        'precio':          '1800.00',
        'precio_monedas':  20,
    },
    {
        'nombre':          'Queso Crema 🍰',
        'descripcion':     'Untable, fresco y versátil. La base de la cheesecake y el secreto de mil rellenos.',
        'stock':           22,
        'precio':          '750.00',
        'precio_monedas':  12,
    },
]


# ── Command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Crea contenido inicial del nido (idempotente)"

    # Títulos renombrados en versiones anteriores del seed — se eliminan sin importar el autor
    TITULOS_OBSOLETOS = [
        'Pizza Margherita Clásica 🍕',
        'Pasta Alfredo Cremosa 🍝',
    ]

    def _get_or_create_autor(self):
        """Devuelve el primer superuser, o crea un usuario sistema como fallback."""
        autor = User.objects.filter(is_superuser=True).order_by('pk').first()
        if autor:
            return autor
        autor, created = User.objects.get_or_create(
            username=SYSTEM_USERNAME,
            defaults={
                'first_name': 'Nido',
                'last_name': 'Mozzarella',
                'is_staff': False,
                'is_superuser': False,
            },
        )
        if created:
            autor.set_unusable_password()
            autor.save()
            self.stdout.write(self.style.WARNING(
                f"Creado usuario sistema '{SYSTEM_USERNAME}' como autor."
            ))
        return autor

    def _seed_recetas(self, autor):
        """Crea las recetas del nido (idempotente por título)."""
        # Limpiar duplicados de versiones anteriores (cualquier autor)
        eliminados = Post.objects.filter(titulo__in=self.TITULOS_OBSOLETOS).delete()
        if eliminados[0]:
            self.stdout.write(self.style.WARNING(
                f"Eliminados {eliminados[0]} posts con títulos obsoletos."
            ))

        for receta in RECETAS:
            post, created = Post.objects.get_or_create(
                titulo=receta['titulo'],
                defaults={
                    'subtitulo':      receta['subtitulo'],
                    'cuerpo':         receta['cuerpo'],
                    'autor':          autor,
                    'precio_monedas': receta['precio_monedas'],
                },
            )

            if not created:
                self.stdout.write(self.style.SUCCESS(f"'{receta['titulo']}' ya existe — ok."))
                continue

            self.stdout.write(f"Creando '{receta['titulo']}'...")
            _create_post_with_image(
                post,
                receta['imagen_filename'],
                receta['imagen_url'],
                receta.get('imagen_fallback'),
                self.stdout,
                self.style,
            )

    def _seed_quesos(self):
        """Crea los quesos del inventario (idempotente por nombre)."""
        for data in QUESOS:
            queso, created = Queso.objects.get_or_create(
                nombre=data['nombre'],
                defaults={
                    'descripcion':    data['descripcion'],
                    'stock':          data['stock'],
                    'precio':         data['precio'],
                    'precio_monedas': data['precio_monedas'],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Queso '{queso.nombre}' creado."))
            else:
                self.stdout.write(f"  · Queso '{queso.nombre}' ya existe — ok.")

    def handle(self, *args, **options):
        autor = self._get_or_create_autor()
        self._seed_recetas(autor)
        self.stdout.write("Sembrando quesos...")
        self._seed_quesos()
        self.stdout.write(self.style.SUCCESS("seed_datos completado ✅"))
