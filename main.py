#ソースコードの中のコメントは日本語にしましょう
# #画面に出力する文字列は英語にしてください。pyxelは日本語フォントを表示できません
# CLAUDE.md を書き込むときは英語にしてください

import pyxel
import random

import Common
import Config
import GameState
# from SpriteManager import SprList  # No longer needed
from StageManager import get_current_stage_map, check_stage_clear
from Enemy import Enemy, ENEMY_MOVE_SPEED, MOVE_THRESHOLD
from ExplodeManager import ExpType

from StarManager import StarManager
from Player import Player

# Title State ----------------------------------------
def update_title(self):
    self.star_manager.update()
    if pyxel.btn(pyxel.KEY_SPACE):
        GameState.GameState = Config.STATE_PLAYING

def draw_title(self):
    
    pyxel.cls(pyxel.COLOR_NAVY)
    self.star_manager.draw()

    pyxel.text(40, 50, "Pyxel Shumup", 7)
    pyxel.text(25, 70, "Press SPACE to Start", 7)
    pyxel.text(40, 110, "Game Ver:" + str(Config.VERSION), 7)
    pyxel.text(40, 120, "Pyxel Ver:" + str(pyxel.VERSION), 7)

# Title State ----------------------------------------

# Playing State ----------------------------------------

