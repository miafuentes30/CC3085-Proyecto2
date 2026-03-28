"""
Solver de laberintos.
BFS, DFS, Greedy y A* con heuristicas.
"""

import heapq
import time
from collections import deque


def load_maze(filepath: str) -> list[list[int]]:
    """Carga un .txt y valida lo basico."""
    maze = []
    with open(filepath, 'r') as f:
        for line_no, line in enumerate(f, start=1):
            raw = line.strip()
            if not raw:
                continue
            invalid_chars = [ch for ch in raw if ch not in '0123']
            if invalid_chars:
                raise ValueError(
                    f"caracter raro en linea {line_no}: {invalid_chars[0]!r}. "
                    "usa solo 0, 1, 2 y 3."
                )
            row = [int(c) for c in raw]
            if row:
                maze.append(row)

    if not maze:
        raise ValueError("archivo vacio o sin filas validas.")

    expected_cols = len(maze[0])
    for i, row in enumerate(maze, start=1):
        if len(row) != expected_cols:
            raise ValueError(
                f"fila dispareja en linea {i}: esperadas {expected_cols}, "
                f"salieron {len(row)}."
            )

    return maze


def find_start_end(maze: list[list[int]]) -> tuple[tuple, tuple]:
    """Busca inicio (2) y salida (3)."""
    start = end = None
    for r, row in enumerate(maze):
        for c, val in enumerate(row):
            if val == 2:
                start = (r, c)
            elif val == 3:
                end = (r, c)
    return start, end


def get_neighbors(maze: list[list[int]], pos: tuple) -> list[tuple]:
    """Vecinos validos: arriba, der, abajo, izq."""
    rows, cols = len(maze), len(maze[0])
    r, c = pos
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # U, R, D, L
    neighbors = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != 1:
            neighbors.append((nr, nc))
    return neighbors


def reconstruct_path(parent: dict, end: tuple) -> list[tuple]:
    """Arma el camino desde el final."""
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = parent.get(node)
    return list(reversed(path))


# bfs
def bfs(maze: list[list[int]], start: tuple, end: tuple) -> dict:
    """Busqueda en anchura."""
    t0 = time.perf_counter()
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    nodes_explored = 0

    while queue:
        current = queue.popleft()
        nodes_explored += 1
        if current == end:
            break
        for neighbor in get_neighbors(maze, current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    elapsed = time.perf_counter() - t0
    path = reconstruct_path(parent, end) if end in parent else []
    return {
        "algorithm": "BFS",
        "path": path,
        "path_length": len(path),
        "nodes_explored": nodes_explored,
        "time": elapsed,
        "visited": visited,
    }


# dfs
def dfs(maze: list[list[int]], start: tuple, end: tuple) -> dict:
    """Busqueda en prof (iterativo)."""
    t0 = time.perf_counter()
    stack = [start]
    visited = {start}
    parent = {start: None}
    nodes_explored = 0

    while stack:
        current = stack.pop()
        nodes_explored += 1
        if current == end:
            break
        for neighbor in reversed(get_neighbors(maze, current)):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

    elapsed = time.perf_counter() - t0
    path = reconstruct_path(parent, end) if end in parent else []
    return {
        "algorithm": "DFS",
        "path": path,
        "path_length": len(path),
        "nodes_explored": nodes_explored,
        "time": elapsed,
        "visited": visited,
    }


# heuristicas
def heuristic_manhattan(a: tuple, b: tuple) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristic_euclidean(a: tuple, b: tuple) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


# greedy
def greedy(maze: list[list[int]], start: tuple, end: tuple,
           heuristic=heuristic_manhattan) -> dict:
    """Greedy best-first."""
    t0 = time.perf_counter()
    h_name = "Manhattan" if heuristic == heuristic_manhattan else "Euclidiana"

    heap = [(heuristic(start, end), start)]
    visited = {start}
    parent = {start: None}
    nodes_explored = 0

    while heap:
        _, current = heapq.heappop(heap)
        nodes_explored += 1
        if current == end:
            break
        for neighbor in get_neighbors(maze, current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                heapq.heappush(heap, (heuristic(neighbor, end), neighbor))

    elapsed = time.perf_counter() - t0
    path = reconstruct_path(parent, end) if end in parent else []
    return {
        "algorithm": f"Greedy ({h_name})",
        "path": path,
        "path_length": len(path),
        "nodes_explored": nodes_explored,
        "time": elapsed,
        "visited": visited,
    }


# a*
def astar(maze: list[list[int]], start: tuple, end: tuple,
          heuristic=heuristic_manhattan) -> dict:
    """A estrella."""
    t0 = time.perf_counter()
    h_name = "Manhattan" if heuristic == heuristic_manhattan else "Euclidiana"

    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    heap = [(f_score[start], 0, start)]  # (f, tie-break, node)
    visited = set()
    parent = {start: None}
    nodes_explored = 0
    counter = 0

    while heap:
        _, _, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1
        if current == end:
            break
        for neighbor in get_neighbors(maze, current):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent[neighbor] = current
                f = tentative_g + heuristic(neighbor, end)
                counter += 1
                heapq.heappush(heap, (f, counter, neighbor))

    elapsed = time.perf_counter() - t0
    path = reconstruct_path(parent, end) if end in parent else []
    return {
        "algorithm": f"A* ({h_name})",
        "path": path,
        "path_length": len(path),
        "nodes_explored": nodes_explored,
        "time": elapsed,
        "visited": visited,
    }