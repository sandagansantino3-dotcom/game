"""Menus for game.py: main menu, pause menu and volume settings."""

import json
from functools import lru_cache
from pathlib import Path

import pygame

HERE = Path(__file__).parent
SAVE, SETTINGS = HERE / "save.json", HERE / "settings.json"
W, H = 800, 448
PANEL, BORDER, SELECT = (231, 239, 203), (70, 91, 72), (251, 250, 232)
DARK, LIGHT, GREY = (28, 34, 30), (255, 245, 255), (170, 176, 160)


def load(path, key, default):
    try:
        return json.loads(path.read_text())[key]
    except (OSError, ValueError, KeyError, TypeError):
        return default


def save(path, **data):
    try:
        path.write_text(json.dumps(data))
    except OSError:
        pass


def save_level(level, name):
    save(SAVE, level=level, name=name)


class Audio:
    """Master volume 0-1, and the looping background music.
    Music: the first .mp3 found in assets/music. Use audio.volume for sound effects."""

    def __init__(self):
        self.set(load(SETTINGS, "volume", 0.7))
        self.fullscreen = load(SETTINGS, "fullscreen", False) is True
        songs = sorted((HERE / "assets" / "music").glob("*.mp3"))
        if songs:
            try:
                pygame.mixer.music.load(str(songs[0]))
                pygame.mixer.music.play(-1)
                self.set(self.volume)
            except pygame.error:
                pass

    def set(self, value):
        self.volume = max(0.0, min(1.0, float(value)))
        try:
            pygame.mixer.music.set_volume(self.volume)
        except pygame.error:
            pass

    def save(self):
        save(
            SETTINGS,
            volume=round(self.volume, 2),
            fullscreen=self.fullscreen,
        )


@lru_cache(maxsize=None)
def font(name, size):
    try:
        return pygame.font.Font(str(HERE / "assets" / "fonts" / name), size)
    except (OSError, pygame.error):
        return pygame.font.Font(None, size + 8)


def text(screen, f, string, color, center):
    surface = f.render(string, True, color)
    screen.blit(surface, surface.get_rect(center=center))


def button(screen, f, rect, label, selected=False, enabled=True):
    fill = SELECT if selected else PANEL
    pygame.draw.rect(screen, GREY if not enabled else fill, rect, border_radius=8)
    border = (35, 95, 145) if selected else BORDER
    pygame.draw.rect(screen, border, rect, 4, border_radius=8)
    text(screen, f, label, DARK if enabled else (110, 116, 104), rect.center)


def dimmer():
    surface = pygame.Surface((W, H), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 110))
    return surface


