import pyxel
import Common
import Config
from SpriteManager import SprList

class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = Config.ENEMY_BULLET_SPEED
        self.active = True
        
        # Collision box
        self.col_x, self.col_y, self.col_w, self.col_h = Config.ENEMY_BULLET_COLLISION_BOX

    def update(self):
        self.y += self.speed
        
        # Screen boundary check
        if self.y > Config.WIN_HEIGHT:
            self.active = False

    def draw(self):
        pyxel.blt(self.x, self.y, Config.TILE_BANK0, 
                  SprList["ENEMY_BULLET"].x, SprList["ENEMY_BULLET"].y, 
                  8, 8, pyxel.COLOR_BLACK)
        
        # Collision Box
        if Config.DEBUG:
            pyxel.rectb(self.x + self.col_x, self.y + self.col_y, 
                       self.col_w, self.col_h, pyxel.COLOR_RED)