# Importa la clase Game desde el módulo game.py
# Esto nos permite crear una instancia de nuestro juego y usar sus funcionalidades.
from game import Game

# Importa el módulo pygame.
# Aunque la mayor parte de la interacción con Pygame ocurre dentro de la clase Game,
# es una buena práctica importarlo aquí para asegurarnos de que esté disponible
# si fuera necesario para funciones de alto nivel o para el cierre final.
import pygame

# Este bloque de código es un estándar en Python para asegurar que cierto código
# solo se ejecute cuando el script es el programa principal (no cuando es importado como módulo).
# En nuestro caso, queremos que el juego se inicie solo cuando ejecutamos main.py directamente.
if __name__ == "__main__":
    # 1. Crear una instancia del juego:
    # Aquí creamos un objeto 'game' a partir de la clase 'Game'.
    # Al hacer esto, se llama automáticamente al método __init__ de la clase Game,
    # lo que inicializa Pygame, configura la pantalla, carga recursos, etc.
    game = Game()

    # 2. Ejecutar el bucle principal del juego:
    # Llamamos al método 'run()' de nuestro objeto 'game'.
    # Este método contiene el bucle principal del juego (el "game loop")
    # que se encarga de manejar eventos, actualizar la lógica del juego y dibujar en pantalla,
    # todo ello repetidamente a una velocidad constante (definida por el `clock.tick(60)` en `game.py`).
    game.run()

    # 3. Cerrar Pygame:
    # Una vez que el bucle `game.run()` termina (por ejemplo, porque el usuario cerró la ventana),
    # esta línea se ejecuta. `pygame.quit()` desinicializa todos los módulos de Pygame que se hayan
    # inicializado (como el de gráficos, sonido, etc.).
    # Es crucial llamar a esto para liberar los recursos del sistema y cerrar la ventana de Pygame
    # de manera limpia, evitando posibles errores o que el programa se quede "colgado" en segundo plano.
    pygame.quit()