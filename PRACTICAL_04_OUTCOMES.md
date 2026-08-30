# IT3012 Practical 04 - A* Search Implementation
## Outcomes & Theoretical Evaluation

---

## Part 1: Implementation Outcomes

### Step 1.1: Heuristic Functions ✓

**Manhattan Distance Implementation:**
```python
def manhattan_distance(self, pos, goal):
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
```
- Test with (0,0) → (3,4): **7** ✓
- Formula: h(n) = |x₁ - x₂| + |y₁ - y₂|

**Euclidean Distance Implementation:**
```python
def euclidean_distance(self, pos, goal):
    return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
```
- Test with (0,0) → (3,4): **5.0** ✓
- Formula: h(n) = √[(x₁ - x₂)² + (y₁ - y₂)²]

### Step 1.2: A* Search Algorithm ✓

**Implementation Details:**
- Uses `heapq` for priority queue management
- Tuple format: (f_cost, g_cost, current_pos, path_taken)
- f(n) = g(n) + h(n) where:
  - g(n) = actual cost from start to current node
  - h(n) = heuristic estimate from current to goal
- Supports both Manhattan and Euclidean heuristics
- Expands nodes in 4-way movement (Up, Down, Left, Right)
- Properly handles walls, grid boundaries, and visited states

**Test Results:**
- Path from (0,0) to (5,5) with Manhattan: 10 steps ✓
- Path from (0,0) to (5,5) with Euclidean: 10 steps ✓
- Blocked goal handling: Correctly finds alternative routes ✓

### Step 1.3: Integration into SearchAgent ✓

**Changes Made:**
1. Added `elif self.active_algo == 'AStar'` block in `sense_and_act()` method
2. Extracts percept data (walls, grid_size, remaining_food)
3. Finds closest food item as goal
4. Calls `astar_search()` and stores result in `self.plan`

**GUI Integration:**
- Added "Run Search Agent (A*)" button to visual_grid_game.py
- Button color: Cyan (#0891b2)
- Properly enables/disables alongside other algorithm buttons
- Runs in the same game loop as BFS, DFS, and UCS

---

## Part 2: Theoretical Evaluation

### Question 1: (Understand) Key Difference between UCS and A* Search

**Answer:**
Uniform-Cost Search (UCS) and A* Search differ in how they prioritize node exploration:

- **UCS (Uniform-Cost Search):** Uses only g(n) - the actual path cost from start to current node. It explores nodes in order of lowest cumulative cost, regardless of distance to goal.

- **A* Search:** Uses f(n) = g(n) + h(n) - combining actual path cost with a heuristic estimate. It explores nodes that are estimated to be most promising (lowest total estimated cost).

**Key Difference:** UCS is "blind" to goal location and explores uniformly in all directions, while A* uses domain knowledge (heuristic) to guide search toward the goal, making it more efficient. A* will typically explore fewer nodes than UCS to find the optimal path.

---

### Question 2: (Analyze) Admissibility of Manhattan Distance for 4-Way Movement

**Answer:**
Manhattan Distance IS an admissible heuristic for 4-way movement grids because:

1. **Definition of Admissible:** A heuristic is admissible if h(n) ≤ h*(n) for all nodes, where h*(n) is the true cost to the goal.

2. **Why Manhattan is Admissible for 4-way:**
   - Manhattan distance counts steps along grid axes (Up/Down/Left/Right)
   - The actual minimum path cost can never be less than Manhattan distance
   - In 4-way movement, you cannot move diagonally, so the Manhattan path IS the optimal path
   - Therefore: h(n) ≤ h*(n) always holds

3. **What Happens with Non-Admissible Heuristics:**
   - If h(n) > h*(n) for some nodes, the heuristic can overestimate
   - This causes A* to prune promising branches
   - The algorithm may still find a path, but it's no longer guaranteed to find the OPTIMAL path
   - A* becomes just a greedy algorithm without optimality guarantee

---

### Question 3: (Evaluate) Manhattan Distance with 8-Way Movement (Diagonal)

**Answer:**
NO, Manhattan Distance would NO LONGER be an admissible heuristic for 8-way movement.

**Why:**
- With 8-way movement, the agent can move diagonally
- Diagonal movement allows reaching a goal in fewer steps than Manhattan suggests
- Example: From (0,0) to (3,3):
  - Manhattan distance: 6 steps (|0-3| + |0-3| = 6)
  - Actual minimum with diagonal: 3 steps (diagonal to (3,3))
  - Since h(n)=6 > h*(n)=3, the heuristic is NOT admissible

**Recommended Metric for 8-Way Movement:**
- **Chebyshev Distance** (also called Chessboard Distance or L∞ metric):
  - Formula: h(n) = max(|x₁ - x₂|, |y₁ - y₂|)
  - Represents the minimum steps needed with diagonal movement
  - IS admissible for 8-way grids because one diagonal step covers max(|Δx|, |Δy|) distance
  - Example: (0,0) to (3,3): max(3,3) = 3 ✓

---

### Question 4: (Create) Stronger Heuristic for Multiple Food Items

**Answer - Minimum Spanning Tree Approximation (MST-based Heuristic):**

For efficiently targeting ALL remaining food items, propose using the **MST (Minimum Spanning Tree) or Closest Pair-based relaxation heuristic**:

**Proposed Heuristic:**
1. **Calculate minimum distance to closest food:** This is the current approach (weak)

2. **Better approach - Approximate TSP heuristic:**
   - Find the distance to the closest food item (nearest neighbor)
   - Add an approximation of the total remaining tour:
     - Sum the Manhattan distances of a greedy path visiting all food items in order
     - Or use MST of remaining food items as lower bound
   
3. **Even Stronger - Multi-food consideration:**
   - Calculate: h(n) = dist_to_nearest_food + (sum of distances between other food pairs) / 2
   - This estimates both reaching the nearest food AND the cost to visit remaining food

**Why This is Stronger:**
- The weak heuristic (distance to closest food only) ignores the total remaining problem
- The MST-based approach provides a better lower bound on total remaining path cost
- It's still admissible (won't overestimate true cost)
- Still computable in reasonable time (O(n²) for n food items)
- Guides A* more effectively toward solutions that cluster nearby food items

