"""Level layouts and boss settings.

Map rows are 32-pixel cells. Platform tiles use the same solid tile symbols
as the ground, so the player can land on their top surfaces.
"""


MAP_HEIGHT = 14
GROUND_ROW = 12


def make_parkour_map(width, platforms, pits=()):
    """Build a larger platform map from (row, column, length) entries.

    `pits` contains half-open column ranges in the upper ground row. The
    bottom row remains solid, so missing ground makes a shallow 32-pixel dip
    instead of an unfair instant-death hole.
    """
    cells = [
        ["."] * width
        for _ in range(MAP_HEIGHT)
    ]

    # Add jumpable, solid platforms. Their outer tiles use the existing
    # left/right edge artwork and all tiles remain part of the collision map.
    for row, start, length in platforms:
        if not (0 <= row < GROUND_ROW):
            raise ValueError(f"Platform row out of bounds: {row}")
        if length < 3 or start < 0 or start + length > width:
            raise ValueError(
                f"Invalid platform: row={row}, start={start}, length={length}"
            )

        cells[row][start] = "<"
        for column in range(start + 1, start + length - 1):
            cells[row][column] = "#"
        cells[row][start + length - 1] = ">"

    # Continuous ground with shallow pits for small parkour sections.
    cells[GROUND_ROW][0] = "<"
    cells[GROUND_ROW][-1] = ">"
    for column in range(1, width - 1):
        cells[GROUND_ROW][column] = "#"

    for start, stop in pits:
        if start < 1 or stop > width - 1 or start >= stop:
            raise ValueError(f"Invalid pit range: {(start, stop)}")
        for column in range(start, stop):
            cells[GROUND_ROW][column] = "."

    cells[GROUND_ROW + 1] = ["#"] * width
    return ["".join(row) for row in cells]


# Easy: longer flat runs and generous jumps between platforms.
LEVEL_1 = make_parkour_map(
    width=72,
    platforms=[
        (10, 5, 5),
        (9, 12, 5),
        (10, 20, 6),
        (8, 28, 5),
        (9, 37, 5),
        (10, 46, 6),
        (8, 56, 5),
        (10, 65, 5),
    ],
    pits=[(16, 18), (33, 35), (51, 53), (62, 64)],
)

# Medium: more frequent height changes, narrower landings, and extra dips.
LEVEL_2 = make_parkour_map(
    width=84,
    platforms=[
        (10, 4, 5),
        (8, 10, 5),
        (10, 17, 6),
        (9, 26, 5),
        (8, 34, 5),
        (10, 42, 6),
        (8, 51, 5),
        (9, 60, 5),
        (10, 69, 6),
        (8, 78, 5),
    ],
    pits=[
        (14, 16),
        (31, 34),
        (48, 51),
        (66, 69),
        (76, 78),
    ],
)

# Hard boss route: the longest map, with a staircase of elevated ledges and
# shallow pits. The row-7 ledges are reachable from row-8 platforms.
LEVEL_3 = make_parkour_map(
    width=96,
    platforms=[
        (10, 3, 4),
        (9, 8, 4),
        (8, 13, 4),
        (7, 17, 3),
        (10, 21, 5),
        (8, 27, 4),
        (9, 32, 4),
        (7, 36, 3),
        (10, 40, 5),
        (8, 46, 4),
        (9, 51, 4),
        (7, 55, 3),
        (10, 59, 5),
        (8, 65, 4),
        (9, 70, 4),
        (7, 74, 3),
        (10, 78, 5),
        (8, 84, 4),
        (9, 89, 4),
    ],
    pits=[
        (12, 15),
        (23, 26),
        (35, 38),
        (48, 51),
        (61, 64),
        (73, 76),
        (85, 88),
    ],
)


LEVELS = [
    {
        "layout": LEVEL_1,
        "background": "parallax",
        "tiles": (
            "tile032.png",
            "tile033.png",
            "tile034.png"
        ),
        "player_start": (80, 200),
        "enemy": {
            "x": 1840,
            "y": 250,
            "width": 64,
            "height": 64,
            "end": 2110,
            "sprite_set": "granny",
        },
        "boss": {
            "name": "Lorna",
            "battle_sprite": "boss/LornaBS.png",
            "attack_sprite": "boss/attack_animations/lorna_attack.png",
            "battle_size": (110, 170),
            "battle_background": "MiguelBattleBG.png",
        },
    },
    {
        "layout": LEVEL_2,
        "background": "parallax",
        "tiles": (
            "tile032.png",
            "tile033.png",
            "tile034.png"
        ),
        "player_start": (80, 200),
        "enemy": {
            "x": 2180,
            "y": 250,
            "width": 64,
            "height": 64,
            "end": 2490,
            "sprite_set": "khal",
        },
        "boss": {
            # Medium uses Lorna's existing art, with the new boss name Dj.
            "name": "Dj",
            "battle_sprite": "boss/LornaBS.png",
            "attack_sprite": "boss/attack_animations/lorna_attack.png",
            "battle_size": (110, 170),
            "battle_background": "MiguelBattleBG.png",
        },
    },
    {
        "layout": LEVEL_3,
        "background": "parallax",
        "tiles": (
            "tile032.png",
            "tile033.png",
            "tile034.png"
        ),
        "player_start": (80, 200),
        "enemy": {
            "x": 2580,
            "y": 250,
            "width": 64,
            "height": 64,
            "end": 2860,
            "sprite_set": "jamis",
        },
        "boss": {
            # Hard uses the existing Jamis art until a Masterbug sprite is added.
            "name": "Masterbug",
            "battle_sprite": "boss/JamisBS.png",
            "attack_sprite": "boss/attack_animations/jamis_attack.png",
            "battle_size": (96, 170),
            "battle_background": "MiguelBattleBG.png",
        },
    },
]
