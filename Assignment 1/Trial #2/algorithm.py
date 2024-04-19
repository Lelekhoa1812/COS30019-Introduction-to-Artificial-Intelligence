# algorithm.py
import math

class Search:
    def __init__(self, grid):
        self.grid = grid

    def search(self, algorithm='dfs', heuristic_func=None):
        if algorithm == 'dfs-r':
            return self.dfs_recursive(self.grid.starting_location, [], set())
        elif algorithm == 'bfs':
            return self.bfs()
        elif algorithm == 'cus1':
            return self.dls(10000000)
        elif algorithm == 'cus1_ext':
            return self.ids()
        elif algorithm == 'gbfs':
            return self.greedy_best_first()
        elif algorithm == 'a':
            return self.a_star(heuristic_func)
        elif algorithm == "cus_2":
            return self.ida_star()

    def dfs_recursive(self, position, path, visited):
        visited.add(position)
        if position in self.grid.goal_states:
            return path + [position], visited

        for neighbor in self.grid.get_neighbors(position):
            if neighbor not in visited:
                result, visited = self.dfs_recursive(neighbor, path + [position], visited)
                if result:
                    return result, visited

        return None, visited

    
    def bfs(self):
        start = self.grid.starting_location
        queue = [(start, [])]

        while queue:
            position, path = queue.pop(0)
            if position in self.grid.goal_states:
                return path + [position], set()
            for neighbor in self.grid.get_neighbors(position):
                queue.append((neighbor, path + [position]))

        return None, set()

    def dls(self, depth_limit):
        start = self.grid.starting_location
        return self.dls_recursive(start, [], set(), depth_limit)

    def dls_recursive(self, position, path, visited, depth_limit):
        visited.add(position)
        if position in self.grid.goal_states:
            return path + [position], visited
        if len(path) >= depth_limit:
            return None, visited

        for neighbor in self.grid.get_neighbors(position):
            if neighbor not in visited:
                result, visited = self.dls_recursive(neighbor, path + [position], visited, depth_limit)
                if result:
                    return result, visited

        return None, visited

    def ids(self):
        start = self.grid.starting_location
        depth_limit = 1
        while True:
            result, _ = self.dls(depth_limit)
            if result:
                return result, set()
            depth_limit += 1

    def heuristic(self, node, goal):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    def greedy_best_first(self):
        start = self.grid.starting_location
        goal = self.grid.goal_states[0]
        frontier = [(self.heuristic(start, goal), start)]
        visited = set()

        while frontier:
            frontier.sort()
            _, position = frontier.pop(0)
            if position in self.grid.goal_states:
                return self.grid.reconstruct_path(position, visited), visited

            visited.add(position)
            for neighbor in self.grid.get_neighbors(position):
                if neighbor not in visited:
                    frontier.append((self.heuristic(neighbor, goal), neighbor))

        return None, visited

    def a_star(self, heuristic_func):
        start = self.grid.starting_location
        goal = self.grid.goal_states[0]
        frontier = [(heuristic_func(start, goal), 0, start)]
        visited = set()

        while frontier:
            frontier.sort()
            _, cost, position = frontier.pop(0)
            if position in self.grid.goal_states:
                return self.grid.reconstruct_path(position, visited), visited

            visited.add(position)
            for neighbor in self.grid.get_neighbors(position):
                if neighbor not in visited:
                    g = cost + 1
                    h = heuristic_func(neighbor, goal)
                    frontier.append((g + h, g, neighbor))

        return None, visited
    
    def ida_star(self):
        start = self.grid.starting_location
        goal = self.grid.goal_states[0]
        threshold = self.heuristic(start, goal)
        path, visited = self.dls_ida(start, [], set(), threshold)
        while path is None:
            threshold += 1
            path, visited = self.dls_ida(start, [], set(), threshold)
        return path, visited

    def dls_ida(self, position, path, visited, threshold):
        visited.add(position)
        f = len(path) + self.heuristic(position, self.grid.goal_states[0])
        if f > threshold:
            return None, visited
        if position in self.grid.goal_states:
            return path + [position], visited

        min_val = float('inf')
        for neighbor in self.grid.get_neighbors(position):
            if neighbor not in visited:
                result, visited = self.dls_ida(neighbor, path + [position], visited, threshold)
                if result:
                    return result, visited
                if result is None:
                    min_val = min(min_val, threshold)
        return None, visited
