from pathlib import Path
import pygame


TILE_SIZE = 32
TILE_FOLDER = Path(__file__).parent / "assets" / "tiles"

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
        tile_files=("tile032.png", "tile033.png", "tile034.png")
    ):
        # tile_files = (left corner, middle, right corner)
        left, middle, right = tile_files

        self.images = {
            "<": pygame.image.load(
                str(TILE_FOLDER / left)
            ).convert_alpha(),

            "#": pygame.image.load(
                str(TILE_FOLDER / middle)
            ).convert_alpha(),

            ">": pygame.image.load(
                str(TILE_FOLDER / right)
            ).convert_alpha(),
        }

        self.tiles = []

        for row_number, row in enumerate(level):
            for column_number, symbol in enumerate(row):
                if symbol != ".":
                    rect = pygame.Rect(
                        column_number * TILE_SIZE,
                        row_number * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )

                    self.tiles.append(
                        (self.images[symbol], rect)
                    )

        self.solid_rects = [
            rect for _, rect in self.tiles
        ]

        self.width = len(level[0]) * TILE_SIZE
        self.height = len(level) * TILE_SIZE

    def draw(self, screen):
        for image, rect in self.tiles:
            screen.blit(image, rect)