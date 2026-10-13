from pathlib import Path
import pygame


class ParallaxBackground:
    def __init__(
        self,
        folder,
        scale=2
    ):
        folder = Path(folder)

        layer_data = [
            ("back.png", 0.10),
            ("middle.png", 0.25),
            ("front.png", 0.45),
        ]

        self.layers = []

        for filename, speed in layer_data:
            image = pygame.image.load(
                str(folder / filename)
            ).convert_alpha()

            size = (
                image.get_width() * scale,
                image.get_height() * scale
            )

            image = pygame.transform.scale(
                image,
                size
            )

            self.layers.append(
                (image, speed)
            )

    def draw(
        self,
        screen,
        camera_x
    ):
        screen.fill(
            (3, 16, 22)
        )

        for image, speed in self.layers:
            image_width = (
                image.get_width()
            )

            draw_y = (
                screen.get_height()
                - image.get_height()
            )

            offset = (
                -int(camera_x * speed)
                % image_width
            )

            draw_x = (
                offset - image_width
            )

            while (
                draw_x
                < screen.get_width()
            ):
                screen.blit(
                    image,
                    (
                        draw_x,
                        draw_y
                    )
                )

                draw_x += image_width