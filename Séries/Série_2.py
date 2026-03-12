import math

class Disque:
    r: int
    c: tuple[int, int]

    def __init__(self, r: int, c: tuple[int, int]):
        self.r = r
        self.c = c

    def area(self) -> float:
        return math.pi * (self.r ** 2)

    def contains_point(self, p: tuple[int, int]) -> bool:
        if math.sqrt((p[0] - self.c[0])**2 + (p[1] - self.c[1])**2) <= self.r:
            return True
        else:
            return False