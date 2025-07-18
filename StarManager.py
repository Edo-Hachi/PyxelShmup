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
    # Star Constants
    COUNT = 100
    SPEED = 0.5
    MIN_SPEED = 0.1
    MAX_SPEED = 3.0
    
    def __init__(self, count=None):
        if count is None:
            count = self.COUNT
        self.stars = [
            Star(
                random.randint(0, Config.WIN_WIDTH - 1),
                random.randint(0, Config.WIN_HEIGHT - 1),
                random.randint(2, 15),  #Color
                #random.randint(1, 3)   #Speed  
                random.uniform(self.MIN_SPEED, self.MAX_SPEED) #Speed
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