**Trade-off:**
- Slightly more computational cost per node expansion
- Significantly better guidance reduces total nodes explored
- Net benefit: Fewer nodes expanded overall → faster pathfinding

---

## Implementation Verification Summary

| Component | Status | Test Result |
|-----------|--------|-------------|
| Manhattan Distance | ✓ | (0,0)→(3,4) = 7 |
| Euclidean Distance | ✓ | (0,0)→(3,4) = 5.0 |
| A* Search Algorithm | ✓ | Optimal paths found |
| Manhattan A* | ✓ | Produces optimal paths |
| Euclidean A* | ✓ | Produces optimal paths |
| SearchAgent Integration | ✓ | Algorithm selection working |
| GUI Button (A*) | ✓ | Button added and functional |
| 4-Way Movement Support | ✓ | All directions work |
| Wall Collision Handling | ✓ | Properly avoids walls |
| Boundary Checking | ✓ | Stays within grid |

---

## Files Modified

1. **agent.py**
   - Added imports: `math`, `heapq`
   - Added `manhattan_distance()` method
   - Added `euclidean_distance()` method
   - Added `astar_search()` method with full A* implementation
   - Updated `sense_and_act()` to support 'AStar' algorithm

2. **visual_grid_game.py**
   - Added A* button to GUI (cyan color)
   - Updated `run_loop()` to manage A* button state
   - Button integrates with existing algorithm selection framework

---

## How to Run

1. **Launch the GUI:**
   ```bash
   python visual_grid_game.py
   ```

2. **Test A* Search:**
   - Click "Run Search Agent (A*)" button
   - Watch the agent navigate using A* algorithm
   - Observe optimized pathfinding with Manhattan heuristic

3. **Compare with Other Algorithms:**
   - Run BFS, DFS, UCS, and A* on same environment
   - A* should typically complete in fewer steps than uninformed searches

---

**Implementation Complete:** All Practical 04 requirements have been successfully implemented and tested.
