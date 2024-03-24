import sys
import re
import heapq
from collections import deque

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0] * cols for _ in range(rows)]  # Initialize map with all cells as 0 (empty)

    def add_wall(self, x, y, w, h):
        for i in range(x, min(x + w, self.rows)):
            for j in range(y, min(y + h, self.cols)):
                self.grid[i][j] = 1  # Add wall cell as 1 (occupied)

    def is_valid(self, x, y): # Valid moves at empty cell and within the map's boundary
        return 0 <= x < self.rows and 0 <= y < self.cols and self.grid[x][y] != 1

class Node:
    def __init__(self, x, y, parent=None, path_cost=0):
        self.x = x
        self.y = y
        self.parent = parent
        self.path_cost = path_cost
        self.depth = 0

    # If sum of x and y should be prioritized
    def __lt__(self, other):
        return self.x + self.y < other.x + other.y

    # If value of x and y should be prioritized
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.x == other.x and self.y == other.y
        return False
    
def reconstruct_path(node):
    path = []
    while node:
        path.append(node)
        node = node.parent
    return path[::-1]

# Uninformed approaches
def depth_first_search(grid, start, goal):
    stack = [(Node(start[0], start[1]), [])]  # Stack (path history)
    visited = set()
    total_nodes = 0

    # Evaluates nodes based on depth of the path and explores deeper levels before branching out.
    while stack:
        current, path = stack.pop()
        total_nodes += 1
        if (current.x, current.y) == goal:
            return path + [current], total_nodes  # Return current path (with goal node) 
        visited.add((current.x, current.y))
        unvisited_neighbors = []
        for dx, dy in [(0, 1), (-1, 0), (0, -1), (1, 0)]:  # Up, Left, Down, Right
            next_x, next_y = current.x + dx, current.y + dy
            if grid.is_valid(next_x, next_y) and (next_x, next_y) not in visited:
                child_node = Node(next_x, next_y, current, current.path_cost + 1)
                unvisited_neighbors.append((child_node, path + [current]))  # Append the current node to the path
        stack.extend(unvisited_neighbors[::-1])  # Add unvisited neighbors in reverse order 
    return None, total_nodes

def breadth_first_search(grid, start, goal, max_iterations=None):
    queue = deque([[Node(start[0], start[1])]])  # Queue of paths
    visited = set()
    total_nodes = 0

    # Evaluates nodes based on breadth of the search tree, exploring all neighbors before moving to the next level.
    while queue:
        path = queue.popleft()
        total_nodes += 1
        current = path[-1]  # Last node in the path
        if (current.x, current.y) == goal:
            return path, total_nodes  # Return path (with goal node)
        if max_iterations is not None and len(path) >= max_iterations:
            continue
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (-1, 0), (0, -1), (1, 0)]:  # Up, Left, Down, Right
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                child_node = Node(next_x, next_y)
                queue.append(path + [child_node])  # Append the new node to the path
                visited.add((next_x, next_y))
    return None, total_nodes

# 1st Custom method: Inspired by the depth_limited method, integrating the combination of DFS and BFS approaches.
# References of the depth_limited method can be found at: https://ai-master.gitbooks.io/classic-search/content/what-is-depth-limited-search.html
def custom_search_1(grid, start, goal):
    depth_limit = 0

    while True:
        result, total_nodes = depth_limited_search(grid, start, goal, depth_limit)
        if result:
            return result, total_nodes
        depth_limit += 1

# The method combine the features of DFS and BFS altogether
def depth_limited_search(grid, start, goal, depth_limit):
    stack = [(Node(start[0], start[1]), [])]  # Stack (path history)
    visited = set()
    total_nodes = 0

    while stack:
        current, path = stack.pop()
        total_nodes += 1
        if (current.x, current.y) == goal:
            return path + [current], total_nodes  # Return the current path (with goal node) 
        # Evaluates nodes based on depth limit
        if current.depth < depth_limit:
            visited.add((current.x, current.y))
            unvisited_neighbors = []
            for dx, dy in [(0, 1), (-1, 0), (0, -1), (1, 0)]:  # Up, Left, Down, Right
                next_x, next_y = current.x + dx, current.y + dy
                if grid.is_valid(next_x, next_y) and (next_x, next_y) not in visited:
                    child_node = Node(next_x, next_y, current, current.path_cost + 1)
                    unvisited_neighbors.append((child_node, path + [current]))  # Append the current node to the path
            stack.extend(unvisited_neighbors[::-1])  # Add unvisited neighbors in reverse order 
    return None, total_nodes

# Informed approaches
def greedy_best_first_search(grid, start, goal, heuristic):
    priority_queue = [(heuristic(start, goal), Node(start[0], start[1]))]
    heapq.heapify(priority_queue)
    visited = set()
    total_nodes = 0

    # Expands nodes in the order of the heuristic values
    while priority_queue:
        _, current = heapq.heappop(priority_queue)
        total_nodes += 1
        if (current.x, current.y) == goal:
            return reconstruct_path(current), total_nodes # Reconstruct path (with goal nodes)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (-1, 0), (0, -1), (1, 0)]:  # Up, Left, Down, Right
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                # Push the node to the priority queue with the heuristic value (h(n)) and the node information
                heapq.heappush(priority_queue, (heuristic((next_x, next_y), goal), Node(next_x, next_y, current)))
                visited.add((next_x, next_y))
    return [], total_nodes

