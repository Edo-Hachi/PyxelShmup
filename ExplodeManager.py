import pyxel
import random
from enum import Enum
import Config
import GameState


class ExpType(Enum):
    """Explosion particle type."""
    RECT = 0
    DOT = 1
    CIRCLE = 2
    DOT_REFRECT = 3

class Explode_CIRCLE:
    def __init__(self, x, y, r=10):
        self.x = x
        self.y = y
        self.r = random.randint(2, 5)
        self.dx = random.uniform(-1.5, 1.5)
        self.dy = random.uniform(-1.5, 1.5)
        self.life = random.randint(10, 25)   #弾の寿命大きいと長く飛び散ります
        self.col = random.randint(8, 15)

        #First Flash
        self.orgx = x
        self.orgy = y
        self.FirstFlash = 4

        self.FirstCircle = 1

        self.trail = []  # 残像履歴（最大10個とか）


    def update(self):
            self.x += self.dx
            self.y += self.dy

            #パーティクルを小さくしていく
            self.r -= 0.05

            self.life -= 1

            #爆発パーティクルの速度減衰
            self.dx *= 0.87
            self.dy *= 0.87

            self.trail.append((self.x, self.y, self.r))  # 現在位置を追加
            if len(self.trail) > 5 :
                self.trail.pop(0)  # 古い残像を削除（最大10個まで）



    def draw(self):

        #最初だけ白でフラッシュを表示
        if 0 < self.FirstFlash:
            #pyxel.rect(self.orgx-8, self.orgy-8, 16, 16, pyxel.COLOR_WHITE)
            pyxel.circ(self.orgx, self.orgy, int(8), pyxel.COLOR_WHITE)
            self.FirstFlash -= 1
        
        #ソニックブーム的な円
        if self.FirstCircle < 20:
            pyxel.circb(self.orgx, self.orgy, self.FirstCircle, pyxel.COLOR_WHITE)
            self.FirstCircle+=2

        _color = pyxel.COLOR_WHITE

        if self.life < 18:
            _color = pyxel.COLOR_YELLOW

        if self.life < 13:
            _color = pyxel.COLOR_ORANGE

        if self.life < 9:
            _color = pyxel.COLOR_BROWN

        if self.life < 5:
            _color = pyxel.COLOR_GRAY
        
        if self.life < 1:
            _color = pyxel.COLOR_NAVY
        
        if self.life > 0:
            pyxel.circ(int(self.x), int(self.y), int(self.r), _color)

        for i, (tx, ty, tr) in enumerate(self.trail):
            fade_color = pyxel.COLOR_YELLOW if i < 3 else pyxel.COLOR_ORANGE
            if i > 6:
                fade_color = pyxel.COLOR_BROWN
            pyxel.circ(int(tx), int(ty), int(tr * 0.7), fade_color)

    @property
    def is_alive(self):
        return self.life > 0

class Explode_RECT:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = random.randint(2, 7)
        self.h = random.randint(2, 6)   
        self.dx = random.uniform(-1.5, 1.5)
        self.dy = random.uniform(-1.5, 1.5)
        self.life = random.randint(10, 25)   #弾の寿命大きいと長く飛び散ります
        self.col = random.randint(8, 15)

        #First Flash
        self.orgx = x
        self.orgy = y
        self.FirstFlash = 4

        self.FirstCircle = 1


    def update(self):
            self.x += self.dx
            self.y += self.dy

            #パーティクルを小さくしていく
            self.w -= 0.05
            self.h -= 0.05  

            self.life -= 1

            #爆発パーティクルの速度減衰
            self.dx *= 0.87
            self.dy *= 0.87


    def draw(self):
        if self.life > 0:
            #最初だけ白でフラッシュを表示
            if 0 < self.FirstFlash:
                pyxel.rect(self.orgx-8, self.orgy-8, 16, 16, pyxel.COLOR_WHITE)
                self.FirstFlash -= 1

            #ソニックブーム的な円
            if self.FirstCircle < 20:
                pyxel.circb(self.orgx, self.orgy, self.FirstCircle, pyxel.COLOR_WHITE)
                self.FirstCircle+=2


            _color = pyxel.COLOR_WHITE

            if self.life < 18:
                _color = pyxel.COLOR_YELLOW

            if self.life < 13:
                _color = pyxel.COLOR_ORANGE

            if self.life < 9:
                _color = pyxel.COLOR_BROWN

            if self.life < 5:
                _color = pyxel.COLOR_GRAY
            
            if self.life < 1:
                _color = pyxel.COLOR_NAVY

            pyxel.rect(int(self.x), int(self.y), int(self.w), int(self.h), _color)
    @property
    def is_alive(self):
        return self.life > 0


class Explode_DOT:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-1.5, 1.5)
        self.dy = random.uniform(-1.5, 1.5)
        self.life = random.randint(5, 20)   #弾の寿命大きいと長く飛び散ります
        self.col = random.randint(8, 15)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

        #爆発パーティクルの速度減衰
        self.dx *= 0.90
        self.dy *= 0.90

    def draw(self):
        if self.life > 0:
            pyxel.pset(int(self.x), int(self.y), self.col)

    @property
    def is_alive(self):
        return self.life > 0

class Explode_DOT_REFRECT:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-1.5, 1.5)
        self.dy = random.uniform(0, 1)
        self.life = random.randint(10,25)   #弾の寿命大きいと長く飛び散ります
        self.col = pyxel.COLOR_WHITE #random.randint(8, 15)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

        #爆発パーティクルの速度減衰
        self.dx *= 0.95
        self.dy *= 0.90

    def draw(self):
        if self.life > 0:
            pyxel.pset(int(self.x), int(self.y), self.col)

    @property
    def is_alive(self):
        return self.life > 0

# class ExplodeManager:
class ExpMan:
    def __init__(self):
        self.explosions = []

    def spawn_explosion(self, x, y, cnt=20, exp_type=ExpType.CIRCLE):
        """Spawn explosion particles of specified type."""
        particle_cls = {
            ExpType.RECT: Explode_RECT,
            ExpType.DOT: Explode_DOT,
            ExpType.CIRCLE: Explode_CIRCLE,
            ExpType.DOT_REFRECT: Explode_DOT_REFRECT,
        }.get(exp_type, Explode_CIRCLE)

        for _ in range(cnt):
            self.explosions.append(particle_cls(x, y))

    def update(self):
        
        if GameState.StopTimer > 0:
            return
          
        for exp in self.explosions:
            exp.update()
        self.explosions = [exp for exp in self.explosions if exp.is_alive]

    def draw(self):
        for exp in self.explosions:
            exp.draw()
