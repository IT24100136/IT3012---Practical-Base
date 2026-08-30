# agent.py
import random
import math
import heapq
from collections import deque
from logic_engine import KnowledgeBase

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
    """Problem-Solving Agent for Practical 3 that uses Breadth-First Search (BFS), DFS, UCS, and A* Search.
    
    Part 3: Practical 04 - Integrates Knowledge Base and Forward Chaining Inference
    to validate tile feasibility before moving.
    """
    
    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'
        
        # Part 3.1: Instantiate Knowledge Base
        self.kb = KnowledgeBase()
        
        # Define safety rules (Horn Clauses)
        # Rule 1: TargetVisible ∧ HasDust ⇒ SafeToEngage
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        
        # Rule 2: SafeToEngage ∧ BloodseekerMissing ⇒ Retreat
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

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
                elif getattr(self, 'active_algo', 'BFS') == 'AStar' and hasattr(self, 'astar_search'):
                    path = self.astar_search(start_pos, goal_pos, walls, grid_size)
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

    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance between pos and goal.
        Formula: h(n) = |x_1 - x_2| + |y_1 - y_2|
        """
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance between pos and goal.
        Formula: h(n) = sqrt((x_1 - x_2)^2 + (y_1 - y_2)^2)
        """
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
    
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        """A* Search algorithm combining g(n) path cost and h(n) heuristic cost.
        f(n) = g(n) + h(n)
        """
        width, height = grid_size
        walls_set = set(walls)
        
        # Priority queue: (f_cost, g_cost, current_pos, path_taken)
        # Using f_cost and g_cost as tiebreakers for consistent ordering
        priority_queue = []
        heapq.heappush(priority_queue, (0, 0, start_pos, []))
        
        reached_states = set()
        
        while priority_queue:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(priority_queue)
            
            # If we reached the goal, return the path
            if current_pos == goal_pos:
                return path_taken
            
            # Skip if already reached this state
            if current_pos in reached_states:
                continue
                
            reached_states.add(current_pos)
            
            # Expand neighbors (Up, Down, Left, Right)
            moves = [
                ('Up', (current_pos[0], current_pos[1] + 1)),
                ('Down', (current_pos[0], current_pos[1] - 1)),
                ('Left', (current_pos[0] - 1, current_pos[1])),
                ('Right', (current_pos[0] + 1, current_pos[1]))
            ]
            
            for action, (next_x, next_y) in moves:
                # Check boundaries
                if 0 <= next_x < width and 0 <= next_y < height:
                    # Check for walls and already visited states
                    if (next_x, next_y) not in walls_set and (next_x, next_y) not in reached_states:
                        
                        # Part 3.2: Feasibility Check using Knowledge Base
                        # =====================================================
                        # Before expanding this neighbor, validate it is feasible
                        next_pos = (next_x, next_y)
                        
                        # 1. Clear KB facts for fresh inference on this tile
                        self.kb.clear_facts()
                        
                        # 2. Feed current percepts for this specific tile into the KB
                        # Simulate tile-specific percepts:
                        # - Assume TargetVisible if this is a goal position
                        if next_pos == goal_pos:
                            self.kb.tell_fact('TargetVisible')
                            self.kb.tell_fact('HasDust')
                        
                        # - Assume BloodseekerMissing if near obstacles (example logic)
                        # For demonstration: if neighbor to a wall, consider Bloodseeker missing
                        if any((next_x + dx, next_y + dy) in walls_set 
                               for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                            self.kb.tell_fact('BloodseekerMissing')
                        
                        # 3. Run forward chaining inference
                        self.kb.forward_chain()
                        
                        # 4. Check feasibility: If 'Retreat' was deduced, tile is infeasible
                        if 'Retreat' in self.kb.facts:
                            # Infeasible tile - skip it even if physically reachable
                            continue
                        
                        # =====================================================
                        # Feasible tile - proceed with normal A* expansion
                        
                        # Calculate costs
                        g_new = g_cost + 1  # Cost of moving one step
                        
                        # Select heuristic
                        if heuristic_type == 'euclidean':
                            h_new = self.euclidean_distance(next_pos, goal_pos)
                        else:  # default to manhattan
                            h_new = self.manhattan_distance(next_pos, goal_pos)
                        
                        f_new = g_new + h_new
                        
                        # Add to priority queue
                        heapq.heappush(priority_queue, (f_new, g_new, next_pos, path_taken + [action]))
        
        # Return empty list if goal is unreachable
        return []

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