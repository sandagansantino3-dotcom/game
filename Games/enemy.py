from pathlib import Path
import pygame


ASSETS = (
    Path(__file__).parent
    / "assets"
)

SPRITE_SETS = {
    "goblin": {
        "folder": "enemy",
        "suffix": "E",
        "count": 11
    },
    "granny": {
        "folder": "enemy",
        "suffix": "G",
        "count": 4
    },
}


def load_frames(
    sprite_set,
    side,
    size
):
    info = SPRITE_SETS[
        sprite_set
    ]

    folder = (
        ASSETS
        / info["folder"]
    )

    frames = []

    for i in range(
        1,
        info["count"] + 1
    ):
        exact = (
            folder
            / (
                f"{side}{i}"
                f"{info['suffix']}.png"
            )
        )

        if exact.exists():
            path = exact

        else:
            matches = sorted(
                folder.glob(
                    f"{side}{i}"
                    f"{info['suffix']}*"
                )
            )

            if not matches:
                raise FileNotFoundError(
                    f"Missing {exact.name}"
                )

            path = matches[0]

        image = pygame.image.load(
            str(path)
        )

        frames.append(
            pygame.transform.scale(
                image,
                size
            )
        )

    return frames


class Enemy:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        end,
        sprite_set="goblin"
    ):
        self.x = float(x)
        self.y = float(y)

        self.width = width
        self.height = height

        self.path = [
            x,
            end
        ]

        self.walk_count = 0

        self.move_speed = 3
        self.speed = self.move_speed
        self.direction = 1

        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = 12
        self.on_ground = False

        self.detection_range = 550
        self.chasing = False

        self.max_health = 100
        self.health = self.max_health
        self.attack_damage = 20

        self.defeated = False

        self.walk_right = load_frames(
            sprite_set,
            "R",
            (width, height)
        )

        self.walk_left = load_frames(
            sprite_set,
            "L",
            (width, height)
        )

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

    def update(
        self,
        solid_rects,
        player,
        level_width
    ):
        enemy_rect = self.rect
        player_rect = player.rect

        distance_x = (
            player_rect.centerx
            - enemy_rect.centerx
        )

        distance_y = (
            player_rect.centery
            - enemy_rect.centery
        )

        self.chasing = (
            abs(distance_x)
            <= self.detection_range
            and abs(distance_y) <= 260
        )

        dx = 0

        if self.chasing:
            if distance_x > 8:
                self.direction = 1
                dx = self.move_speed

            elif distance_x < -8:
                self.direction = -1
                dx = -self.move_speed

        else:
            if self.x <= self.path[0]:
                self.direction = 1

            elif self.x >= self.path[1]:
                self.direction = -1

            dx = (
                self.move_speed
                * self.direction
            )

        self.speed = (
            self.move_speed
            * self.direction
        )

        if (
            dx != 0
            and self.on_ground
        ):
            wall_test = (
                self.rect.move(
                    dx,
                    0
                )
            )

            wall_ahead = any(
                wall_test.colliderect(tile)
                for tile in solid_rects
            )

            if self.direction > 0:
                probe_x = (
                    wall_test.right + 2
                )
            else:
                probe_x = (
                    wall_test.left - 6
                )

            ground_probe = pygame.Rect(
                probe_x,
                wall_test.bottom + 1,
                4,
                14
            )

            ground_ahead = any(
                ground_probe.colliderect(tile)
                for tile in solid_rects
            )

            player_above = (
                distance_y < -45
                and abs(distance_x) < 220
            )

            if (
                self.chasing
                and (
                    wall_ahead
                    or not ground_ahead
                    or player_above
                )
            ):
                self.velocity_y = (
                    -self.jump_speed
                )

                self.on_ground = False

            elif (
                not self.chasing
                and (
                    wall_ahead
                    or not ground_ahead
                )
            ):
                self.direction *= -1

                self.speed = (
                    self.move_speed
                    * self.direction
                )

                dx = self.speed
                self.walk_count = 0

        rect = self.rect
        rect.x += dx

        for tile in solid_rects:
            if rect.colliderect(tile):
                if dx > 0:
                    rect.right = tile.left

                elif dx < 0:
                    rect.left = tile.right

                break

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
        frames_per_image = 3

        if self.direction > 0:
            frames = self.walk_right
        else:
            frames = self.walk_left

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

        draw_x = round(
            self.x - camera_x
        )

        draw_y = round(
            self.y
        )

        window.blit(
            image,
            (
                draw_x,
                draw_y
            )
        )

        self.walk_count += 1

        sprite_rect = image.get_rect(
            topleft=(
                draw_x,
                draw_y
            )
        )

        bar_width = max(
            40,
            int(
                sprite_rect.width * 0.8
            )
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