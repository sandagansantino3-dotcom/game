class MapScene:
    def __init__(
        self,
        player,
        enemy,
        tile_map,
        background
    ):
        self.player = player
        self.enemy = enemy
        self.tile_map = tile_map
        self.background = background
        self.camera_x = 0

    def update(self, keys):
        self.player.update(
            keys,
            self.tile_map.solid_rects,
            self.tile_map.width
        )

        if not self.enemy.defeated:
            self.enemy.update(
                self.tile_map.solid_rects
            )

            if self.player.rect.colliderect(
                self.enemy.rect
            ):
                return "enemy"

        elif (
            self.player.rect.right
            >= self.tile_map.width
        ):
            return "exit"

        return None

    def update_camera(self, screen):
        target_x = (
            self.player.rect.centerx
            - screen.get_width() // 2
        )

        max_camera_x = max(
            0,
            self.tile_map.width
            - screen.get_width()
        )

        self.camera_x = max(
            0,
            min(
                target_x,
                max_camera_x
            )
        )

    def draw(self, screen):
        self.update_camera(screen)

        screen.blit(
            self.background,
            (0, 0)
        )

        self.tile_map.draw(
            screen,
            self.camera_x
        )

        self.player.draw(
            screen,
            self.camera_x
        )

        if not self.enemy.defeated:
            self.enemy.draw(
                screen,
                self.camera_x
            )