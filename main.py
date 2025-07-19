#ソースコードの中のコメントは日本語にしましょう
# #画面に出力する文字列は英語にしてください。pyxelは日本語フォントを表示できません
# CLAUDE.md を書き込むときは英語にしてください
# 変数の型は宣言してください

#todo
#Enemyの出現パターンを２種類くらいふやす（四角軌跡、３角軌跡、ダブルループ）
#攻撃ステート中に、宙返りとかする敵作ってみる
#EnemyにLifeを設定（jsonから）
#面クリア時の演出


import pyxel
import random
import os

import Common
import Config
import GameState
# from SpriteManager import SprList  # No longer needed
from StageManager import get_current_stage_map, check_stage_clear
from Enemy import Enemy, formation_manager
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
        # 新しいFormationManagerで隊列移動を処理
        formation_manager.update(Common.enemy_list)

    # 各敵のupdateを呼び出す（シンプル化）
    for _e in Common.enemy_list:
        _e.update()

    #ゲームスタート時の敵スポーン処理（ウェーブキューシステム）
    if GameState.GameStateSub == Config.STATE_PLAYING_ENEMY_ENTRY:
        if not hasattr(self, 'spawn_timer'):
            self.spawn_timer = 0
            self.spawn_index = 0
            # ウェーブキューの初期化
            self.wave_queue = [
                {"row": 0, "state": 1, "spawn_index": 0},  # 1行目：出現中
                {"row": 1, "state": 0, "spawn_index": 0},  # 2行目：待機中
                {"row": 2, "state": 0, "spawn_index": 0},  # 3行目：待機中
                {"row": 3, "state": 0, "spawn_index": 0},  # 4行目：待機中
            ]
            # Clear existing enemies for new stage
            Common.enemy_list.clear()

        self.spawn_timer += 1
        
        # 定数定義
        BASEX = 11
        OFSX = 10
        BASEY = 11
        OFSY = 10
        
        # 各ウェーブの状態管理
        for wave in self.wave_queue:
            row = wave["row"]
            state = wave["state"]
            
            # 出現中のウェーブの処理
            if state == 1 and self.spawn_timer % 6 == 0:  # SPAWNING
                if wave["spawn_index"] < 10:
                    _y = row
                    _x = wave["spawn_index"]

                    enemy_y = OFSY + (BASEY * _y)
                    enemy_x = OFSX + (BASEX * _x)
                    sprite_num = get_current_stage_map()[_y][_x]
                    
                    # 登場パターンの設定（左右交互：偶数行は左から、奇数行は右から）
                    if _y % 2 == 0:  # 偶数行（0,2行目）は左から水平移動
                        entry_pattern = "left_horizontal"
                    else:  # 奇数行（1,3行目）は右から水平移動
                        entry_pattern = "right_horizontal"
                    
                    # ウェーブ単位でランダムY座標を生成（初回のみ）
                    if wave["spawn_index"] == 0 and entry_pattern in ["left_horizontal", "right_horizontal"]:
                        # 64±32の範囲でランダムY座標を生成
                        wave["random_entry_y"] = 64 + random.randint(-32, 32)
                        if Config.DEBUG:
                            print(f"Wave {row} ({entry_pattern}): Generated random entry_y = {wave['random_entry_y']}")
                    
                    # ウェーブ共通のランダムY座標を使用
                    random_entry_y = wave.get("random_entry_y", None)
                    
                    # 敵生成（登場パターン対応 + デバッグ情報 + EntryPattern統合テスト）
                    # テスト: 1行目はLeftLoop(1)、2行目はRightLoop(2)、3行目はZigzag(3)、4行目は従来の水平移動
                    if row == 0:
                        test_pattern_id = 1  # LeftLoopPattern
                    elif row == 1:
                        test_pattern_id = 2  # RightLoopPattern
                    elif row == 2:
                        test_pattern_id = 3  # ZigzagPattern
                    else:
                        test_pattern_id = None  # 従来の水平移動
                    
                    _Enemy = Enemy(x=enemy_x, y=enemy_y, sprite_num=sprite_num, w=8, h=8, life=2, score=100, 
                                 entry_pattern=entry_pattern, entry_y=random_entry_y, 
                                 wave_id=row, enemy_index=wave["spawn_index"], entry_pattern_id=test_pattern_id)
                    Common.enemy_list.append(_Enemy)
                    
                    wave["spawn_index"] += 1
                    
                    # 出現完了チェック
                    if wave["spawn_index"] >= 10:
                        wave["state"] = 2  # ENTERING状態へ遷移
            
            # 入場中のウェーブの完了チェック
            elif state == 2:  # ENTERING
                # 現在の行の全敵をスポーン順序で特定（row基準）
                current_row_enemies = [e for e in Common.enemy_list if e.active and abs(e.formation_y - (OFSY + BASEY * row)) < 5]
                
                # ホームポジション到達済みの敵をカウント
                ready_enemies = [e for e in current_row_enemies if e.is_ready_for_formation_movement()]
                
                # デバッグ情報（登場シーケンス対応）
                if Config.DEBUG and len(current_row_enemies) > 0:
                    entry_enemies = [e for e in current_row_enemies if e.state == -1]  # ENTRY_SEQUENCE
                    moving_enemies = [e for e in current_row_enemies if e.state == -2]  # MOVING_TO_HOME
                    reached_enemies = [e for e in current_row_enemies if e.state == -3]  # HOME_REACHED
                    normal_enemies = [e for e in current_row_enemies if e.state == 0]  # NORMAL
                    print(f"Wave {row}: Total={len(current_row_enemies)}, Entry={len(entry_enemies)}, Moving={len(moving_enemies)}, Reached={len(reached_enemies)}, Normal={len(normal_enemies)}")
                
                # 入場完了判定（全員がホームポジション到達済み）
                if len(ready_enemies) == len(current_row_enemies) and len(current_row_enemies) > 0:
                    wave["state"] = 3  # COMPLETED状態へ遷移
                    if Config.DEBUG:
                        print(f"Wave {row} completed! All enemies reached home position. Triggering next wave.")
                    
                    # 次のウェーブを起動
                    next_wave_index = row + 1
                    if next_wave_index < len(self.wave_queue):
                        self.wave_queue[next_wave_index]["state"] = 1  # SPAWNING状態へ
        
        # 全ウェーブ完了チェック
        all_completed = all(wave["state"] == 3 for wave in self.wave_queue)
        if all_completed:
            # 全隊列の出現・入場完了判定
            active_enemies = [e for e in Common.enemy_list if e.active]
            all_ready_for_formation = [e for e in active_enemies if e.is_ready_for_formation_movement()]
            
            if len(active_enemies) == 0:
                # 全員撃墜された場合は即クリア判定へ
                GameState.GameStateSub = Config.STATE_PLAYING_STAGE_CLEAR
                if Config.DEBUG:
                    print("All enemies destroyed during entry sequence! Stage clear.")
            elif len(all_ready_for_formation) == len(active_enemies):
                # 全員がホームポジション到達・隊列移動準備完了
                # 全敵をNORMAL状態に遷移
                for enemy in active_enemies:
                    if enemy.state == -3:  # HOME_REACHED
                        old_state = enemy.state
                        enemy.state = 0  # NORMAL
                        # 最初と最後の敵の状態遷移をログ出力
                        if hasattr(enemy, '_log_state_change'):
                            enemy._log_state_change(old_state, enemy.state, "all waves completed")
                
                GameState.GameStateSub = Config.STATE_PLAYING_FIGHT
                if Config.DEBUG:
                    print(f"All waves completed! {len(active_enemies)} enemies ready for formation movement. Starting battle.")
            
            # クリーンアップ
            if hasattr(self, 'spawn_timer'):
                del self.spawn_timer
            if hasattr(self, 'spawn_index'):
                del self.spawn_index
            if hasattr(self, 'wave_queue'):
                del self.wave_queue

    # 星の背景アニメーションは常に更新（ヒットストップの影響を受けない）
    self.star_manager.update()

    # ステージクリア時の処理
    # プレイヤーの更新処理（ステージクリア中でも移動可能にする）
    if GameState.StopTimer <= 0:  # ヒットストップ中以外は常に更新
        self.player.update()

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
        self.star_manager = StarManager()        

        #Player Star Ship
        self.player = Player(64-4, 108)

        GameState.Score = 10
        GameState.HighScore = 100

        # デバッグログファイルの初期化
        if Config.DEBUG:
            # 既存のログファイルを削除
            if os.path.exists("debug_enemy.log"):
                os.remove("debug_enemy.log")
            # 新しいログファイルを作成
            with open("debug_enemy.log", "w") as f:
                f.write("=== Enemy Debug Log Started ===\n")

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
