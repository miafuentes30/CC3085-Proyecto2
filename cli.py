"""
CLI de texto para resolver laberintos.
Uso: python cli.py <ruta_laberinto>
"""

import sys
import random
from collections import deque
from maze import (load_maze, find_start_end, bfs, dfs, greedy, astar,
                  heuristic_manhattan, heuristic_euclidean)


def print_results(result: dict):
    algo = result["algorithm"]
    print(f"\n{'─'*38}")
    print(f"  {algo}")
    print(f"{'─'*38}")
    print(f"  nodos vistos : {result['nodes_explored']:,}")
    print(f"  largo camino : {result['path_length']:,}")
    print(f"  tiempo       : {result['time']*1000:.4f} ms")
    if result['path_length'] == 0:
        print("  no se encontro salida")


def run_all(maze, start, end, label=""):
    if label:
        print(f"\n{'═'*44}")
        print(f"  {label}")
        print(f"{'═'*44}")
    print(f"  inicio: {start}  ->  salida: {end}")

    results = [
        bfs(maze, start, end),
        dfs(maze, start, end),
        greedy(maze, start, end, heuristic_manhattan),
        greedy(maze, start, end, heuristic_euclidean),
        astar(maze, start, end, heuristic_manhattan),
        astar(maze, start, end, heuristic_euclidean),
    ]
    for r in results:
        print_results(r)
    return results


def print_branching_table(results: list[dict], title: str):
    print(f"\n{'═'*38}")
    print(f"  ramif est - {title}")
    print(f"{'═'*38}")
    print(f"  {'algoritmo':<30} {'bf':>8}")
    print(f"  {'─'*38}")
    for r in results:
        bf = compute_branching_factor(r)
        print(f"  {r['algorithm']:<30} {bf:>8.4f}")


def print_branching_summary(branching_samples: dict[str, list[float]]):
    print(f"\n{'═'*44}")
    print("  resumen bf (base + random)")
    print(f"{'═'*44}")
    print(f"  {'algoritmo':<30} {'prom':>10} {'min':>10} {'max':>10}")
    print(f"  {'─'*44}")
    for algorithm, values in branching_samples.items():
        if values:
            avg = sum(values) / len(values)
            print(f"  {algorithm:<30} {avg:>10.4f} {min(values):>10.4f} {max(values):>10.4f}")
        else:
            print(f"  {algorithm:<30} {'0.0000':>10} {'0.0000':>10} {'0.0000':>10}")


def find_reachable_cells(maze, start):
    """
    Saca todas las celdas alcansables desde 'start' con BFS.
    Asi los inicios random quedan conectados y no fallan tan feo.
    """
    rows, cols = len(maze), len(maze[0])
    visited = {start}
    queue = deque([start])
    reachable = []
    while queue:
        r, c = queue.popleft()
        reachable.append((r, c))
        for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if maze[nr][nc] != 1 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
    return reachable


def compute_branching_factor(result: dict) -> float:
    """
    Estimacion simple del factor de ramificacion:
    b^d = nodes_explored  ->  b = nodes_explored^(1/d)
    donde d es el largo del camino.
    """
    n = result["nodes_explored"]
    d = result["path_length"]
    if d <= 0 or n <= 0:
        return 0.0
    return n ** (1 / d)


def estimate_distance_to_goal(maze, start, end) -> int:
    base = bfs(maze, start, end)
    if base["path_length"] <= 0:
        return 0
    # Distancia en pasos, no en numero de nodos
    return base["path_length"] - 1


def analyze_maze(path: str):
    print(f"\nCargando: {path}")
    maze = load_maze(path)
    rows, cols = len(maze), len(maze[0])
    print(f"    tam: {rows} x {cols}")
    if rows != 128 or cols != 128:
        print("    aviso: no es 128x128, igual se corre")

    start, end = find_start_end(maze)
    if not start or not end:
        print("no encontre inicio (2) o salida (3)")
        return

    # caso base
    base_results = run_all(maze, start, end, "CASO BASE")
    print_branching_table(base_results, "Caso base")

    branching_samples = {}
    for r in base_results:
        branching_samples[r["algorithm"]] = [compute_branching_factor(r)]

    # inicios random (solo celdas alcansables)
    reachable = [
        cell for cell in find_reachable_cells(maze, start)
        if cell != start and cell != end and maze[cell[0]][cell[1]] == 0
    ]

    n_samples = min(3, len(reachable))
    random.seed(42)
    random_starts = random.sample(reachable, n_samples)

    print(f"\n{'═'*44}")
    print(f"  simulacion con {n_samples} inicios random")
    print("  (celdas conectadas al mapa)")
    print(f"{'═'*44}")

    for i, rand_start in enumerate(random_starts, 1):
        approx_dist = estimate_distance_to_goal(maze, rand_start, end)
        label = f"Inicio random #{i}: {rand_start} | dist aprox: {approx_dist}"
        random_results = run_all(maze, rand_start, end, label)
        print_branching_table(random_results, f"Inicio aleatorio #{i}")
        for r in random_results:
            branching_samples[r["algorithm"]].append(compute_branching_factor(r))

    print_branching_summary(branching_samples)
    print("\nanalisis listo\n")


def main():
    maze_paths = sys.argv[1:] if len(sys.argv) > 1 else ["test_maze.txt"]
    print(f"\nlaberintos: {len(maze_paths)}")
    for i, maze_path in enumerate(maze_paths, start=1):
        print(f" LABERINTO {i} de {len(maze_paths)}")
        print(f"{'-'*70}")
        try:
            analyze_maze(maze_path)
        except FileNotFoundError:
            print(f"no existe el archivo: {maze_path}")
        except ValueError as err:
            print(f"error de formato en '{maze_path}': {err}")


if __name__ == "__main__":
    main()