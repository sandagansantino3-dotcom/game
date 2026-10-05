import sys
from pathlib import Path
import pygame

from battle_scene import BattleScene
from enemy import Enemy
from player import Player
from tilemap import TileMap
from transition_scene import BattleTransition


pygame.init()

GAME_FOLDER = Path(__file__).parent
SCREEN_SIZE = (800, 448)

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    SCREEN_SIZE
)

pygame.display.set_caption("MIGUEL")

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
    SCREEN_SIZE
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

transition = BattleTransition()

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
            keys = pygame.key.get_pressed()

            man.update(
                keys,
                tile_map.solid_rects,
                tile_map.width
            )

            goblin.update(
                tile_map.solid_rects
            )

            if man.rect.colliderect(
                goblin.rect
            ):
                transition.start()

        screen.blit(
            background,
            (0, 0)
        )

        tile_map.draw(screen)
        man.draw(screen)
        goblin.draw(screen)

    elif current_scene == "battle":
        battle.update()
        battle.draw(screen)

    if transition.active:
        if transition.update():
            current_scene = "battle"

        transition.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()