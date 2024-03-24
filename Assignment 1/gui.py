import tkinter as tk
from searchmain import Node

class GUI(tk.Tk):
    def __init__(self, grid, start, goal, path):
        super().__init__()
        self.title("Grid Display")
        window_width = 330 #10 * self.grid.cols  
        window_height = 330 #10 * self.grid.rows  
        self.geometry(f"{window_width}x{window_height}") # Size of the GUI display window is designed to fit the map    
        self.grid = grid
        self.start = start
        self.goal = goal
        self.path = [Node(x, y) for x, y in path]
        self.cell_size = 30
        self.canvas = tk.Canvas(self, width=window_width, height=window_height)
        self.canvas.pack()
        self.draw_grid()

    def draw_grid(self):
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                x0, y0 = i * self.cell_size, j * self.cell_size  # Swap x and y
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                if (i, j) == self.goal:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="lime green")
                elif (i, j) == self.start:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="red")
                elif (i, j) in self.path:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="yellow")
                elif self.grid.grid[i][j] == 1:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="dark gray")
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="white")


if __name__ == "__main__":
   pass