def settings(screen, audio, backdrop, toggle_fullscreen=None):
    """Adjust volume and toggle fullscreen; Esc to go back."""
    clock, dim, f = pygame.time.Clock(), dimmer(), font("VT323-Regular.ttf", 34)
    track = pygame.Rect(220, 220, 360, 14)
    fullscreen_button = pygame.Rect(250, 267, 300, 42)
    back = pygame.Rect(250, 322, 300, 42)
    dragging = done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.event.post(event)
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    done = True
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    step = 1 if event.key == pygame.K_RIGHT else -1
                    audio.set(round(audio.volume * 20 + step) / 20)
                elif event.key == pygame.K_f and toggle_fullscreen:
                    screen = toggle_fullscreen() or screen
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if track.inflate(24, 36).collidepoint(event.pos):
                    dragging = True
                elif fullscreen_button.collidepoint(event.pos):
                    if toggle_fullscreen:
                        screen = toggle_fullscreen() or screen
                elif back.collidepoint(event.pos):
                    done = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if dragging and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                audio.set((event.pos[0] - track.x) / track.width)

        backdrop(screen)
        screen.blit(dim, (0, 0))
        pygame.draw.rect(screen, PANEL, (150, 130, 500, 250), border_radius=10)
        pygame.draw.rect(screen, BORDER, (150, 130, 500, 250), 4, border_radius=10)
        text(screen, f, f"Volume: {round(audio.volume * 100)}%", DARK, (W // 2, 178))
        pygame.draw.rect(screen, (170, 40, 40), track)
        pygame.draw.rect(screen, (40, 190, 80), (*track.topleft, int(track.width * audio.volume), track.height))
        pygame.draw.rect(screen, (20, 20, 25), track, 3)
        handle = pygame.Rect(0, 0, 14, 32)
        handle.center = (track.x + int(track.width * audio.volume), track.centery)
        pygame.draw.rect(screen, SELECT, handle, border_radius=3)
        pygame.draw.rect(screen, (35, 95, 145), handle, 3, border_radius=3)
        button(
            screen,
            f,
            fullscreen_button,
            f"Fullscreen: {'On' if audio.fullscreen else 'Off'}",
        )
        button(screen, f, back, "Back", True)
        text(screen, f, "F: toggle fullscreen    Esc: back", LIGHT, (W // 2, 424))
        pygame.display.flip()
        clock.tick(60)

    audio.save()
    return screen


def run_menu(screen, audio, title, items, backdrop, disabled=(), selected=0, escape="Quit", toggle_fullscreen=None):
    """Shows a list of buttons and returns the name of the one chosen.
    "Settings" is handled here, so it is never returned."""
    clock, dim = pygame.time.Clock(), dimmer()
    big, small = font("Silkscreen-Regular.ttf", 54), font("VT323-Regular.ttf", 34)
    rects = [pygame.Rect((W - 300) // 2, 168 + i * 58, 300, 46) for i in range(len(items))]
    index = selected

    while True:
        for event in pygame.event.get():
            choice = None
            if event.type == pygame.QUIT:
                return "Quit"
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    for _ in items:
                        index = (index + (-1 if event.key == pygame.K_UP else 1)) % len(items)
                        if items[index] not in disabled:
                            break
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = items[index]
                elif event.key == pygame.K_ESCAPE:
                    choice = escape
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos) and items[i] not in disabled:
                        index = i
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            choice = items[i]

            if choice == "Settings":
                screen = settings(screen, audio, backdrop, toggle_fullscreen)
            elif choice:
                return choice

        backdrop(screen)
        screen.blit(dim, (0, 0))
        text(screen, big, title, LIGHT, (W // 2, 82))
        for i, rect in enumerate(rects):
            button(screen, small, rect, items[i], i == index, items[i] not in disabled)
        pygame.display.flip()
        clock.tick(60)


def draw_name(screen, name, center):
    """Player name, centred on `center` (used above the character)."""
    f, x, y = font("VT323-Regular.ttf", 26), round(center[0]), round(center[1])
    text(screen, f, name, (20, 20, 25), (x + 1, y + 1))
    text(screen, f, name, LIGHT, (x, y))


def ask_name(screen, backdrop, name=""):
    """Type a name (12 characters max). Enter confirms, Esc goes back (returns None)."""
    clock, dim, f = pygame.time.Clock(), dimmer(), font("VT323-Regular.ttf", 34)
    box = pygame.Rect(200, 220, 400, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.event.post(event)
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode and event.unicode.isprintable() and len(name) < 12:
                    name += event.unicode

        backdrop(screen)
        screen.blit(dim, (0, 0))
        pygame.draw.rect(screen, PANEL, (150, 140, 500, 190), border_radius=10)
        pygame.draw.rect(screen, BORDER, (150, 140, 500, 190), 4, border_radius=10)
        text(screen, f, "Enter your name", DARK, (W // 2, 180))
        pygame.draw.rect(screen, SELECT, box, border_radius=4)
        pygame.draw.rect(screen, (35, 95, 145), box, 3, border_radius=4)
        cursor = "_" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
        screen.blit(f.render(name + cursor, True, DARK), (box.x + 12, box.y + 12))
        text(screen, f, "Enter: confirm    Esc: back", LIGHT, (W // 2, 424))
        pygame.display.flip()
        clock.tick(60)


def difficulty_menu(screen, backdrop):
    """Show the difficulty selection screen. Easy is currently available."""
    clock = pygame.time.Clock()
    dim = dimmer()
    title_font = font("Silkscreen-Regular.ttf", 38)
    option_font = font("VT323-Regular.ttf", 34)
    detail_font = font("VT323-Regular.ttf", 24)
    options = [
        {
            "name": "EASY",
            "status": "AVAILABLE",
            "detail": "Standard challenge",
            "enabled": True,
        },
        {
            "name": "MEDIUM",
            "status": "LOCKED",
            "detail": "Boss: Dj",
            "enabled": False,
        },
        {
            "name": "HARD",
            "status": "LOCKED",
            "detail": "Boss: Masterbug",
            "enabled": False,
        },
    ]
    cards = [
        pygame.Rect(42 + index * 244, 164, 220, 174)
        for index in range(len(options))
    ]
    back_rect = pygame.Rect(250, 370, 300, 46)

    while True:
        mouse_position = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.event.post(event)
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "easy"

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                if back_rect.collidepoint(event.pos):
                    return None
                if cards[0].collidepoint(event.pos):
                    return "easy"

        backdrop(screen)
        screen.blit(dim, (0, 0))

        title_surface = title_font.render(
            "SELECT DIFFICULTY",
            True,
            LIGHT
        )
        screen.blit(
            title_surface,
            title_surface.get_rect(center=(W // 2, 92))
        )

        for index, (card, option) in enumerate(zip(cards, options)):
            enabled = option["enabled"]
            hovered = enabled and card.collidepoint(mouse_position)

            fill = SELECT if hovered else PANEL
            border = (35, 95, 145) if hovered else BORDER
            label_color = DARK if enabled else (110, 116, 104)
            detail_color = (35, 76, 120) if enabled else (110, 116, 104)

            pygame.draw.rect(
                screen,
                fill,
                card,
                border_radius=10
            )
            pygame.draw.rect(
                screen,
                border,
                card,
                4,
                border_radius=10
            )

            text(
                screen,
                option_font,
                option["name"],
                label_color,
                (card.centerx, card.y + 46)
            )
            text(
                screen,
                detail_font,
                option["status"],
                detail_color,
                (card.centerx, card.y + 94)
            )
            text(
                screen,
                detail_font,
                option["detail"],
                detail_color,
                (card.centerx, card.y + 128)
            )

        button(
            screen,
            option_font,
            back_rect,
            "Back",
            selected=back_rect.collidepoint(mouse_position)
        )
        text(
            screen,
            detail_font,
            "Choose Easy to start",
            LIGHT,
            (W // 2, 432)
        )

        pygame.display.flip()
        clock.tick(60)


def main_menu(screen, audio, level_count, toggle_fullscreen=None):
    """Returns (level, name) to start with, or None if the player quit."""
    try:
        from parallax import ParallaxBackground

        scenery = ParallaxBackground(HERE / "assets" / "backgrounds" / "parallax", scale=2)
    except Exception:
        scenery = None
    scroll = [0]

    def backdrop(screen):
        scroll[0] += 1
        if scenery:
            scenery.draw(screen, scroll[0])
        else:
            screen.fill((3, 16, 22))

    while True:
        level, name = load(SAVE, "level", None), load(SAVE, "name", "")
        name = name if isinstance(name, str) else ""
        has_save = isinstance(level, int) and level >= 0 and bool(name.strip())
        choice = run_menu(
            screen, audio, "MIGUEL", ["New Game", "Continue", "Settings", "Quit"], backdrop,
            disabled=() if has_save else ("Continue",), selected=1 if has_save else 0,
            toggle_fullscreen=toggle_fullscreen,
        )
        if choice == "New Game":
            name = ask_name(screen, backdrop, name)
            if name:
                difficulty = difficulty_menu(screen, backdrop)
                if difficulty == "easy":
                    return 0, name
        elif choice == "Continue":
            return min(level, level_count - 1), name
        else:
            return None


def pause_menu(screen, audio, toggle_fullscreen=None):
    """Returns "resume", "main_menu" or "quit"."""
    snapshot = screen.copy()
    choice = run_menu(
        screen, audio, "PAUSED", ["Resume", "Settings", "Main Menu", "Quit"],
        lambda s: s.blit(snapshot, (0, 0)), escape="Resume",
        toggle_fullscreen=toggle_fullscreen,
    )
    return choice.lower().replace(" ", "_")
