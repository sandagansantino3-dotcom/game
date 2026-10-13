import sys
from pathlib import Path
import pygame

from battle_scene import BattleScene
from enemy import Enemy
from player import Player
from tilemap import TileMap
from transition_scene import BattleTransition
from map_scene import MapScene


pygame.init()

GAME_FOLDER = Path(__file__).parent

GAME_SIZE = (800, 450)
FULLSCREEN_SIZE = (1920, 1080)

windowed_size = GAME_SIZE
fullscreen = False

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    windowed_size,
    pygame.RESIZABLE
)

game_surface = pygame.Surface(GAME_SIZE)

pygame.display.set_caption("Miguel")

background_path = (
    GAME_FOLDER
    / "assets"
    / "backgrounds"
    / "bg1.png"
)

background = pygame.image.load(
    str(background_path)
).convert()

background = pygame.transform.scale(
    background,
    GAME_SIZE
)

tile_map = TileMap()

man = Player(
    80,
    200,
    80,
    80
)

goblin = Enemy(
    560,
    250,
    64,
    64,
    720
)

battle = BattleScene(
    man,
    goblin
)

map_scene = MapScene(
    man,
    goblin,
    tile_map,
    background
)

transition = BattleTransition()

current_scene = "map"
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif (
            event.type == pygame.VIDEORESIZE
            and not fullscreen
        ):
            windowed_size = (
                max(400, event.w),
                max(225, event.h)
            )

            screen = pygame.display.set_mode(
                windowed_size,
                pygame.RESIZABLE
            )

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_m:
                pygame.display.iconify()

            elif event.key == pygame.K_f:
                fullscreen = not fullscreen

                if fullscreen:
                    screen = pygame.display.set_mode(
                        FULLSCREEN_SIZE,
                        pygame.FULLSCREEN
                    )
                else:
                    screen = pygame.display.set_mode(
                        windowed_size,
                        pygame.RESIZABLE
                    )

            elif (
                event.key == pygame.K_SPACE
                and current_scene == "map"
                and not transition.active
            ):
                man.jump()

        if current_scene == "battle":
            battle.handle_event(event)

    if current_scene == "map":
        if not transition.active:
            touched_enemy = map_scene.update(
                pygame.key.get_pressed()
            )

            if touched_enemy:
                transition.start()

        map_scene.draw(game_surface)

    elif current_scene == "battle":
        battle.update()
        battle.draw(game_surface)

    if transition.active:
        if transition.update():
            current_scene = "battle"

        transition.draw(game_surface)

    display_width, display_height = (
        screen.get_size()
    )

    scale = min(
        display_width / GAME_SIZE[0],
        display_height / GAME_SIZE[1]
    )

    scaled_size = (
        int(GAME_SIZE[0] * scale),
        int(GAME_SIZE[1] * scale)
    )

    scaled_game = pygame.transform.scale(
        game_surface,
        scaled_size
    )

    screen.fill((0, 0, 0))

    screen.blit(
        scaled_game,
        (
            (
                display_width
                - scaled_size[0]
            ) // 2,
            (
                display_height
                - scaled_size[1]
            ) // 2
        )
    )

    pygame.display.flip()

pygame.quit()
sys.exit()