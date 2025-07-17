import pyxel
import Common
import Config
import GameState
from SpriteManager import sprite_manager

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
        
        # アニメーション設定をJSONから取得
        self.animation_speed = self._get_animation_speed()

    def update(self):
        self.y -= self.speed  #テスト 1/110の速度で
        
        # Screen boundary check
        if self.y < -self.h:
            self.active = False

    def draw(self):
        # JSON駆動のアニメーション付き弾丸スプライト取得
        anim_frame = self._get_animation_frame(GameState.GameTimer)
        bullet_sprite = self._get_bullet_sprite(anim_frame)
        
        pyxel.blt(self.x, self.y, Config.TILE_BANK0, 
                  bullet_sprite.x, bullet_sprite.y, 
                  self.w, self.h, pyxel.COLOR_BLACK)
        
        # Collision Box
        if Config.DEBUG:
            pyxel.rectb(self.x + self.col_x, self.y + self.col_y, 
                       self.col_w, self.col_h, pyxel.COLOR_GREEN)
    
    def _get_animation_speed(self):
        """JSONからアニメーション速度を取得する"""
        anim_spd = sprite_manager.get_sprite_metadata("PBULLET", "ANIM_SPD", "3")
        try:
            return int(anim_spd)
        except (ValueError, TypeError):
            return 3
    
    def _get_animation_frame(self, game_timer):
        """ゲームタイマーに基づいてアニメーションフレームを計算する"""
        cycle_position = game_timer % (self.animation_speed * 2)
        return 0 if cycle_position < self.animation_speed else 1
    
    def _get_bullet_sprite(self, frame_number):
        """弾丸のスプライトを取得する"""
        return sprite_manager.get_sprite_by_name_and_field("PBULLET", "FRAME_NUM", str(frame_number % 2))