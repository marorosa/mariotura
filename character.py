# --- Importaciones ---
import pygame  # Importa la librería Pygame para gráficos y funcionalidades de juego.
from constants import * # Importa todas las constantes, como GRAVITY, PLAYER_NORMAL_SIZE, etc.

# --- Clase Base: Personaje ---
class Personaje:
    def __init__(self, id, nombre, x, y, estado="Vivo"):
        """
        Constructor de la clase base Personaje.
        Representa cualquier entidad con posición, nombre y estado en el juego (jugador, enemigos).

        Args:
            id (int): Identificador único del personaje.
            nombre (str): Nombre del personaje (ej., "Mario", "Goomba").
            x (int): Posición inicial en el eje X de la pantalla.
            y (int): Posición inicial en el eje Y de la pantalla.
            estado (str, optional): Estado actual del personaje (ej., "Vivo", "Muerto"). Por defecto es "Vivo".
        """
        self.id = id
        self.nombre = nombre
        self.posicionX = x          # Posición horizontal del personaje.
        self.posicionY = y          # Posición vertical del personaje.
        self.estado = estado        # Estado del personaje.
        self.image = None           # Superficie de Pygame que representa la imagen actual.
        # Rect inicial con tamaño mínimo; se ajustará cuando se cargue la imagen real.
        self.rect = pygame.Rect(x, y, 1, 1) 
        self.grounded = True        # Booleano: True si el personaje está tocando el suelo.
        self.velocidadY = 0         # Velocidad vertical, usada para gravedad y salto.

    def mover(self, dx=0, dy=0):
        """
        Mueve el personaje por los valores especificados en dx y dy.
        Actualiza tanto las posiciones `posicionX`, `posicionY` como el `rect`.

        Args:
            dx (int, optional): Cambio en la posición X. Por defecto es 0.
            dy (int, optional): Cambio en la posición Y. Por defecto es 0.
        """
        self.posicionX += dx # Actualiza la posición horizontal.
        self.posicionY += dy # Actualiza la posición vertical.
        if self.rect:
            # Si el rectángulo existe, actualiza su posición para que coincida con el personaje.
            self.rect.x = self.posicionX
            self.rect.y = self.posicionY
            
    def set_image(self, image_surface, target_size=None, flip_x=False):
        """
        Asigna una imagen al personaje, la escala y opcionalmente la voltea.
        Ajusta el `rect` manteniendo la parte inferior del personaje en la misma posición Y
        para evitar que el personaje se "hunda" o "levante" al cambiar de tamaño (ej. Mario Grande).

        Args:
            image_surface (pygame.Surface): La superficie de Pygame de la imagen original.
            target_size (tuple, optional): Una tupla (ancho, alto) para escalar la imagen.
                                           Si es None, la imagen no se escala.
            flip_x (bool, optional): Si True, la imagen se voltea horizontalmente. Por defecto es False.
        """
        # Guardar la posición inferior actual del rectángulo para mantenerla después del escalado.
        # Si el rect aún no se ha inicializado correctamente (altura muy pequeña), usa self.posicionY como base.
        old_rect_bottom = self.rect.bottom if self.rect and self.rect.height > 1 else self.posicionY

        if target_size:
            # Escala la imagen a target_size si se proporciona.
            scaled_image = pygame.transform.scale(image_surface, target_size)
        else:
            # Usa la imagen original si no se especifica un tamaño.
            scaled_image = image_surface

        if flip_x:
            # Voltea la imagen horizontalmente si flip_x es True.
            self.image = pygame.transform.flip(scaled_image, True, False)
        else:
            self.image = scaled_image
        
        # Crea un nuevo rectángulo a partir de la imagen (escalada/volteada).
        new_rect = self.image.get_rect()
        new_rect.x = self.posicionX        # Establece la posición X del nuevo rectángulo.
        new_rect.bottom = old_rect_bottom  # Establece la parte inferior del nuevo rectángulo en la posición guardada.
        
        self.rect = new_rect               # Asigna el nuevo rectángulo al personaje.
        self.posicionY = self.rect.y       # Sincroniza `posicionY` con la parte superior del nuevo rectángulo.

    def aplicar_gravedad(self):
        """
        Aplica la gravedad al personaje, incrementando su velocidad Y si no está en el suelo.
        También maneja la colisión con el suelo (SCREEN_HEIGHT - GROUND_LEVEL_OFFSET).
        """
        if not self.grounded:
            self.velocidadY += GRAVITY # Incrementa la velocidad Y por la constante de gravedad.
            self.mover(dy=self.velocidadY) # Mueve el personaje verticalmente.
            
            # Calcula la posición Y del "suelo" para el borde inferior del personaje.
            floor_y_for_char_bottom = SCREEN_HEIGHT - GROUND_LEVEL_OFFSET
            
            # Si el personaje ha caído por debajo del suelo:
            if self.rect.bottom >= floor_y_for_char_bottom:
                self.rect.bottom = floor_y_for_char_bottom # Ajusta la parte inferior del rect al suelo.
                self.posicionY = self.rect.y               # Sincroniza posicionY.
                self.velocidadY = 0                        # Detiene la caída.
                self.grounded = True                       # Marca al personaje como en el suelo.
                self.is_jumping = False                    # Asegura que el estado de salto se reinicie.

