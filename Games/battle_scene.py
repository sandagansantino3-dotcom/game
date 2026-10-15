from pathlib import Path
from functools import lru_cache
import pygame

from challenges import (
    BOSS_CHALLENGES,
    DEFAULT_CHALLENGES
)


@lru_cache(maxsize=64)
def cached_font(path, size):
    """Avoid reopening the same font while the battle panel redraws."""
    return pygame.font.Font(path, size)


@lru_cache(maxsize=32)
def cached_image(path, size, alpha):
    """Cache loaded and scaled battle images between level changes."""
    image = pygame.image.load(path)
    image = image.convert_alpha() if alpha else image.convert()
    return pygame.transform.scale(image, size)


class BattleScene:
    def __init__(
        self,
        player,
        boss,
        boss_data
    ):
        self.player = player
        self.boss = boss
        self.boss_name = boss_data["name"]
        self.player_name = "Player"

        self.challenges = (
            BOSS_CHALLENGES.get(
                self.boss_name,
                DEFAULT_CHALLENGES
            )
        )

        assets = (
            Path(__file__).parent
            / "assets"
        )

        background_path = (
            assets
            / "backgrounds"
            / boss_data[
                "battle_background"
            ]
        )

        self.background = cached_image(
            str(background_path),
            (800, 450),
            False
        )

        self.player_image = cached_image(
            str(assets / "player" / "PlayerBS.png"),
            (150, 150),
            True
        )

        self.boss_image = cached_image(
            str(assets / boss_data["battle_sprite"]),
            tuple(boss_data["battle_size"]),
            True
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

        self.text_font_path = str(
            text_font_path
        )

        self.title_font = cached_font(str(title_font_path), 28)

        self.normal_font = cached_font(self.text_font_path, 26)

        self.code_font = self.normal_font

        self.small_font = cached_font(self.text_font_path, 22)

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
            35,
            95,
            145
        )

        self.start_time = (
            pygame.time.get_ticks()
        )

        self.feedback_start = 0
        self.feedback_duration = 1200
        self.end_start = 0

        pygame.key.start_text_input()

    def handle_event(
        self,
        event
    ):
        if self.state == "victory":
            return

        if self.state == "defeat":
            if (
                event.type
                == pygame.KEYDOWN
                and event.key
                == pygame.K_r
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
                170,
                45,
                45
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
                35,
                125,
                65
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
                170,
                45,
                45
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

        return max(
            0,
            self.current_challenge["time"]
            - elapsed
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

    def get_fitted_font(
        self,
        text,
        max_width,
        start_size=26,
        minimum_size=18
    ):
        lines = (
            text.splitlines()
            or [""]
        )

        for size in range(
            start_size,
            minimum_size - 1,
            -1
        ):
            font = cached_font(self.text_font_path, size)

            widest = max(
                font.size(line)[0]
                for line in lines
            )

            if widest <= max_width:
                return font

        return cached_font(self.text_font_path, minimum_size)

    def wrap_text(
        self,
        text,
        font,
        max_width
    ):
        wrapped = []

        for source_line in (
            text.splitlines()
            or [""]
        ):
            if not source_line:
                wrapped.append("")
                continue

            current = ""

            for character in source_line:
                test_line = (
                    current + character
                )

                if (
                    current
                    and font.size(
                        test_line
                    )[0] > max_width
                ):
                    wrapped.append(current)
                    current = character

                else:
                    current = test_line

            wrapped.append(current)

        return wrapped

    def draw_panel_frame(
        self,
        screen,
        panel
    ):
        pygame.draw.rect(
            screen,
            (231, 239, 203),
            panel,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            (70, 91, 72),
            panel,
            4,
            border_radius=10
        )

    def draw_dialogue_panel(
        self,
        screen
    ):
        screen_width = (
            screen.get_width()
        )

        screen_height = (
            screen.get_height()
        )

        horizontal_margin = 14
        padding = 14

        panel_width = (
            screen_width
            - horizontal_margin * 2
        )

        content_width = (
            panel_width
            - padding * 2
        )

        question_width = (
            content_width - 125
        )

        broken = (
            self.current_challenge[
                "broken"
            ]
        )

        broken_lines = (
            broken.splitlines()
            or [""]
        )

        question_text = (
            "Fix the broken code: "
            + broken_lines[0]
        )

        if len(broken_lines) > 1:
            question_text += (
                "\n"
                + "\n".join(
                    broken_lines[1:]
                )
            )

        question_font = (
            self.get_fitted_font(
                question_text,
                question_width,
                26,
                18
            )
        )

        question_lines = self.wrap_text(
            question_text,
            question_font,
            question_width
        )

        question_line_height = max(
            20,
            question_font.get_linesize()
        )

        question_height = (
            len(question_lines)
            * question_line_height
        )

        answer_lines = (
            self.answer.split("\n")
        )

        visible_answer_lines = (
            answer_lines[-4:]
        )

        visible_line_count = max(
            1,
            len(visible_answer_lines)
        )

        answer_text = max(
            visible_answer_lines,
            key=len,
            default=""
        )

        answer_font = (
            self.get_fitted_font(
                answer_text,
                content_width - 44,
                26,
                18
            )
        )

        answer_line_height = max(
            22,
            answer_font.get_linesize()
        )

        answer_box_height = max(
            38,
            visible_line_count
            * answer_line_height
            + 12
        )

        status_height = 24

        panel_height = (
            padding
            + question_height
            + 8
            + answer_box_height
            + 7
            + status_height
            + 8
        )

        panel = pygame.Rect(
            horizontal_margin,
            screen_height
            - panel_height
            - 8,
            panel_width,
            panel_height
        )

        self.draw_panel_frame(
            screen,
            panel
        )

        question_x = (
            panel.x + padding
        )

        question_y = (
            panel.y + padding - 2
        )

        for index, line in enumerate(
            question_lines
        ):
            surface = question_font.render(
                line,
                True,
                (28, 34, 30)
            )

            screen.blit(
                surface,
                (
                    question_x,
                    question_y
                    + index
                    * question_line_height
                )
            )

        time_left = int(
            self.get_time_left() + 0.99
        )

        timer_surface = (
            self.normal_font.render(
                f"Time {time_left}s",
                True,
                (35, 76, 120)
            )
        )

        screen.blit(
            timer_surface,
            (
                panel.right
                - padding
                - timer_surface.get_width(),
                question_y
            )
        )

        answer_box = pygame.Rect(
            panel.x + padding,
            question_y
            + question_height
            + 8,
            content_width,
            answer_box_height
        )

        pygame.draw.rect(
            screen,
            (251, 250, 232),
            answer_box,
            border_radius=3
        )

        pygame.draw.rect(
            screen,
            (42, 48, 43),
            answer_box,
            2,
            border_radius=3
        )

        prompt_surface = (
            answer_font.render(
                ">",
                True,
                (25, 29, 27)
            )
        )

        first_line_y = (
            answer_box.y + 6
        )

        screen.blit(
            prompt_surface,
            (
                answer_box.x + 8,
                first_line_y
            )
        )

        cursor_visible = (
            self.state == "answering"
            and pygame.time.get_ticks()
            // 500 % 2 == 0
        )

        for index, line in enumerate(
            visible_answer_lines
        ):
            display_line = line

            if (
                index
                == len(
                    visible_answer_lines
                ) - 1
                and cursor_visible
            ):
                display_line += "_"

            line_surface = (
                answer_font.render(
                    display_line,
                    True,
                    (25, 29, 27)
                )
            )

            screen.blit(
                line_surface,
                (
                    answer_box.x + 30,
                    first_line_y
                    + index
                    * answer_line_height
                )
            )

        if self.message:
            status_text = self.message
            status_color = (
                self.message_color
            )

        else:
            status_text = (
                "Shift+Enter: new line   "
                "Tab: indent   "
                "Enter: submit"
            )

            status_color = (
                35,
                76,
                120
            )

        status_font = (
            self.get_fitted_font(
                status_text,
                content_width,
                22,
                17
            )
        )

        status_surface = (
            status_font.render(
                status_text,
                True,
                status_color
            )
        )

        screen.blit(
            status_surface,
            (
                panel.x + padding,
                answer_box.bottom + 5
            )
        )

        return panel

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
            + self.player_image.get_width()
            // 2
            - bar_width // 2
        )

        boss_bar_x = (
            boss_x
            + self.boss_image.get_width()
            // 2
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
            self.player_name
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

        if self.state in (
            "victory",
            "defeat"
        ):
            panel = pygame.Rect(
                14,
                height - 134,
                width - 28,
                126
            )

            self.draw_panel_frame(
                screen,
                panel
            )

            self.draw_end_screen(
                screen,
                panel
            )

            return

        self.draw_dialogue_panel(screen)

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
            - label_surface.get_width()
            // 2
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
                35,
                125,
                65
            )

        else:
            text = (
                "You were defeated!"
            )

            color = (
                170,
                45,
                45
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
                panel.y + 25
            )
        )

        if self.state == "defeat":
            restart_text = (
                self.normal_font.render(
                    "Press R to battle again",
                    True,
                    (35, 76, 120)
                )
            )

            screen.blit(
                restart_text,
                (
                    panel.centerx
                    - restart_text.get_width()
                    // 2,
                    panel.y + 75
                )
            )
