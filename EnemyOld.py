#ソースコードの中のコメントは日本語にしましょう
# #画面に出力する文字列は英語にしてください。pyxelは日本語フォントを表示できません
# CLAUDE.md を書き込むときは英語にしてください
# 変数の型は宣言してください

import pyxel
import Common
import Config
import GameState
from SpriteManager import sprite_manager
import random
import math
from ExplodeManager import ExpType
from EnemyBullet import EnemyBullet
from EntryPatterns import EntryPatternFactory

# Enemy States
ENEMY_STATE_ENTERING = -1
ENEMY_STATE_FORMATION_READY = -2
ENEMY_STATE_NORMAL = 0
ENEMY_STATE_PREPARE_ATTACK = 1
ENEMY_STATE_ATTACK = 2
ENEMY_STATE_RETURNING = 3
ENEMY_STATE_DESCENDING = 4
ENEMY_STATE_CONTINUOUS_ATTACK = 5

class Enemy:
    # Enemy Movement Constants
    MOVE_SPEED = 0.5
    MOVE_THRESHOLD = 1
    
    # Enemy Shooting Constants
    SHOOT_INTERVAL = 60
    BASE_SHOOT_CHANCE = 0.10
    MAX_SHOOT_CHANCE = 0.30
    ANIM_FRAME = 10
    COLLISION_BOX = (1, 1, 6, 6)  # x, y, w, h
    
    # Enemy Attack System Constants
    PREPARE_ATTACK_DURATION = 60
    PREPARE_SHAKE_AMPLITUDE_X = 1.0
    PREPARE_SHAKE_AMPLITUDE_Y = 1.2
    PREPARE_SHAKE_FREQUENCY_X = 0.2
    PREPARE_SHAKE_FREQUENCY_Y = 1.0
    
    ATTACK_MOVE_SPEED = 0.8
    ATTACK_SWAY_AMPLITUDE = 1.5
    ATTACK_SWAY_FREQUENCY = 0.08
    RETURN_DELAY = 180
    RETURN_DELAY_CONTINUOUS = 60
    DESCEND_SPEED = 1.5
    FORMATION_PROXIMITY = 8
    ATTACK_COOLDOWN = 300
    
    # Enemy AI Constants
    ATTACK_SELECTION_INTERVAL = 240
    ATTACK_CHANCE = 0.75
    def __init__(self, x, y, w=8, h=8, life=1, score=10, sprite_num=1, formation_pos=None, entry_pattern=None):
        self.base_x = x  # 初期X座標を保存
        self.base_y = y  # 初期Y座標を保存（隊列復帰用）
        self.x = x
        self.y = y
        self.w = w  # Sprite Width
        self.h = h  # Sprite Height

        self.col_x = self.COLLISION_BOX[0] #Collision Box
        self.col_y = self.COLLISION_BOX[1]
        self.col_w = self.COLLISION_BOX[2]
        self.col_h = self.COLLISION_BOX[3]

        self.Life = life
        self.Score = score

        self.flash = 0

        # Enemy sprite id (1-5)
        self.sprite_num = sprite_num
        
        # アニメーション設定をJSONから取得
        self.animation_speed = self._get_animation_speed()

        self.active = True
        self.shoot_timer = random.randint(0, self.SHOOT_INTERVAL)  # 発射タイマー
        
        # 攻撃ステート関連のプロパティ
        self.state = ENEMY_STATE_NORMAL  # 敵の現在の状態
        self.attack_timer = 0           # 攻撃関連のタイマー
        self.sway_phase = random.uniform(0, 6.28)  # 左右の揺れ位相（ランダム初期値）
        self.shake_phase_x = random.uniform(0, 6.28)  # 左右身震い位相（ランダム初期値）
        self.shake_phase_y = random.uniform(0, 6.28)  # 上下身震い位相（ランダム初期値）
        self.exit_x = x  # 画面外に出た時のX座標を記録
        
        # 隊列内位置追跡用（攻撃中でも隊列移動を追跡）
        self.formation_x = x  # 隊列内での現在のX位置
        self.formation_y = y  # 隊列内での現在のY位置
        
        # 攻撃クールダウン管理
        self.attack_cooldown_timer = 0  # 攻撃クールダウンタイマー

        # Entry animation properties
        self.entry_pattern = entry_pattern
        self.entry_timer = 0
        self.entry_handler = None
        if formation_pos and entry_pattern:
            self.state = ENEMY_STATE_ENTERING
            self.formation_x, self.formation_y = formation_pos
            # 隊列判定のためにbase_yを正しく設定
            self.base_y = self.formation_y
            
            # 入場パターンハンドラーを作成
            self.entry_handler = EntryPatternFactory.create(entry_pattern)
            
            # パターンに応じた初期位置を設定
            initial_x, initial_y = EntryPatternFactory.get_initial_position(entry_pattern)
            self.x = initial_x
            self.y = initial_y
        else:
            # Default spawn off-screen top
            self.x = self.formation_x
            self.y = -16


    def update(self, move_amount_x=0):
        # 攻撃クールダウンタイマーの更新
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1

        # 状態に応じた処理を分岐
        if self.state == ENEMY_STATE_ENTERING:
            self._update_entering(move_amount_x)
        elif self.state == ENEMY_STATE_FORMATION_READY:
            self._update_formation_ready(move_amount_x)
        elif self.state == ENEMY_STATE_NORMAL:
            self._update_normal(move_amount_x)
        elif self.state == ENEMY_STATE_PREPARE_ATTACK:
            self._update_prepare_attack(move_amount_x)
        elif self.state == ENEMY_STATE_ATTACK:
            self._update_attack(move_amount_x)
        elif self.state == ENEMY_STATE_RETURNING:
            self._update_returning(move_amount_x)
        elif self.state == ENEMY_STATE_DESCENDING:
            self._update_descending(move_amount_x)
        elif self.state == ENEMY_STATE_CONTINUOUS_ATTACK:
            self._update_continuous_attack(move_amount_x)

        # 射撃処理
        self._update_shooting()

    def _update_entering(self, move_amount_x):
        """入場アニメーション処理（リファクタリング後）"""
        if self.entry_handler:
            # パターンハンドラーに処理を委譲
            if self.entry_handler.update(self):
                # 入場パターン完了
                self.state = ENEMY_STATE_FORMATION_READY
        else:
            # デフォルトの直線降下パターン
            target_x = self.formation_x
            target_y = self.formation_y
            
            # Y軸方向の移動
            self.y += self.DESCEND_SPEED
            
            # X軸方向の移動
            x_diff = target_x - self.x
            if abs(x_diff) > 1:
                self.x += math.copysign(min(abs(x_diff), 2), x_diff)
            else:
                self.x = target_x
            
            # 到達判定
            distance_to_formation = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
            if distance_to_formation <= self.FORMATION_PROXIMITY or self.y > target_y:
                self.x = target_x
                self.y = target_y
                self.base_x = target_x
                self.base_y = target_y
                self.state = ENEMY_STATE_FORMATION_READY

    def _update_formation_ready(self, move_amount_x):
        """隊列準備完了状態処理"""
        # Wait for all enemies to be ready
        pass

    def _update_normal(self, move_amount_x):
        """通常の隊列移動処理"""
        # 通常状態：隊列移動（main.pyで処理される）
        old_x = self.x
        old_base_x = self.base_x
        old_formation_x = self.formation_x
        self.x += move_amount_x
        self.base_x += move_amount_x # base_xも更新
        self.formation_x += move_amount_x  # formation_xも更新（重要！）
        
        # デバッグ情報（隊列移動中の敵の座標）
        if Config.DEBUG and move_amount_x != 0:
            debug_msg = f"[NORMAL] Enemy {id(self) % 1000}: move_amount={move_amount_x}\n"
            debug_msg += f"  x: {old_x:.1f} -> {self.x:.1f}, base_x: {old_base_x:.1f} -> {self.base_x:.1f}\n"
            debug_msg += f"  formation_x: {old_formation_x:.1f} -> {self.formation_x:.1f}\n"
            print(debug_msg.strip())
            # ファイルにも出力
            with open("debug_enemy.log", "a") as f:
                f.write(debug_msg)

    def _update_prepare_attack(self, move_amount_x):
        """攻撃準備状態処理"""
        # 攻撃準備状態：隊列位置キープ＋上下プルプル身震い
        self.attack_timer += 1
        
        # X座標は隊列移動に従う（main.pyで更新される）
        # Y座標のみ上下プルプル動作
        self.shake_phase_y += self.PREPARE_SHAKE_FREQUENCY_Y
        shake_offset_y = math.sin(self.shake_phase_y) * self.PREPARE_SHAKE_AMPLITUDE_Y
        self.y = self.base_y + shake_offset_y
        self.x += move_amount_x # グループ移動を反映
        self.base_x += move_amount_x # base_xも更新
        self.formation_x += move_amount_x  # formation_xも更新（重要！）
        
        # 準備時間が経過したら攻撃状態に移行
        if self.attack_timer >= self.PREPARE_ATTACK_DURATION:
            self.state = ENEMY_STATE_ATTACK
            self.attack_timer = 0  # タイマーリセット

    def _update_attack(self, move_amount_x):
        """攻撃状態処理"""
        # 攻撃状態：下方向移動＋フラフラ動作
        self.attack_timer += 1
        
        # 下方向に移動
        self.y += self.ATTACK_MOVE_SPEED
        
        # 左右の揺れ動作
        self.sway_phase += self.ATTACK_SWAY_FREQUENCY
        sway_offset = math.sin(self.sway_phase) * self.ATTACK_SWAY_AMPLITUDE
        self.x = self.base_x + sway_offset + move_amount_x # グループ移動を反映
        
        # 攻撃中も隊列位置を追跡（重要！）
        self.formation_x += move_amount_x
        
        # 画面下に出た場合
        if self.y > Config.WIN_HEIGHT:
            # 他のアクティブな敵がいるかチェック
            other_active_enemies = [e for e in Common.enemy_list if e.active and e != self]
            
            if not other_active_enemies:
                # 他に敵がいない場合は連続攻撃モードに移行
                self.state = ENEMY_STATE_CONTINUOUS_ATTACK
            else:
                # 他に敵がいる場合は通常の復帰処理
                self.state = ENEMY_STATE_RETURNING
            
            self.attack_timer = 0  # タイマーリセット
            # 画面外に出た時のX座標を記録
            self.exit_x = self.x
            # 画面下の待機位置に移動（プレイヤーの弾が届かない位置）
            self.y = Config.WIN_HEIGHT + 16

    def _update_returning(self, move_amount_x):
        """復帰待機状態処理"""
        # 復帰待機状態（画面下で待機）
        self.attack_timer += 1
        
        # 他のアクティブな敵がいるかチェック
        other_active_enemies = [e for e in Common.enemy_list if e.active and e != self]
        
        if not other_active_enemies:
            # 他に敵がいない場合は連続攻撃モードに移行
            self.state = ENEMY_STATE_CONTINUOUS_ATTACK
            self.attack_timer = 0  # タイマーリセット
            return
        
        # 画面下の待機位置をキープ（プレイヤーの弾が当たらない）
        self.y = Config.WIN_HEIGHT + 16
        self.x = self.exit_x  # 画面外に出た時のX座標で待機
        self.x += move_amount_x # グループ移動を反映
        
        # 復帰待機中も隊列位置を追跡（重要！）
        self.formation_x += move_amount_x
        
        # 復帰時間が経過したら上から復帰降下開始
        if self.attack_timer >= self.RETURN_DELAY:
            # 画面外に出た時のX座標で上から復帰
            self.x = self.exit_x
            self.y = -16  # 画面上部から開始
            self.state = ENEMY_STATE_DESCENDING  # 復帰降下状態に移行

    def _update_descending(self, move_amount_x):
        """復帰降下状態処理"""
        # 復帰降下状態：元の隊列位置に向かって移動
        
        # 他のアクティブな敵がいるかチェック
        other_active_enemies = [e for e in Common.enemy_list if e.active and e != self]
        
        if not other_active_enemies:
            # 他に敵がいない場合は連続攻撃モードに移行
            self.state = ENEMY_STATE_CONTINUOUS_ATTACK
            self.attack_timer = 0  # タイマーリセット
            return
        
        # 下方向に降下
        self.y += self.DESCEND_SPEED
        
        # 現在の隊列位置（formation_x, formation_y）に向かって移動
        target_x = self.formation_x
        target_y = self.formation_y
        
        # X方向の移動（隊列位置に向かって）
        x_diff = target_x - self.x
        if abs(x_diff) > 1:  # まだ離れている場合
            self.x += math.copysign(min(abs(x_diff), 2), x_diff)  # 最大2ピクセル/フレームで移動
        else:
            self.x = target_x  # 十分近づいたら正確な位置に
        
        # 隊列位置に近づいたかチェック（グループ移動を考慮する前に）
        distance_to_formation = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
        if distance_to_formation <= self.FORMATION_PROXIMITY:
            # 隊列に復帰（グループ移動を考慮した正確な位置に設定）
            old_x = self.x
            old_base_x = self.base_x
            self.x = self.formation_x + move_amount_x  # グループ移動を反映した位置
            self.y = target_y
            self.base_x = self.formation_x  # base_xは現在の隊列位置と同じ値
            self.base_y = target_y  # base_yも更新
            self.state = ENEMY_STATE_NORMAL  # 通常状態に戻る
            self.attack_cooldown_timer = self.ATTACK_COOLDOWN  # 攻撃クールダウン開始
            
            # デバッグ情報（攻撃モードからの復帰）
            if Config.DEBUG:
                debug_msg = f"[RETURN] Enemy {id(self) % 1000}: RETURNED TO FORMATION\n"
                debug_msg += f"  target_x: {target_x:.1f}, target_y: {target_y:.1f}\n"
                debug_msg += f"  move_amount_x: {move_amount_x}\n"
                debug_msg += f"  formation_x: {self.formation_x:.1f}, formation_y: {self.formation_y:.1f}\n"
                debug_msg += f"  x: {old_x:.1f} -> {self.x:.1f}, base_x: {old_base_x:.1f} -> {self.base_x:.1f}\n"
                print(debug_msg.strip())
                # ファイルにも出力
                with open("debug_enemy.log", "a") as f:
                    f.write(debug_msg)
        else:
            # まだ復帰中の場合はグループ移動を反映
            old_x = self.x
            self.x += move_amount_x
            
            # デバッグ情報（復帰中の移動）
            if Config.DEBUG and move_amount_x != 0:
                debug_msg = f"[DESCENDING] Enemy {id(self) % 1000}: move_amount={move_amount_x}, x: {old_x:.1f} -> {self.x:.1f}, target_x: {target_x:.1f}, distance: {distance_to_formation:.1f}\n"
                print(debug_msg.strip())
                # ファイルにも出力
                with open("debug_enemy.log", "a") as f:
                    f.write(debug_msg)

    def _update_continuous_attack(self, move_amount_x):
        """連続攻撃モード処理"""
        # 連続攻撃モード：最後の敵が永続的に攻撃を続ける
        self.attack_timer += 1
        
        # 画面下の待機位置をキープ（短い時間）
        self.y = Config.WIN_HEIGHT + 16
        self.x = self.exit_x  # 画面外に出た時のX座標で待機
        self.x += move_amount_x # グループ移動を反映
        
        # 連続攻撃待機中も隊列位置を追跡（重要！）
        self.formation_x += move_amount_x
        
        # 短い復帰時間が経過したら再び攻撃開始
        if self.attack_timer >= self.RETURN_DELAY_CONTINUOUS:
            # ランダムなX座標で上から再出現
            self.x = random.randint(8, Config.WIN_WIDTH - 16)
            self.y = -16  # 画面上部から開始
            self.state = ENEMY_STATE_ATTACK  # 攻撃状態に移行
            self.attack_timer = 0  # タイマーリセット
            self.base_x = self.x  # 新しい基準位置を設定
            self.sway_phase = random.uniform(0, 6.28)  # 揺れ位相をランダム化

    def _update_shooting(self):
        """射撃処理"""
        # 発射処理（通常状態と連続攻撃モードの敵）
        if self.state == ENEMY_STATE_NORMAL or self.state == ENEMY_STATE_CONTINUOUS_ATTACK:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                # 残りの敵の数に応じて発射確率を調整
                remaining_enemies = len([e for e in Common.enemy_list if e.active])
                if remaining_enemies > 0:
                    if self.state == ENEMY_STATE_CONTINUOUS_ATTACK:
                        # 連続攻撃モードの敵は高い発射確率
                        shoot_chance = self.MAX_SHOOT_CHANCE
                    else:
                        # 通常状態の敵：敵の数が減るほど発射確率が上がる
                        shoot_chance = min(
                            self.BASE_SHOOT_CHANCE + (self.BASE_SHOOT_CHANCE * (40 - remaining_enemies) / 40),
                            self.MAX_SHOOT_CHANCE
                        )
                    if random.random() < shoot_chance:  # 確率で発射
                        Common.enemy_bullet_list.append(
                            EnemyBullet(self.x + 4, self.y + 8)  # エネミーの中心から発射
                        )
                self.shoot_timer = self.SHOOT_INTERVAL

    def on_hit(self, bullet):
        # 弾を消す
        bullet.active = False
        self.Life -= 1

        if self.Life <= 0:
            self.active = False  # エネミーを非アクティブに
            # ENEMY_STATE_ENTERING中に破壊された場合は、整列済み扱いとする
            if self.state == ENEMY_STATE_ENTERING:
                self.state = ENEMY_STATE_FORMATION_READY
            # デバッグ出力
            GameState.debug_print(f"[DEBUG] Enemy destroyed: state={self.state}, active={self.active}")
            GameState.Score += self.Score  # スコア加算
            pyxel.play(0, 1)  # 効果音再生
            Common.explode_manager.spawn_explosion(self.x + 4, self.y + 4, 20, ExpType.RECT)
            #Common.explode_manager.spawn_explosion(self.x + 4, self.y + 4, 20, ExpType.CIRCLE)
        else:
            self.flash = 6  # 点滅処理
            Common.explode_manager.spawn_explosion(self.x + 4, self.y + 8, 5, ExpType.DOT_REFRECT)
            pyxel.play(0, 2)  # 効果音再生

    def draw(self):
        if self.flash > 0:
            # Flash
            for i in range(1, 15):
                pyxel.pal(i, pyxel.COLOR_WHITE)

        self.flash -= 1

        # JSON駆動のアニメーション計算
        anim_pat = self._get_animation_frame(pyxel.frame_count)
        
        # JSON駆動のスプライト取得
        sprite_idx = self._get_enemy_sprite(anim_pat)

        pyxel.blt(
            self.x,
            self.y,
            Config.TILE_BANK0,
            sprite_idx.x,
            sprite_idx.y,
            self.w,
            self.h,
            pyxel.COLOR_BLACK,
        )

        pyxel.pal()

        # Collision Box
        if Config.DEBUG:
            pyxel.rectb(self.x + self.col_x, self.y + self.col_y, self.col_w, self.col_h, pyxel.COLOR_RED)
    
    def _get_animation_speed(self):
        """JSONからエネミーアニメーション速度を取得する"""
        enemy_name = f"ENEMY{self.sprite_num:02d}"
        anim_spd = sprite_manager.get_sprite_metadata(enemy_name, "ANIM_SPD", "10")
        try:
            return int(anim_spd)
        except (ValueError, TypeError):
            return 10  # デフォルト値
    
    def _get_animation_frame(self, frame_count):
        """フレームカウントに基づいてアニメーションフレームを計算する"""
        return frame_count // self.animation_speed % 4  # 0～3でぐるぐる
    
    def _get_enemy_sprite(self, anim_pat):
        """エネミーのスプライトを取得する"""
        enemy_name = f"ENEMY{self.sprite_num:02d}"
        return sprite_manager.get_sprite_by_name_and_field(enemy_name, "FRAME_NUM", str(anim_pat % 4))
