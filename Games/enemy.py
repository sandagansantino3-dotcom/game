import pygame
from pathlib import Path

ENEMY_ASSETS = Path(__file__).parent / "assets" / "enemies"

walkRight = [
    pygame.image.load(str(ENEMY_ASSETS / f"R{i}E.png"))
    for i in range(1, 12)
]

walkLeft = [
    pygame.image.load(str(ENEMY_ASSETS / f"L{i}E.png"))
    for i in range(1, 12)
]


class Enemy:
    def __init__(self, x, y, width, height, end):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.end = end
        self.path = [self.x, self.end]

        self.walkCount = 0
        self.vel = 3

        self.max_health = 10
        self.health = self.max_health

    def draw(self, window):
        self.move()

        if self.walkCount + 1 >= 33:
            self.walkCount = 0

        if self.vel > 0:
            window.blit(
                walkRight[self.walkCount // 3],
                (self.x, self.y)
            )
        else:
            window.blit(
                walkLeft[self.walkCount // 3],
                (self.x, self.y)
            )

        self.walkCount += 1

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

    def move(self):
        if self.vel > 0:
            if self.x + self.vel < self.path[1]:
                self.x += self.vel
            else:
                self.vel *= -1
                self.walkCount = 0

        else:
            if self.x + self.vel > self.path[0]:
                self.x += self.vel
            else:
                self.vel *= -1
                self.walkCount = 0