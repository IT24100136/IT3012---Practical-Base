# agent.py
import random
from collections import deque

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """A purely reactive agent using Condition-Action rules without memory."""
    
    def sense_and_act(self, percept: dict) -> str:
        # Condition-Action Rules responding only to immediate percepts
        if percept.get('food_here'):
            return 'Stay' # Consume food
            
        if percept.get('wall_ahead'):
            # Reflexively turn when a wall is encountered
            return 'Left' 
            
        # Default action
        return 'Up'


class ModelBasedAgent:
    """An agent that maintains internal state to handle partial observability and escape loops."""
    
    def __init__(self):
        # Internal memory state to track if we are stuck in a loop
        self.last_percept_wall = False
        self.escape_actions = ['Left', 'Right', 'Down', 'Up']
        self.stuck_attempts = 0

    def sense_and_act(self, percept: dict) -> str:
        # 1. Update State & 2. Condition-Action rules using Memory
        if percept.get('food_here'):
            return 'Stay'
            
        if percept.get('wall_ahead'):
            # If we were already facing a wall last turn, we are stuck in a loop
            if self.last_percept_wall:
                self.stuck_attempts += 1
            else:
                self.stuck_attempts = 0
                
            self.last_percept_wall = True
            
            # Use internal memory (stuck_attempts) to pick a different action and escape
            return self.escape_actions[self.stuck_attempts % len(self.escape_actions)]
            
        # Reset memory state if path is clear
        self.last_percept_wall = False
        return 'Up'


class SearchAgent:
    """Problem-Solving Agent for Practical 3 that uses Breadth-First Search (BFS)."""
    
    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'suck'
            
        if not self.plan:
            start_pos = percept['agent_pos']
            walls = percept['walls']
            grid_size = percept['grid_size']
            all_food = percept['all_food']
            
            if not all_food:
                return 'Stay'
                
            best_path = None
            
            for goal_pos in all_food:
                if getattr(self, 'active_algo', 'BFS') == 'DFS' and hasattr(self, 'dfs_search'):
                    path = self.dfs_search(start_pos, goal_pos, walls, grid_size)
                elif getattr(self, 'active_algo', 'BFS') == 'UCS' and hasattr(self, 'ucs_search'):
                    path = self.ucs_search(start_pos, goal_pos, walls, grid_size)
                else:
                    path = self.bfs_search(start_pos, goal_pos, walls, grid_size)
                    
                if path:
                    if best_path is None or len(path) < len(best_path):
                        best_path = path
                        
            if best_path:
                self.plan = best_path.copy()
            else:
                return 'Stay'
                
        return self.plan.pop(0)

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        width, height = grid_size
        walls_set = set(walls)
        
        # A queue to store tuples of (current_position, path_taken)
        queue = deque([(start_pos, [])])
        visited = set([start_pos])
        
        while queue:
            (curr_x, curr_y), path = queue.popleft()
            
            # If we reached the goal, return the path of actions we took to get here
            if (curr_x, curr_y) == goal_pos:
                return path
            
            # Define possible movements and their coordinate changes
            moves = [
                ('Up', (curr_x, curr_y + 1)),
                ('Down', (curr_x, curr_y - 1)),
                ('Left', (curr_x - 1, curr_y)),
                ('Right', (curr_x + 1, curr_y))
            ]
            
            for action, (next_x, next_y) in moves:
                # Check if the next move is inside the grid boundaries
                if 0 <= next_x < width and 0 <= next_y < height:
                    # Check if the next move avoids walls and hasn't been visited yet
                    if (next_x, next_y) not in walls_set and (next_x, next_y) not in visited:
                        visited.add((next_x, next_y))
                        queue.append(((next_x, next_y), path + [action]))
                        
        # Return an empty list if the goal is completely blocked off
        return []