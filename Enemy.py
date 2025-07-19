# Enemy.py - Simplified Enemy Management
# シンプルで理解しやすい敵管理システム
# 座標管理の単純化とFormationIssue.mdの提案を反映

import pyxel
import Common
import Config
import GameState
from SpriteManager import sprite_manager
import random

# Enemy States - 最初は基本状態のみ
ENEMY_STATE_NORMAL = 0          # 通常の隊列移動

class Enemy:
    """シンプルな敵クラス - 基本的な隊列移動のみ"""
    
    # Constants
    MOVE_SPEED = 0.5                    # 隊列移動速度
    COLLISION_BOX = (1, 1, 6, 6)       # 当たり判定ボックス
    
    def __init__(self, x: float, y: float, sprite_num: int = 1, w: int = 8, h: int = 8, life: int = 1, score: int = 10):
        """
        シンプルな敵の初期化
        座標管理をformation_x/y + x/yの2つのみに単純化
        """
        # 隊列内での位置（理論位置）
        self.formation_x = float(x)     # 隊列内X座標
        self.formation_y = float(y)     # 隊列内Y座標
        
        # 実際の表示位置
        self.x = float(x)               # 表示X座標  
        self.y = float(y)               # 表示Y座標
        
        # スプライト設定
        self.w = w                      # スプライト幅
        self.h = h                      # スプライト高さ
        self.sprite_num = sprite_num    # 敵種類（1-5）
        
        # 当たり判定
        self.col_x = self.COLLISION_BOX[0]
        self.col_y = self.COLLISION_BOX[1] 
        self.col_w = self.COLLISION_BOX[2]
        self.col_h = self.COLLISION_BOX[3]
        
        # ゲーム属性
        self.life = life
        self.score = score
        self.active = True
        self.flash = 0                  # ヒット時の点滅
        
        # 状態管理
        self.state = ENEMY_STATE_NORMAL
        
        # JSON駆動アニメーション
        self.animation_speed = self._get_animation_speed()

    def update(self):
        """
        敵の更新処理
        隊列移動はmain.pyで一括処理される
        """
        if self.state == ENEMY_STATE_NORMAL:
            self._update_normal()
    
    def _update_normal(self):
        """通常状態の更新処理 - 隊列位置と表示位置を同期"""
        self.x = self.formation_x
        self.y = self.formation_y
    
    def update_formation_position(self, move_x: float, move_y: float = 0):
        """
        隊列位置の更新（main.pyから呼び出される）
        隊列移動の一元化
        """
        self.formation_x += move_x
        self.formation_y += move_y
    
    def is_in_formation(self) -> bool:
        """隊列にいるかどうかの判定"""
        return self.state == ENEMY_STATE_NORMAL
    
    def get_left_edge(self) -> float:
        """左端座標を取得"""
        return self.formation_x
    
    def get_right_edge(self) -> float:
        """右端座標を取得"""
        return self.formation_x + self.w
    
    def on_hit(self, bullet):
        """弾との衝突処理"""
        bullet.active = False
        self.life -= 1
        
        if self.life <= 0:
            self.active = False
            GameState.Score += self.score
            pyxel.play(0, 1)  # 破壊音
            # 爆発エフェクト
            if hasattr(Common, 'explode_manager'):
                from ExplodeManager import ExpType
                Common.explode_manager.spawn_explosion(self.x + 4, self.y + 4, 20, ExpType.RECT)
        else:
            self.flash = 6  # ヒット点滅
            pyxel.play(0, 2)  # ヒット音
            # 小さな爆発エフェクト
            if hasattr(Common, 'explode_manager'):
                from ExplodeManager import ExpType
                Common.explode_manager.spawn_explosion(self.x + 4, self.y + 4, 5, ExpType.DOT_REFRECT)
    
    def draw(self):
        """敵の描画処理"""
        # ヒット時の点滅処理
        if self.flash > 0:
            for i in range(1, 15):
                pyxel.pal(i, pyxel.COLOR_WHITE)
        
        self.flash = max(0, self.flash - 1)
        
        # JSON駆動のアニメーション
        anim_frame = self._get_animation_frame(pyxel.frame_count)
        sprite_idx = self._get_enemy_sprite(anim_frame)
        
        # スプライト描画
        pyxel.blt(
            int(self.x),
            int(self.y),
            Config.TILE_BANK0,
            sprite_idx.x,
            sprite_idx.y,
            self.w,
            self.h,
            pyxel.COLOR_BLACK,
        )
        
        pyxel.pal()  # パレットリセット
        
        # デバッグ用当たり判定表示
        if Config.DEBUG:
            pyxel.rectb(
                int(self.x + self.col_x), 
                int(self.y + self.col_y), 
                self.col_w, 
                self.col_h, 
                pyxel.COLOR_RED
            )

    def _get_animation_speed(self) -> int:
        """JSONからアニメーション速度を取得"""
        enemy_name = f"ENEMY{self.sprite_num:02d}"
        anim_spd = sprite_manager.get_sprite_metadata(enemy_name, "ANIM_SPD", "10")
        try:
            return int(anim_spd)
        except (ValueError, TypeError):
            return 10  # デフォルト値
    
    def _get_animation_frame(self, frame_count: int) -> int:
        """アニメーションフレーム計算"""
        return frame_count // self.animation_speed % 4  # 4フレーム循環
    
    def _get_enemy_sprite(self, anim_frame: int):
        """JSON駆動のスプライト取得"""
        enemy_name = f"ENEMY{self.sprite_num:02d}"
        return sprite_manager.get_sprite_by_name_and_field(enemy_name, "FRAME_NUM", str(anim_frame % 4))


