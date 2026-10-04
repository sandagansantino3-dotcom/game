import pygame
from pathlib import Path

PLAYER_ASSETS = Path(__file__).parent / "assets" / "player"

walkRight = [
    pygame.image.load('assets/player/R1.png'),
    pygame.image.load('assets/player/R2.png'),
    pygame.image.load('assets/player/R3.png'),
    pygame.image.load('assets/player/R4.png'),
    pygame.image.load('assets/player/R5.png'),
    pygame.image.load('assets/player/R6.png'),
    pygame.image.load('assets/player/R7.png'),
    pygame.image.load('assets/player/R8.png'),
    pygame.image.load('assets/player/R9.png'),
]

walkLeft = [
    pygame.image.load('assets/player/L1.png'),
    pygame.image.load('assets/player/L2.png'),
    pygame.image.load('assets/player/L3.png'),
    pygame.image.load('assets/player/L4.png'),
    pygame.image.load('assets/player/L5.png'),
    pygame.image.load('assets/player/L6.png'),
    pygame.image.load('assets/player/L7.png'),
    pygame.image.load('assets/player/L8.png'),
    pygame.image.load('assets/player/L9.png'),
]

standing = pygame.image.load(str(PLAYER_ASSETS / "standing.png"))


class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.vel = 5
        self.isJump = False
        self.jumpCount = 10

        self.left = False
        self.right = False
        self.walkCount = 0

        self.health = 10
        self.max_health = 10

    def draw(self, window):
        if self.walkCount + 1 >= 27:
            self.walkCount = 0

        if self.left:
            window.blit(walkLeft[self.walkCount // 3], (self.x, self.y))
            self.walkCount += 1

        elif self.right:
            window.blit(walkRight[self.walkCount // 3], (self.x, self.y))
            self.walkCount += 1

        else:
            window.blit(standing, (self.x, self.y))

        bar_width = 50
        bar_height = 10
        bar_x = self.x + self.width // 2 - bar_width // 2
        bar_y = self.y - 15

        pygame.draw.rect(
            window,
            (255, 0, 0),
            (bar_x, bar_y, bar_width, bar_height)
        )

        pygame.draw.rect(
            window,
            (0, 128, 0),
            (
                bar_x,
                bar_y,
                int(bar_width * self.health / self.max_health),
                bar_height
            )
        )