import pygame


class BattleTransition:
    def __init__(self, duration=500):
        # Duration of closing/opening 
        self.duration = duration

        self.active = False
        self.phase = "closing"
        self.phase_start = 0

    def start(self):
        if self.active:
            return

        self.active = True
        self.phase = "closing"
        self.phase_start = pygame.time.get_ticks()

    def update(self):
        if not self.active:
            return False

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.phase_start

        if elapsed >= self.duration:

            if self.phase == "closing":
                self.phase = "opening"
                self.phase_start = current_time

                return True

            elif self.phase == "opening":
                self.active = False

        return False

    def get_cover_amount(self):
        if not self.active:
            return 0

        elapsed = (
            pygame.time.get_ticks() - self.phase_start
        )

        progress = min(1, elapsed / self.duration)

        if self.phase == "closing":
            return progress
        
        return 1 - progress

    def draw(self, screen):
        if not self.active:
            return

        width = screen.get_width()
        height = screen.get_height()

        cover_amount = self.get_cover_amount()

        bar_height = int(
            (height / 2) * cover_amount
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            pygame.Rect(
                0,
                0,
                width,
                bar_height
            )
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            pygame.Rect(
                0,
                height - bar_height,
                width,
                bar_height
            )
        )