class FormationManager:
    """
    隊列移動の一元管理クラス
    FormationIssue.mdの提案を実装
    """
    
    MOVE_SPEED = 0.7        # 隊列移動速度（少し高速化）
    MOVE_THRESHOLD = 1.0    # 移動閾値
    
    def __init__(self):
        self.move_direction = 1         # 1=右, -1=左
        self.accumulated_movement = 0.0  # 累積移動量
    
    def update(self, enemy_list):
        """
        隊列移動の更新処理
        main.pyから呼び出される
        """
        # アクティブで隊列にいる敵のみを対象
        formation_enemies = [e for e in enemy_list if e.active and e.is_in_formation()]
        
        if not formation_enemies:
            return
        
        # 累積移動量を更新
        self.accumulated_movement += self.MOVE_SPEED * self.move_direction
        
        # 閾値を超えたら実際に移動
        if abs(self.accumulated_movement) >= self.MOVE_THRESHOLD:
            move_amount = int(self.accumulated_movement)
            self.accumulated_movement -= move_amount
            
            # 方向転換チェック（移動前に実行）
            self._check_direction_change(formation_enemies)
            
            # デバッグ出力（移動時のみ）
            if Config.DEBUG:
                leftmost = min(e.get_left_edge() for e in formation_enemies)
                rightmost = max(e.get_right_edge() for e in formation_enemies)
                print(f"[FormationManager] Moving {move_amount}px, direction={self.move_direction}, enemies={len(formation_enemies)}, range=[{leftmost:.1f}-{rightmost:.1f}]")
            
            # 全ての隊列敵の位置を一括更新
            for enemy in formation_enemies:
                enemy.update_formation_position(move_amount)
    
    def _check_direction_change(self, formation_enemies):
        """端の敵の位置を監視して方向転換"""
        if not formation_enemies:
            return
        
        # 隊列の端点を取得
        leftmost_x = min(e.get_left_edge() for e in formation_enemies)
        rightmost_x = max(e.get_right_edge() for e in formation_enemies)
        
        # 方向転換判定（少し余裕を持たせる）
        old_direction = self.move_direction
        MARGIN = 2  # 画面端から2ピクセル手前で方向転換
        if self.move_direction == 1 and rightmost_x >= Config.WIN_WIDTH - MARGIN:
            self.move_direction = -1  # 左へ
        elif self.move_direction == -1 and leftmost_x <= MARGIN:
            self.move_direction = 1   # 右へ
        
        # 方向転換のデバッグ出力
        if Config.DEBUG and old_direction != self.move_direction:
            print(f"[FormationManager] Direction changed: {old_direction} -> {self.move_direction}, leftmost={leftmost_x:.1f}, rightmost={rightmost_x:.1f}")


# グローバルな隊列管理インスタンス
formation_manager = FormationManager()