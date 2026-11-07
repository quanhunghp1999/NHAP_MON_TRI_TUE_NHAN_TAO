# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 13:51:53 2020
@author: Raul Ortega Ochoa
(fixed version)
"""
import pygame, time, csv, argparse
import numpy as np
from time import sleep
from helper_aStar import generate_step, pick_node_from_list, Node

if __name__ == "__main__":

  start_t0 = time.time()

  # example: python aStar_pathfinder.py --display=1 --maze_file=maze_1.csv
  parser = argparse.ArgumentParser()
  parser.add_argument("--display", help="Display generating process 0: False, 1:True", default=1, type=int)
  parser.add_argument("--maze_file", help="filename (csv) of the maze to load.", default="maze_7.csv", type=str)
  args = parser.parse_args()

  address = "mazes/" + args.maze_file
  # FIX: dtype=int could read "1.0" as -1; read as float then convert
  grid = np.genfromtxt(address, delimiter=',').astype(int)

  # define goal and start
  num_rows = len(grid)
  num_columns = len(grid[0])
  goal = (num_rows-1, num_columns-1)
  start = (0, 0)

  # define start node
  start_node = Node(None, 0, start)

  # initialize seen, frontier list
  seen = []
  frontier = [start_node]

  if args.display == 1:

    black = (0, 0, 0)
    white = (255, 255, 255)
    green = (50, 205, 50)
    red = (255, 99, 71)
    grey = (211, 211, 211)
    blue = (153, 255, 255)
    magenta = (255, 0, 255)

    height = 7
    width = height
    margin = 1

    pygame.init()

    WINDOW_SIZE = [330, 330]
    screen = pygame.display.set_mode(WINDOW_SIZE)

    pygame.display.set_caption(f"A* Pathfinder. Solving: {address}")
    clock = pygame.time.Clock()

    idx_to_color = [black, white, green, red, blue, magenta]

    interrupt = False  # when user clicks exit
    run = False        # when algorithm starts (press ENTER)
    finish = False
    last_iter = False
    astar_start = None

    while not interrupt:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                interrupt = True
            # wait for user to press RETURN key to start
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
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

        if last_iter:
            interrupt = True
            run = False
        elif run:
            if astar_start is None:
                astar_start = time.time()

            # FIX: no path -> frontier is empty, avoid crash
            if len(frontier) == 0:
                print("No path found!")
                last_iter = True
                continue

            current_node = pick_node_from_list(frontier)
            grid, frontier, seen, current_node = generate_step(grid, frontier, seen, current_node)

            if current_node.position == goal:
                last_iter = True
                # follow the parents back to the origin
                while current_node.parent is not None:
                    x, y = current_node.position
                    grid[x, y] = 5
                    current_node = current_node.parent

            sleep(0.01)

    if astar_start is not None:
        print(f"A* time: {time.time() - astar_start:.3f} s")
    print("Solved! Click exit.")
    pygame.event.clear()  # FIX: drop the ENTER press that started the run
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True
            elif event.type == pygame.KEYDOWN:
                finish = True
    pygame.quit()

  else:

    print(f"A* Pathfinder. Solving: {address}")

    done = False
    while not done:

      # FIX: no path -> frontier is empty, avoid crash
      if len(frontier) == 0:
        print("No path found!")
        break

      current_node = pick_node_from_list(frontier)
      grid, frontier, seen, current_node = generate_step(grid, frontier, seen, current_node)

      if current_node.position == goal:
        done = True
        while current_node.parent is not None:
          x, y = current_node.position
          grid[x, y] = 5
          current_node = current_node.parent

  # export maze to .csv file
  with open(f"mazes_solutions/aStar_{args.maze_file}", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(grid)

  print(f"--- finished {time.time()-start_t0:.3f} s---")
  exit(0)