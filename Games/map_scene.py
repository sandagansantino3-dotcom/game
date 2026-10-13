class MapScene:
    def __init__(self, player, enemy, tile_map, background):
        self.player = player
        self.enemy = enemy
        self.tile_map = tile_map
        self.background = background

    def update(self, keys):
        
        self.player.update(
            keys,
            self.tile_map.solid_rects,
            self.tile_map.width
        )

        if not self.enemy.defeated:
            self.enemy.update(self.tile_map.solid_rects)

            if self.player.rect.colliderect(self.enemy.rect):
                return "enemy"

        # Only reached when the enemy is defeated. Before that, the
        # right edge simply acts like a wall.
        elif self.player.rect.right >= self.tile_map.width:
            return "exit"

        return None

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.tile_map.draw(screen)
        self.player.draw(screen)

        # A defeated enemy disappears from the map
        if not self.enemy.defeated:
            self.enemy.draw(screen)