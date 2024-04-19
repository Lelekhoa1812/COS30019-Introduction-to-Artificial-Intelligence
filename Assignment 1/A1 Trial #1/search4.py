import sys
import re
import heapq

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0] * cols for _ in range(rows)]  # Initialize grid with all cells as 0 (empty)

    def add_wall(self, x, y, w, h):
        for i in range(x, min(x + w, self.rows)):
            for j in range(y, min(y + h, self.cols)):
                self.grid[i][j] = 1  # Mark cells occupied by wall as 1

    def is_valid(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols and self.grid[x][y] != 1

class Node:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent

    def __lt__(self, other):
        # Define comparison logic here
        # For example, you could compare based on some attribute such as distance from the start
        # Here's an example comparing based on the sum of x and y coordinates
        return self.x + self.y < other.x + other.y

    def __eq__(self, other):
        # Define equality comparison logic here
        return self.x == other.x and self.y == other.y

def reconstruct_path(node):
    path = []
    while node:
        path.append(node)
        node = node.parent
    return path[::-1]

def depth_first_search(grid, start, goals, max_depth=None):
    visited = set()

    def dfs_helper(current, depth):
        if depth == max_depth:
            return []
        if (current.x, current.y) in goals:
            goals.remove((current.x, current.y))
            if not goals:
                return [current]
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                path = dfs_helper(Node(next_x, next_y, current), depth + 1)
                if path:
                    return [current] + path
        return []

    return reconstruct_path(dfs_helper(Node(start[0], start[1]), 0))

def breadth_first_search(grid, start, goals, max_iterations=None):
    queue = [(Node(start[0], start[1]), 0)]  # Include depth in the queue
    visited = set()

    while queue:
        current, depth = queue.pop(0)
        if (current.x, current.y) in goals:
            goals.remove((current.x, current.y))
            if not goals:
                return reconstruct_path(current)
        if max_iterations is not None and depth >= max_iterations:
            continue
        visited.add((current.x, current.y))
        # Explore all possible directions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                queue.append((Node(next_x, next_y, current), depth + 1))
    return []

def greedy_best_first_search(grid, start, goals, heuristic):
    priority_queue = [(heuristic(start, list(goals)[0]), Node(start[0], start[1]))] # List goal target
    heapq.heapify(priority_queue)
    visited = set()
    # Expands nodes in the order of the heuristic values
    while priority_queue:
        _, current = heapq.heappop(priority_queue)
        if (current.x, current.y) in goals:
            goals.remove((current.x, current.y))
            if not goals:
                return reconstruct_path(current)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                heapq.heappush(priority_queue, (heuristic((next_x, next_y), list(goals)[0]), Node(next_x, next_y, current)))
                visited.add((next_x, next_y))
    return []

def a_star_search(grid, start, goals, heuristic):
    goals = list(goals)  # List goal target
    priority_queue = [(0, heuristic(start, goals[0]), Node(start[0], start[1]))]
    heapq.heapify(priority_queue)
    visited = set()
    # Evaluates nodes based on both cost to reach the node and the heuristic estimate of the cost 
    while priority_queue:
        _, _, current = heapq.heappop(priority_queue)
        if (current.x, current.y) in goals:
            goals.remove((current.x, current.y))
            if not goals:
                return reconstruct_path(current)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                for goal in goals:
                    heapq.heappush(priority_queue, (heuristic(start, goal) + heuristic((next_x, next_y), goal), heuristic((next_x, next_y), goal), Node(next_x, next_y, current)))
                visited.add((next_x, next_y))
    return []

# Custom heuristic function (Manhattan Distance)
def heuristic(current, goal):
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

def get_direction(current, next):
    if current.y < next.y:
        return 'down'
    elif current.y > next.y:
        return 'up'
    elif current.x < next.x:
        return 'right'
    elif current.x > next.x:
        return 'left'
    else:
        return 'stay' 
    
def extract_goals(lines):
    # Extract goal coordinates variable from the map
    set_goal_coords = re.findall(r'\((\d+),\s*(\d+)\)', lines[2])
    gc = {(int(x_str), int(y_str)) for x_str, y_str in set_goal_coords}
    return gc

# Trial attempt notice
def count_goals(lines):
    # Set the number of goal targets from the map
    num_goals = lines[2].count('|') + 1
    return num_goals

if __name__ == "__main__":
    filename = sys.argv[1]
    method = sys.argv[2]

    # Read grid configuration from file
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        # Read map's dimensions
        dimension_match = re.match(r'\[(\d+),\s*(\d+)\]', lines[0])
        cols, rows = map(int, (dimension_match.group(1), dimension_match.group(2)))
        # Match's start coordinates
        start_match = re.match(r'\((\d+),\s*(\d+)\)', lines[1])  
        start = (int(start_match.group(1)), int(start_match.group(2)))
        
        # Extract goal coordinates
        goal_coords = re.findall(r'\((\d+),\s*(\d+)\)', lines[2])
        goals = {(int(x_str), int(y_str)) for x_str, y_str in goal_coords}

        # Fixed goal nodes' coordinates
        gc = extract_goals(lines)

        # Initialize the wall
        walls = []
        for wall in lines[3:]:
            wall_coords = re.findall(r'\d+', wall)
            if len(wall_coords) == 4:  # Ensure correct number of the wall's coordinates
                walls.append(tuple(map(int, wall_coords)))

        # Initialize the grid
        grid = Grid(rows, cols)
        for wall in walls:
            grid.add_wall(*wall)

        # Perform search by relevant method
        if method == "DFS":
            path = depth_first_search(grid, start, goals)
        elif method == "BFS":
            path = breadth_first_search(grid, start, goals)
        elif method == "GBFS":
            path = greedy_best_first_search(grid, start, goals, heuristic)
        elif method == "AS":
            path = a_star_search(grid, start, goals, heuristic)
        else: # Not a valid method
            print("Invalid search method. Please choose one of: DFS, BFS, GBFS, AS")
            sys.exit(1)

        # Print result (including the pathway)
        if path:
            for goal in path:
                if (goal.x, goal.y) in gc:
                    print(f"{filename} {method}")
                    print(f"< Node ({goal.x}, {goal.y})> {len(path)}")
                    print([get_direction(path[i], path[i+1]) for i in range(len(path)-1)])
        else:
            print(f"{filename} {method}")
            print("No goal is reachable")