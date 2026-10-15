import sys
from functools import lru_cache
from pathlib import Path
import pygame

import menu
from battle_scene import BattleScene
from enemy import Enemy
from levels import LEVELS
from player import Player
from tilemap import TileMap
from transition_scene import BattleTransition
from map_scene import MapScene
from parallax import ParallaxBackground

pygame.init()

GAME_FOLDER = Path(__file__).parent
SCREEN_SIZE = (800, 448)

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    SCREEN_SIZE
)

pygame.display.set_caption("Real of Syntax Errors")

audio = menu.Audio()
fullscreen = audio.fullscreen

if fullscreen:
    screen = pygame.display.set_mode(
        SCREEN_SIZE,
        pygame.FULLSCREEN | pygame.SCALED,
    )


def toggle_fullscreen():
    global screen, fullscreen

    fullscreen = not fullscreen
    flags = (
        pygame.FULLSCREEN | pygame.SCALED
        if fullscreen
        else 0
    )
    screen = pygame.display.set_mode(SCREEN_SIZE, flags)
    audio.fullscreen = fullscreen
    audio.save()
    return screen


@lru_cache(maxsize=8)
def load_background(folder_name):
    path = (
        GAME_FOLDER
        / "assets"
        / "backgrounds"
        / folder_name
    )

    return ParallaxBackground(
        path,
        scale=2
    )


man = Player(
    80,
    200,
    80,
    80
)


def load_level(index):
    data = LEVELS[index]

    man.x, man.y = data["player_start"]
    man.velocity_y = 0

    background = load_background(
        data["background"]
    )

    tile_map = TileMap(
        data["layout"],
        data["tiles"]
    )

    enemy = Enemy(
        **data["enemy"]
    )

    battle = BattleScene(
        man,
        enemy,
        data["boss"]
    )

    battle.player_name = player_name

    map_scene = MapScene(
        man,
        enemy,
        tile_map,
        background
    )

    return battle, map_scene


def show_main_menu():
    result = menu.main_menu(
        screen,
        audio,
        len(LEVELS),
        toggle_fullscreen,
    )

    if result is None:
        pygame.quit()
        sys.exit()

    menu.save_level(*result)

    return result


current_level, player_name = show_main_menu()

battle, map_scene = load_level(
    current_level
)

transition = BattleTransition()
transition_target = "battle"

current_scene = "map"
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_ESCAPE
                and not transition.active
            ):
                paused_at = pygame.time.get_ticks()

                choice = menu.pause_menu(
                    screen,
                    audio,
                    toggle_fullscreen,
                )

                paused_for = (
                    pygame.time.get_ticks()
                    - paused_at
                )

                if choice == "quit":
                    running = False

                elif choice == "main_menu":
                    current_level, player_name = show_main_menu()

                    battle, map_scene = load_level(
                        current_level
                    )

                    transition = BattleTransition()
                    transition_target = "battle"
                    current_scene = "map"

                else:
                    # Resume: the battle timers use the clock,
                    # so give back the time spent paused
                    battle.start_time += paused_for
                    battle.feedback_start += paused_for
                    battle.end_start += paused_for
                    transition.phase_start += paused_for

            elif (
                event.key == pygame.K_f
                and current_scene == "map"
            ):
                toggle_fullscreen()

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
            keys = pygame.key.get_pressed()

            result = map_scene.update(
                keys
            )

            if result == "enemy":
                transition_target = "battle"
                transition.start()

            elif (
                result == "exit"
                and current_level + 1
                < len(LEVELS)
            ):
                transition_target = (
                    "next_level"
                )

                transition.start()

        map_scene.draw(screen)

        menu.draw_name(
            screen,
            player_name,
            (
                man.x - map_scene.camera_x
                + man.width / 2,
                man.y - 28
            )
        )

    elif current_scene == "battle":
        battle.update()
        battle.draw(screen)

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
            if transition_target == "battle":
                current_scene = "battle"

            elif transition_target == "map":
                current_scene = "map"
 
            elif (
                transition_target
                == "next_level"
            ):
                current_level += 1

                menu.save_level(
                    current_level,
                    player_name
                )

                battle, map_scene = (
                    load_level(current_level)
                )

        transition.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

#
