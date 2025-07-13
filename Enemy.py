import pyxel
import Common
import random
import math
from ExplodeManager import ExpType
from EnemyBullet import EnemyBullet

ANIM_FRAME = 10
ENEMY_MOVE_SPEED = 0.5  # 移動速度
MOVE_THRESHOLD = 1  # 移動閾値
SHOOT_INTERVAL = 60  # 発射間隔（フレーム）
BASE_SHOOT_CHANCE = 0.10  # 基本発射確率
MAX_SHOOT_CHANCE = 0.30  # 最大発射確率

# 敵の攻撃ステート定義
ENEMY_STATE_ENTERING = -1       # 入場中
ENEMY_STATE_FORMATION_READY = -2 # 隊列準備完了
ENEMY_STATE_NORMAL = 0          # 通常の隊列移動
ENEMY_STATE_PREPARE_ATTACK = 1  # 攻撃準備中（身震い）
ENEMY_STATE_ATTACK = 2          # 攻撃状態（下降中）
ENEMY_STATE_RETURNING = 3       # 復帰待機中（画面下）
ENEMY_STATE_DESCENDING = 4      # 復帰降下中（隊列位置に向かって）
ENEMY_STATE_CONTINUOUS_ATTACK = 5  # 連続攻撃モード（隊列復帰なし）

# 攻撃モード関連の定数
PREPARE_ATTACK_DURATION = 60  # 攻撃準備時間（フレーム：3秒）
PREPARE_SHAKE_AMPLITUDE_X = 1.0  # 準備中の左右身震い幅
PREPARE_SHAKE_AMPLITUDE_Y = 1.2  # 準備中の上下身震い幅（より目立つプルプル感）
PREPARE_SHAKE_FREQUENCY_X = 0.2  # 準備中の左右身震い頻度（ゆっくり）
PREPARE_SHAKE_FREQUENCY_Y = 1.0  # 準備中の上下身震い頻度（プルプル感）

ATTACK_MOVE_SPEED = 0.8    # 攻撃時の移動速度（速すぎると避けにくい）
ATTACK_SWAY_AMPLITUDE = 1.5  # 左右の揺れ幅（程よい揺れ）
ATTACK_SWAY_FREQUENCY = 0.08  # 揺れ頻度（少し遅めでより自然）
RETURN_DELAY = 180         # 画面下に消えてから復帰するまでの時間（フレーム：2秒）
RETURN_DELAY_CONTINUOUS = 60  # 連続攻撃モード時の復帰時間（フレーム：1秒）
DESCEND_SPEED = 1.5        # 復帰時の降下速度
FORMATION_PROXIMITY = 8    # 隊列位置への近似判定距離（後で微調整可能）
ATTACK_COOLDOWN = 300      # 隊列復帰後の攻撃クールダウン時間（5秒）