def a_star_search(grid, start, goal, heuristic):
    priority_queue = [(0, heuristic(start, goal), Node(start[0], start[1]))]
    heapq.heapify(priority_queue)
    visited = set()
    total_nodes = 0

    # Evaluates nodes based on both cost to reach the node and the heuristic estimate of the cost 
    while priority_queue:
        _, _, current = heapq.heappop(priority_queue)
        total_nodes += 1
        if (current.x, current.y) == goal:
            return reconstruct_path(current), total_nodes # Reconstruct path (with goal nodes)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (-1, 0), (0, -1), (1, 0)]:  # Up, Left, Down, Right
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                # Push the node to the priority queue with the total estimated cost (f(n) = g(n) + h(n))
                heapq.heappush(priority_queue, (heuristic(start, goal) + heuristic((next_x, next_y), goal), heuristic((next_x, next_y), goal), Node(next_x, next_y, current)))
                visited.add((next_x, next_y))
    return [], total_nodes

# 2nd Custom method: a combination of  Greedy Best First Search and A* search methods
def custom_search_2(grid, start, goal, heuristic):
    priority_queue = [(0, 0, Node(start[0], start[1]))]  # (total_cost, path_cost, node)
    heapq.heapify(priority_queue)
    visited = set()
    total_nodes = 0

    while priority_queue:
        _, _, current = heapq.heappop(priority_queue)
        total_nodes += 1
        if (current.x, current.y) == goal:
            return reconstruct_path(current), total_nodes  # Reconstruct path (with goal nodes)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (-1, 0), (0, -1), (1, 0)]:  # Up, Left, Down, Right
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                # Calculate total cost based on the sum of the path cost and heuristic value (f(n) = g(n) + h(n))
                total_cost = current.path_cost + heuristic((next_x, next_y), goal)
                 # Push the node to the priority queue with total cost, path cost, and node information 
                heapq.heappush(priority_queue, (total_cost, current.path_cost + 1, Node(next_x, next_y, current)))
                visited.add((next_x, next_y))            
    return [], total_nodes # Return an empty path and the total number of nodes explored if no path is found

# Heuristic functions (Manhattan and Euclidean distance)
# Change htype value to 2 to set  Euclidean distance as the heuristic function
def heuristic(current, goal, htype = 1):
    if htype == 1: # Manhattan distance: |x1 - x2|, |y1 - y2|
        return abs(current[0] - goal[0]) + abs(current[1] - goal[1])
    elif htype == 2: # Euclidean distance: sqrt((x2 - x1)^2 + (y2 - y1)^2))
        return ((current[0] - goal[0]) ** 2 + (current[1] - goal[1]) ** 2) ** 0.5

# Return direction taken from action
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
        return 'stay' # This scenario will not happen!

if __name__ == "__main__":
    filename = sys.argv[1]
    method = sys.argv[2]

    # Read map configuration from file
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
        goal = []
        for x_str, y_str in goal_coords:
            try:
                x, y = map(int, (x_str, y_str))
                goal.append((x, y))
            except ValueError:
                print(f"Invalid coordinate format: ({x_str}, {y_str}).")
        if not goal:
            print("No valid goal node found.")
            sys.exit(1)

        # Initialize the wall
        walls = []
        for wall in lines[3:]:
            wall_coords = re.findall(r'\d+', wall)
            if len(wall_coords) == 4:  # Ensure correct wall's coordinates as template
                walls.append(tuple(map(int, wall_coords)))

        # Initialize the grid
        grid = Grid(rows, cols)
        for wall in walls:
            grid.add_wall(*wall)

        # Perform search by relevant method, obtain path and total_nodes variable
        if method == "DFS":
            path, total_nodes = depth_first_search(grid, start, goal[0])
        elif method == "BFS":
            path, total_nodes = breadth_first_search(grid, start, goal[0])
        elif method == "CUS1":
            path, total_nodes = custom_search_1(grid, start, goal[0])
        elif method == "GBFS":
            path, total_nodes = greedy_best_first_search(grid, start, goal[0], heuristic)
        elif method == "AS":
            path, total_nodes = a_star_search(grid, start, goal[0], heuristic)
        elif method == "CUS2":
            path, total_nodes = custom_search_2(grid, start, goal[0], heuristic)

        else: 
            print("Invalid search method. Please choose among: DFS, BFS, CUS1 (uninformed) and GBFS, AS, CUS2 (informed)")
            sys.exit(1)

        # Print result (including the total nodes and path)
        if path:
            print(f"{filename} {method}")
            print(f"< Node ({goal[0][0]}, {goal[0][1]})> {total_nodes}") # add {len(path)} component for printing total_moves
            print([get_direction(path[i], path[i+1]) for i in range(len(path)-1)])
        else:
            print(f"{filename} {method}")
            print(f"No goal is reachable; {total_nodes}")

    # Create GUI window if path is not None
    # if path:
        #from gui import GUI
        #app = GUI(grid, start, goal[0], [tuple((node.x, node.y)) for node in path])
        #app.mainloop()