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
    def __init__(self, level=LEVEL):
        self.images = {
            "<": pygame.image.load(
                str(TILE_FOLDER / "tile032.png")
            ).convert_alpha(),

            "#": pygame.image.load(
                str(TILE_FOLDER / "tile033.png")
            ).convert_alpha(),

            ">": pygame.image.load(
                str(TILE_FOLDER / "tile034.png")
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