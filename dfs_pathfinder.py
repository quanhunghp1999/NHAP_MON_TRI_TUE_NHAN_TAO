import pygame, time, argparse, csv
import numpy as np
import os
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
        return len(self.Queue)

    def append(self, node):
        self.Queue.append(node)

    def get_node(self):
        return self.Queue[-1]

    def remove(self):
        self.Queue = self.Queue[:-1]


class DFS:
    def __init__(self, start_pos, goal_pos, grid_dim):
        self.grid_dim = grid_dim
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.explored = Queue()
        self.frontier = Queue()
        self.frontier.append(Node(pos=start_pos, parent=None))

    def backtrack_solution(self, curr_node):
        solution = []
        while curr_node.parent is not None:
            solution.append(curr_node.position())
            curr_node = curr_node.parent
        return solution

    def compute_successors(self, grid):
        if len(self.frontier) == 0:
            print("Khong tim thay duong di!")
            return [], True

        curr_node = self.frontier.get_node()
        x, y = curr_node.position()

        buffer_nodes = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_pos = (x + dx, y + dy)

            if is_in_map(new_pos, self.grid_dim) and grid[new_pos[0], new_pos[1]] in [1, 3]:
                new_node = Node(pos=new_pos, parent=curr_node)
                buffer_nodes.append(new_node)

                if new_pos == self.goal_pos:
                    self.explored.append(curr_node)
                    self.frontier.remove()
                    return self.backtrack_solution(new_node), True

        self.explored.append(curr_node)
        self.frontier.remove()
        for n in buffer_nodes:
            self.frontier.append(n)
        return [], False


def draw_grid(screen, grid, idx_to_color, num_rows, num_columns, width, height, margin, grey):
    screen.fill(grey)
    for row in range(num_rows):
        for column in range(num_columns):
            color = idx_to_color[grid[row, column]]
            pygame.draw.rect(screen, color,
                             [(margin + width) * column + margin,
                              (margin + height) * row + margin,
                              width, height])


if __name__ == "__main__":
    start_t0 = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument("--display", help="Display generating process 0: False, 1:True", default=1, type=int)
    parser.add_argument("--maze_file", help="filename (csv) of the maze to load.", default="maze_7.csv", type=str)
    args = parser.parse_args()

    base = r"C:\Users\Quan Hung\PyCharmMiscProject\ai-maze-python-master"
    address = os.path.join(base, "mazes", args.maze_file)
    grid = np.genfromtxt(address, delimiter=',').astype(int)
    num_rows = len(grid)
    num_columns = len(grid[0])

    start_pos = (0, 0)
    goal_pos = (num_rows - 1, num_columns - 1)

    grid[0, 0] = 2
    grid[-1, -1] = 3

    grid_dim = (num_rows - 1, num_columns - 1)
    solution = []

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
        WINDOW_SIZE = [(margin + width) * num_columns + margin,
                       (margin + height) * num_rows + margin]
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(f"DFS Pathfinder. Solving: {address}")

        done = False
        run = False
        close = False
        clock = pygame.time.Clock()

        dfs = DFS(start_pos=start_pos, goal_pos=goal_pos, grid_dim=grid_dim)

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    run = True

            draw_grid(screen, grid, idx_to_color, num_rows, num_columns, width, height, margin, grey)
            clock.tick(60)
            pygame.display.flip()

            if run and not done:
                sleep(0.01)
                solution, done = dfs.compute_successors(grid=grid)
                for node in dfs.explored.Queue:
                    grid[node.x, node.y] = 4

        for pos in solution:
            grid[pos[0], pos[1]] = 5
        grid[0, 0] = 2
        grid[-1, -1] = 3

        draw_grid(screen, grid, idx_to_color, num_rows, num_columns, width, height, margin, grey)
        clock.tick(60)
        pygame.display.flip()

        print("Solved! Click exit.")
        while not close:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close = True
                elif event.type == pygame.KEYDOWN:
                    close = True
        pygame.quit()

    else:
        print(f"Pathfinder DFS. solving: {address}")

        done = False
        dfs = DFS(start_pos=start_pos, goal_pos=goal_pos, grid_dim=grid_dim)

        while not done:
            solution, done = dfs.compute_successors(grid=grid)
            for node in dfs.explored.Queue:
                grid[node.x, node.y] = 4

        for pos in solution:
            grid[pos[0], pos[1]] = 5

        grid[0, 0] = 2
        grid[-1, -1] = 3

    out_dir = os.path.join(base, "mazes_solutions")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"dfs_{args.maze_file}"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(grid)

    print(f"--- finished {time.time() - start_t0:.3f} s---")
    exit(0)