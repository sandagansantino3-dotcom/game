from pathlib import Path
import pygame


ENEMY_ASSETS = Path(__file__).parent / "assets" / "enemy"

walk_right_images = [
    pygame.image.load(
        str(ENEMY_ASSETS / f"R{i}E.png")
    )
    for i in range(1, 12)
]

walk_left_images = [
    pygame.image.load(
        str(ENEMY_ASSETS / f"L{i}E.png")
    )
    for i in range(1, 12)
]


class Enemy:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        end
    ):
        self.x = float(x)
        self.y = float(y)

        self.width = width
        self.height = height

        self.path = [x, end]

        self.walk_count = 0
        self.speed = 3

        self.velocity_y = 0
        self.gravity = 0.8

        self.max_health = 100
        self.health = self.max_health
        self.attack_damage = 20

        self.walk_right = [
            pygame.transform.scale(
                image,
                (width, height)
            )
            for image in walk_right_images
        ]

        self.walk_left = [
            pygame.transform.scale(
                image,
                (width, height)
            )
            for image in walk_left_images
        ]

    @property
    def rect(self):
        hitbox_width = int(
            self.width * 0.55
        )

        hitbox_height = int(
            self.height * 0.85
        )

        return pygame.Rect(
            round(
                self.x
                + (self.width - hitbox_width) / 2
            ),
            round(
                self.y
                + self.height
                - hitbox_height
            ),
            hitbox_width,
            hitbox_height
        )

    def update(self, solid_rects):
        dx = self.speed

        if (
            self.x + dx < self.path[0]
            or self.x + dx > self.path[1]
        ):
            self.speed *= -1
            dx = self.speed
            self.walk_count = 0

        rect = self.rect
        rect.x += dx

        for tile in solid_rects:
            if rect.colliderect(tile):
                if dx > 0:
                    rect.right = tile.left
                else:
                    rect.left = tile.right

                self.speed *= -1
                self.walk_count = 0
                break

        self.x = (
            rect.centerx - self.width / 2
        )

        self.velocity_y = min(
            self.velocity_y + self.gravity,
            16
        )

        rect = self.rect
        rect.y += round(self.velocity_y)

        for tile in solid_rects:
            if rect.colliderect(tile):
                if self.velocity_y > 0:
                    rect.bottom = tile.top
                    self.velocity_y = 0

                elif self.velocity_y < 0:
                    rect.top = tile.bottom
                    self.velocity_y = 0

        self.y = rect.bottom - self.height

    def draw(self, window):
        frames_per_image = 3

        if self.speed > 0:
            frames = self.walk_right
        else:
            frames = self.walk_left

        animation_length = (
            len(frames) * frames_per_image
        )

        self.walk_count %= animation_length

        frame = (
            self.walk_count
            // frames_per_image
        )

        window.blit(
            frames[frame],
            (round(self.x), round(self.y))
        )

        self.walk_count += 1

        bar_width = 50

        bar_x = (
            self.x
            + self.width / 2
            - bar_width / 2
        )

        bar_y = self.y - 15

        health_width = int(
            bar_width
            * self.health
            / self.max_health
        )

        pygame.draw.rect(
            window,
            (255, 0, 0),
            (
                bar_x,
                bar_y,
                bar_width,
                10
            )
        )

        pygame.draw.rect(
            window,
            (0, 128, 0),
            (
                bar_x,
                bar_y,
                health_width,
                10
            )
        )