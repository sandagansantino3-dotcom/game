import json
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


def save(path, key, value):
    try:
        path.write_text(json.dumps({key: value}))
    except OSError:
        pass


def save_level(level):
    save(SAVE, "level", level)


class Audio:
    

    def __init__(self):
        self.set(load(SETTINGS, "volume", 0.7))
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
        save(SETTINGS, "volume", round(self.volume, 2))


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


def settings(screen, audio, backdrop):
    
    clock, dim, f = pygame.time.Clock(), dimmer(), font("VT323-Regular.ttf", 34)
    track, back = pygame.Rect(220, 232, 360, 14), pygame.Rect(250, 318, 300, 46)
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
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if track.inflate(24, 36).collidepoint(event.pos):
                    dragging = True
                elif back.collidepoint(event.pos):
                    done = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if dragging and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                audio.set((event.pos[0] - track.x) / track.width)

        backdrop(screen)
        screen.blit(dim, (0, 0))
        pygame.draw.rect(screen, PANEL, (150, 140, 500, 240), border_radius=10)
        pygame.draw.rect(screen, BORDER, (150, 140, 500, 240), 4, border_radius=10)
        text(screen, f, f"Volume: {round(audio.volume * 100)}%", DARK, (W // 2, 190))
        pygame.draw.rect(screen, (170, 40, 40), track)
        pygame.draw.rect(screen, (40, 190, 80), (*track.topleft, int(track.width * audio.volume), track.height))
        pygame.draw.rect(screen, (20, 20, 25), track, 3)
        handle = pygame.Rect(0, 0, 14, 32)
        handle.center = (track.x + int(track.width * audio.volume), track.centery)
        pygame.draw.rect(screen, SELECT, handle, border_radius=3)
        pygame.draw.rect(screen, (35, 95, 145), handle, 3, border_radius=3)
        button(screen, f, back, "Back", True)
        text(screen, f, "Left/Right: volume    Esc: back", LIGHT, (W // 2, 424))
        pygame.display.flip()
        clock.tick(60)

    audio.save()


def run_menu(screen, audio, title, items, backdrop, disabled=(), selected=0, escape="Quit"):
  
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
                settings(screen, audio, backdrop)
            elif choice:
                return choice

        backdrop(screen)
        screen.blit(dim, (0, 0))
        text(screen, big, title, LIGHT, (W // 2, 82))
        for i, rect in enumerate(rects):
            button(screen, small, rect, items[i], i == index, items[i] not in disabled)
        pygame.display.flip()
        clock.tick(60)


def main_menu(screen, audio, level_count):
    
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

    level = load(SAVE, "level", None)
    has_save = isinstance(level, int) and level >= 0
    choice = run_menu(
        screen, audio, "MIGUEL", ["New Game", "Continue", "Settings", "Quit"], backdrop,
        disabled=() if has_save else ("Continue",), selected=1 if has_save else 0,
    )
    if choice == "New Game":
        return 0
    if choice == "Continue":
        return min(level, level_count - 1)
    return None

def pause_menu(screen, audio):
   
    snapshot = screen.copy()
    choice = run_menu(
        screen, audio, "PAUSED", ["Resume", "Settings", "Main Menu", "Quit"],
        lambda s: s.blit(snapshot, (0, 0)), escape="Resume",
    )
    return choice.lower().replace(" ", "_")