import random
from collections import deque
import heapq
import math


class SearchAgent:
    """Goal-Based Planning Agent: Uses BFS, DFS, or UCS to find paths to food."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def bfs_search(self, start, goal, grid_size, walls):
        """Breadth-First Search: explores shallowest nodes first using FIFO queue."""
        width, height = grid_size
        queue = deque([(start, [start])])
        reached = {start}

        while queue:
            current, path = queue.popleft()

            if current == goal:
                return self._path_to_actions(path)

            # Expand neighbors (Up, Down, Left, Right)
            for action, (dx, dy) in [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]:
                neighbor = (current[0] + dx, current[1] + dy)

                # Check if valid position
                if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and
                    neighbor not in walls and neighbor not in reached):
                    reached.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []  # No path found

    def dfs_search(self, start, goal, grid_size, walls):
        """Depth-First Search: explores deepest nodes first using LIFO stack."""
        width, height = grid_size
        stack = [(start, [start])]
        reached = {start}

        while stack:
            current, path = stack.pop()

            if current == goal:
                return self._path_to_actions(path)

            # Expand neighbors (Up, Down, Left, Right)
            for action, (dx, dy) in [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]:
                neighbor = (current[0] + dx, current[1] + dy)

                # Check if valid position
                if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and
                    neighbor not in walls and neighbor not in reached):
                    reached.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))

        return []  # No path found

    def ucs_search(self, start, goal, grid_size, walls):
        """Uniform-Cost Search: explores by total path cost using priority queue."""
        width, height = grid_size
        # Priority queue: (cost, current_pos, path)
        heap = [(0, start, [start])]
        reached = {start: 0}

        while heap:
            cost, current, path = heapq.heappop(heap)

            if current == goal:
                return self._path_to_actions(path)

            # Only process if this is the best path to current node
            if reached.get(current, float('inf')) < cost:
                continue

            # Expand neighbors (Up, Down, Left, Right)
            for action, (dx, dy) in [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]:
                neighbor = (current[0] + dx, current[1] + dy)

                # Check if valid position
                if 0 <= neighbor[0] < width and 0 <= neighbor[1] < height and neighbor not in walls:
                    new_cost = cost + 1
                    if neighbor not in reached or reached[neighbor] > new_cost:
                        reached[neighbor] = new_cost
                        heapq.heappush(heap, (new_cost, neighbor, path + [neighbor]))

        return []  # No path found

    def _path_to_actions(self, path):
        """Convert a path of coordinates to a list of directional actions."""
        actions = []
        for i in range(1, len(path)):
            prev = path[i - 1]
            curr = path[i]
            dx = curr[0] - prev[0]
            dy = curr[1] - prev[1]

            if dy > 0:
                actions.append('Up')
            elif dy < 0:
                actions.append('Down')
            elif dx < 0:
                actions.append('Left')
            elif dx > 0:
                actions.append('Right')

        return actions

    def _find_closest_food(self, agent_pos, food_positions):
        """Find the closest food pellet using Manhattan distance."""
        if not food_positions:
            return None

        closest_food = min(food_positions, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))
        return closest_food

    def sense_and_act(self, percept: dict) -> str:
        """Sense percept and execute planned actions or generate new plan."""
        if not self.plan:
            # Plan is empty, generate a new one
            agent_pos = tuple(percept.get('agent_pos', [0, 0]))
            grid_size = percept.get('grid_size', (10, 10))
            walls = set(percept.get('walls', []))
            all_food = list(percept.get('all_food', []))

            if all_food:
                goal = self._find_closest_food(agent_pos, all_food)

                if goal:
                    # Execute the active search algorithm
                    if self.active_algo == 'BFS':
                        self.plan = self.bfs_search(agent_pos, goal, grid_size, walls)
                    elif self.active_algo == 'DFS':
                        self.plan = self.dfs_search(agent_pos, goal, grid_size, walls)
                    elif self.active_algo == 'UCS':
                        self.plan = self.ucs_search(agent_pos, goal, grid_size, walls)

        # Execute the next action from the plan
        if self.plan:
            return self.plan.pop(0)
        else:
            # No plan available, default to forward movement
            return 'move_forward'


class SimpleReflexAgent:
    """Simple reflex agent: reacts only to the current percept."""

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'suck'
        if percept.get('wall_ahead'):
            return 'Left'
        return 'move_forward'


class ModelBasedAgent:
    """Model-based agent: stores a small internal memory to avoid repeating the same response."""

    def __init__(self):
        self.visited_states = set()
        self.last_action = None
        self._turn_preference = 'Left'

    def sense_and_act(self, percept: dict) -> str:
        state = (bool(percept.get('wall_ahead')), bool(percept.get('food_here')))
        repeated_state = state in self.visited_states
        self.visited_states.add(state)

        if percept.get('food_here'):
            action = 'suck'
        elif percept.get('wall_ahead'):
            action = 'Right' if repeated_state or self._turn_preference == 'Right' else 'Left'
            self._turn_preference = 'Right' if self._turn_preference == 'Left' else 'Left'
        else:
            action = 'move_forward'

        self.last_action = action
        return action


