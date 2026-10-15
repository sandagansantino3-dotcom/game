from pathlib import Path
from functools import lru_cache
import pygame


TILE_SIZE = 32

TILE_FOLDER = (
    Path(__file__).parent
    / "assets"
    / "tiles"
)


@lru_cache(maxsize=32)
def load_tile_image(path):
    """Load and convert each tile image once for reuse across levels."""
    return pygame.image.load(str(path)).convert_alpha()

LEVEL = [
    ".........................",
    ".........................",
    ".........................",
    ".........................",
    ".........................",
    ".........................",
    ".........................",
    ".........................",
    ".....<###>...............",
    ".........................",
    "..............<###>......",
    ".........................",
    "<#######################>",
    "#########################",
]


class TileMap:
    def __init__(
        self,
        level=LEVEL,
        tile_files=(
            "tile032.png",
            "tile033.png",
            "tile034.png"
        )
    ):
        left, middle, right = tile_files

        self.images = {
            "<": load_tile_image(TILE_FOLDER / left),

            "#": load_tile_image(TILE_FOLDER / middle),

            ">": load_tile_image(TILE_FOLDER / right),
        }

        self.tiles = []

        for row_number, row in enumerate(
            level
        ):
            for column_number, symbol in enumerate(
                row
            ):
                if symbol != ".":
                    rect = pygame.Rect(
                        column_number * TILE_SIZE,
                        row_number * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )

                    self.tiles.append(
                        (
                            self.images[symbol],
                            rect
                        )
                    )

        self.solid_rects = [
            rect
            for _, rect in self.tiles
        ]

        self.width = (
            len(level[0]) * TILE_SIZE
        )

        self.height = (
            len(level) * TILE_SIZE
        )

    def draw(
        self,
        screen,
        camera_x=0
    ):
        for image, rect in self.tiles:
            draw_rect = rect.move(
                -camera_x,
                0
            )

            if (
                draw_rect.right >= 0
                and draw_rect.left
                <= screen.get_width()
            ):
                screen.blit(
                    image,
                    draw_rect
                )
