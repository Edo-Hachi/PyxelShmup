#型のチェックは適度にお願いします

import pyxel
import Common
import Config
import GameState
from SpriteManager import sprite_manager
import math
from ExplodeManager import ExpType

from Bullet import Bullet

ExtNames = ["EXT01", "EXT02", "EXT03", "EXT04"]
ExtMax = len(ExtNames)

# Use Config values instead of local constants

MuzlNames = ["MUZL01", "MUZL02", "MUZL03"] #0-2
MuzlStarIndex = 2

# Use Config values instead of local constants

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8

        self.col_x = 2  # Collision X
        self.col_y = 2  # Collision Y
        self.col_w = 4  # Collision Width
        self.col_h = 4

        self.speed = 1
        self.col_active = True
        self.ShotTimer = Config.PLAYER_SHOT_INTERVAL

        self.ExplodeCoolTimer = -1
        self.NowExploding = False

        self.SprName = "TOP"    #Drawing Sprite Name

        # エグゾーストアニメーション管理
        self.ExtIndex = 0
        self.ExtTimer = 0
        self.exhaust_duration = self._get_exhaust_animation_duration()

        self.MuzlFlash = -1  # Muzzle Flash List



    def update(self):
        
        if GameState.StopTimer > 0:
            return  
        
        #Exhaust Animation -------- JSON駆動の持続時間制御
        self.ExtTimer += 1
        
        if self.ExtTimer >= self.exhaust_duration:
            self.ExtTimer = 0
            self.ExtIndex += 1
            if self.ExtIndex >= ExtMax:
                self.ExtIndex = 0

        #Movement -----------
        self.SprName = "TOP"
        dx = 0  #direction
        dy = 0

        if pyxel.btn(pyxel.KEY_LEFT):
            dx -= 1
            self.SprName = "LEFT"

        if pyxel.btn(pyxel.KEY_RIGHT):
            dx += 1
            self.SprName = "RIGHT"

        if pyxel.btn(pyxel.KEY_UP):
            dy -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            dy += 1 

        # 斜め移動時の速度を正規化（1/√2 ≈ 0.707を掛けて対角線上の速度を調整）
        if dx != 0 and dy != 0:
            DIAGONAL_NORMALIZE = 0.707  # 1/√2 の近似値
            dx *= DIAGONAL_NORMALIZE
            dy *= DIAGONAL_NORMALIZE

        self.x += dx * self.speed
        self.y += dy * self.speed

        # 画面端での境界チェック
        self.x = max(0, min(self.x, Config.WIN_WIDTH - self.width))
        self.y = max(0, min(self.y, Config.WIN_HEIGHT - (self.height+8)))
        
        #弾の発射
        if pyxel.btn(pyxel.KEY_SPACE):
            if(self.ShotTimer <= 0):
                pyxel.play(Config.AUDIO_CHANNEL_PLAYER, 0)  # 効果音再生
                Common.player_bullet_list.append(Bullet(self.x-4, self.y-4, 8, 8)) # 弾の情報をリストに追加
                Common.player_bullet_list.append(Bullet(self.x+4, self.y-4, 8, 8)) # 弾の情報をリストに追加
                self.ShotTimer = Config.PLAYER_SHOT_INTERVAL  # 再発射までの時間をリセット

                self.MuzlFlash = MuzlStarIndex  # Muzzle Flash Animate Start

        
        self.ShotTimer -= 1  # 発射間隔のカウントダウン

        # クールタイムの更新
        if self.ExplodeCoolTimer > 0:
            self.ExplodeCoolTimer -= 1
            self.NowExploding = False

    
    def draw(self):
        # クールタイム中のみ点滅処理
        if self.ExplodeCoolTimer > 0:
            if math.sin(GameState.GameTimer/3) < 0:
                for n in range(1, 15):
                    pyxel.pal(n,pyxel.COLOR_YELLOW)
        else:
            pyxel.pal()  # クールタイム終了時はパレットをリセット

        #Player Ship - JSON駆動のスプライト取得
        player_sprite = self._get_player_sprite()
        pyxel.blt(self.x, self.y, Config.TILE_BANK0,
                player_sprite.x, player_sprite.y, self.width, self.height, pyxel.COLOR_BLACK)

        #デフォルトパレットに戻す
        pyxel.pal()
        
        #Exhaust - JSON駆動のエグゾーストスプライト取得
        exhaust_sprite = self._get_exhaust_sprite()
        pyxel.blt(self.x, self.y+8, Config.TILE_BANK0,
            exhaust_sprite.x, exhaust_sprite.y, self.width, self.height, pyxel.COLOR_BLACK)

        #Muzzle Flash - JSON駆動のスプライト取得
        if self.MuzlFlash >= 0:
            muzzle_sprite = self._get_muzzle_flash_sprite()
            pyxel.blt(self.x-4, self.y-6, Config.TILE_BANK0,
                      muzzle_sprite.x, muzzle_sprite.y, 8, 8, pyxel.COLOR_BLACK)
            pyxel.blt(self.x+4, self.y-6, Config.TILE_BANK0,
                      muzzle_sprite.x, muzzle_sprite.y, 8, 8, pyxel.COLOR_BLACK)

        self.MuzlFlash -= 1
        
        #弾描画
        for _bullet in Common.player_bullet_list:
            _bullet.draw()
       
        # Collision Box 
        if Config.DEBUG:
            pyxel.rectb(self.x + self.col_x, self.y + self.col_y, self.col_w, self.col_h, pyxel.COLOR_GREEN)

    def on_hit(self):
        """プレイヤーが敵または敵弾に当たった時の処理"""
        if self.ExplodeCoolTimer <= 0:  # クールタイム中でない場合のみ
            # 爆発エフェクト
            Common.explode_manager.spawn_explosion(
                self.x + 4, self.y + 4, 20, ExpType.CIRCLE
            )
            # クールタイム設定
            self.ExplodeCoolTimer = Config.PLAYER_EXPLODE_TIMER
            self.NowExploding = True
            # 画面効果
            GameState.ShakeTimer = Config.SHAKE_TIME
            GameState.StopTimer = Config.STOP_TIME
    
    def _get_player_sprite(self):
        """プレイヤーの現在のスプライトを取得する"""
        return sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", self.SprName)
    
    def _get_exhaust_sprite(self):
        """エグゾーストの現在のスプライトを取得する"""
        return sprite_manager.get_sprite_by_name_and_field("EXHST", "FRAME_NUM", str(self.ExtIndex))
    
    def _get_exhaust_animation_duration(self):
        """エグゾーストアニメーションの持続時間を取得する"""
        anim_spd = sprite_manager.get_sprite_metadata("EXHST", "ANIM_SPD", "1")
        try:
            return int(anim_spd)
        except (ValueError, TypeError):
            return 1
    
    def _get_muzzle_flash_sprite(self):
        """マズルフラッシュのスプライトを取得する"""
        return sprite_manager.get_sprite_by_name_and_field("MZLFLSH", "FRAME_NUM", str(self.MuzlFlash))
