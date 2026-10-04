import pygame

from challenges import CHALLENGES


class BattleScene:
    def __init__(self, player, boss):
        self.player = player
        self.boss = boss

        # Temporary battle stats
        self.player.max_health = 100
        self.player.health = 100

        self.boss.max_health = 100
        self.boss.health = 100
        self.boss.attack_damage = 20

        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.normal_font = pygame.font.Font(None, 28)
        self.code_font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 22)

        # Challenge information
        self.challenge_index = 0
        self.current_challenge = CHALLENGES[0]

        # Player's typed answer
        self.answer = ""

        # Battle states:
        # answering, feedback, victory, defeat
        self.state = "answering"

        self.message = ""
        self.message_color = (255, 255, 255)

        # Timer
        self.start_time = pygame.time.get_ticks()
        self.feedback_start = 0
        self.feedback_duration = 1200

    # EVENT HANDLING

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # Restart battle after winning or losing
        if self.state in ("victory", "defeat"):
            if event.key == pygame.K_r:
                self.reset_battle()

            return

        # Do not allow typing while feedback is displayed
        if self.state != "answering":
            return

        if event.key == pygame.K_BACKSPACE:
            self.answer = self.answer[:-1]

        elif event.key == pygame.K_TAB:
            # Add four spaces for Python indentation
            self.answer += "    "

        elif event.key == pygame.K_RETURN:
            keys = pygame.key.get_mods()

            # Shift + Enter creates a new line
            if keys & pygame.KMOD_SHIFT:
                self.answer += "\n"

            # Enter submits the answer
            else:
                self.check_answer()

        else:
            # event.unicode contains the character typed
            if event.unicode and len(self.answer) < 300:
                self.answer += event.unicode

    # UPDATE

    def update(self):
        if self.state == "answering":
            if self.get_time_left() <= 0:
                self.player.health -= self.boss.attack_damage

                self.player.health = max(
                    0,
                    self.player.health
                )

                self.message = "TIME UP! You were damaged!"
                self.message_color = (255, 80, 80)

                self.begin_feedback()

        elif self.state == "feedback":
            current_time = pygame.time.get_ticks()

            if (
                current_time - self.feedback_start
                >= self.feedback_duration
            ):
                if self.boss.health <= 0:
                    self.state = "victory"

                elif self.player.health <= 0:
                    self.state = "defeat"

                else:
                    self.load_next_challenge()

    # ANSWER CHECKING

    def check_answer(self):
        submitted_answer = self.answer.strip()

        correct_answer = (
            self.current_challenge["answer"].strip()
        )

        if submitted_answer == correct_answer:
            damage = self.current_challenge["damage"]

            self.boss.health -= damage
            self.boss.health = max(0, self.boss.health)

            self.message = f"CORRECT! Boss took {damage} damage!"
            self.message_color = (80, 255, 120)

        else:
            self.player.health -= self.boss.attack_damage

            self.player.health = max(
                0,
                self.player.health
            )

            self.message = "WRONG! You were damaged!"
            self.message_color = (255, 80, 80)

        self.begin_feedback()

    def begin_feedback(self):
        self.state = "feedback"
        self.feedback_start = pygame.time.get_ticks()

    def load_next_challenge(self):
        self.challenge_index += 1

        if self.challenge_index >= len(CHALLENGES):
            self.challenge_index = 0

        self.current_challenge = CHALLENGES[
            self.challenge_index
        ]

        self.answer = ""
        self.message = ""
        self.state = "answering"
        self.start_time = pygame.time.get_ticks()

    def reset_battle(self):
        self.player.health = self.player.max_health
        self.boss.health = self.boss.max_health

        self.challenge_index = 0
        self.current_challenge = CHALLENGES[0]

        self.answer = ""
        self.message = ""
        self.state = "answering"
        self.start_time = pygame.time.get_ticks()

    # TIMER

    def get_time_left(self):
        if self.state != "answering":
            return 0

        elapsed = (
            pygame.time.get_ticks() - self.start_time
        ) / 1000

        time_limit = self.current_challenge["time"]

        return max(0, time_limit - elapsed)

    # DRAWING

    def draw(self, screen):
        width = screen.get_width()
        height = screen.get_height()

        # Battle background
        screen.fill((135, 190, 220))

        # Ground
        pygame.draw.rect(
            screen,
            (95, 150, 90),
            (
                0,
                int(height * 0.48),
                width,
                int(height * 0.20)
            )
        )

        # Battle title
        title = self.title_font.render(
            "CODE BATTLE",
            True,
            (20, 20, 30)
        )

        screen.blit(
            title,
            (
                width // 2 - title.get_width() // 2,
                10
            )
        )

        # Player is larger and closer to the screen
        player_box = pygame.Rect(
            int(width * 0.10),
            int(height * 0.34),
            int(width * 0.18),
            int(height * 0.28)
        )

        # Boss is smaller and farther from the screen
        boss_box = pygame.Rect(
            int(width * 0.72),
            int(height * 0.15),
            int(width * 0.12),
            int(height * 0.20)
        )

        # Player box
        pygame.draw.rect(
            screen,
            (50, 120, 255),
            player_box
        )

        pygame.draw.rect(
            screen,
            (20, 20, 30),
            player_box,
            4
        )

        # Boss box
        pygame.draw.rect(
            screen,
            (220, 60, 60),
            boss_box
        )

        pygame.draw.rect(
            screen,
            (20, 20, 30),
            boss_box,
            4
        )

        # Character labels
        player_label = self.normal_font.render(
            "PLAYER",
            True,
            (255, 255, 255)
        )

        boss_label = self.small_font.render(
            "BOSS",
            True,
            (255, 255, 255)
        )

        screen.blit(
            player_label,
            (
                player_box.centerx
                - player_label.get_width() // 2,

                player_box.centery
                - player_label.get_height() // 2
            )
        )

        screen.blit(
            boss_label,
            (
                boss_box.centerx
                - boss_label.get_width() // 2,

                boss_box.centery
                - boss_label.get_height() // 2
            )
        )

        # ----------------------------------------------
        # Health bars
        # ----------------------------------------------

        self.draw_health_bar(
            screen,
            x=int(width * 0.05),
            y=55,
            bar_width=int(width * 0.30),
            health=self.boss.health,
            max_health=self.boss.max_health,
            label="BOSS"
        )

        self.draw_health_bar(
            screen,
            x=int(width * 0.62),
            y=int(height * 0.45),
            bar_width=int(width * 0.30),
            health=self.player.health,
            max_health=self.player.max_health,
            label="PLAYER"
        )

        # ----------------------------------------------
        # Bottom coding panel
        # ----------------------------------------------

        panel = pygame.Rect(
            int(width * 0.03),
            int(height * 0.69),
            int(width * 0.94),
            int(height * 0.28)
        )

        pygame.draw.rect(
            screen,
            (28, 32, 42),
            panel,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            (235, 235, 245),
            panel,
            3,
            border_radius=10
        )

        if self.state in ("victory", "defeat"):
            self.draw_end_screen(screen, panel)
            return

        # Broken-code label
        challenge_label = self.small_font.render(
            "FIX THE BROKEN CODE:",
            True,
            (255, 220, 80)
        )

        screen.blit(
            challenge_label,
            (panel.x + 15, panel.y + 10)
        )

        # Broken code
        self.draw_multiline_text(
            screen,
            self.current_challenge["broken"],
            panel.x + 15,
            panel.y + 35,
            (255, 255, 255)
        )

        # Answer box
        answer_box = pygame.Rect(
            panel.x + 15,
            panel.y + int(panel.height * 0.60),
            panel.width - 130,
            38
        )

        pygame.draw.rect(
            screen,
            (245, 245, 245),
            answer_box
        )

        pygame.draw.rect(
            screen,
            (80, 150, 255),
            answer_box,
            3
        )

        answer_text = self.code_font.render(
            self.answer.replace("\n", " ↵ "),
            True,
            (20, 20, 25)
        )

        screen.blit(
            answer_text,
            (
                answer_box.x + 8,
                answer_box.y + 8
            )
        )

        # Timer
        time_left = int(self.get_time_left() + 0.99)

        timer_text = self.normal_font.render(
            f"TIME: {time_left}",
            True,
            (255, 220, 60)
        )

        screen.blit(
            timer_text,
            (
                panel.right - timer_text.get_width() - 15,
                answer_box.y + 5
            )
        )

        # Feedback message
        if self.message:
            message_surface = self.small_font.render(
                self.message,
                True,
                self.message_color
            )

            screen.blit(
                message_surface,
                (
                    panel.centerx
                    - message_surface.get_width() // 2,

                    panel.bottom - 25
                )
            )

    def draw_health_bar(
        self,
        screen,
        x,
        y,
        bar_width,
        health,
        max_health,
        label
    ):
        label_surface = self.small_font.render(f"{label} HP: {health}/{max_health}",True,(20, 20, 25))

        screen.blit(label_surface, (x, y))

        bar_y = y + 23
        bar_height = 18

        # Red background
        pygame.draw.rect(
            screen,
            (170, 40, 40),
            (x, bar_y, bar_width, bar_height)
        )

        health_percent = health / max_health

        # Green remaining health
        pygame.draw.rect(
            screen,
            (40, 190, 80),
            (
                x,
                bar_y,
                int(bar_width * health_percent),
                bar_height
            )
        )

        pygame.draw.rect(
            screen,
            (20, 20, 25),
            (x, bar_y, bar_width, bar_height),
            3
        )

    def draw_multiline_text(self, screen, text, x, y, color):
        for line_number, line in enumerate(text.splitlines()):
            line_surface = self.code_font.render(
                line,
                True,
                color
            )

            screen.blit(
                line_surface,
                (
                    x,
                    y + line_number * 22
                )
            )

    def draw_end_screen(self, screen, panel):
        if self.state == "victory":
            text = "YOU DEFEATED THE BUG!"
            color = (80, 255, 120)

        else:
            text = "YOU WERE DEFEATED!"
            color = (255, 80, 80)

        end_text = self.title_font.render(
            text,
            True,
            color
        )

        restart_text = self.normal_font.render(
            "Press R to battle again",
            True,
            (255, 255, 255)
        )

        screen.blit(
            end_text,
            (
                panel.centerx - end_text.get_width() // 2,
                panel.y + 35
            )
        )

        screen.blit(
            restart_text,
            (
                panel.centerx
                - restart_text.get_width() // 2,

                panel.y + 85
            )
        )