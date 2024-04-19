# grid.py
class Grid:
    def __init__(self, rows, cols, cell_size, starting_location, goal_states, walls):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.starting_location = starting_location
        self.goal_states = goal_states
        self.walls = walls
        self.goals_found = 0

    def get_neighbors(self, position):
        neighbors = []
        for move in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (position[0] + move[0], position[1] + move[1])
            if 0 <= neighbor[0] < self.rows and 0 <= neighbor[1] < self.cols and neighbor not in self.walls:
                neighbors.append(neighbor)
        return neighbors

    def reconstruct_path(self, position, search_nodes):
        current = position
        path = [current]
        while current != self.starting_location:
            for node in self.get_neighbors(current):
                if node in search_nodes:
                    current = node
                    path.insert(0, current)
                    break
        return path
