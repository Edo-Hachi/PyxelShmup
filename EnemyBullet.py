import pyxel
import Common
import Config
from SpriteManager import sprite_manager

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
        # JSON駆動のスプライト取得
        bullet_sprite = self._get_enemy_bullet_sprite()
        
        pyxel.blt(self.x, self.y, Config.TILE_BANK0, 
                  bullet_sprite.x, bullet_sprite.y, 
                  8, 8, pyxel.COLOR_BLACK)
        
        # Collision Box
        if Config.DEBUG:
            pyxel.rectb(self.x + self.col_x, self.y + self.col_y, 
                       self.col_w, self.col_h, pyxel.COLOR_RED)
    
    def _get_enemy_bullet_sprite(self):
        """敵弾丸のスプライトを取得する"""
        return sprite_manager.get_sprite_by_name_and_field("ENMYBLT", "ACT_NAME", "UNDEF")