def update_playing(self):
    #爆発エフェクトはヒットストップに含めない
    Common.explode_manager.update()
    
    # --- 弾の移動処理（プレイヤーの弾） ---
    for _b in Common.player_bullet_list:
        _b.update()

    # --- 敵の弾の移動処理 ---
    for _b in Common.enemy_bullet_list:
        _b.update()

    # move_amountを初期化
    move_amount = 0

    # --- 敵の移動処理（戦闘中のみ） ---
    if GameState.GameStateSub == Config.STATE_PLAYING_FIGHT:
        # グループ移動の更新
        GameState.enemy_group_x += ENEMY_MOVE_SPEED * GameState.enemy_move_direction
        
        # 移動量が閾値を超えたら整数値で移動
        if abs(GameState.enemy_group_x) >= MOVE_THRESHOLD:
            move_amount = int(GameState.enemy_group_x)
            GameState.enemy_group_x -= move_amount
            
            # 画面端での方向転換チェック
            formation_enemies = [e for e in Common.enemy_list if e.active and (e.state == 0 or e.state == 1)]
            if formation_enemies:
                if GameState.enemy_move_direction == GameState.ENEMY_MOVE_RIGHT:
                    # 右端のエネミーを探す
                    rightmost_x = max(enemy.base_x for enemy in formation_enemies)
                    if rightmost_x + 8 >= Config.WIN_WIDTH:  # 8はエネミーの幅
                        GameState.enemy_move_direction = GameState.ENEMY_MOVE_LEFT
                else:
                    # 左端のエネミーを探す
                    leftmost_x = min(enemy.base_x for enemy in formation_enemies)
                    if leftmost_x <= 0:
                        GameState.enemy_move_direction = GameState.ENEMY_MOVE_RIGHT

        # 攻撃ステート選択の更新
        Common.update_enemy_attack_selection()

    # 各敵のupdateを呼び出す (ヒットストップ中も状態遷移は進める)
    for _e in Common.enemy_list:
        _e.update(move_amount)

    #ゲームスタート時の敵スポーン処理
    if GameState.GameStateSub == Config.STATE_PLAYING_ENEMY_ENTRY:
        if not hasattr(self, 'spawn_timer'):
            self.spawn_timer = 0
            self.spawn_index = 0
            # Clear existing enemies for new stage
            Common.enemy_list.clear()

        self.spawn_timer += 1
        if self.spawn_timer % 6 == 0 and self.spawn_index < 40:
            _y = self.spawn_index // 10
            _x = self.spawn_index % 10

            BASEX = 11
            OFSX = 10
            BASEY = 11
            OFSY = 10

            enemy_y = OFSY + (BASEY * _y)
            enemy_x = OFSX + (BASEX * _x)
            sprite_num = get_current_stage_map()[_y][_x]
            
            pattern = 1 if _x < 5 else 2

            _Enemy = Enemy(0, 0, 8, 8, 2, 100, sprite_num, formation_pos=(enemy_x, enemy_y), entry_pattern=pattern)
            Common.enemy_list.append(_Enemy)
            
            self.spawn_index += 1

        # Check if all enemies are spawned and ready
        if self.spawn_index >= 40:
            # activeな敵のうち、全員がFORMATION_READYならNORMALへ遷移
            active_ready = [e for e in Common.enemy_list if e.active and e.state == -2]
            active_count = len([e for e in Common.enemy_list if e.active])
            if active_count == 0:
                # 全員倒された場合は即クリア判定へ
                GameState.GameStateSub = Config.STATE_PLAYING_STAGE_CLEAR
                del self.spawn_timer
                del self.spawn_index
            elif active_count > 0 and len(active_ready) == active_count:
                # activeな敵だけNORMALへ遷移
                for enemy in Common.enemy_list:
                    if enemy.active and enemy.state == -2:
                        enemy.state = 0 # ENEMY_STATE_NORMAL
                        enemy.attack_cooldown_timer = random.randint(0, 300)
                del self.spawn_timer
                del self.spawn_index
                GameState.GameStateSub = Config.STATE_PLAYING_FIGHT

    # ステージクリア時の処理
    if GameState.GameStateSub == Config.STATE_PLAYING_STAGE_CLEAR:
        if pyxel.btn(pyxel.KEY_Z):
            GameState.CURRENT_STAGE += 1
            # Reset enemy_list for the new stage
            Common.enemy_list.clear()
            GameState.GameStateSub = Config.STATE_PLAYING_ENEMY_ENTRY
        return

    # ここから下の処理はヒットストップの影響を受ける
    if GameState.StopTimer > 0:
        GameState.StopTimer -= 1
        return

    self.star_manager.update()
    self.player.update()

    # --- 衝突判定：プレイヤー弾 vs 敵 ---
    for bullet in Common.player_bullet_list:
        if not bullet.active:
            continue  # 非アクティブな弾はスキップ

        for enemy in Common.enemy_list:
            if not enemy.active:
                continue  # 非アクティブな敵はスキップ

            # 衝突しているかをチェック
            if Common.check_collision(
                bullet.x + bullet.col_x, bullet.y + bullet.col_y, bullet.col_w, bullet.col_h,
                enemy.x + enemy.col_x, enemy.y + enemy.col_y, enemy.col_w, enemy.col_h
            ):
                enemy.on_hit(bullet)  # ヒット処理（敵のライフ減少、爆発など）

    # --- 衝突判定：敵弾 vs プレイヤー ---
    for bullet in Common.enemy_bullet_list:
        if not bullet.active:
            continue  # 非アクティブな弾はスキップ

        # プレイヤーとの衝突チェック
        if Common.check_collision(
            bullet.x + bullet.col_x, bullet.y + bullet.col_y, bullet.col_w, bullet.col_h,
            self.player.x + self.player.col_x, self.player.y + self.player.col_y, 
            self.player.col_w, self.player.col_h
        ):
            bullet.active = False  # 弾を消す
            self.player.on_hit()  # プレイヤーのヒット処理

    # --- 衝突判定：プレイヤー vs 敵 ---
    for enemy in Common.enemy_list:
        if not enemy.active:
            continue  # 非アクティブな敵はスキップ

        # プレイヤーとの衝突チェック
        if Common.check_collision(
            self.player.x + self.player.col_x, self.player.y + self.player.col_y,
            self.player.col_w, self.player.col_h,
            enemy.x + enemy.col_x, enemy.y + enemy.col_y,
            enemy.col_w, enemy.col_h
        ):
            self.player.on_hit()  # プレイヤーのヒット処理

    # --- ガベージコレクション（死んだ敵、自弾も除去） ---
    Common.enemy_list = [e for e in Common.enemy_list if e.active]
    Common.player_bullet_list = [b for b in Common.player_bullet_list if b.active]
    Common.enemy_bullet_list = [b for b in Common.enemy_bullet_list if b.active]

    # ステージクリア判定は戦闘中のみ行う
    if GameState.GameStateSub == Config.STATE_PLAYING_FIGHT:
        check_stage_clear(Common.enemy_list)

