# -*- coding: utf-8 -*-
"""
@author: Raul Ortega
(fixed version)
"""
import pygame, time, argparse, csv
import numpy as np
from time import sleep


def is_in_map(pos, grid_dim):
    (max_x, max_y) = grid_dim
    (x, y) = pos
    return 0 <= x <= max_x and 0 <= y <= max_y


class Node:
    def __init__(self, pos, parent):
        self.x = pos[0]
        self.y = pos[1]
        self.parent = parent

    def position(self):
        return (self.x, self.y)


class Queue:
    def __init__(self):
        self.Queue = []

    def __len__(self):
        return len(self.Queue)  # FIX: was len(Queue) (the class, not the list)

    def append(self, node):
        self.Queue.append(node)

    def get_node(self):
        return self.Queue[0]

    def get_node_position(self):
        return self.Queue[0].position()

    def remove(self):
        self.Queue = self.Queue[1:]


class BFS:
    def __init__(self, start_pos, goal_pos, grid_dim):
        self.grid_dim = grid_dim
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.explored = Queue()
        self.frontier = Queue()
        self.frontier.append(Node(pos=start_pos, parent=None))

    def backtrack_solution(self, grid, curr_node):
        solution = []
        while curr_node.parent is not None:
            solution.append(curr_node.position())
            curr_node = curr_node.parent
        return solution

    def compute_successors(self, grid):
        # FIX: no path -> frontier is empty, avoid IndexError
        if len(self.frontier) == 0:
            print("No path found!")
            return [], True

        curr_node = self.frontier.get_node()
        x, y = curr_node.position()

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_pos = (x + dx, y + dy)

            if is_in_map(new_pos, self.grid_dim) and grid[new_pos[0], new_pos[1]] in [1, 3]:
                new_node = Node(pos=new_pos, parent=curr_node)
                self.frontier.append(new_node)

                # FIX: compare tuples directly (set() ignored coordinate order and used a global)
                if new_pos == self.goal_pos:
                    self.explored.append(curr_node)
                    self.frontier.remove()
                    solution = self.backtrack_solution(grid, curr_node=new_node)
                    return solution, True

                # FIX: mark as visited when queued, so a cell is not queued twice
                grid[new_pos[0], new_pos[1]] = 4

        self.explored.append(curr_node)
        self.frontier.remove()
        return [], False


if __name__ == "__main__":
  start_t0 = time.time()

  # example: python bfs_pathfinder.py --display=1 --maze_file=maze_1.csv
  parser = argparse.ArgumentParser()
  parser.add_argument("--display", help="Display generating process 0: False, 1:True", default=1, type=int)
  parser.add_argument("--maze_file", help="filename (csv) of the maze to load.", default="maze_7.csv", type=str)
  args = parser.parse_args()

  address = "mazes/" + args.maze_file
  # FIX: dtype=int could read "1.0" as -1; read as float then convert
  grid = np.genfromtxt(address, delimiter=',').astype(int)
  num_rows = len(grid)
  num_columns = len(grid[0])

  start_pos = (0, 0)
  goal_pos = (num_rows - 1, num_columns - 1)

  grid[0, 0] = 2
  grid[-1, -1] = 3

  grid_dim = (num_rows - 1, num_columns - 1)

  if args.display == 1:
    black = (0, 0, 0)
    white = (255, 255, 255)
    green = (50, 205, 50)
    red = (255, 99, 71)
    grey = (211, 211, 211)
    blue = (153, 255, 255)
    magenta = (255, 0, 255)

    idx_to_color = [black, white, green, red, blue, magenta]

    height = 7
    width = height
    margin = 1

    pygame.init()

    WINDOW_SIZE = [330, 330]
    screen = pygame.display.set_mode(WINDOW_SIZE)

    pygame.display.set_caption(f"BFS Pathfinder. Solving: {address}")

    done = False
    run = False
    close = False
    solution = []  # FIX: avoid NameError if window is closed early

    clock = pygame.time.Clock()

    bfs = BFS(start_pos=start_pos, goal_pos=goal_pos, grid_dim=grid_dim)
    bfs_start = None

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                run = True

        screen.fill(grey)

        for row in range(num_rows):
            for column in range(num_columns):
                color = idx_to_color[grid[row, column]]
                pygame.draw.rect(screen, color,
                                 [(margin + width) * column + margin,
                                  (margin + height) * row + margin,
                                  width, height])

        clock.tick(60)
        pygame.display.flip()

        if run:
            if bfs_start is None:
                bfs_start = time.time()
            sleep(0.01)
            solution, done = bfs.compute_successors(grid=grid)

            for node in bfs.explored.Queue:
                grid[node.x, node.y] = 4

        if done:
            for pos in solution:
                grid[pos[0], pos[1]] = 5

            grid[0, 0] = 2
            grid[-1, -1] = 3

            screen.fill(grey)

            for row in range(num_rows):
                for column in range(num_columns):
                    color = idx_to_color[grid[row, column]]
                    pygame.draw.rect(screen, color,
                                     [(margin + width) * column + margin,
                                      (margin + height) * row + margin,
                                      width, height])

            clock.tick(60)
            pygame.display.flip()

    if bfs_start is not None:
        print(f"BFS time: {time.time() - bfs_start:.3f} s")
    print("Solved! Click exit.")
    pygame.event.clear()  # FIX: drop the key press that started the run
    while not close:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close = True
            elif event.type == pygame.KEYDOWN:
                close = True
    pygame.quit()

  else:
    print(f"Pathfinder BFS. solving: {address}")

    done = False
    bfs = BFS(start_pos=start_pos, goal_pos=goal_pos, grid_dim=grid_dim)

    while not done:
        solution, done = bfs.compute_successors(grid=grid)

        for node in bfs.explored.Queue:
            grid[node.x, node.y] = 4

    for pos in solution:
        grid[pos[0], pos[1]] = 5

    grid[0, 0] = 2
    grid[-1, -1] = 3

  # export maze to .csv file
  with open(f"mazes_solutions/bfs_{args.maze_file}", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(grid)

  print(f"--- finished {time.time()-start_t0:.3f} s---")
  exit(0)