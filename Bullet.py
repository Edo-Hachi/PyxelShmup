import pyxel
import Common
import Config
import GameState
from SpriteManager import SprList, sprite_manager, get_bullet_animation_frame

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
        self.y -= self.speed  #テスト 1/110の速度で
        
        # Screen boundary check
        if self.y < -self.h:
            self.active = False

    def draw(self):
        # JSON駆動のアニメーション付き弾丸スプライト取得
        anim_frame = get_bullet_animation_frame(GameState.GameTimer)  # JSONから持続時間取得
        bullet_sprite = sprite_manager.get_bullet_sprite(anim_frame)
        
        pyxel.blt(self.x, self.y, Config.TILE_BANK0, 
                  bullet_sprite.x, bullet_sprite.y, 
                  self.w, self.h, pyxel.COLOR_BLACK)
        
        # Collision Box
        if Config.DEBUG:
            pyxel.rectb(self.x + self.col_x, self.y + self.col_y, 
                       self.col_w, self.col_h, pyxel.COLOR_GREEN)