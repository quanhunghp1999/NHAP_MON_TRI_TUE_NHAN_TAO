                       
from __future__ import annotations

import random
import time
import heapq
import itertools
import csv
import os
from datetime import datetime
from collections import deque
import tkinter as tk
from tkinter import messagebox, ttk

BG = (244, 247, 251)
INK = (23, 43, 77)
MUTED = (100, 116, 139)
WALL = (29, 41, 63)
FLOOR = (255, 255, 255)
START = (36, 160, 98)
GOAL = (226, 78, 78)
PLAYER = (40, 100, 220)
PATH = (247, 190, 75)
VISITED = (194, 219, 246)
GRID = (220, 228, 239)

LEVELS = {
    "Easy":   {"rows": 11, "cols": 15, "time": 90, "bonus": 100},
    "Medium": {"rows": 17, "cols": 23, "time": 120, "bonus": 200},
    "Hard":   {"rows": 23, "cols": 31, "time": 180, "bonus": 350},
}
ALGORITHMS = ("BFS", "DFS", "A*")


def generate_maze(rows, cols):
    rows = rows if rows % 2 else rows + 1
    cols = cols if cols % 2 else cols + 1
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    start = (1, 1)
    grid[start[0]][start[1]] = 1
    stack = [start]
    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    while stack:
        r, c = stack[-1]
        choices = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr][nc] == 0:
                choices.append((nr, nc, dr, dc))
        if choices:
            nr, nc, dr, dc = random.choice(choices)
            grid[r + dr // 2][c + dc // 2] = 1
            grid[nr][nc] = 1
            stack.append((nr, nc))
        else:
            stack.pop()
    grid[1][0] = 1
    grid[rows - 2][cols - 1] = 1
    grid[rows - 2][cols - 2] = 1

                                                                              
                                                                           
                                                                            
    candidates = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] != 0:
                continue
            horizontal = grid[r][c - 1] == 1 and grid[r][c + 1] == 1
            vertical = grid[r - 1][c] == 1 and grid[r + 1][c] == 1
            if horizontal or vertical:
                candidates.append((r, c))
    random.shuffle(candidates)
                                                                                 
    open_count = max(1, int(len(candidates) * 0.10)) if candidates else 0
    for r, c in candidates[:open_count]:
        grid[r][c] = 1

    return grid, (1, 0), (rows - 2, cols - 1)


def find_path(grid, start, goal, algorithm="BFS", collect_metrics=False):
    rows, cols = len(grid), len(grid[0])
    began = time.perf_counter()
    parent = {start: None}
    explored = []
    moves = ((-1, 0), (1, 0), (0, -1), (0, 1))
    discovered_count = 1
    max_frontier = 1

    def adjacent(pos):
        r, c = pos
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                yield nr, nc

    if algorithm == "BFS":
        frontier = deque([start])
        seen = {start}
        while frontier:
            cur = frontier.popleft()
            explored.append(cur)
            if cur == goal:
                break
            for nxt in adjacent(cur):
                if nxt not in seen:
                    seen.add(nxt)
                    parent[nxt] = cur
                    frontier.append(nxt)
            discovered_count = len(seen)
            max_frontier = max(max_frontier, len(frontier))

    elif algorithm == "DFS":
        frontier = [start]
        seen = {start}
        while frontier:
            cur = frontier.pop()
            explored.append(cur)
            if cur == goal:
                break
            for nxt in adjacent(cur):
                if nxt not in seen:
                    seen.add(nxt)
                    parent[nxt] = cur
                    frontier.append(nxt)
            discovered_count = len(seen)
            max_frontier = max(max_frontier, len(frontier))

    elif algorithm == "A*":
        count = itertools.count()
        g_score = {start: 0}
        heuristic = lambda p: abs(goal[0] - p[0]) + abs(goal[1] - p[1])
        frontier = [(heuristic(start), 0, next(count), start)]
        closed = set()
        while frontier:
            _, g, _, cur = heapq.heappop(frontier)
            if cur in closed:
                continue
            closed.add(cur)
            explored.append(cur)
            if cur == goal:
                break
            for nxt in adjacent(cur):
                tentative = g_score[cur] + 1
                if tentative < g_score.get(nxt, float("inf")):
                    g_score[nxt] = tentative
                    parent[nxt] = cur
                    heapq.heappush(frontier, (tentative + heuristic(nxt), tentative, next(count), nxt))
            discovered_count = len(g_score)
            max_frontier = max(max_frontier, len(frontier))
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    elapsed = time.perf_counter() - began
    if goal not in parent:
        path = []
    else:
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()

    if collect_metrics:
        metrics = {
            "path_steps": max(0, len(path) - 1),
            "explored_nodes": len(explored),
            "discovered_nodes": discovered_count,
            "max_frontier": max_frontier,
            "runtime_ms": elapsed * 1000,
            "success": bool(path),
        }
        return path, explored, elapsed, metrics
    return path, explored, elapsed


