import timeit
import matplotlib.pyplot as plt
import arcade
from map import map_from_string
from game_view import GameView

window = arcade.Window( 1, 1, "Benchmark", visible=False)
def create_map(size: int) -> str:
    """crée un fichier de map de taille size**2"""
    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            # les bords buissons :
            if (
                x == 0
                or y == 0
                or x == size - 1
                or y == size - 1
            ):
                row.append("x")
            # le joueur :
            elif x == 1 and y == 1:
                row.append("P")
            # de l'herbe
            else:
                row.append(" ")

        rows.append("".join(row))

    return (
        f"width: {size}\n"
        f"height: {size}\n"
        "---\n"
        + "\n".join(rows)
        + "\n---\n"
    )


sizes = [10, 20, 50, 100, 150]

cells = []
times = []

NUMBER = 10

for size in sizes:
    print(f"Benchmark map {size}x{size}")
    text = create_map(size)
    def benchmark() -> None:
        #on lit la map avec map_from_string
        game_map = map_from_string(text)
        #on instancie gameview avec
        GameView(game_map)
    #on utilise timeit et benchmark pour connaître le temps total
    total_time = timeit.timeit(
        benchmark,
        number=NUMBER,
    )
    average_time = total_time / NUMBER
    cell_count = size * size
    cells.append(cell_count)
    times.append(average_time)
    print(
        f"{cell_count} cellules "
        f"-> {average_time:.6f} s"
    )

plt.plot(cells, times, marker="o")

plt.xlabel("Nombre de cellules")
plt.ylabel("Temps moyen de chargement (s)")

plt.title("Temps de chargement selon la taille de la map")

plt.grid(True)

plt.savefig("loading_benchmark.png")

plt.show()
