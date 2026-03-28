# CC3085-Proyecto2

Implementacion de BFS, DFS, Greedy y A* para resolver laberintos.

## Estructura del proyecto

```text
CC3085-Proyecto2/
├─ maze.py
├─ cli.py
├─ visualize.py
├─ test_maze.txt
├─ Laberinto1.txt
├─ Laberinto2.txt
└─ Laberinto3.txt
```

## Como ejecutar

### 1. Ejecutar por consola (CLI)

```bash
python cli.py test_maze.txt
```

Tambien podes pasar varios archivos:

```bash
python cli.py Laberinto1.txt Laberinto2.txt
```

### 2. Ejecutar visualizacion

```bash
python visualize.py test_maze.txt
```

Esto genera una imagen con los resultados de los algoritmos en la misma carpeta.

## Formato del laberinto

- `0`: camino libre
- `1`: pared
- `2`: inicio
- `3`: salida