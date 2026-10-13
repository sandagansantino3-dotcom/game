from pathlib import Path
import pygame

from challenges import (
    BOSS_CHALLENGES,
    DEFAULT_CHALLENGES
)


class BattleScene:
    def __init__(self, player, boss, boss_data):
        self.player = player
        self.boss = boss
        self.boss_name = boss_data["name"]
        self.challenges = (
            BOSS_CHALLENGES.get(
            self.boss_name,
            DEFAULT_CHALLENGES
            )
        )
        assets = Path(__file__).parent / "assets"

        background_path = (
            assets
            / "backgrounds"
            / boss_data["battle_background"]
        )

        self.background = pygame.image.load(
            str(background_path)
        ).convert()

        self.background = pygame.transform.scale(
            self.background,
            (800, 450)
        )

        player_image_path = (
            assets
            / "player"
            / "PlayerBS.png"
        )

        self.player_image = pygame.image.load(
            str(player_image_path)
        ).convert_alpha()

        self.player_image = pygame.transform.scale(
            self.player_image,
            (150, 150)
        )

        boss_image_path = (
            assets
            / boss_data["battle_sprite"]
        )

        self.boss_image = pygame.image.load(
            str(boss_image_path)
        ).convert_alpha()

        self.boss_image = pygame.transform.scale(
            self.boss_image,
            boss_data["battle_size"]
        )

        title_font_path = (
            assets
            / "fonts"
            / "Silkscreen-Regular.ttf"
        )

        text_font_path = (
            assets
            / "fonts"
            / "VT323-Regular.ttf"
        )

        self.title_font = pygame.font.Font(
            str(title_font_path),
            28
        )

        self.normal_font = pygame.font.Font(
            str(text_font_path),
            26
        )

        self.code_font = pygame.font.Font(
            str(text_font_path),
            26
        )

        self.small_font = pygame.font.Font(
            str(text_font_path),
            22
        )

        self.player.max_health = 100
        self.player.health = 100

        self.boss.max_health = 100
        self.boss.health = 100
        self.boss.attack_damage = 10

        self.challenge_index = 0
        self.current_challenge = (
            self.challenges[0]
        )

        self.answer = ""
        self.state = "answering"

        self.message = ""
        self.message_color = (
            255,
            255,
            255
        )

        self.start_time = pygame.time.get_ticks()

        self.feedback_start = 0
        self.feedback_duration = 1200
        self.end_start = 0

        pygame.key.start_text_input()

    def handle_event(self, event):
        if self.state == "victory":
            return

        if self.state == "defeat":
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):
                self.reset_battle()

            return

        if self.state != "answering":
            return

        if event.type == pygame.TEXTINPUT:
            remaining = (
                300 - len(self.answer)
            )

            if remaining > 0:
                self.answer += (
                    event.text[:remaining]
                )

            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_BACKSPACE:
            self.answer = self.answer[:-1]

        elif event.key == pygame.K_TAB:
            remaining = (
                300 - len(self.answer)
            )

            self.answer += (
                "    "[:remaining]
            )

        elif event.key == pygame.K_RETURN:
            if (
                pygame.key.get_mods()
                & pygame.KMOD_SHIFT
            ):
                if len(self.answer) < 300:
                    self.answer += "\n"

            else:
                self.check_answer()

    def update(self):
        if (
            self.state == "answering"
            and self.get_time_left() <= 0
        ):
            self.player.health = max(
                0,
                self.player.health
                - self.boss.attack_damage
            )

            self.message = (
                "Time is up! "
                "You were damaged!"
            )

            self.message_color = (
                255,
                80,
                80
            )

            self.begin_feedback()

        elif self.state == "feedback":
            elapsed = (
                pygame.time.get_ticks()
                - self.feedback_start
            )

            if (
                elapsed
                >= self.feedback_duration
            ):
                if self.boss.health <= 0:
                    self.state = "victory"

                    self.end_start = (
                        pygame.time.get_ticks()
                    )

                elif self.player.health <= 0:
                    self.state = "defeat"

                else:
                    self.load_next_challenge()

    def check_answer(self):
        submitted = (
            self.answer.strip()
        )

        correct = (
            self.current_challenge[
                "answer"
            ].strip()
        )

        if submitted == correct:
            damage = (
                self.current_challenge[
                    "damage"
                ]
            )

            self.boss.health = max(
                0,
                self.boss.health - damage
            )

            self.message = (
                f"Correct! "
                f"{self.boss_name} took "
                f"{damage} damage!"
            )

            self.message_color = (
                80,
                255,
                120
            )

        else:
            self.player.health = max(
                0,
                self.player.health
                - self.boss.attack_damage
            )

            self.message = (
                "Wrong! "
                "You were damaged!"
            )

            self.message_color = (
                255,
                80,
                80
            )

        self.begin_feedback()

    def begin_feedback(self):
        self.state = "feedback"

        self.feedback_start = (
            pygame.time.get_ticks()
        )

    def load_next_challenge(self):
        self.challenge_index = (
            self.challenge_index + 1
        ) % len(self.challenges)

        self.current_challenge = (
            self.challenges[
        self.challenge_index
            ]
        )

        self.answer = ""
        self.message = ""
        self.state = "answering"

        self.start_time = (
            pygame.time.get_ticks()
        )

    def reset_battle(self):
        self.player.health = (
            self.player.max_health
        )

        self.boss.health = (
            self.boss.max_health
        )

        self.challenge_index = 0
        self.current_challenge = (
            self.challenges[0]
        )

        self.answer = ""
        self.message = ""
        self.state = "answering"

        self.start_time = (
            pygame.time.get_ticks()
        )

    def get_time_left(self):
        if self.state != "answering":
            return 0

        elapsed = (
            pygame.time.get_ticks()
            - self.start_time
        ) / 1000

        time_limit = (
            self.current_challenge["time"]
        )

        return max(
            0,
            time_limit - elapsed
        )

    def victory_delay_done(
        self,
        delay=1500
    ):
        return (
            pygame.time.get_ticks()
            - self.end_start
            >= delay
        )

    def draw(self, screen):
        width = screen.get_width()
        height = screen.get_height()

        screen.blit(
            self.background,
            (0, 0)
        )

        title = self.title_font.render(
            "Code Battle",
            True,
            (255, 245, 255)
        )

        screen.blit(
            title,
            (
                width // 2
                - title.get_width() // 2,
                10
            )
        )

        player_x = int(
            width * 0.16
        )

        player_y = (
            int(height * 0.68)
            - self.player_image.get_height()
        )

        boss_x = (
            int(width * 0.84)
            - self.boss_image.get_width()
        )

        boss_y = (
            int(height * 0.62)
            - self.boss_image.get_height()
        )

        screen.blit(
            self.player_image,
            (
                player_x,
                player_y
            )
        )

        screen.blit(
            self.boss_image,
            (
                boss_x,
                boss_y
            )
        )

        bar_width = 160

        player_bar_x = (
            player_x
            + self.player_image.get_width() // 2
            - bar_width // 2
        )

        boss_bar_x = (
            boss_x
            + self.boss_image.get_width() // 2
            - bar_width // 2
        )

        player_bar_y = max(
            45,
            player_y - 48
        )

        boss_bar_y = max(
            45,
            boss_y - 48
        )

        self.draw_health_bar(
            screen,
            player_bar_x,
            player_bar_y,
            bar_width,
            self.player.health,
            self.player.max_health,
            "Player"
        )

        self.draw_health_bar(
            screen,
            boss_bar_x,
            boss_bar_y,
            bar_width,
            self.boss.health,
            self.boss.max_health,
            self.boss_name
        )

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

        if self.state in (
            "victory",
            "defeat"
        ):
            self.draw_end_screen(
                screen,
                panel
            )

            return

        challenge_label = (
            self.small_font.render(
                "Fix the broken code:",
                True,
                (255, 220, 80)
            )
        )

        screen.blit(
            challenge_label,
            (
                panel.x + 15,
                panel.y + 8
            )
        )

        self.draw_multiline_text(
            screen,
            self.current_challenge[
                "broken"
            ],
            panel.x + 15,
            panel.y + 32,
            (255, 255, 255)
        )

        answer_box = pygame.Rect(
            panel.x + 15,
            panel.y
            + int(panel.height * 0.60),
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
            self.answer.replace(
                "\n",
                " ↵ "
            ),
            True,
            (20, 20, 25)
        )

        old_clip = screen.get_clip()

        screen.set_clip(
            answer_box.inflate(
                -12,
                -6
            )
        )

        screen.blit(
            answer_text,
            (
                answer_box.x + 8,
                answer_box.y + 5
            )
        )

        screen.set_clip(old_clip)

        time_left = int(
            self.get_time_left() + 0.99
        )

        timer_text = (
            self.normal_font.render(
                f"Time: {time_left}",
                True,
                (255, 220, 60)
            )
        )

        screen.blit(
            timer_text,
            (
                panel.right
                - timer_text.get_width()
                - 15,
                answer_box.y + 5
            )
        )

        if self.message:
            message_surface = (
                self.small_font.render(
                    self.message,
                    True,
                    self.message_color
                )
            )

            screen.blit(
                message_surface,
                (
                    panel.centerx
                    - message_surface.get_width()
                    // 2,
                    panel.bottom - 24
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
        label_surface = (
            self.small_font.render(
                (
                    f"{label} HP: "
                    f"{health}/{max_health}"
                ),
                True,
                (225, 245, 255)
            )
        )

        label_x = (
            x
            + bar_width // 2
            - label_surface.get_width() // 2
        )

        screen.blit(
            label_surface,
            (
                label_x,
                y
            )
        )

        bar_y = y + 23
        bar_height = 18

        health_percent = (
            health / max_health
        )

        pygame.draw.rect(
            screen,
            (170, 40, 40),
            (
                x,
                bar_y,
                bar_width,
                bar_height
            )
        )

        pygame.draw.rect(
            screen,
            (40, 190, 80),
            (
                x,
                bar_y,
                int(
                    bar_width
                    * health_percent
                ),
                bar_height
            )
        )

        pygame.draw.rect(
            screen,
            (20, 20, 25),
            (
                x,
                bar_y,
                bar_width,
                bar_height
            ),
            3
        )

    def draw_multiline_text(
        self,
        screen,
        text,
        x,
        y,
        color
    ):
        for line_number, line in enumerate(
            text.splitlines()
        ):
            line_surface = (
                self.code_font.render(
                    line,
                    True,
                    color
                )
            )

            screen.blit(
                line_surface,
                (
                    x,
                    y + line_number * 24
                )
            )

    def draw_end_screen(
        self,
        screen,
        panel
    ):
        if self.state == "victory":
            text = (
                f"You defeated "
                f"{self.boss_name}!"
            )

            color = (
                80,
                255,
                120
            )

        else:
            text = (
                "You were defeated!"
            )

            color = (
                255,
                80,
                80
            )

        end_text = (
            self.title_font.render(
                text,
                True,
                color
            )
        )

        screen.blit(
            end_text,
            (
                panel.centerx
                - end_text.get_width()
                // 2,
                panel.y + 30
            )
        )

        if self.state == "defeat":
            restart_text = (
                self.normal_font.render(
                    "Press R to battle again",
                    True,
                    (255, 255, 255)
                )
            )

            screen.blit(
                restart_text,
                (
                    panel.centerx
                    - restart_text.get_width()
                    // 2,
                    panel.y + 85
                )
            )