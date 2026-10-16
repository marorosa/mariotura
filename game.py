import pygame
import random
import os
import sys
from pygame.locals import *
from constants import *
from character import Personaje, Enemigo, Goomba, Jugador
from powerup import Poder, Hongo, Moneda, Estrella

class Game:
    def __init__(self):
        """
        Constructor de la clase Game.
        Se encarga de inicializar Pygame, configurar la ventana, cargar recursos
        y establecer el estado inicial del juego.
        """
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario en Buenaventura")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.floor_y = SCREEN_HEIGHT - GROUND_LEVEL_OFFSET
        self.imgs = {}
        self.load_images()
        self.clouds = []
        self.palm_trees = []  # Lista para almacenar las palmeras
        self.cloud_spawn_timer = 0
        self.palm_spawn_timer = 0  # Temporizador para generar palmeras
        self.bg_width = self.imgs["fondo"].get_width() if "fondo" in self.imgs else SCREEN_WIDTH
        self.bg_x = 0
        self.last_spawn_x = 0
        self.music_path = os.path.join(os.getcwd(), "assets", "sound", "background_music.mp3")
        if os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)
        else:
            print(f"Advertencia: Archivo de música no encontrado en {self.music_path}.")
        self.game_running = False
        self.in_menu = True
        self.game_over = False
        self.players = []
        self.poderes_activos = []
        self.monedas_activas = []
        self.estrella_activa = None
        self.enemigos_activos = []
        self.total_goombas_generados = 0
        self.max_goombas = 2
        self.max_total_goombas = 10
        self.current_player = None
        self.spawn_timer = 0
        self.goomba_timer = 0
        self.immunity_timers = {}
        self.world_scroll_x = 0

    def load_images(self):
        """Carga todas las imágenes del juego."""
        for key, path in IMG_PATHS.items():
            full_path = os.path.join(os.getcwd(), path)
            try:
                if not os.path.exists(full_path):
                    print(f"Error: Imagen no encontrada en {full_path}. Usando marcador de posición para '{key}'.")
                    size = (30, 30)
                    if key.startswith("mario_"): size = PLAYER_NORMAL_SIZE
                    elif key == "goomba": size = GOOMBA_SIZE
                    elif key.startswith("nube"): size = (100, 50)
                    elif key.startswith("hongo_"): size = MUSHROOM_SIZE
                    elif key == "moneda": size = COIN_SIZE
                    elif key == "estrella": size = STAR_SIZE
                    elif key == "palmera": size = PALM_TREE_SIZE  # Tamaño para la palmera
                    placeholder_img = pygame.Surface(size, pygame.SRCALPHA)
                    placeholder_img.fill(RED if key.startswith("mario_") else BLUE)
                    pygame.draw.rect(placeholder_img, BLACK, placeholder_img.get_rect(), 1)
                    self.imgs[key] = placeholder_img
                    continue
                img = pygame.image.load(full_path).convert_alpha()
                if key == "fondo":
                    self.imgs[key] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                elif key.startswith("nube"):
                    self.imgs[key] = pygame.transform.scale(img, (100, 50))
                elif key.startswith("mario_"):
                    self.imgs[key] = img
                elif key.startswith("hongo_"):
                    self.imgs[key] = pygame.transform.scale(img, MUSHROOM_SIZE)
                elif key == "moneda":
                    self.imgs[key] = pygame.transform.scale(img, COIN_SIZE)
                elif key == "estrella":
                    self.imgs[key] = pygame.transform.scale(img, STAR_SIZE)
                elif key == "goomba":
                    self.imgs[key] = pygame.transform.scale(img, GOOMBA_SIZE)
                elif key == "palmera":
                    self.imgs[key] = pygame.transform.scale(img, PALM_TREE_SIZE)  # Escalar la palmera
            except pygame.error as e:
                print(f"Error de Pygame al cargar {full_path}: {e}. Usando marcador de posición para '{key}'.")
                size = (30, 30)
                if key.startswith("mario_"): size = PLAYER_NORMAL_SIZE
                elif key == "goomba": size = GOOMBA_SIZE
                placeholder_img = pygame.Surface(size, pygame.SRCALPHA)
                placeholder_img.fill(GREEN)
                pygame.draw.rect(placeholder_img, BLACK, placeholder_img.get_rect(), 1)
                self.imgs[key] = placeholder_img

        if "mario_normal" not in self.imgs:
            self.imgs["mario_normal"] = pygame.Surface(PLAYER_NORMAL_SIZE, pygame.SRCALPHA)
            self.imgs["mario_normal"].fill((0, 255, 0, 128))
        if "mario_normal_izquierda" not in self.imgs:
            self.imgs["mario_normal_izquierda"] = pygame.transform.flip(self.imgs["mario_normal"], True, False)
        if "mario_corriendo_derecha_1" not in self.imgs:
            self.imgs["mario_corriendo_derecha_1"] = self.imgs["mario_normal"]
        if "mario_corriendo_izquierda_1" not in self.imgs:
            self.imgs["mario_corriendo_izquierda_1"] = self.imgs["mario_normal_izquierda"]
        if "mario_agachado" not in self.imgs:
            self.imgs["mario_agachado"] = pygame.Surface(PLAYER_DUCK_SIZE, pygame.SRCALPHA)
            self.imgs["mario_agachado"].fill((0, 0, 255, 128))

    def spawn_clouds(self):
        """Genera nubes en el fondo de manera aleatoria."""
        current_time = pygame.time.get_ticks()
        if current_time - self.cloud_spawn_timer > random.randint(2000, 5000):
            self.cloud_spawn_timer = current_time
            cloud_type = random.choice(["nube1", "nube2", "nube3"])
            x_pos = SCREEN_WIDTH  # Aparecen fuera de la pantalla a la derecha
            y_pos = random.randint(50, 200)  # Altura aleatoria en la parte superior
            speed = random.uniform(0.5, 1.5)  # Velocidad lenta para efecto de parallax
            self.clouds.append({"type": cloud_type, "x": x_pos, "y": y_pos, "speed": speed})

    def update_clouds(self, scroll_speed=0):
        """Actualiza la posición de las nubes."""
        for cloud in self.clouds:
            cloud["x"] -= cloud["speed"]  # Las nubes se mueven más lento que el scroll
            cloud["x"] += scroll_speed * 0.2  # Efecto parallax (opcional)
        # Elimina nubes que salieron de la pantalla
        self.clouds = [cloud for cloud in self.clouds if cloud["x"] > -100]

    def spawn_palm_trees(self):
      """Genera palmeras en el fondo de manera aleatoria."""
      current_time = pygame.time.get_ticks()
       # Reducir el tiempo entre generación de palmeras para que aparezcan más frecuentemente
      if current_time - self.palm_spawn_timer > random.randint(2000, 4000):  # Cambiado de 4000-8000 a 2000-4000
        self.palm_spawn_timer = current_time
        x_pos = SCREEN_WIDTH  # Aparecen fuera de la pantalla a la derecha
        y_pos = self.floor_y - PALM_TREE_SIZE[1]  # Alineado con el suelo
        self.palm_trees.append({"x": x_pos, "y": y_pos})

    def update_palm_trees(self, scroll_speed=0):
       """Actualiza la posición de las palmeras."""
       for palm_tree in self.palm_trees:
        palm_tree["x"] -= scroll_speed + 1  # Añadido +1 para que se muevan un poco más rápido
      # Elimina palmeras que salieron de la pantalla
       self.palm_trees = [palm_tree for palm_tree in self.palm_trees if palm_tree["x"] > -PALM_TREE_SIZE[0]]

    def start_game(self):
        """Inicializa una nueva partida del juego."""
        self.players = []
        self.poderes_activos = []
        self.monedas_activas = []
        self.estrella_activa = None
        self.enemigos_activos = []
        self.total_goombas_generados = 0
        self.immunity_timers = {}
        self.world_scroll_x = 0
        self.clouds = []
        self.palm_trees = []  # Reinicia las palmeras
        self.in_menu = False
        self.game_running = True
        self.game_over = False
        p1 = Jugador(1, "Mario", SCREEN_WIDTH // 4, self.floor_y - PLAYER_NORMAL_SIZE[1])
        p1.load_player_images(self.imgs)
        self.players.append(p1)
        self.current_player = p1
        p1.set_current_animation_frame()
        self.spawn_timer = pygame.time.get_ticks()
        self.goomba_timer = pygame.time.get_ticks()
        self.cloud_spawn_timer = pygame.time.get_ticks()
        self.palm_spawn_timer = pygame.time.get_ticks()  # Inicializa el temporizador de palmeras
        if pygame.mixer.music.get_busy() == 0:
            if os.path.exists(self.music_path):
                pygame.mixer.music.play(-1)
            else:
                print(f"Advertencia: Archivo de música no encontrado en {self.music_path} al intentar reiniciar.")

    def spawn_objects(self):
        current_world_x = abs(self.world_scroll_x)
        if current_world_x - self.last_spawn_x > random.randint(300, 500):
            x_pos = current_world_x + SCREEN_WIDTH + random.randint(50, 200)
            object_type = random.choice(["hongo_crecimiento", "hongo_vida", "moneda", "estrella"])
            if object_type.startswith("hongo"):
                y_pos = self.floor_y - MUSHROOM_SIZE[1]
                tipo = object_type.split("_")[1]
                hongo = Hongo(len(self.poderes_activos), x_pos, y_pos, tipo)
                hongo.set_image(self.imgs[object_type], MUSHROOM_SIZE)
                self.poderes_activos.append(hongo)
            elif object_type == "moneda":
                y_pos = self.floor_y - random.randint(50, 150)
                moneda = Moneda(len(self.monedas_activas), x_pos, y_pos)
                moneda.set_image(self.imgs["moneda"], COIN_SIZE)
                self.monedas_activas.append(moneda)
            elif object_type == "estrella" and not self.estrella_activa:
                y_pos = self.floor_y - random.randint(80, 200)
                estrella = Estrella(1, x_pos, y_pos)
                estrella.set_image(self.imgs["estrella"], STAR_SIZE)
                self.estrella_activa = estrella
        self.last_spawn_x = current_world_x

    def spawn_goomba(self):
        """Genera enemigos (Goombas) en el juego."""
        current_time = pygame.time.get_ticks()
        if (current_time - self.goomba_timer > random.randint(2000, 5000)) and \
           (len(self.enemigos_activos) < self.max_goombas) and \
           (self.total_goombas_generados < self.max_total_goombas):
            self.goomba_timer = current_time
            x_pos = SCREEN_WIDTH + 50
            y_pos = self.floor_y - GOOMBA_SIZE[1]
            goomba = Goomba(len(self.enemigos_activos), x_pos, y_pos)
            goomba.set_image(self.imgs["goomba"], GOOMBA_SIZE)
            self.enemigos_activos.append(goomba)
            self.total_goombas_generados += 1

    def check_collision(self, rect1, rect2):
        """Verifica si dos rectángulos están colisionando."""
        if rect1 and rect2:
            return rect1.colliderect(rect2)
        return False

    def handle_collisions(self):
        """Maneja todas las colisiones del jugador con otros elementos del juego."""
        player = self.current_player
        if not player or not player.rect:
            return
        for hongo in list(self.poderes_activos):
            if self.check_collision(player.rect, hongo.rect):
                old_player_size = player.tamaño
                if hongo.tipo == "crecimiento":
                    player.tamaño = "grande"
                    player.puntos += 100
                elif hongo.tipo == "vida":
                    player.vidas += 1
                    player.tamaño = "grande"
                    player.puntos += 200
                if old_player_size != "grande" and player.tamaño == "grande":
                    height_diff = PLAYER_BIG_SIZE[1] - PLAYER_NORMAL_SIZE[1]
                    player.posicionY -= height_diff
                    player.rect.y = player.posicionY
                    player.set_current_animation_frame()
                self.poderes_activos.remove(hongo)
        for moneda in list(self.monedas_activas):
            if self.check_collision(player.rect, moneda.rect):
                player.monedas += 1
                player.puntos += 100
                self.monedas_activas.remove(moneda)
                if player.monedas >= 10:
                    player.vidas += 1
                    player.monedas = 0
                    player.puntos += 500
        if self.estrella_activa and self.check_collision(player.rect, self.estrella_activa.rect):
            player.puntos += 500
            player.inmune = True
            self.immunity_timers[player.id] = pygame.time.get_ticks()
            self.estrella_activa = None
        for goomba in list(self.enemigos_activos):
            if self.check_collision(player.rect, goomba.rect):
                if player.velocidadY > 0 and player.rect.bottom - player.velocidadY <= goomba.rect.centery:
                    player.puntos += 100
                    self.enemigos_activos.remove(goomba)
                    player.velocidadY = -JUMP_STRENGTH_MIN
                    player.grounded = False
                    player.is_jumping = True
                elif player.inmune:
                    player.puntos += 200
                    self.enemigos_activos.remove(goomba)
                else:
                    if player.tamaño == "grande":
                        player.tamaño = "normal"
                        player.inmune = True
                        self.immunity_timers[player.id] = pygame.time.get_ticks()
                        height_diff = PLAYER_BIG_SIZE[1] - PLAYER_NORMAL_SIZE[1]
                        player.posicionY += height_diff
                        player.rect.y = player.posicionY
                        player.set_current_animation_frame()
                    else:
                        player.vidas -= 1
                        if player.vidas <= 0:
                            player.estado = "Muerto"
                            self.game_over = True
                            self.game_running = False
                            pygame.mixer.music.stop()
                        else:
                            player.inmune = True
                            self.immunity_timers[player.id] = pygame.time.get_ticks()
                    self.enemigos_activos.remove(goomba)

    def update_immunity(self):
        """Actualiza el estado de inmunidad del jugador."""
        current_time = pygame.time.get_ticks()
        for player_id, start_time in list(self.immunity_timers.items()):
            if current_time - start_time > IMMUNITY_DURATION:
                for player in self.players:
                    if player.id == player_id:
                        player.inmune = False
                del self.immunity_timers[player_id]

    def update(self):
        """Actualiza el estado de todos los elementos del juego en cada fotograma."""
        if not self.game_running:
            return
        player = self.current_player
        if not player:
            return
        scroll_speed = 0
        if player.posicionX > SCREEN_WIDTH * 0.6 and player.direccion == "right":
            scroll_speed = -player.velocidadX
            player.posicionX = SCREEN_WIDTH * 0.6
        elif player.posicionX < SCREEN_WIDTH * 0.4 and player.direccion == "left" and self.world_scroll_x < 0:
            scroll_speed = -player.velocidadX
            player.posicionX = SCREEN_WIDTH * 0.4
        self.world_scroll_x += scroll_speed
        player.update()
        player.rect.x = player.posicionX
        self.spawn_objects()
        self.spawn_goomba()
        self.spawn_clouds()
        self.update_clouds(scroll_speed)
        self.spawn_palm_trees()  # Genera nuevas palmeras
        self.update_palm_trees(scroll_speed)  # Actualiza las posiciones de las palmeras
        for hongo in self.poderes_activos:
            hongo.update(scroll_speed)
        for moneda in self.monedas_activas:
            moneda.update(scroll_speed)
        if self.estrella_activa:
            self.estrella_activa.update(scroll_speed)
        for goomba in self.enemigos_activos:
            goomba.update(scroll_speed)
        self.poderes_activos = [obj for obj in self.poderes_activos if obj.posicionX > -obj.rect.width]
        self.monedas_activas = [obj for obj in self.monedas_activas if obj.posicionX > -obj.rect.width]
        if self.estrella_activa and self.estrella_activa.posicionX < -self.estrella_activa.rect.width:
            self.estrella_activa = None
        self.enemigos_activos = [obj for obj in self.enemigos_activos if obj.posicionX > -obj.rect.width]
        self.handle_collisions()
        self.update_immunity()

    def draw(self):
        """Dibuja todos los elementos del juego en la pantalla."""
        self.screen.fill(SKY_BLUE)

        # Dibuja las nubes primero (fondo)
        for cloud in self.clouds:
            cloud_img = self.imgs[cloud["type"]]
            self.screen.blit(cloud_img, (cloud["x"], cloud["y"]))

        # Dibuja las palmeras
        for palm_tree in self.palm_trees:
            self.screen.blit(self.imgs["palmera"], (palm_tree["x"], palm_tree["y"]))

        pygame.draw.rect(self.screen, BROWN, (0, self.floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.floor_y))

        for hongo in self.poderes_activos:
            if hongo.image and hongo.rect:
                self.screen.blit(hongo.image, hongo.rect)
        for moneda in self.monedas_activas:
            if moneda.image and moneda.rect:
                self.screen.blit(moneda.image, moneda.rect)
        if self.estrella_activa and self.estrella_activa.image and self.estrella_activa.rect:
            self.screen.blit(self.estrella_activa.image, self.estrella_activa.rect)
        for goomba in self.enemigos_activos:
            if goomba.image and goomba.rect:
                self.screen.blit(goomba.image, goomba.rect)
        if self.current_player and self.current_player.image and self.current_player.rect:
            if self.current_player.inmune and pygame.time.get_ticks() % 200 < 100:
                pass
            else:
                self.screen.blit(self.current_player.image, self.current_player.rect)

        if self.current_player:
            stats = [
                f"Vidas: {self.current_player.vidas}",
                f"Monedas: {self.current_player.monedas}",
                f"Puntos: {self.current_player.puntos}",
                f"Tamaño: {self.current_player.tamaño}",
                f"Inmune: {'Sí' if self.current_player.inmune else 'No'}"
            ]
            for i, stat in enumerate(stats):
                text = self.small_font.render(stat, True, BLACK)
                self.screen.blit(text, (10, 10 + i * 20))

        if self.in_menu:
            self.draw_menu()
        elif self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self):
        """Dibuja la pantalla del menú principal."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        title = self.font.render("MARIO EN BUENAVENTURA", True, WHITE)
        start_text = self.small_font.render("Presiona ESPACIO para iniciar", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def draw_game_over(self):
        """Dibuja la pantalla de fin de juego (Game Over)."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        game_over_text = self.font.render("GAME OVER", True, RED)
        restart_text = self.small_font.render("Presiona R para reiniciar", True, WHITE)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def handle_events(self):
        """Maneja los eventos de entrada del usuario."""
        keys = pygame.key.get_pressed()
        running = True
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if self.in_menu and event.key == K_SPACE:
                    self.start_game()
                elif self.game_over and event.key == K_r:
                    self.start_game()
                elif self.game_running and self.current_player:
                    if event.key in (K_LSHIFT, K_RSHIFT):
                        self.current_player.is_running = True
                    elif event.key == K_UP:
                        self.current_player.try_jump()
                    elif event.key == K_DOWN:
                        self.current_player.is_ducking = True
            if event.type == KEYUP and self.current_player:
                if event.key in (K_LSHIFT, K_RSHIFT):
                    self.current_player.is_running = False
                elif event.key == K_UP:
                    self.current_player.end_jump_key()
                elif event.key == K_DOWN:
                    self.current_player.is_ducking = False
        if self.game_running and self.current_player:
            if not self.current_player.is_ducking:
                speed = PASO_X * (RUNNING_MULTIPLIER if self.current_player.is_running else 1)
                self.current_player.is_moving = False
                if keys[K_RIGHT]:
                    self.current_player.direccion = "right"
                    self.current_player.mover(dx=speed)
                    self.current_player.is_moving = True
                    self.current_player.velocidadX = speed
                elif keys[K_LEFT]:
                    self.current_player.direccion = "left"
                    self.current_player.mover(dx=-speed)
                    self.current_player.is_moving = True
                    self.current_player.velocidadX = -speed
                else:
                    self.current_player.velocidadX = 0
            else:
                self.current_player.is_moving = False
                self.current_player.velocidadX = 0
        return running

    def run(self):
        """Bucle principal del juego."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()