class Enemy:
    def __init__(self, x, y, w=8, h=8, life=1, score=10, sprite_num=1, formation_pos=None, entry_pattern=None):
        self.base_x = x  # 初期X座標を保存
        self.base_y = y  # 初期Y座標を保存（隊列復帰用）
        self.x = x
        self.y = y
        self.w = w  # Sprite Width
        self.h = h  # Sprite Height

        self.col_x = 1 #Collision Box
        self.col_y = 1
        self.col_w = 6
        self.col_h = 6

        self.Life = life
        self.Score = score

        self.flash = 0

        # Enemy sprite id (1-5)
        self.sprite_num = sprite_num

        self.active = True
        self.shoot_timer = random.randint(0, SHOOT_INTERVAL)  # 発射タイマー
        
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
        if formation_pos and entry_pattern:
            self.state = ENEMY_STATE_ENTERING
            self.formation_x, self.formation_y = formation_pos
            # Set initial position based on pattern
            if self.entry_pattern == 1:
                self.x = -16
                self.y = Common.WIN_HEIGHT - 20
            elif self.entry_pattern == 2:
                self.x = Common.WIN_WIDTH + 16
                self.y = Common.WIN_HEIGHT - 20
            else: # Default spawn off-screen top
                self.x = self.formation_x
                self.y = -16


    def update(self, move_amount_x=0):
        # 攻撃クールダウンタイマーの更新
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1

        # 状態に応じた移動処理
        if self.state == ENEMY_STATE_ENTERING:
            self.entry_timer += 1
            entry_duration = 120  # 2 seconds for the loop animation

            if self.entry_timer <= entry_duration:
                if self.entry_pattern == 1: # Left loop
                    loop_center_x = Common.WIN_WIDTH / 4
                    loop_center_y = Common.WIN_HEIGHT / 2
                    radius = 40
                    angle = (self.entry_timer / entry_duration) * 2 * math.pi - math.pi / 2
                    progress = self.entry_timer / entry_duration
                    current_radius = progress * radius
                    self.x = loop_center_x + math.cos(angle) * current_radius
                    self.y = loop_center_y + math.sin(angle) * current_radius
                elif self.entry_pattern == 2: # Right loop
                    loop_center_x = Common.WIN_WIDTH * 3 / 4
                    loop_center_y = Common.WIN_HEIGHT / 2
                    radius = 40
                    angle = (self.entry_timer / entry_duration) * 2 * math.pi - math.pi / 2
                    progress = self.entry_timer / entry_duration
                    current_radius = progress * radius
                    self.x = loop_center_x - math.cos(angle) * current_radius # Mirrored X
                    self.y = loop_center_y + math.sin(angle) * current_radius
            else:
                # After loop, move to formation position (descending logic)
                target_x = self.formation_x
                target_y = self.formation_y

                # Y-axis movement
                self.y += DESCEND_SPEED

                # X-axis movement
                x_diff = target_x - self.x
                if abs(x_diff) > 1:
                    self.x += math.copysign(min(abs(x_diff), 2), x_diff)
                else:
                    self.x = target_x

                # Check for arrival
                distance_to_formation = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
                if distance_to_formation <= FORMATION_PROXIMITY or self.y > target_y:
                    self.x = target_x
                    self.y = target_y
                    self.base_x = target_x
                    self.base_y = target_y
                    self.state = ENEMY_STATE_FORMATION_READY

        elif self.state == ENEMY_STATE_FORMATION_READY:
            # Wait for all enemies to be ready
            pass

        elif self.state == ENEMY_STATE_NORMAL:
            # 通常状態：隊列移動（main.pyで処理される）
            self.x += move_amount_x
            self.base_x += move_amount_x # base_xも更新

        elif self.state == ENEMY_STATE_PREPARE_ATTACK:
            # 攻撃準備状態：隊列位置キープ＋上下プルプル身震い
            self.attack_timer += 1
            
            # X座標は隊列移動に従う（main.pyで更新される）
            # Y座標のみ上下プルプル動作
            self.shake_phase_y += PREPARE_SHAKE_FREQUENCY_Y
            shake_offset_y = math.sin(self.shake_phase_y) * PREPARE_SHAKE_AMPLITUDE_Y
            self.y = self.base_y + shake_offset_y
            self.x += move_amount_x # グループ移動を反映
            self.base_x += move_amount_x # base_xも更新
            
            # 準備時間が経過したら攻撃状態に移行
            if self.attack_timer >= PREPARE_ATTACK_DURATION:
                self.state = ENEMY_STATE_ATTACK
                self.attack_timer = 0  # タイマーリセット
                
        elif self.state == ENEMY_STATE_ATTACK:
            # 攻撃状態：下方向移動＋フラフラ動作
            self.attack_timer += 1
            
            # 下方向に移動
            self.y += ATTACK_MOVE_SPEED
            
            # 左右の揺れ動作
            self.sway_phase += ATTACK_SWAY_FREQUENCY
            sway_offset = math.sin(self.sway_phase) * ATTACK_SWAY_AMPLITUDE
            self.x = self.base_x + sway_offset + move_amount_x # グループ移動を反映
            
            # 画面下に出た場合
            if self.y > Common.WIN_HEIGHT:
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
                self.y = Common.WIN_HEIGHT + 16
                
        elif self.state == ENEMY_STATE_RETURNING:
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
            self.y = Common.WIN_HEIGHT + 16
            self.x = self.exit_x  # 画面外に出た時のX座標で待機
            self.x += move_amount_x # グループ移動を反映
            
            # 復帰時間が経過したら上から復帰降下開始
            if self.attack_timer >= RETURN_DELAY:
                # 画面外に出た時のX座標で上から復帰
                self.x = self.exit_x
                self.y = -16  # 画面上部から開始
                self.state = ENEMY_STATE_DESCENDING  # 復帰降下状態に移行
                
        elif self.state == ENEMY_STATE_DESCENDING:
            # 復帰降下状態：元の隊列位置に向かって移動
            
            # 他のアクティブな敵がいるかチェック
            other_active_enemies = [e for e in Common.enemy_list if e.active and e != self]
            
            if not other_active_enemies:
                # 他に敵がいない場合は連続攻撃モードに移行
                self.state = ENEMY_STATE_CONTINUOUS_ATTACK
                self.attack_timer = 0  # タイマーリセット
                return
            
            # 下方向に降下
            self.y += DESCEND_SPEED
            
            # 現在の隊列位置（formation_x, formation_y）に向かって移動
            target_x = self.formation_x
            target_y = self.formation_y
            
            # X方向の移動（隊列位置に向かって）
            x_diff = target_x - self.x
            if abs(x_diff) > 1:  # まだ離れている場合
                self.x += math.copysign(min(abs(x_diff), 2), x_diff)  # 最大2ピクセル/フレームで移動
            else:
                self.x = target_x  # 十分近づいたら正確な位置に
            self.x += move_amount_x # グループ移動を反映
            
            # 隊列位置に近づいたかチェック
            distance_to_formation = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
            if distance_to_formation <= FORMATION_PROXIMITY:
                # 隊列に復帰
                self.x = target_x
                self.y = target_y
                self.base_x = target_x  # base_xも更新
                self.base_y = target_y  # base_yも更新
                self.state = ENEMY_STATE_NORMAL  # 通常状態に戻る
                self.attack_cooldown_timer = ATTACK_COOLDOWN  # 攻撃クールダウン開始
                
        elif self.state == ENEMY_STATE_CONTINUOUS_ATTACK:
            # 連続攻撃モード：最後の敵が永続的に攻撃を続ける
            self.attack_timer += 1
            
            # 画面下の待機位置をキープ（短い時間）
            self.y = Common.WIN_HEIGHT + 16
            self.x = self.exit_x  # 画面外に出た時のX座標で待機
            self.x += move_amount_x # グループ移動を反映
            
            # 短い復帰時間が経過したら再び攻撃開始
            if self.attack_timer >= RETURN_DELAY_CONTINUOUS:
                # ランダムなX座標で上から再出現
                self.x = random.randint(8, Common.WIN_WIDTH - 16)
                self.y = -16  # 画面上部から開始
                self.state = ENEMY_STATE_ATTACK  # 攻撃状態に移行
                self.attack_timer = 0  # タイマーリセット
                self.base_x = self.x  # 新しい基準位置を設定
                self.sway_phase = random.uniform(0, 6.28)  # 揺れ位相をランダム化

        # 発射処理（通常状態と連続攻撃モードの敵）
        if self.state == ENEMY_STATE_NORMAL or self.state == ENEMY_STATE_CONTINUOUS_ATTACK:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                # 残りの敵の数に応じて発射確率を調整
                remaining_enemies = len([e for e in Common.enemy_list if e.active])
                if remaining_enemies > 0:
                    if self.state == ENEMY_STATE_CONTINUOUS_ATTACK:
                        # 連続攻撃モードの敵は高い発射確率
                        shoot_chance = MAX_SHOOT_CHANCE
                    else:
                        # 通常状態の敵：敵の数が減るほど発射確率が上がる
                        shoot_chance = min(
                            BASE_SHOOT_CHANCE + (BASE_SHOOT_CHANCE * (40 - remaining_enemies) / 40),
                            MAX_SHOOT_CHANCE
                        )
                    if random.random() < shoot_chance:  # 確率で発射
                        Common.enemy_bullet_list.append(
                            EnemyBullet(self.x + 4, self.y + 8)  # エネミーの中心から発射
                        )
                self.shoot_timer = SHOOT_INTERVAL

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
            print(f"[DEBUG] Enemy destroyed: state={self.state}, active={self.active}")
            Common.Score += self.Score  # スコア加算
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

        #anim_pat = 0 ~ 3
        AnimFrame = 10  #アニメーションの速度を変更できるよ
        anim_pat = pyxel.frame_count // AnimFrame % 4  # 0～3でぐるぐる（アニメ切り替え）

        # get sprite coordinates from Common by enemy number
        sprite_idx = Common.get_enemy_sprite(self.sprite_num, anim_pat)

        pyxel.blt(
            self.x,
            self.y,
            Common.TILE_BANK0,
            sprite_idx.x,
            sprite_idx.y,
            self.w,
            self.h,
            pyxel.COLOR_BLACK,
        )

        pyxel.pal()

        # Collision Box
        if Common.DEBUG:
            pyxel.rectb(self.x + self.col_x, self.y + self.col_y, self.col_w, self.col_h, pyxel.COLOR_RED)