# --- Clase Enemigo (Hereda de Personaje) ---
class Enemigo(Personaje):
    def __init__(self, id, nombre, x, y, velocidad_x, estado="Vivo"):
        """
        Constructor de la clase Enemigo. Representa un enemigo móvil en el juego.

        Args:
            id (int): Identificador único del enemigo.
            nombre (str): Nombre del enemigo.
            x (int): Posición inicial en el eje X.
            y (int): Posición inicial en el eje Y.
            velocidad_x (int): Velocidad horizontal del enemigo.
            estado (str, optional): Estado actual del enemigo. Por defecto es "Vivo".
        """
        super().__init__(id, nombre, x, y, estado)
        self.velocidad_x = velocidad_x # Velocidad horizontal específica del enemigo.
        self.grounded = False          # Los enemigos pueden empezar en el aire y caer.

    def update(self, scroll_speed=0):
        """
        Actualiza el estado del enemigo en cada fotograma.
        Mueve el enemigo horizontalmente y aplica gravedad.

        Args:
            scroll_speed (int, optional): La velocidad de desplazamiento del mundo en el eje X.
                                          Los enemigos se moverán en la dirección opuesta al scroll del mundo.
        """
        # Mueve el enemigo considerando su propia velocidad y el desplazamiento del mundo.
        self.mover(dx=self.velocidad_x + scroll_speed)
        self.aplicar_gravedad() # Aplica la gravedad para que caiga si no está en el suelo.

# --- Clase Goomba (Hereda de Enemigo) ---
class Goomba(Enemigo):
    def __init__(self, id, x, y, velocidad_x=-GOOMBA_SPEED):
        """
        Constructor de la clase Goomba. Representa un enemigo Goomba específico.

        Args:
            id (int): Identificador único del Goomba.
            x (int): Posición inicial en el eje X.
            y (int): Posición inicial en el eje Y.
            velocidad_x (int, optional): Velocidad horizontal inicial del Goomba.
                                         Por defecto es -GOOMBA_SPEED (se mueve a la izquierda).
        """
        # Llama al constructor de Enemigo con los detalles específicos de Goomba.
        super().__init__(id, "Goomba", x, y, velocidad_x, "Vivo")
        # Ajusta el rectángulo inicial al tamaño definido para Goomba.
        self.rect = pygame.Rect(x, y, GOOMBA_SIZE[0], GOOMBA_SIZE[1])

