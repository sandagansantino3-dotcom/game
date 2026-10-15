from pathlib import Path
from functools import lru_cache
import heapq
import math
import pygame


TILE_SIZE = 32

ASSETS = (
    Path(__file__).parent
    / "assets"
)

SPRITE_SETS = {
    "granny": {
        "folder": "enemy",
        "suffix": "G",
        "count": 4
    },
    # Khal El: only right-facing frames R1K..R4K are needed;
    # the left-facing frames are made by flipping them.
    "khal": {
        "folder": "enemy",
        "suffix": "K",
        "count": 4,
        "mirror": True
    },
    # Prof. Jamis: only right-facing frames R1J..R5J are needed;
    # the left-facing frames are made by flipping them.
    "jamis": {
        "folder": "enemy",
        "suffix": "J",
        "count": 5,
        "mirror": True
    },
}


@lru_cache(maxsize=32)
def load_frames(
    sprite_set,
    side,
    size
):
    info = SPRITE_SETS[sprite_set]
    folder = ASSETS / info["folder"]
    frames = []

    mirror = (
        info.get("mirror", False)
        and side == "L"
    )

    file_side = "R" if mirror else side

    for i in range(1, info["count"] + 1):
        exact = folder / (
            f"{file_side}{i}"
            f"{info['suffix']}.png"
        )

        if exact.exists():
            path = exact
        else:
            matches = sorted(
                folder.glob(
                    f"{file_side}{i}"
                    f"{info['suffix']}*"
                )
            )

            if not matches:
                raise FileNotFoundError(
                    f"Missing {exact.name}"
                )

            path = matches[0]

        image = pygame.image.load(str(path))

        if mirror:
            image = pygame.transform.flip(
                image,
                True,
                False
            )

        frames.append(
            pygame.transform.scale(image, size)
        )

    return frames


