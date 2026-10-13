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
SCREEN_SIZE = (800, 448)

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    SCREEN_SIZE
)

pygame.display.set_caption("MIGUEL")


def load_background(filename):
    """Load one background image and scale it to the screen."""
    path = GAME_FOLDER / "assets" / "backgrounds" / filename

    image = pygame.image.load(str(path)).convert()

    return pygame.transform.scale(image, SCREEN_SIZE)


# The player is created once, so the same character is used in every level
man = Player(
    80,
    200,
    80,
    80
)


def load_level(index):
    """Build everything that changes from level to level."""
    data = LEVELS[index]

    # Put the player back at this level's starting spot
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

# What the running transition is for: "battle", "map" or "next_level"
transition_target = "battle"

current_scene = "map"
fullscreen = False
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif (
                event.key == pygame.K_f
                and current_scene == "map"
            ):
                fullscreen = not fullscreen

                if fullscreen:
                    flags = (
                        pygame.FULLSCREEN
                        | pygame.SCALED
                    )
                else:
                    flags = 0

                screen = pygame.display.set_mode(
                    SCREEN_SIZE,
                    flags
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

            # Touched the enemy: go to the battle
            if result == "enemy":
                transition_target = "battle"
                transition.start()

            # Enemy defeated and player reached the edge: next level
            elif result == "exit" and current_level + 1 < len(LEVELS):
                transition_target = "next_level"
                transition.start()

        map_scene.draw(screen)

    elif current_scene == "battle":
        battle.update()
        battle.draw(screen)

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

        transition.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()