import sys
from pathlib import Path
from transition_scene import BattleTransition
import pygame

from player import Player
from enemy import Enemy
from battle_scene import BattleScene


pygame.init()

GAME_FOLDER = Path(__file__).parent
clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    (800, 450),
    pygame.RESIZABLE
)

pygame.display.set_caption("MIGUEL")

fullscreen = False
window_size = (800, 450)

monitor_size = (
    pygame.display.Info().current_w,
    pygame.display.Info().current_h
)

background_path = (
    GAME_FOLDER/ "assets"/ "backgrounds"/ "bg1.png")

original_bg = pygame.image.load(
    str(background_path)
).convert()

# Characters
man = Player(300, 215, 64, 64)
goblin = Enemy(100, 220, 64, 64, 450)

# Scenes
battle = BattleScene(man, goblin)
current_scene = "map"

run = True


while run:
    clock.tick(30)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False

        elif (
            event.type == pygame.VIDEORESIZE
            and not fullscreen
        ):
            window_size = event.size

            screen = pygame.display.set_mode(
                window_size,
                pygame.RESIZABLE
            )

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                run = False

            # F only changes fullscreen while on the map.
            # This allows the player to type F during battle.
            elif (
                event.key == pygame.K_f
                and current_scene == "map"
            ):
                fullscreen = not fullscreen

                if fullscreen:
                    screen = pygame.display.set_mode(
                        monitor_size,
                        pygame.FULLSCREEN
                    )

                else:
                    screen = pygame.display.set_mode(
                        window_size,
                        pygame.RESIZABLE
                    )

            # battle button (temporary)
            elif (
                event.key == pygame.K_b
                and current_scene == "map"
            ):
                current_scene = "battle"

                # Prevents B from being typed
                # inside the battle answer.
                continue

        # Send keyboard events to the battle.
        if current_scene == "battle":
            battle.handle_event(event)

    # MAP SCENE

    if current_scene == "map":
        keys = pygame.key.get_pressed()

        # Horizontal movement
        if (
            keys[pygame.K_LEFT]
            and man.x > man.vel
        ):
            man.x -= man.vel
            man.left = True
            man.right = False

        elif (
            keys[pygame.K_RIGHT]
            and man.x
            < screen.get_width() - man.width - man.vel
        ):
            man.x += man.vel
            man.right = True
            man.left = False

        else:
            man.right = False
            man.left = False
            man.walkCount = 0

        # Jumping
        if not man.isJump:
            if keys[pygame.K_SPACE]:
                man.isJump = True
                man.right = False
                man.left = False
                man.walkCount = 0

        else:
            if man.jumpCount >= -10:
                neg = 1

                if man.jumpCount < 0:
                    neg = -1

                man.y -= (
                    man.jumpCount ** 2
                ) * 0.5 * neg

                man.jumpCount -= 1

            else:
                man.isJump = False
                man.jumpCount = 10

        # Resize and draw the map background
        bg = pygame.transform.scale(
            original_bg,
            screen.get_size()
        )

        screen.blit(bg, (0, 0))

        # Draw map characters
        man.draw(screen)
        goblin.draw(screen)

    # BATTLE SCENE

    elif current_scene == "battle":
        battle.update()
        battle.draw(screen)

    # Show the completed frame
    pygame.display.update()


pygame.quit()
sys.exit()