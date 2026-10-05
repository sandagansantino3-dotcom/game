from pathlib import Path
import pygame


PLAYER_ASSETS = Path(__file__).parent / "assets" / "player"

walk_right_images = [
    pygame.image.load(
        str(PLAYER_ASSETS / f"R{i}.png")
    )
    for i in range(8)
]

walk_left_images = [
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
        self.x = float(x)
        self.y = float(y)

        self.width = width
        self.height = height

        self.speed = 5
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = 14
        self.on_ground = False

        self.left = False
        self.right = False
        self.walk_count = 0

        self.max_health = 100
        self.health = self.max_health

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

        self.standing = pygame.transform.scale(
            standing_image,
            (width, height)
        )

    @property
    def rect(self):
        hitbox_width = int(self.width * 0.5)
        hitbox_height = int(self.height * 0.8)

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

    def jump(self):
        if self.on_ground:
            self.velocity_y = -self.jump_speed
            self.on_ground = False

    def update(
        self,
        keys,
        solid_rects,
        level_width
    ):
        dx = 0

        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.left = True
            self.right = False

        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.right = True
            self.left = False

        else:
            self.left = False
            self.right = False
            self.walk_count = 0

        rect = self.rect
        rect.x += dx

        for tile in solid_rects:
            if rect.colliderect(tile):
                if dx > 0:
                    rect.right = tile.left

                elif dx < 0:
                    rect.left = tile.right

        if rect.left < 0:
            rect.left = 0

        if rect.right > level_width:
            rect.right = level_width

        self.x = (
            rect.centerx - self.width / 2
        )

        self.velocity_y = min(
            self.velocity_y + self.gravity,
            16
        )

        rect = self.rect
        rect.y += round(self.velocity_y)
        self.on_ground = False

        for tile in solid_rects:
            if rect.colliderect(tile):
                if self.velocity_y > 0:
                    rect.bottom = tile.top
                    self.velocity_y = 0
                    self.on_ground = True

                elif self.velocity_y < 0:
                    rect.top = tile.bottom
                    self.velocity_y = 0

        self.y = rect.bottom - self.height

    def draw(self, window):
        frames_per_image = 3

        if self.left or self.right:
            if self.left:
                frames = self.walk_left
            else:
                frames = self.walk_right

            animation_length = (
                len(frames) * frames_per_image
            )

            self.walk_count %= animation_length

            frame = (
                self.walk_count
                // frames_per_image
            )

            image = frames[frame]
            self.walk_count += 1

        else:
            image = self.standing

        window.blit(
            image,
            (round(self.x), round(self.y))
        )

        bar_width = self.width

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