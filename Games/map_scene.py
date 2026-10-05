class MapScene:
    def __init__(self, player, enemy, tile_map, background):
        self.player = player
        self.enemy = enemy
        self.tile_map = tile_map
        self.background = background

    def update(self, keys):
        """Move everything. Returns True if the player touched the enemy."""
        self.player.update(
            keys,
            self.tile_map.solid_rects,
            self.tile_map.width
        )

        self.enemy.update(self.tile_map.solid_rects)

        return self.player.rect.colliderect(self.enemy.rect)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.tile_map.draw(screen)
        self.player.draw(screen)
        self.enemy.draw(screen)