class Enemy:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        end,
        sprite_set="khal"
    ):
        self.x = float(x)
        self.y = float(y)

        self.width = width
        self.height = height

        # Patrol limits.
        self.path = [x, end]

        self.walk_count = 0

        self.move_speed = 3
        self.speed = self.move_speed
        self.direction = 1

        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = 12
        self.on_ground = False

        self.detection_range = 550
        self.chasing = False

        # Pathfinding A* route state.
        self._route = []
        self._path_timer = 0
        self._nav_source = None
        self._nav_graph_cache = None

        self.max_health = 100
        self.health = self.max_health
        self.attack_damage = 20

        self.defeated = False

        self.walk_right = load_frames(
            sprite_set,
            "R",
            (width, height)
        )

        self.walk_left = load_frames(
            sprite_set,
            "L",    
            (width, height)
        )

    @property
    def rect(self):
        hitbox_width = int(self.width * 0.55)
        hitbox_height = int(self.height * 0.85)

        return pygame.Rect(
            round(
                self.x
                + (self.width - hitbox_width) / 2
            ),
            round(
                self.y
                + self.height
                - hitbox_height
            ),
            hitbox_width,
            hitbox_height
        )

    def _standing_rect(self, center_x, feet_y):
        """Return the enemy hitbox at a possible standing position."""
        hitbox_width = int(self.width * 0.55)
        hitbox_height = int(self.height * 0.85)

        return pygame.Rect(
            round(center_x - hitbox_width / 2),
            round(feet_y - hitbox_height),
            hitbox_width,
            hitbox_height
        )

    def _can_stand(self, center_x, feet_y, solid_rects):
        """Check that the enemy fits at this position and has ground beneath it."""
        body = self._standing_rect(center_x, feet_y)

        if any(body.colliderect(tile) for tile in solid_rects):
            return False

        foot_probe = pygame.Rect(
            round(center_x - 2),
            round(feet_y),
            4,
            2
        )

        return any(
            foot_probe.colliderect(tile)
            for tile in solid_rects
        )

    def _jump_reaches(self, start, goal, solid_rects):
        """Check whether the enemy can jump from one platform node to another."""
        start_x, start_y = start
        goal_x, goal_y = goal

        horizontal_distance = goal_x - start_x

        if horizontal_distance == 0:
            direction = 0
        else:
            direction = 1 if horizontal_distance > 0 else -1

        center_x = float(start_x)
        feet_y = float(start_y)
        velocity_y = -self.jump_speed

        for _ in range(45):
            # Move horizontally.
            center_x += direction * self.move_speed
            body = self._standing_rect(center_x, feet_y)

            if any(
                body.colliderect(tile)
                for tile in solid_rects
            ):
                return False

            # Apply gravity and move vertically.
            velocity_y = min(
                velocity_y + self.gravity,
                16
            )
            feet_y += round(velocity_y)
            body = self._standing_rect(center_x, feet_y)

            for tile in solid_rects:
                if not body.colliderect(tile):
                    continue

                # The enemy landed. It only counts if this is the goal platform.
                if velocity_y > 0:
                    landed_on_goal = (
                        tile.top == goal_y
                        and tile.left <= center_x <= tile.right
                        and abs(center_x - goal_x) <= TILE_SIZE
                    )
                    return landed_on_goal

                # The enemy hit the underside or side of a platform.
                return False

            if feet_y > goal_y + TILE_SIZE * 2:
                return False

        return False

    def _build_navigation_graph(self, solid_rects):
        """
        Create a graph of platform positions.

        Walking links connect neighboring positions on the same platform.
        Jump links are added only when a jump simulation can reach the target.
        """
        # Tile geometry stays fixed during a level. Reuse the jump-tested
        # graph instead of rebuilding it every time A* runs.
        if (
            solid_rects is self._nav_source
            and self._nav_graph_cache is not None
        ):
            return self._nav_graph_cache

        nodes = set()

        for tile in solid_rects:
            center_x = tile.centerx
            feet_y = tile.top

            if self._can_stand(
                center_x,
                feet_y,
                solid_rects
            ):
                nodes.add((center_x, feet_y))

        graph = {
            node: []
            for node in nodes
        }

        max_jump_distance = (
            self.move_speed
            * (2 * self.jump_speed / self.gravity)
            + TILE_SIZE
        )

        max_jump_height = (
            self.jump_speed * self.jump_speed
            / (2 * self.gravity)
        )

        for node in nodes:
            x, y = node

            # Walking links to the tiles directly beside this position.
            for direction in (-1, 1):
                walk_node = (
                    x + direction * TILE_SIZE,
                    y
                )

                if walk_node in nodes:
                    graph[node].append(walk_node)

            # Test possible jump links.
            for target in nodes:
                if target == node:
                    continue

                target_x, target_y = target
                horizontal_distance = abs(target_x - x)
                vertical_change = target_y - y

                if horizontal_distance > max_jump_distance:
                    continue

                # A positive value means the target platform is higher.
                if vertical_change < -max_jump_height:
                    continue

                # Adjacent nodes on the same level already have walk links.
                if (
                    horizontal_distance <= TILE_SIZE
                    and vertical_change == 0
                ):
                    continue

                if self._jump_reaches(
                    node,
                    target,
                    solid_rects
                ):
                    graph[node].append(target)

        self._nav_source = solid_rects
        self._nav_graph_cache = graph
        return graph

    def _a_star(self, start, goal, graph):
        """Find a route through the platform graph using A*."""
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}

        max_tiles_per_jump = max(
            1,
            (
                self.move_speed
                * (2 * self.jump_speed / self.gravity)
            ) / TILE_SIZE
        )

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for neighbor in graph.get(current, []):
                new_cost = cost_so_far[current] + 1

                if new_cost >= cost_so_far.get(
                    neighbor,
                    float("inf")
                ):
                    continue

                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current

                distance = math.hypot(
                    neighbor[0] - goal[0],
                    neighbor[1] - goal[1]
                )

                heuristic = distance / (
                    TILE_SIZE * max_tiles_per_jump
                )

                heapq.heappush(
                    frontier,
                    (new_cost + heuristic, neighbor)
                )

        if goal not in came_from:
            return []

        route = []
        current = goal

        while current is not None:
            route.append(current)
            current = came_from[current]

        route.reverse()
        return route

    def _find_route(self, solid_rects, player):
        """Find an A* route from the enemy to the platform nearest the player."""
        graph = self._build_navigation_graph(solid_rects)

        if not graph:
            return []

        enemy_rect = self.rect
        player_rect = player.rect

        start = min(
            graph,
            key=lambda node: (
                abs(node[0] - enemy_rect.centerx)
                + abs(node[1] - enemy_rect.bottom) * 2
            )
        )

        goal = min(
            graph,
            key=lambda node: (
                abs(node[0] - player_rect.centerx)
                + abs(node[1] - player_rect.bottom) * 2
            )
        )

        route = self._a_star(start, goal, graph)

        # The first node is the enemy's current platform position.
        return route[1:]

    def update(
        self,
        solid_rects,
        player,
        level_width
    ):
        enemy_rect = self.rect
        player_rect = player.rect

        distance_x = (
            player_rect.centerx
            - enemy_rect.centerx
        )

        distance_y = (
            player_rect.centery
            - enemy_rect.centery
        )

        self.chasing = (
            abs(distance_x) <= self.detection_range
            and abs(distance_y) <= 260
        )

        dx = 0

        if self.chasing:
            self._path_timer -= 1

            # Recalculate periodically so the enemy can follow a moving player.
            if self._path_timer <= 0:
                self._route = self._find_route(
                    solid_rects,
                    player
                )
                self._path_timer = 12

            # Remove waypoints the enemy has reached.
            while self._route:
                target_x, target_y = self._route[0]

                reached_waypoint = (
                    abs(enemy_rect.centerx - target_x) <= 12
                    and abs(enemy_rect.bottom - target_y) <= 20
                    and self.on_ground
                )

                if reached_waypoint:
                    self._route.pop(0)
                else:
                    break

            if self._route:
                target_x, target_y = self._route[0]
                horizontal_distance = (
                    target_x - enemy_rect.centerx
                )

                if abs(horizontal_distance) > 8:
                    self.direction = (
                        1 if horizontal_distance > 0 else -1
                    )
                    dx = self.move_speed * self.direction

                should_jump = (
                    target_y < enemy_rect.bottom - 8
                    or abs(horizontal_distance) > TILE_SIZE * 1.5
                )

                if self.on_ground and should_jump:
                    self.velocity_y = -self.jump_speed
                    self.on_ground = False

            else:
                # Fallback chase if no platform route can be found.
                if distance_x > 8:
                    self.direction = 1
                    dx = self.move_speed
                elif distance_x < -8:
                    self.direction = -1
                    dx = -self.move_speed

                if self.on_ground and (
                    distance_y < -45
                    or abs(distance_x) > TILE_SIZE * 1.5
                ):
                    self.velocity_y = -self.jump_speed
                    self.on_ground = False

        else:
            # Patrol between the configured endpoints.
            if self.x <= self.path[0]:
                self.direction = 1
            elif self.x >= self.path[1]:
                self.direction = -1

            dx = self.move_speed * self.direction

            # Turn around during patrol if a wall or gap is ahead.
            if dx != 0 and self.on_ground:
                wall_test = self.rect.move(dx, 0)

                wall_ahead = any(
                    wall_test.colliderect(tile)
                    for tile in solid_rects
                )

                if self.direction > 0:
                    probe_x = wall_test.right + 2
                else:
                    probe_x = wall_test.left - 6

                ground_probe = pygame.Rect(
                    probe_x,
                    wall_test.bottom + 1,
                    4,
                    14
                )

                ground_ahead = any(
                    ground_probe.colliderect(tile)
                    for tile in solid_rects
                )

                if wall_ahead or not ground_ahead:
                    self.direction *= -1
                    dx = self.move_speed * self.direction
                    self.walk_count = 0

        self.speed = self.move_speed * self.direction

        # Horizontal movement and collision.
        rect = self.rect
        rect.x += round(dx)

        for tile in solid_rects:
            if rect.colliderect(tile):
                if dx > 0:
                    rect.right = tile.left
                elif dx < 0:
                    rect.left = tile.right
                break

        if rect.left < 0:
            rect.left = 0

        if rect.right > level_width:
            rect.right = level_width

        self.x = rect.centerx - self.width / 2

        # Gravity and vertical collision.
        self.velocity_y = min(
            self.velocity_y + self.gravity,
            16
        )

        rect = self.rect
        rect.y += round(self.velocity_y)
        self.on_ground = False

        for tile in solid_rects:
            if rect.colliderect(tile):
                if self.velocity_y > 0:
                    rect.bottom = tile.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    rect.top = tile.bottom
                    self.velocity_y = 0

        self.y = rect.bottom - self.height

    def draw(
        self,
        window,
        camera_x=0
    ):
        frames_per_image = 3

        if self.direction > 0:
            frames = self.walk_right
        else:
            frames = self.walk_left

        animation_length = (
            len(frames)
            * frames_per_image
        )

        self.walk_count %= animation_length
        frame = self.walk_count // frames_per_image
        image = frames[frame]

        draw_x = round(self.x - camera_x)
        draw_y = round(self.y)

        window.blit(
            image,
            (draw_x, draw_y)
        )

        self.walk_count += 1

        sprite_rect = image.get_rect(
            topleft=(draw_x, draw_y)
        )

        bar_width = max(
            40,
            int(sprite_rect.width * 0.8)
        )

        bar_x = sprite_rect.centerx - bar_width // 2
        bar_y = sprite_rect.top - 15

        health_width = int(
            bar_width * self.health / self.max_health
        )

        pygame.draw.rect(
            window,
            (255, 0, 0),
            (bar_x, bar_y, bar_width, 10)
        )

        pygame.draw.rect(
            window,
            (0, 128, 0),
            (bar_x, bar_y, health_width, 10)
        )
