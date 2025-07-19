# Enemy.py - Simplified Enemy Management
# シンプルで理解しやすい敵管理システム
# 座標管理の単純化とFormationIssue.mdの提案を反映

import pyxel
import Common
import Config
import GameState
from SpriteManager import sprite_manager
from EntryPatterns import EntryPatternFactory
from EnemyBullet import EnemyBullet
import random
import math

# Enemy States - 登場シーケンス対応
ENEMY_STATE_ENTRY_SEQUENCE = -1     # 登場シーケンス中（左から水平移動等）
ENEMY_STATE_MOVING_TO_HOME = -2     # ホームポジション移動中
ENEMY_STATE_HOME_REACHED = -3       # ホームポジション到達・待機中
ENEMY_STATE_NORMAL = 0              # 通常の隊列移動

class Enemy:
    """シンプルな敵クラス - 基本的な隊列移動のみ"""
    
    # Constants
    MOVE_SPEED = 0.5                    # 隊列移動速度
    COLLISION_BOX = (1, 1, 6, 6)       # 当たり判定ボックス
    
    # Shooting Constants
    SHOOT_INTERVAL = 60                 # 射撃間隔（1秒）
    BASE_SHOOT_CHANCE = 0.10           # 基本射撃確率（10%）
    MAX_SHOOT_CHANCE = 0.30            # 最大射撃確率（30%）
    
    def __init__(self, x: float, y: float, sprite_num: int = 1, w: int = 8, h: int = 8, life: int = 1, score: int = 10, entry_pattern: str = None, entry_y: float = None, wave_id: int = -1, enemy_index: int = -1, entry_pattern_id: int = None):
        """
        敵の初期化 - 登場シーケンス対応（EntryPattern統合版）
        座標管理をformation_x/y + x/yの2つのみに単純化
        """
        # 隊列内での位置（理論位置・最終目標位置）
        self.formation_x = float(x)     # 隊列内X座標
        self.formation_y = float(y)     # 隊列内Y座標
        
        # EntryPatternシステム統合
        self.entry_pattern_obj = EntryPatternFactory.create(entry_pattern_id) if entry_pattern_id else None
        self.entry_pattern_str = entry_pattern  # 従来の文字列パターン
        self.entry_timer = 0
        
        # 実際の表示位置の初期化
        if self.entry_pattern_obj:
            # EntryPatternを使用する場合
            init_x, init_y = EntryPatternFactory.get_initial_position(entry_pattern_id)
            self.x = float(init_x)
            self.y = float(init_y)
            self.state = ENEMY_STATE_ENTRY_SEQUENCE
            if Config.DEBUG:
                print(f"Enemy created with EntryPattern {entry_pattern_id}: init=({init_x},{init_y}), target=({x},{y})")
        elif entry_pattern == "left_horizontal":
            # 左から水平移動パターン（従来）
            self.x = -16.0
            self.entry_y = entry_y if entry_y is not None else 64
            self.y = float(self.entry_y)
            self.state = ENEMY_STATE_ENTRY_SEQUENCE
            if Config.DEBUG:
                print(f"Left enemy created: entry_y={self.entry_y}, target_y={self.formation_y}")
        elif entry_pattern == "right_horizontal":
            # 右から水平移動パターン（従来）
            self.x = Config.WIN_WIDTH + 8.0
            self.entry_y = entry_y if entry_y is not None else 64
            self.y = float(self.entry_y)
            self.state = ENEMY_STATE_ENTRY_SEQUENCE
            if Config.DEBUG:
                print(f"Right enemy created: entry_y={self.entry_y}, target_y={self.formation_y}")
        else:
            # デフォルトは即座に隊列位置
            self.x = float(x)
            self.y = float(y)
        
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
        
        # 状態管理 - 登場シーケンス対応
        if entry_pattern in ["left_horizontal", "right_horizontal"]:
            self.state = ENEMY_STATE_ENTRY_SEQUENCE
        else:
            self.state = ENEMY_STATE_NORMAL
        
        # 登場パターン情報
        self.entry_pattern = entry_pattern
        
        # デバッグ用識別情報
        self.wave_id = wave_id              # ウェーブID (0-3)
        self.enemy_index = enemy_index      # ウェーブ内での順番 (0-9)
        self.enemy_id = f"W{wave_id}E{enemy_index:02d}"  # 一意なID (例: W0E00, W1E09)
        
        # 移動・到達判定用の定数
        self.ENTRY_MOVE_SPEED = 1.5         # 登場時の移動速度
        self.HOME_MOVE_SPEED = 2.0          # ホームポジション移動速度  
        self.HOME_PROXIMITY_THRESHOLD = 4.0 # ホームポジション到達判定の閾値
        
        # JSON駆動アニメーション
        self.animation_speed = self._get_animation_speed()
        
        # 射撃システム
        self.shoot_timer = random.randint(0, self.SHOOT_INTERVAL)  # 射撃タイマー（ランダム初期値）
        
        # 初期状態をログ出力
        if Config.DEBUG and (self.enemy_index == 0 or self.enemy_index == 9):  # 最初と最後の敵のみ
            print(f"[{self.enemy_id}] Created: state={self.state}, pattern={self.entry_pattern_str}, entry_y={getattr(self, 'entry_y', 'N/A')}")

    def _log_state_change(self, old_state: int, new_state: int, reason: str = ""):
        """状態変更をログ出力（最初と最後の敵のみ）"""
        if Config.DEBUG and (self.enemy_index == 0 or self.enemy_index == 9):
            state_names = {
                -1: "ENTRY_SEQUENCE",
                -2: "MOVING_TO_HOME", 
                -3: "HOME_REACHED",
                0: "NORMAL"
            }
            old_name = state_names.get(old_state, f"UNKNOWN({old_state})")
            new_name = state_names.get(new_state, f"UNKNOWN({new_state})")
            reason_str = f" ({reason})" if reason else ""
            print(f"[{self.enemy_id}] State: {old_name} -> {new_name}{reason_str}")

    def update(self):
        """
        敵の更新処理 - 登場シーケンス対応
        隊列移動はmain.pyで一括処理される
        """
        if self.state == ENEMY_STATE_ENTRY_SEQUENCE:
            self._update_entry_sequence()
        elif self.state == ENEMY_STATE_MOVING_TO_HOME:
            self._update_moving_to_home()
        elif self.state == ENEMY_STATE_HOME_REACHED:
            self._update_home_reached()
        elif self.state == ENEMY_STATE_NORMAL:
            self._update_normal()
        
        # 射撃処理（隊列移動中のみ）
        if self.state == ENEMY_STATE_NORMAL:
            self._update_shooting()
    
    def _update_entry_sequence(self):
        """登場シーケンス処理 - EntryPattern統合版"""
        if self.entry_pattern_obj:
            # EntryPatternを使用
            formation_reached = self.entry_pattern_obj.update(self)
            if formation_reached:
                # EntryPatternが完了してホームポジションに到達
                old_state = self.state
                self.state = ENEMY_STATE_HOME_REACHED
                self._log_state_change(old_state, self.state, "EntryPattern completed")
            elif hasattr(self.entry_pattern_obj, 'moving_to_formation') and self.entry_pattern_obj.moving_to_formation:
                # EntryPatternがホームポジション移動中
                old_state = self.state
                self.state = ENEMY_STATE_MOVING_TO_HOME
                self._log_state_change(old_state, self.state, "EntryPattern moving to formation")
        else:
            # 従来の水平移動パターン
            screen_center_x = Config.WIN_WIDTH // 2
            
            if self.entry_pattern_str == "left_horizontal":
                # 画面中央（64px）まで右に移動
                if self.x < screen_center_x:
                    self.x += self.ENTRY_MOVE_SPEED
                else:
                    old_state = self.state
                    self.state = ENEMY_STATE_MOVING_TO_HOME
                    self._log_state_change(old_state, self.state, "reached center from left")
            elif self.entry_pattern_str == "right_horizontal":
                # 画面中央（64px）まで左に移動
                if self.x > screen_center_x:
                    self.x -= self.ENTRY_MOVE_SPEED
                else:
                    old_state = self.state
                    self.state = ENEMY_STATE_MOVING_TO_HOME
                    self._log_state_change(old_state, self.state, "reached center from right")
    
    def _update_moving_to_home(self):
        """ホームポジション移動処理"""
        # 目標位置への移動
        target_x = self.formation_x
        target_y = self.formation_y
        
        # X方向の移動
        x_diff = target_x - self.x
        if abs(x_diff) > 1:
            self.x += math.copysign(min(abs(x_diff), self.HOME_MOVE_SPEED), x_diff)
        else:
            self.x = target_x
        
        # Y方向の移動
        y_diff = target_y - self.y
        if abs(y_diff) > 1:
            self.y += math.copysign(min(abs(y_diff), self.HOME_MOVE_SPEED), y_diff)
        else:
            self.y = target_y
        
        # 到達判定
        distance_to_home = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
        if distance_to_home <= self.HOME_PROXIMITY_THRESHOLD:
            self.x = target_x
            self.y = target_y
            old_state = self.state
            self.state = ENEMY_STATE_HOME_REACHED
            self._log_state_change(old_state, self.state, f"reached home (distance={distance_to_home:.1f})")
    
    def _update_home_reached(self):
        """ホームポジション到達・待機状態"""
        # ホームポジションで待機（隊列移動は別処理）
        self.x = self.formation_x
        self.y = self.formation_y
    
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
        """隊列にいるかどうかの判定 - 登場シーケンス対応"""
        return self.state == ENEMY_STATE_NORMAL
    
    def is_ready_for_formation_movement(self) -> bool:
        """隊列移動準備完了かどうかの判定"""
        return self.state in [ENEMY_STATE_HOME_REACHED, ENEMY_STATE_NORMAL]
    
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
    
    def _update_shooting(self):
        """
        射撃処理 - 隊列移動中の敵機射撃システム
        EnemyOld.pyの射撃ロジックを移植
        """
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            # 残りの敵の数を取得
            remaining_enemies = len([e for e in Common.enemy_list if e.active])
            if remaining_enemies > 0:
                # 敵の数が減るほど射撃確率が上がる
                shoot_chance = min(
                    self.BASE_SHOOT_CHANCE + (self.BASE_SHOOT_CHANCE * (40 - remaining_enemies) / 40),
                    self.MAX_SHOOT_CHANCE
                )
                
                if random.random() < shoot_chance:
                    # 敵弾を発射（敵の中心から）
                    bullet_x = self.x + 4
                    bullet_y = self.y + 8
                    Common.enemy_bullet_list.append(EnemyBullet(bullet_x, bullet_y))
                    
                    if Config.DEBUG:
                        print(f"[{self.enemy_id}] Shot fired! Chance: {shoot_chance:.2f}, Remaining: {remaining_enemies}")
            
            # 射撃タイマーをリセット
            self.shoot_timer = self.SHOOT_INTERVAL


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