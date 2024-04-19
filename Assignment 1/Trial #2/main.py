# main.py

import pygame
import time
import sys
from grid import Grid
from algorithm import Search

def read_map(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    rows = len(lines)
    grid = []
    start = None
    goal = None
    for i in range(rows):
        row = []
        line = lines[i].strip()  
        cols = len(line)
        for j in range(cols):
            if line[j] == 'S':
                start = (i, j)
            elif line[j] == 'G':
                goal = (i, j)
            elif line[j] == '#':
                wall = (i, j)
            else:
                row.append((i, j))
        if row:
            grid.append(row)
    return grid, start, goal

# Define heuristic functions
def manhattan_distance(node, goal):
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

def chebyshev_distance(node, goal):
    return max(abs(node[0] - goal[0]), abs(node[1] - goal[1]))

def euclidean_distance(node, goal):
    return math.sqrt((node[0] - goal[0]) ** 2 + (node[1] - goal[1]) ** 2)

def execute_search(search, algorithm, heuristic_func=None):
    if algorithm == 'a':
        result, visited = search.search(algorithm=algorithm, heuristic_func=heuristic_func)
    else:
        result, visited = search.search(algorithm=algorithm)

    print("Algorithm:", algorithm)
    print("Result:", result)
    print("Visited:", visited)

    if result is not None:
        return result, visited
    else:
        return None, visited

# Update main function to accept heuristic function parameter
def main():
    if len(sys.argv) != 4:
        print("Usage: python main.py [map_file] [method] [heuristic]")
        return

    map_file = sys.argv[1]
    method = sys.argv[2]
    heuristic = sys.argv[3]

    grid, start, goal = read_map(map_file)
    rows = len(grid)
    cols = len(grid[0])
    grid = Grid(rows, cols, 40, start, [goal], [])  # Assuming no walls in this version
    search = Search(grid)

    # Select the appropriate heuristic function
    heuristic_func = None
    if heuristic == 'manhattan':
        heuristic_func = manhattan_distance
    elif heuristic == 'chebyshev':
        heuristic_func = chebyshev_distance
    elif heuristic == 'euclidean':
        heuristic_func = euclidean_distance

    result, visited = execute_search(search, method, heuristic_func)
    if result:
        print_result(result)
    else:
        print("No path found.")

if __name__ == "__main__":
    main()