class MazeQuest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Maze Quest — Desktop Maze Game")
        self.root.geometry("540x650")
        self.root.minsize(520, 620)
        self.root.configure(bg="#F4F7FB")

        self.level = tk.StringVar(value="Easy")
        self.mode = tk.StringVar(value="Player")
        self.algorithm = tk.StringVar(value="BFS")
        self.status = tk.StringVar(value="Choose a level and press Start Game.")
        self.score = 0
        self.best_score = 0
        self.moves = 0
        self.remaining = LEVELS["Easy"]["time"]
        self.deadline = None
        self.game_over = False
        self.game_started = False
        self.ai_after_id = None

        self._build_menu()
        self._new_game()
        self.root.after(250, self._tick)

    def _build_menu(self):
        tk.Label(self.root, text="MAZE QUEST", font=("Segoe UI", 23, "bold"),
                 fg="#172B4D", bg="#F4F7FB").pack(pady=(16, 2))
        tk.Label(self.root, text="Find the exit before time runs out",
                 font=("Segoe UI", 10), fg="#64748B", bg="#F4F7FB").pack(pady=(0, 12))

        panel = tk.Frame(self.root, bg="white", padx=12, pady=10,
                         highlightbackground="#DCE4EF", highlightthickness=1)
        panel.pack(fill="x", padx=18)

        fields = tk.Frame(panel, bg="white")
        fields.pack(fill="x")
        self._field(fields, "Level", self.level, list(LEVELS.keys()), 0)
        self._field(fields, "Mode", self.mode, ["Player", "AI Solver"], 1)
        self._field(fields, "Algorithm", self.algorithm, list(ALGORITHMS), 2)

        buttons = tk.Frame(self.root, bg="#F4F7FB")
        buttons.pack(pady=10)
        tk.Button(buttons, text="New Maze", command=self._new_game, width=11,
                  bg="#2563EB", fg="white", activebackground="#1D4ED8",
                  relief="flat", padx=7, pady=7).pack(side="left", padx=4)
        tk.Button(buttons, text="Start Game", command=self._start_game, width=12,
                  bg="#172B4D", fg="white", activebackground="#233D68",
                  relief="flat", padx=7, pady=7).pack(side="left", padx=4)
        tk.Button(buttons, text="Show Solution", command=self._show_solution, width=12,
                  bg="#E8EEF7", fg="#172B4D", activebackground="#D8E3F3",
                  relief="flat", padx=7, pady=7).pack(side="left", padx=4)
        tk.Button(buttons, text="Reset", command=self._restart, width=8,
                  bg="#E8EEF7", fg="#172B4D", relief="flat", padx=7, pady=7).pack(side="left", padx=4)
        tk.Button(self.root, text="Compare Algorithms & Log Results", command=self._compare_algorithms,
                  bg="#DCEAFE", fg="#172B4D", relief="flat", padx=10, pady=5).pack(pady=(0, 8))

        legend = tk.Frame(self.root, bg="#F4F7FB")
        legend.pack(fill="x", padx=22, pady=(0, 6))
        for color, label in [(START, "Start"), (GOAL, "Exit"), (PLAYER, "Player"), (PATH, "Solution")]:
            item = tk.Frame(legend, bg="#F4F7FB")
            item.pack(side="left", padx=(0, 14))
            tk.Label(item, text="  ", bg=self._hex(color), relief="flat").pack(side="left", padx=(0, 4))
            tk.Label(item, text=label, bg="#F4F7FB", fg="#64748B",
                     font=("Segoe UI", 8)).pack(side="left")

        self.canvas = tk.Canvas(self.root, width=500, height=330,
                                bg="white", highlightbackground="#DCE4EF",
                                highlightthickness=1)
        self.canvas.pack(padx=18, pady=(0, 10))

        info = tk.Frame(self.root, bg="#F4F7FB")
        info.pack(fill="x", padx=22)
        self.score_label = tk.Label(info, text="Score: 0", bg="#F4F7FB",
                                    fg="#172B4D", font=("Segoe UI", 10, "bold"))
        self.score_label.pack(side="left")
        self.moves_label = tk.Label(info, text="Moves: 0", bg="#F4F7FB",
                                    fg="#172B4D", font=("Segoe UI", 10, "bold"))
        self.moves_label.pack(side="left", padx=18)
        self.timer_label = tk.Label(info, text="Time: 00:00", bg="#F4F7FB",
                                    fg="#172B4D", font=("Segoe UI", 10, "bold"))
        self.timer_label.pack(side="right")

        tk.Label(self.root, textvariable=self.status, bg="#F4F7FB",
                 fg="#64748B", font=("Segoe UI", 9), wraplength=490).pack(pady=(8, 0))
        self.root.bind("<KeyPress>", self._on_key)
        self.root.focus_force()

    def _field(self, parent, label, variable, values, column):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=0, column=column, padx=(0 if column == 0 else 12, 0), sticky="w")
        tk.Label(frame, text=label, bg="white", fg="#172B4D",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        menu = tk.OptionMenu(frame, variable, *values)
        menu.config(width=10, bg="#F4F7FB", relief="flat", highlightthickness=0)
        menu.pack(anchor="w", pady=(3, 0))

    def _new_game(self):
        self._cancel_ai()
        cfg = LEVELS[self.level.get()]
        self.grid, self.start, self.goal = generate_maze(cfg["rows"], cfg["cols"])
        self.player = self.start
        self.moves = 0
        self.remaining = cfg["time"]
        self.deadline = None
        self.game_over = False
        self.game_started = False
        self.solution_path = []
        self.explored = []
        self.status.set("Green = start, red = exit, blue = player. Press Start Game.")
        self._draw()
        self._update_stats()

    def _restart(self):
        self._cancel_ai()
        self.player = self.start
        self.moves = 0
        self.remaining = LEVELS[self.level.get()]["time"]
        self.deadline = None
        self.game_over = False
        self.game_started = False
        self.solution_path = []
        self.explored = []
        self.status.set("Reset complete. Press Start Game to begin.")
        self._draw()
        self._update_stats()

    def _start_game(self):
        if self.game_over:
            self._restart()
        if not self.game_started:
            self.game_started = True
            self.deadline = time.monotonic() + self.remaining
        if self.mode.get() == "AI Solver":
            self._start_ai()
        else:
            self.status.set("Game started! Use arrow keys or WASD to reach the red exit.")
            self.root.focus_force()

    def _on_key(self, event):
        if self.game_over or not self.game_started or self.mode.get() != "Player":
            return
        key = event.keysym.lower()
        directions = {
            "up": (-1, 0), "w": (-1, 0),
            "down": (1, 0), "s": (1, 0),
            "left": (0, -1), "a": (0, -1),
            "right": (0, 1), "d": (0, 1),
        }
        if key not in directions:
            return
        dr, dc = directions[key]
        nr, nc = self.player[0] + dr, self.player[1] + dc
        if not (0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0])):
            return
        if self.grid[nr][nc] == 0:
            self.status.set("Blocked by a wall — try another direction.")
            return
        self.player = (nr, nc)
        self.moves += 1
        self._draw()
        self._update_stats()
        if self.player == self.goal:
            self._win()

    def _tick(self):
        if self.game_started and not self.game_over and self.deadline is not None:
            self.remaining = max(0, int(self.deadline - time.monotonic()))
            self._update_stats()
            if self.remaining <= 0:
                self.game_over = True
                self._cancel_ai()
                self.status.set("Time is up! Press Reset or New Maze to try again.")
                messagebox.showinfo("Time's up", "Time is up! Try again.")
        self.root.after(250, self._tick)

    def _win(self):
        self.game_over = True
        self._cancel_ai()
        cfg = LEVELS[self.level.get()]
        elapsed = cfg["time"] - self.remaining
        gained = max(50, cfg["bonus"] + self.remaining * 2 - self.moves)
        self.score += gained
        self.best_score = max(self.best_score, self.score)
        self.status.set(f"Completed in {self.moves} moves. +{gained} points.")
        self._update_stats()
        messagebox.showinfo(
            "Maze completed!",
            f"You reached the exit!\n\nMoves: {self.moves}\nTime used: {elapsed} seconds\nPoints earned: {gained}\nTotal score: {self.score}"
        )

    def _show_solution(self):
        self.solution_path, self.explored, _ = find_path(
            self.grid, self.start, self.goal, self.algorithm.get()
        )
        if not self.solution_path:
            self.status.set("No route found for this maze.")
            return
        self._draw(show_solution=True)
        self.status.set(
            f"{self.algorithm.get()} solution highlighted in yellow: {len(self.solution_path)-1} steps. "
            "Press Reset to hide the solution and play."
        )

    def _compare_algorithms(self):
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        timestamp = datetime.now().isoformat(timespec="seconds")
        rows = []
        for algorithm in ALGORITHMS:
            path, explored, _, metrics = find_path(
                self.grid, self.start, self.goal, algorithm, collect_metrics=True
            )
            row = {
                "run_id": run_id,
                "timestamp": timestamp,
                "level": self.level.get(),
                "algorithm": algorithm,
                **metrics,
            }
            rows.append(row)

        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "algorithm_comparison_log.csv")
        columns = ["run_id", "timestamp", "level", "algorithm", "path_steps",
                   "explored_nodes", "discovered_nodes", "max_frontier", "runtime_ms", "success"]
        write_header = not os.path.exists(log_path) or os.path.getsize(log_path) == 0
        with open(log_path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            if write_header:
                writer.writeheader()
            for row in rows:
                writer.writerow({**row, "runtime_ms": f"{row['runtime_ms']:.3f}"})

        window = tk.Toplevel(self.root)
        window.title("Algorithm Comparison — same maze")
        window.geometry("780x290")
        window.configure(bg="#F4F7FB")
        tk.Label(window, text="All algorithms ran on the same maze", font=("Segoe UI", 12, "bold"),
                 bg="#F4F7FB", fg="#172B4D").pack(anchor="w", padx=12, pady=(12, 4))
        tk.Label(window, text=f"CSV log saved to: {log_path}", bg="#F4F7FB", fg="#64748B",
                 wraplength=750, justify="left").pack(anchor="w", padx=12, pady=(0, 8))
        cols = ("algorithm", "path_steps", "explored_nodes", "discovered_nodes", "max_frontier", "runtime_ms", "success")
        table = ttk.Treeview(window, columns=cols, show="headings", height=4)
        labels = {"algorithm": "Algorithm", "path_steps": "Path steps", "explored_nodes": "Explored",
                  "discovered_nodes": "Discovered", "max_frontier": "Max frontier", "runtime_ms": "Runtime (ms)", "success": "Success"}
        widths = {"algorithm": 90, "path_steps": 90, "explored_nodes": 90, "discovered_nodes": 100,
                  "max_frontier": 100, "runtime_ms": 100, "success": 70}
        for col in cols:
            table.heading(col, text=labels[col])
            table.column(col, width=widths[col], anchor="center")
        for row in rows:
            table.insert("", "end", values=(row["algorithm"], row["path_steps"], row["explored_nodes"],
                row["discovered_nodes"], row["max_frontier"], f"{row['runtime_ms']:.3f}", row["success"]))
        table.pack(fill="x", padx=12, pady=(0, 10))
        tk.Label(window, text="Path steps may still match: BFS and A* find shortest paths; DFS may also find one by chance. "
                 "Explored nodes and runtime show the search effort.", wraplength=750, justify="left",
                 bg="#F4F7FB", fg="#172B4D").pack(anchor="w", padx=12, pady=(0, 10))

    def _start_ai(self):
        self._cancel_ai()
        self.solution_path, self.explored, _ = find_path(
            self.grid, self.start, self.goal, self.algorithm.get()
        )
        if not self.solution_path:
            self.status.set("AI could not find a route.")
            return
        self.player = self.start
        self.moves = 0
        self.game_over = False
        self._draw(show_solution=False)
        self.status.set(f"AI running {self.algorithm.get()}... press Reset to stop.")
        self._animate_ai(0)

    def _animate_ai(self, index):
        if self.game_over:
            return
        if index >= len(self.solution_path):
            self.player = self.goal
            self.moves = len(self.solution_path) - 1
            self._draw(show_solution=True)
            self._update_stats()
            self._win()
            return
        self.player = self.solution_path[index]
        self.moves = index
        self._draw(show_solution=False)
        self._update_stats()
        self.ai_after_id = self.root.after(100, lambda: self._animate_ai(index + 1))

    def _cancel_ai(self):
        if self.ai_after_id is not None:
            try:
                self.root.after_cancel(self.ai_after_id)
            except tk.TclError:
                pass
            self.ai_after_id = None

    def _draw(self, show_solution=False):
        self.canvas.delete("all")
        rows, cols = len(self.grid), len(self.grid[0])
        cell = min(500 // cols, 330 // rows)
        xoff = (500 - cols * cell) // 2
        yoff = (330 - rows * cell) // 2
        path_set = set(self.solution_path) if show_solution and self.solution_path else set()
        explored_set = set(self.explored) if show_solution and self.explored else set()

        for r in range(rows):
            for c in range(cols):
                pos = (r, c)
                x1, y1 = xoff + c * cell, yoff + r * cell
                x2, y2 = x1 + cell - 1, y1 + cell - 1
                color = WALL if self.grid[r][c] == 0 else FLOOR
                if pos in explored_set and pos not in (self.start, self.goal):
                    color = VISITED
                if pos in path_set and pos not in (self.start, self.goal):
                    color = PATH
                if pos == self.start:
                    color = START
                if pos == self.goal:
                    color = GOAL
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=self._hex(color),
                                             outline=self._hex(GRID), width=1)

                                                                                          
        r, c = self.player
        x1, y1 = xoff + c * cell, yoff + r * cell
        inset = max(3, cell // 3)
        self.canvas.create_oval(
            x1 + inset, y1 + inset, x1 + cell - inset, y1 + cell - inset,
            fill=self._hex(PLAYER), outline="white", width=1
        )
                                                                 
        for pos, label in ((self.start, "S"), (self.goal, "E")):
            rr, cc = pos
            cx = xoff + cc * cell + cell / 2
            cy = yoff + rr * cell + cell / 2
            self.canvas.create_text(cx, cy, text=label, fill="white",
                                    font=("Segoe UI", max(6, cell // 2), "bold"))

    @staticmethod
    def _hex(rgb):
        return "#%02x%02x%02x" % rgb

    def _update_stats(self):
        self.score_label.config(text=f"Score: {self.score}")
        self.moves_label.config(text=f"Moves: {self.moves}")
        minutes, seconds = divmod(int(self.remaining), 60)
        self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    MazeQuest().run()
