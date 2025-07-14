import random
import pyxel
import Config
from dataclasses import dataclass

@dataclass
class Star:
    x: int
    y: int
    col: int
    speed: float

class StarManager:
    def __init__(self, count=100):
        self.stars = [
            Star(
                random.randint(0, Config.WIN_WIDTH - 1),
                random.randint(0, Config.WIN_HEIGHT - 1),
                random.randint(2, 15),  #Color
                #random.randint(1, 3)   #Speed  
                random.uniform(0.1, 3.0) #Speed
            )
            for _ in range(count)
        ]

    def update(self):
        for star in self.stars:
            star.y += star.speed
            if star.y >= Config.WIN_HEIGHT:
                star.x = random.randint(0, Config.WIN_WIDTH - 1)
                star.y = -10
                #star.col = random.randint(0, 15)
                #star.speed = random.randint(1, 10)

    def draw(self):
        for star in self.stars:
            pyxel.pset(star.x, star.y, star.col)
