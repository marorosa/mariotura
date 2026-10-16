# --- Importaciones ---
import pygame  # Importa la librería Pygame, necesaria para el manejo de gráficos y rectángulos.
from constants import * # Importa todas las constantes definidas en constants.py.
                        # Esto incluye, por ejemplo, OBJECT_SPEED, MUSHROOM_SIZE, etc.

# --- Clase Base: Poder ---
class Poder:
    def __init__(self, id, nombre, descripcion, x, y, estado="activo"):
        """
        Constructor de la clase base Poder.
        Representa un objeto genérico en el juego que el jugador puede recolectar o interactuar.

        Args:
            id (int): Identificador único del poder.
            nombre (str): Nombre del poder (ej., "Hongo de crecimiento").
            descripcion (str): Descripción del efecto del poder.
            x (int): Posición inicial en el eje X de la pantalla.
            y (int): Posición inicial en el eje Y de la pantalla.
            estado (str, optional): Estado actual del poder (ej., "activo", "recolectado"). Por defecto es "activo".
        """
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.posicionX = x          # Posición horizontal del poder.
        self.posicionY = y          # Posición vertical del poder.
        self.estado = estado        # Estado del poder.
        self.image = None           # Superficie de Pygame que representa la imagen actual del poder.
        self.rect = None            # Objeto Rect de Pygame para manejar la posición y las colisiones.
        self.original_image = None  # Almacena la imagen original antes de cualquier escalado.
                                    # Útil si necesitas reescalar o manipular la imagen base.
        
    def set_image(self, image, size=None):
        """
        Establece la imagen para el poder y crea su rectángulo de colisión.

        Args:
            image (pygame.Surface): La superficie de Pygame a usar como imagen del poder.
            size (tuple, optional): Una tupla (ancho, alto) para escalar la imagen.
                                    Si es None, la imagen se usa en su tamaño original.
        """
        self.original_image = image # Guarda la imagen original sin escalar.
        if size:
            # Si se proporciona un tamaño, escala la imagen.
            self.image = pygame.transform.scale(self.original_image, size)
        else:
            # Si no se proporciona tamaño, usa la imagen original tal cual.
            self.image = self.original_image
            
        # Si la imagen se ha cargado correctamente (no es None), crea su rectángulo.
        if self.image:
            self.rect = self.image.get_rect() # Obtiene un nuevo rectángulo que cubre toda la imagen.
            self.rect.x = self.posicionX      # Establece la posición X del rectángulo.
            self.rect.y = self.posicionY      # Establece la posición Y del rectángulo.
            
    def update(self, scroll_speed=0):
        """
        Actualiza el estado del poder en cada fotograma.
        Por defecto, los poderes se mueven hacia la izquierda para simular el desplazamiento del mundo.

        Args:
            scroll_speed (int, optional): La velocidad de desplazamiento del mundo en el eje X.
                                          Los objetos se moverán en la dirección opuesta al scroll del mundo.
        """
        # Mueve el poder hacia la izquierda a OBJECT_SPEED, ajustado por el desplazamiento del mundo.
        # Si scroll_speed es negativo (mundo se mueve a la izquierda), entonces se suma para compensar.
        self.mover(dx=OBJECT_SPEED + scroll_speed) 
        
    def mover(self, dx=0, dy=0):
        """
        Mueve el poder por los valores especificados en dx y dy.

        Args:
            dx (int, optional): Cambio en la posición X. Por defecto es 0.
            dy (int, optional): Cambio en la posición Y. Por defecto es 0.
        """
        self.posicionX += dx # Actualiza la posición X del poder.
        self.posicionY += dy # Actualiza la posición Y del poder.
        if self.rect:
            # Si el rectángulo existe, actualiza su posición para que coincida con la del poder.
            self.rect.x = self.posicionX
            self.rect.y = self.posicionY

# --- Clase Hongo (Hereda de Poder) ---
class Hongo(Poder):
    def __init__(self, id, x, y, tipo, estado="activo"):
        """
        Constructor de la clase Hongo. Representa un hongo de crecimiento o de vida.

        Args:
            id (int): Identificador único del hongo.
            x (int): Posición inicial en el eje X.
            y (int): Posición inicial en el eje Y.
            tipo (str): El tipo de hongo ("crecimiento" o "vida").
            estado (str, optional): Estado actual del hongo. Por defecto es "activo".
        """
        # Determina el nombre y la descripción del hongo basándose en su tipo.
        nombre = "Hongo de crecimiento" if tipo == "crecimiento" else "Hongo de vida"
        descripcion = "Hace crecer al jugador" if tipo == "crecimiento" else "Da una vida extra"
        
        # Llama al constructor de la clase base (Poder) para inicializar los atributos comunes.
        super().__init__(id, nombre, descripcion, x, y, estado)
        self.tipo = tipo # Atributo específico para el tipo de hongo.

# --- Clase Moneda (Hereda de Poder) ---
class Moneda(Poder):
    def __init__(self, id, x, y, estado="activa"):
        """
        Constructor de la clase Moneda. Representa una moneda recolectable.

        Args:
            id (int): Identificador único de la moneda.
            x (int): Posición inicial en el eje X.
            y (int): Posición inicial en el eje Y.
            estado (str, optional): Estado actual de la moneda. Por defecto es "activa".
        """
        # Llama al constructor de la clase base (Poder) con los detalles específicos de la moneda.
        super().__init__(id, "Moneda", "Otorga puntos y contribuye a una vida extra", x, y, estado)

# --- Clase Estrella (Hereda de Poder) ---
class Estrella(Poder):
    def __init__(self, id, x, y, estado="activa"):
        """
        Constructor de la clase Estrella. Representa una estrella de inmunidad.

        Args:
            id (int): Identificador único de la estrella.
            x (int): Posición inicial en el eje X.
            y (int): Posición inicial en el eje Y.
            estado (str, optional): Estado actual de la estrella. Por defecto es "activa".
        """
        # Llama al constructor de la clase base (Poder) con los detalles específicos de la estrella.
        super().__init__(id, "Estrella", "Otorga inmunidad temporal", x, y, estado)