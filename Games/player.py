from pathlib import Path
import pygame


PLAYER_ASSETS = (
    Path(__file__).parent
    / "assets"
    / "player"
)

def load_image(name):
    return pygame.image.load(
        str(PLAYER_ASSETS / name)
    )


# Gamer Man sprites (all face right; left-facing is made by flipping)
walk_right_images = [
    load_image(f"gm_walk{i}.png")
    for i in range(1, 5)
]

standing_image = load_image("gm_stand.png")
jump_up_image = load_image("gm_jump_up.png")
jump_down_image = load_image("gm_jump_down.png")


class Player:
    def __init__(
        self,
        x,
        y,
        width,
        height
    ):
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

        self.facing = 1

        self.walk_right = [
            pygame.transform.scale(
                image,
                (width, height)
            )
            for image in walk_right_images
        ]

        self.walk_left = [
            pygame.transform.flip(
                image,
                True,
                False
            )
            for image in self.walk_right
        ]

        self.standing = (
            pygame.transform.scale(
                standing_image,
                (width, height)
            )
        )

        self.jump_up_right = (
            pygame.transform.scale(
                jump_up_image,
                (width, height)
            )
        )

        self.jump_down_right = (
            pygame.transform.scale(
                jump_down_image,
                (width, height)
            )
        )

        self.jump_up_left = pygame.transform.flip(
            self.jump_up_right,
            True,
            False
        )

        self.jump_down_left = pygame.transform.flip(
            self.jump_down_right,
            True,
            False
        )

    @property
    def rect(self):
        hitbox_width = int(
            self.width * 0.5
        )

        hitbox_height = int(
            self.height * 0.8
        )

        return pygame.Rect(
            round(
                self.x
                + (
                    self.width
                    - hitbox_width
                ) / 2
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
            self.velocity_y = (
                -self.jump_speed
            )

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
            self.facing = -1

        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.right = True
            self.left = False
            self.facing = 1

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
            rect.centerx
            - self.width / 2
        )

        self.velocity_y = min(
            self.velocity_y
            + self.gravity,
            16
        )

        rect = self.rect

        rect.y += round(
            self.velocity_y
        )

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

        self.y = (
            rect.bottom
            - self.height
        )

    def draw(
        self,
        window,
        camera_x=0
    ):
        frames_per_image = 6

        if not self.on_ground:
            if self.velocity_y < 0:
                if self.facing < 0:
                    image = self.jump_up_left
                else:
                    image = self.jump_up_right
            else:
                if self.facing < 0:
                    image = self.jump_down_left
                else:
                    image = self.jump_down_right

        elif self.left or self.right:
            if self.left:
                frames = self.walk_left
            else:
                frames = self.walk_right

            animation_length = (
                len(frames)
                * frames_per_image
            )

            self.walk_count %= (
                animation_length
            )

            frame = (
                self.walk_count
                // frames_per_image
            )

            image = frames[frame]
            self.walk_count += 1

        else:
            image = self.standing

        draw_x = (
            self.x - camera_x
        )

        window.blit(
            image,
            (
                round(draw_x),
                round(self.y)
            )
        )

        sprite_rect = image.get_rect(
            topleft=(
                round(draw_x),
                round(self.y)
            )
        )

        bar_width = int(
            sprite_rect.width * 0.8
        )

        bar_x = (
            sprite_rect.centerx
            - bar_width // 2
        )

        bar_y = (
            sprite_rect.top - 15
        )

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