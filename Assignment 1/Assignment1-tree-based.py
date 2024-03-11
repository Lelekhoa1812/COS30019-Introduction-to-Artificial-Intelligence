import sys
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

def reconstruct_path(node):
    path = []
    while node:
        path.append((node.x, node.y))
        node = node.parent
    return path[::-1]

def depth_first_search(grid, start, goal):
    stack = [Node(start[0], start[1])]
    visited = set()

    while stack:
        current = stack.pop()
        if (current.x, current.y) == goal:
            return reconstruct_path(current)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                stack.append(Node(next_x, next_y, current))
                visited.add((next_x, next_y))
    return []

def breadth_first_search(grid, start, goal):
    queue = [Node(start[0], start[1])]
    visited = set()

    while queue:
        current = queue.pop(0)
        if (current.x, current.y) == goal:
            return reconstruct_path(current)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                queue.append(Node(next_x, next_y, current))
                visited.add((next_x, next_y))
    return []

def greedy_best_first_search(grid, start, goal, heuristic):
    priority_queue = [(heuristic(start, goal), Node(start[0], start[1]))]
    heapq.heapify(priority_queue)
    visited = set()

    while priority_queue:
        _, current = heapq.heappop(priority_queue)
        if (current.x, current.y) == goal:
            return reconstruct_path(current)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                heapq.heappush(priority_queue, (heuristic((next_x, next_y), goal), Node(next_x, next_y, current)))
                visited.add((next_x, next_y))
    return []

def a_star_search(grid, start, goal, heuristic):
    priority_queue = [(0, heuristic(start, goal), Node(start[0], start[1]))]
    heapq.heapify(priority_queue)
    visited = set()

    while priority_queue:
        _, _, current = heapq.heappop(priority_queue)
        if (current.x, current.y) == goal:
            return reconstruct_path(current)
        visited.add((current.x, current.y))
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Right, Down, Left, Up
            next_x, next_y = current.x + dx, current.y + dy
            if (next_x, next_y) not in visited and grid.is_valid(next_x, next_y):
                heapq.heappush(priority_queue, (heuristic(start, goal) + heuristic((next_x, next_y), goal), heuristic((next_x, next_y), goal), Node(next_x, next_y, current)))
                visited.add((next_x, next_y))
    return []

# Custom heuristic function (e.g., Manhattan distance)
def heuristic(current, goal):
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

# Example usage:
if __name__ == "__main__":
    filename = sys.argv[1]
    method = sys.argv[2]

    # Read grid configuration from file
    with open(filename, 'r') as file:
        lines = file.readlines()
        rows, cols = map(int, lines[0][1:-2].split(','))
        start = tuple(map(int, lines[1][1:-2].split(',')))
        goal = [tuple(map(int, coord.strip()[1:-1].split(','))) for coord in lines[2][1:-2].split('|') if coord.strip()]
        walls = [tuple(map(int, wall.split(','))) for wall in lines[3:]]

    grid = Grid(rows, cols)
    for wall in walls:
        grid.add_wall(*wall)

    # Perform search based on specified method
    if method == "DFS":
        path = depth_first_search(grid, start, goal)
    elif method == "BFS":
        path = breadth_first_search(grid, start, goal)
    elif method == "GBFS":
        path = greedy_best_first_search(grid, start, goal[0], heuristic)
    elif method == "AS":
        path = a_star_search(grid, start, goal[0], heuristic)
    else:
        print("Invalid search method. Please choose one of: DFS, BFS, GBFS, AS")
        sys.exit(1)

    # Print result
    if path:
        print(f"{filename} {method} {goal[0]} {len(path)} {' '.join(map(str, path))}")
    else:
        print(f"{filename} {method}")
        print("No goal is reachable")
