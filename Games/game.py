import sys
from pathlib import Path
import pygame

from battle_scene import BattleScene
from enemy import Enemy
from levels import LEVELS
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


def load_background(filename):
    """Load one background image and scale it to the screen."""
    path = GAME_FOLDER / "assets" / "backgrounds" / filename

    image = pygame.image.load(str(path)).convert()

    return pygame.transform.scale(image, SCREEN_SIZE)



man = Player(
    80,
    200,
    80,
    80
)


def load_level(index):
    """Build everything that changes from level to level."""
    data = LEVELS[index]

   
    man.x, man.y = data["player_start"]
    man.velocity_y = 0

    background = load_background(data["background"])
    tile_map = TileMap(data["layout"], data["tiles"])
    enemy = Enemy(**data["enemy"])

    battle = BattleScene(man, enemy)
    map_scene = MapScene(man, enemy, tile_map, background)

    return battle, map_scene


current_level = 0
battle, map_scene = load_level(current_level)

transition = BattleTransition()


transition_target = "battle"

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
            result = map_scene.update(pygame.key.get_pressed())

            if result == "enemy":
                transition_target = "battle"
                transition.start()

      
            elif result == "exit" and current_level + 1 < len(LEVELS):
                transition_target = "next_level"
                transition.start()

        map_scene.draw(game_surface)

    elif current_scene == "battle":
        battle.update()
        battle.draw(game_surface)

        # After the victory message, go back to the map
        if (
            battle.state == "victory"
            and battle.victory_delay_done()
            and not transition.active
        ):
            battle.boss.defeated = True
            transition_target = "map"
            transition.start()

    if transition.active:
        if transition.update():
            # The screen is fully black right now, so it's safe to swap
            if transition_target == "battle":
                current_scene = "battle"

            elif transition_target == "map":
                current_scene = "map"

            elif transition_target == "next_level":
                current_level += 1
                battle, map_scene = load_level(current_level)

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