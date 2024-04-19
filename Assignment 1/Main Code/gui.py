import tkinter as tk
from searchmain import Node

class GUI(tk.Tk):
    # Draw the dmap display
    def __init__(self, grid_instance, grid, start, goal, path, traversed):
        super().__init__()
        self.title("GUI Display")
        window_width = 30 * grid_instance.rows # Cell size * num_of_rows  
        window_height = 30 * grid_instance.cols  # Cell size * num_of_cols
        self.geometry(f"{window_width}x{window_height}") # Size of the GUI display window is designated to fit the map    
        self.grid = grid
        self.start = start
        self.goal = [goal] # List of goal nodes
        self.path = [Node(x, y) for x, y in path]
        self.traversed = [Node(x, y) for x, y in traversed] 
        self.cell_size = 30 # Each cell sized as a square 30x30
        self.canvas = tk.Canvas(self, width=window_width, height=window_height)
        self.canvas.pack()
        self.draw_grid()
        self.current_step = 1 # Started from the first step
        self.current_traversed = 1 # Started from the first step
        self.display_next_step() # Show paths as a sequent of motion by gradual changess.
 
    def draw_grid(self):
        for i in range(self.grid.rows): # x0, y0, x1, y1 is positional data of a polygon
            for j in range(self.grid.cols):
                x0, y0 = i * self.cell_size, j * self.cell_size  
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                if (i, j) in self.goal: # Goal cell(s) as lime color
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="lime")
                elif (i, j) == self.start: # Match starting cell as red color
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="red")
                elif self.grid.grid[i][j] == 1: # Wall cell(s) as gray color
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="dark gray")
                elif (i, j) in self.traversed: # All explored cells as purple color
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="purple") 
                else: # Empty cell(s) as white color
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="white")
    
    # For n steps, display from 1 to (n-1)th step, for either node expansion (traversed) and path finding.
    # Node expansion are displayed gradually by each 0.2s, until it find the goal node, the path will be shown by each 0.1s
    def display_next_step(self):
        if self.current_traversed < (len(self.traversed)-1):  # If traversed reach n-1 step
            node = self.traversed[self.current_traversed]
            x0, y0 = node.x * self.cell_size, node.y * self.cell_size
            x1, y1 = x0 + self.cell_size, y0 + self.cell_size
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="purple") # Display explored node as purple color
            self.current_traversed += 1
            self.after(200, self.display_next_step)  # Update traversed expansion every 0.2 seconds

        elif self.current_traversed == (len(self.traversed)-1): # Once the node expansion reach the goal node, start displaying path
            if self.current_step < (len(self.path)-1): # If path reach n-1 step
                node = self.path[self.current_step]
                x0, y0 = node.x * self.cell_size, node.y * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="yellow") # Path displayed as yellow color.
                self.current_step += 1 # Add step variable  by 1 after each function call
                self.after(100, self.display_next_step)  # After 0.1 seconds, update next steps.

if __name__ == "__main__":
   pass
