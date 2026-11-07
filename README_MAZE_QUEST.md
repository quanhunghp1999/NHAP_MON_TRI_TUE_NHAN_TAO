# Maze Quest – Desktop Maze Game

A small desktop maze game built with Python and Tkinter.

## Features
- Player mode with arrow keys or WASD.
- AI Solver mode with BFS, DFS and A*.
- Easy, Medium and Hard levels.
- Solution display and algorithm comparison.
- CSV results log for each comparison run.

## Run

Requires Python 3 with Tkinter. On Windows, double-click `run_game.bat` or run:

```bash
python maze_game.py
```

## Compare algorithms

Select a maze and click **Compare Algorithms & Log Results**. The game runs BFS, DFS and A* on the same maze and displays:

- Path steps
- Explored and discovered nodes
- Maximum frontier size
- Runtime in milliseconds

Results are appended to `algorithm_comparison_log.csv` in the same folder as `maze_game.py`. Each comparison uses a shared `run_id`.

BFS and A* should return a shortest path on this unweighted grid. DFS is not guaranteed to return a shortest path. Different algorithms may still return paths with the same length.
