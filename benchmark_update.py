import timeit
import matplotlib.pyplot as plt
import arcade

from map import map_from_string
from game_view import GameView

window=arcade.Window(1,1,"Benchmark", visible=False)
MAP_SIZE=100
def create_map(slime_count: int)->str :
    rows= []
    current_slimes=0
    for y in range(MAP_SIZE):
        row = []
        for x in range(MAP_SIZE):
            # les bords buissons :
            if (
                x == 0
                or y == 0
                or x == MAP_SIZE - 1
                or y == MAP_SIZE - 1
            ):
                row.append("x")
            # le joueur :
            elif x == 1 and y == 1:
                row.append("P")
            #les slimes:
            elif current_slimes<slime_count:
                row.append("m")
                current_slimes+=1
            # de l'herbe
            else:
                row.append(" ")

        rows.append("".join(row))
    return (
    f"width: {MAP_SIZE}\n"
    f"height: {MAP_SIZE}\n"
    "---\n"
    + "\n".join(rows)
    + "\n---\n"
    )

def benchmark(view:GameView)->None:
    view.on_update(1/60)

SLIME_COUNTS=[1,5,10,20,50,100]
times=[]
NUMBER=100

for slime_count in SLIME_COUNTS:
    print(f"Benchmark avec {slime_count} slimes")
    text=create_map(slime_count)
    game_map=map_from_string(text)

    view = GameView(game_map)
    total_time=timeit.timeit(
        lambda :benchmark(view),
        number=NUMBER
    )
    average_time=total_time/NUMBER
    times.append(average_time)
    print(
        f"{slime_count} slimes"
        f"-> {average_time:.7f} s"
    )

plt.plot(SLIME_COUNTS, times, marker='o')
plt.xlabel("Nombre de slimes")
plt.ylabel("Temps moyen de on_update en (s)")
plt.title("Temps de on_update en fct du nbr de slimes")
plt.show()