def draw_playing(self):

    if GameState.ShakeTimer == 10:
        pyxel.cls(pyxel.COLOR_WHITE)
    else:
        pyxel.cls(pyxel.COLOR_NAVY)

    if GameState.ShakeTimer > 0:
        # カメラシェイクの実装
        shake_offset_x = random.randint(-Config.SHAKE_STRENGTH, Config.SHAKE_STRENGTH)
        shake_offset_y = random.randint(-Config.SHAKE_STRENGTH, Config.SHAKE_STRENGTH)
        pyxel.camera(shake_offset_x, shake_offset_y)
        GameState.ShakeTimer -= 1
    else:
        pyxel.camera(0, 0)  

    self.star_manager.draw()

    self.player.draw()

    for _e in Common.enemy_list:
        _e.draw()
    
    # 敵の弾の描画
    for _b in Common.enemy_bullet_list:
        _b.draw()
    
    #爆発描画ーーーーーーーーーーーーーーーーーーーー
    Common.explode_manager.draw()
    #ばくはつだーーーーーーーーーーーーーーーーーーーー

    #Draw HUD
    pyxel.camera(0, 0)      
    pyxel.text(8, 0, "Score: " + str(GameState.Score), 7)

    # ステージクリア表示
    if GameState.GameStateSub == Config.STATE_PLAYING_STAGE_CLEAR:
        pyxel.text(40, 50, "Stage Clear!", 7)
        pyxel.text(20, 70, "Press Z to continue", 7)

class App:
    def __init__(self):
        pyxel.init(Config.WIN_WIDTH, Config.WIN_HEIGHT, title="Pyxel Shump!!", display_scale=Config.DISPLAY_SCALE, fps=Config.FPS)
        pyxel.load("my_resource.pyxres")

        GameState.GameState = Config.STATE_TITLE

        #Bg Stars
        self.star_manager = StarManager(count=Config.STAR_COUNT)        

        #Player Star Ship
        self.player = Player(64-4, 108)

        GameState.Score = 10
        GameState.HighScore = 100

        pyxel.run(self.update, self.draw)
        

    def update(self):
        GameState.GameTimer += 1

        match GameState.GameState:
        
            case Config.STATE_TITLE:
                update_title(self)
            case Config.STATE_PLAYING:
                update_playing(self)
            case Config.STATE_GAMEOVER:
                #print("Game Over")
                pass     
            case Config.STATE_PAUSE:
                pass
            case Config.STATE_GAMECLEAR:
                # zキーでタイトルに戻る
                if pyxel.btn(pyxel.KEY_Z):
                    GameState.GameState = Config.STATE_TITLE

        #Esc Key Down
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()

   
    def draw(self):

        match GameState.GameState:
            case Config.STATE_TITLE:
                draw_title(self)

            case Config.STATE_PLAYING:
                draw_playing(self)
            case Config.STATE_GAMEOVER:
                pyxel.text(40, 50, "Game Over", 7)
                pass
            case Config.STATE_PAUSE:
                pass
            case Config.STATE_GAMECLEAR:
                pyxel.cls(pyxel.COLOR_NAVY)
                self.star_manager.draw()
                pyxel.text(35, 50, "Congratulations!", pyxel.COLOR_YELLOW)
                pyxel.text(35, 80, "Press Z to Title", 7)


App()