# --- Clase Jugador (Hereda de Personaje) ---
class Jugador(Personaje):
    def __init__(self, id, nombre, x, y):
        """
        Constructor de la clase Jugador. Representa el personaje principal (Mario).

        Args:
            id (int): Identificador único del jugador.
            nombre (str): Nombre del jugador (ej., "Mario").
            x (int): Posición inicial en el eje X.
            y (int): Posición inicial en el eje Y.
        """
        super().__init__(id, nombre, x, y, "Vivo")
        self.is_ducking = False     # Booleano: True si el jugador está agachado.
        self.vidas = 3              # Número de vidas del jugador.
        self.monedas = 0            # Número de monedas recolectadas.
        self.puntos = 0             # Puntuación del jugador.
        self.tiempo = 300           # Tiempo restante en el nivel.
        self.dispara = False        # Booleano: True si el jugador puede disparar (Mario de fuego).
        self.direccion = "right"    # Dirección actual mirando ("right" o "left").
        self.tamaño = "normal"      # Tamaño actual del jugador ("normal" o "grande").
        self.inmune = False         # Booleano: True si el jugador es inmune (por estrella).
        self.inmunidad_timer = None # py.time.get_ticks() al inicio de la inmunidad.
        self.is_jumping = False     # Booleano: True si el jugador está en un salto (ascendiendo o cayendo por salto).
        self.jump_key_held = False  # Booleano: True si la tecla de salto está siendo mantenida.
        self.is_running = False     # Booleano: True si el jugador está corriendo.
        self.is_moving = False      # Booleano: True si el jugador se está moviendo horizontalmente.

        # Estado de animación
        self.current_frame_index = 0    # Índice del frame actual de la animación.
        self.last_frame_update = pygame.time.get_ticks() # Última vez que se actualizó el frame.

        # Almacenamiento de imágenes para diferentes estados y tamaños.
        # Se prefiere cargar las imágenes base y luego escalarlas o voltearlas según se necesite.
        self.images = {
            "idle_right": None,     # Imagen de Mario quieto mirando a la derecha.
            "idle_left": None,      # Imagen de Mario quieto mirando a la izquierda.
            "run_right": [],        # Lista de imágenes para la animación de correr a la derecha.
            "run_left": [],         # Lista de imágenes para la animación de correr a la izquierda.
            "jump_right": None,     # Imagen de Mario saltando a la derecha.
            "jump_left": None,      # Imagen de Mario saltando a la izquierda.
            "duck": None            # Imagen de Mario agachado.
        }
        
    def load_player_images(self, imgs_dict):
        """
        Carga y prepara todas las imágenes base de Mario (normal).
        Las imágenes se escalarán a "grande" o "normal" en el método `set_current_animation_frame`.

        Args:
            imgs_dict (dict): Un diccionario que contiene las superficies de Pygame precargadas,
                              con claves como "mario_normal", "mario_corriendo_derecha_1", etc.
        """
        # Asigna las imágenes a los estados base. Si no existe una versión "_izquierda", la voltea.
        self.images["idle_right"] = imgs_dict["mario_normal"]
        self.images["idle_left"] = imgs_dict.get("mario_normal_izquierda", 
                                                 pygame.transform.flip(imgs_dict["mario_normal"], True, False))

        # Configura los frames de la animación de correr.
        # Puedes añadir más frames si tienes una animación más compleja.
        self.images["run_right"].append(imgs_dict["mario_normal"]) 
        self.images["run_right"].append(imgs_dict["mario_corriendo_derecha_1"])

        self.images["run_left"].append(imgs_dict.get("mario_normal_izquierda", 
                                                  pygame.transform.flip(imgs_dict["mario_normal"], True, False))) 
        self.images["run_left"].append(imgs_dict["mario_corriendo_izquierda_1"])
        
        # Para la pose de salto, usamos la imagen "idle" por simplicidad, pero se podría tener una imagen específica.
        self.images["jump_right"] = imgs_dict["mario_normal"]
        self.images["jump_left"] = imgs_dict.get("mario_normal_izquierda", 
                                                 pygame.transform.flip(imgs_dict["mario_normal"], True, False))

        self.images["duck"] = imgs_dict["mario_agachado"] # Imagen para agacharse.

        # Una vez cargadas las imágenes, establece el frame de animación inicial.
        self.set_current_animation_frame()

    def set_current_animation_frame(self):
        """
        Determina y establece la imagen actual de Mario basándose en su estado (agachado, saltando,
        corriendo, quieto) y su tamaño ("normal" o "grande").
        Mantiene la base del personaje en la misma posición Y al cambiar de tamaño o estado.
        """
        current_time = pygame.time.get_ticks() # Tiempo actual para controlar la velocidad de la animación.
        
        # Determinar el tamaño objetivo según el atributo self.tamaño del jugador.
        if self.tamaño == "normal":
            target_size = PLAYER_NORMAL_SIZE
            target_duck_size = PLAYER_DUCK_SIZE
        elif self.tamaño == "grande":
            target_size = PLAYER_BIG_SIZE
            # Ajustar el tamaño de agacharse para Mario Grande.
            # Puedes definir una constante PLAYER_BIG_DUCK_SIZE si el tamaño es fijo.
            target_duck_size = (PLAYER_BIG_SIZE[0], int(PLAYER_BIG_SIZE[1] * 0.7)) # Ejemplo: 70% de la altura de Mario grande
        else:
            # Por defecto, si el tamaño no es reconocido, usa el tamaño normal.
            target_size = PLAYER_NORMAL_SIZE 
            target_duck_size = PLAYER_DUCK_SIZE

        # Guardar la parte inferior del rect antes de cualquier cambio para mantenerla al reescalar.
        old_rect_bottom = self.rect.bottom

        # 1. Lógica para agacharse (tiene prioridad sobre otras animaciones si el jugador está agachado).
        if self.is_ducking:
            # Usar la imagen de agacharse y escalarla al tamaño de pato correspondiente.
            # Voltea la imagen si la dirección es "left".
            self.set_image(self.images["duck"], target_duck_size, flip_x=(self.direccion == "left"))
            # Asegurar que el jugador agachado esté en el suelo.
            self.rect.bottom = SCREEN_HEIGHT - GROUND_LEVEL_OFFSET 
            self.posicionY = self.rect.y # Sincroniza posicionY con el rect.
            return # Termina la función aquí si está agachado.

        # 2. Lógica para salto/caída (tiene prioridad sobre correr/quieto si no está agachado).
        if not self.grounded: 
            if self.direccion == "right":
                # Usa la imagen de salto a la derecha y la escala al tamaño actual del jugador.
                self.set_image(self.images["jump_right"], target_size) 
            else:
                # Usa la imagen de salto a la izquierda y la escala.
                self.set_image(self.images["jump_left"], target_size) 
            # Se asume que la posición Y ya se maneja por la gravedad, solo se actualiza X.
            self.rect.topleft = (self.posicionX, self.posicionY) 
            return # Termina la función aquí si está saltando/cayendo.

        # 3. Lógica para correr/movimiento (solo si no está agachado o saltando/cayendo).
        if self.is_moving:
            # Actualiza el frame de la animación de correr si ha pasado suficiente tiempo.
            if current_time - self.last_frame_update > PLAYER_RUN_ANIMATION_SPEED:
                # Avanza al siguiente frame; usa el operador módulo para ciclar los frames.
                self.current_frame_index = (self.current_frame_index + 1) % len(self.images["run_right"])
                self.last_frame_update = current_time # Reinicia el temporizador de animación.

            if self.direccion == "right":
                # Establece la imagen actual de correr a la derecha y la escala.
                self.set_image(self.images["run_right"][self.current_frame_index], target_size) 
            else:
                # Establece la imagen actual de correr a la izquierda y la escala.
                self.set_image(self.images["run_left"][self.current_frame_index], target_size) 
        else: # Si no se está moviendo (está quieto).
            self.current_frame_index = 0 # Reinicia el índice del frame a 0 (primera pose de quieto).
            if self.direccion == "right":
                # Establece la imagen de quieto a la derecha y la escala.
                self.set_image(self.images["idle_right"], target_size) 
            else:
                # Establece la imagen de quieto a la izquierda y la escala.
                self.set_image(self.images["idle_left"], target_size) 
            
        # Asegurarse de que la parte inferior del jugador esté siempre en el suelo si está `grounded`.
        if self.grounded:
            self.rect.bottom = SCREEN_HEIGHT - GROUND_LEVEL_OFFSET
            self.posicionY = self.rect.y # Sincroniza posicionY con el rect.

    def try_jump(self):
        """
        Intenta iniciar un salto o añadir un impulso si ya está en el aire (salto más alto).
        Permite que el salto sea más alto si la tecla se mantiene presionada (variable jump_key_held).
        """
        if self.grounded:
            self.is_jumping = True      # Marca que el jugador está saltando.
            self.grounded = False       # Ya no está en el suelo.
            self.jump_key_held = True   # La tecla de salto está presionada.
            self.velocidadY = -JUMP_STRENGTH_MIN # Aplica una velocidad inicial de salto hacia arriba.
            self.set_current_animation_frame() # Actualiza la animación a la pose de salto.
        # Si el jugador está cayendo (velocidadY positiva) y no ha tocado el suelo, permite un pequeño "doble salto" o impulso.
        elif self.velocidadY > 0: 
            self.velocidadY = -JUMP_STRENGTH_MIN * JUMP_AIR_IMPULSE_FACTOR # Aplica un impulso menor en el aire.
            self.is_jumping = True      # Marca que el jugador sigue saltando.
            self.jump_key_held = True   # La tecla de salto está presionada.
            self.set_current_animation_frame() # Actualiza la animación a la pose de salto.
        elif self.velocidadY < 0 and self.jump_key_held: 
            # Si ya está ascendiendo en un salto y la tecla sigue presionada, no hace nada aquí.
            # La función `update_jump_height` manejará la aceleración continua.
            pass

    def end_jump_key(self):
        """
        Finaliza la fase de "mantener presionado" el salto.
        Si el jugador aún está ascendiendo, "corta" el salto para una caída más rápida.
        """
        self.jump_key_held = False # Marca que la tecla de salto ha sido liberada.
        if self.velocidadY < 0: # Si el jugador está ascendiendo (velocidadY negativa).
            self.velocidadY *= JUMP_CUT_FACTOR # Reduce la velocidad de ascenso para una caída más rápida.

    def update_jump_height(self):
        """
        Actualiza la altura del salto basándose en si la tecla de salto está siendo mantenida.
        Permite una aceleración adicional hacia arriba si la tecla se mantiene.
        """
        if self.is_jumping and self.jump_key_held and self.velocidadY < 0:
            self.velocidadY += JUMP_ACCELERATION_FACTOR # Aumenta la velocidad de ascenso (hace que suba más).
            # Limita la velocidad máxima de ascenso para evitar saltos infinitos o excesivamente altos.
            self.velocidadY = max(self.velocidadY, -JUMP_STRENGTH_MAX) 
        
    def update(self, scroll_speed=0):
        """
        Actualiza el estado general del jugador en cada fotograma.
        Aplica la gravedad, actualiza la altura del salto y gestiona las animaciones.

        Args:
            scroll_speed (int, optional): La velocidad de desplazamiento del mundo en el eje X.
                                          El jugador se moverá en la dirección opuesta al scroll del mundo.
        """
        self.update_jump_height() # Llama a la función para ajustar la altura del salto.
        self.aplicar_gravedad()   # Aplica la gravedad al jugador.
        # Aquí se añadiría la lógica para colisiones con enemigos, power-ups, etc.
        # También se podría pasar el scroll_speed a `mover` si el jugador se "mueve con el mundo"
        # en lugar de mover el mundo alrededor del jugador (lo cual es más común en juegos de plataformas).
        # Por ahora, el jugador se mantiene en su `posicionX` relativa a la pantalla.
        self.set_current_animation_frame() # Actualiza la imagen del jugador según su estado.