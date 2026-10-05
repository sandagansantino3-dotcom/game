import pygame
from pathlib import Path

PLAYER_ASSETS = Path(__file__).parent / "assets" / "player"

# Right-facing sprites are named R0.png to R7.png
walkRight = [
    pygame.image.load(
        str(PLAYER_ASSETS / f"R{i}.png")
    )
    for i in range(0, 8)
]

# Left-facing sprites are named L1.png to L8.png
walkLeft = [
    pygame.image.load(
        str(PLAYER_ASSETS / f"L{i}.png")
    )
    for i in range(1, 9)
]

standing_image = pygame.image.load(
    str(PLAYER_ASSETS / "standing.png")
)


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

        self.max_health = 100
        self.health = self.max_health

        # Resize all sprites to the player's chosen size
        self.walk_right = [
            pygame.transform.scale(image, (width, height))
            for image in walkRight
        ]

        self.walk_left = [
            pygame.transform.scale(image, (width, height))
            for image in walkLeft
        ]

        self.standing = pygame.transform.scale(
            standing_image,
            (width, height)
        )

    def draw(self, window):
        frames_per_sprite = 3
        animation_length = (
            len(self.walk_right) * frames_per_sprite
        )

        # Prevent animation index errors
        if self.walkCount >= animation_length:
            self.walkCount = 0

        if self.left:
            frame = self.walkCount // frames_per_sprite

            window.blit(
                self.walk_left[frame],
                (self.x, self.y)
            )

            self.walkCount += 1

        elif self.right:
            frame = self.walkCount // frames_per_sprite

            window.blit(
                self.walk_right[frame],
                (self.x, self.y)
            )

            self.walkCount += 1

        else:
            window.blit(
                self.standing,
                (self.x, self.y)
            )

        # Health bar matches the player's new width
        bar_width = self.width
        bar_height = 10

        bar_x = (
            self.x
            + self.width // 2
            - bar_width // 2
        )

        bar_y = self.y - 15

        pygame.draw.rect(
            window,
            (255, 0, 0),
            (bar_x, bar_y, bar_width, bar_height)
        )

        health_percent = (
            self.health / self.max_health
        )

        pygame.draw.rect(
            window,
            (0, 128, 0),
            (
                bar_x,
                bar_y,
                int(bar_width * health_percent),
                bar_height
            )
        )