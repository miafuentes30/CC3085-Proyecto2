"""
Visualisacion del laberinto con matplotlib.
Uso: python visualize.py <ruta_laberinto>
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from maze import load_maze, find_start_end, bfs, dfs, greedy, astar
from maze import heuristic_manhattan, heuristic_euclidean


def maze_to_image(maze):
    rows, cols = len(maze), len(maze[0])
    img = np.zeros((rows, cols, 3), dtype=np.float32)
    for r in range(rows):
        for c in range(cols):
            v = maze[r][c]
            if v == 1:
                img[r, c] = [0.1, 0.1, 0.18]
            elif v == 2:
                img[r, c] = [0.0, 0.83, 0.67]
            elif v == 3:
                img[r, c] = [1.0, 0.42, 0.42]
            else:
                img[r, c] = [0.94, 0.94, 0.94]
    return img


def draw_solution(maze, result, ax, title=""):
    img = maze_to_image(maze)
    for (r, c) in result.get("visited", set()):
        if maze[r][c] not in (1, 2, 3):
            img[r, c] = [0.18, 0.29, 0.48]
    for (r, c) in result.get("path", []):
        if maze[r][c] not in (2, 3):
            img[r, c] = [1.0, 0.85, 0.0]
    ax.imshow(img, interpolation="nearest")
    ax.set_title(
        f"{title}\nnodos: {result['nodes_explored']} | "
        f"largo: {result['path_length']} | "
        f"tiempo: {result['time']*1000:.2f}ms",
        fontsize=9, pad=4
    )
    ax.axis("off")


def visualize_all(maze_path: str):
    maze = load_maze(maze_path)
    start, end = find_start_end(maze)
    print(f"Laberinto: {len(maze)}x{len(maze[0])} | inicio: {start} | fin: {end}")

    algorithms = [
        bfs(maze, start, end),
        dfs(maze, start, end),
        greedy(maze, start, end, heuristic_manhattan),
        greedy(maze, start, end, heuristic_euclidean),
        astar(maze, start, end, heuristic_manhattan),
        astar(maze, start, end, heuristic_euclidean),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.patch.set_facecolor("#0d0d1a")
    fig.suptitle("Maze Solver - comp de algoritmos",
                 color="white", fontsize=14, fontweight="bold", y=0.98)

    for ax, result in zip(axes.flat, algorithms):
        draw_solution(maze, result, ax, result["algorithm"])

    legend_elements = [
        mpatches.Patch(color=[0.1, 0.1, 0.18], label="Pared"),
        mpatches.Patch(color=[0.94, 0.94, 0.94], label="Camino libre"),
        mpatches.Patch(color=[0.18, 0.29, 0.48], label="Nodos explorados"),
        mpatches.Patch(color=[1.0, 0.85, 0.0], label="Solución"),
        mpatches.Patch(color=[0.0, 0.83, 0.67], label="Inicio"),
        mpatches.Patch(color=[1.0, 0.42, 0.42], label="Salida"),
    ]
    fig.legend(handles=legend_elements, loc="lower center",
               ncol=6, framealpha=0.3, labelcolor="white",
               facecolor="#1a1a2e", edgecolor="none", fontsize=8,
               bbox_to_anchor=(0.5, 0.01))

    plt.tight_layout(rect=[0, 0.05, 1, 0.96])

    # guarda en la misma carpeta del script
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "visualization.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0d0d1a")
    print(f"imagen guardada en: {out_path}")
    return algorithms


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "test_maze.txt"
    visualize_all(path)