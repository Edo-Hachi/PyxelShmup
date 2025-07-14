import pyxel
import Common
import Config
from SpriteManager import SprList

class Bullet:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = Config.BULLET_SPEED
        self.active = True
        
        # Collision box
        self.col_x, self.col_y, self.col_w, self.col_h = Config.BULLET_COLLISION_BOX

    def update(self):
        self.y -= self.speed
        
        # Screen boundary check
        if self.y < -self.h:
            self.active = False

    def draw(self):
        pyxel.blt(self.x, self.y, Config.TILE_BANK0, 
                  SprList["BULLET01"].x, SprList["BULLET01"].y, 
                  self.w, self.h, pyxel.COLOR_BLACK)
        
        # Collision Box
        if Config.DEBUG:
            pyxel.rectb(self.x + self.col_x, self.y + self.col_y, 
                       self.col_w, self.col_h, pyxel.COLOR_GREEN)