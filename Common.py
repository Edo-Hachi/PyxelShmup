from collections import namedtuple
from ExplodeManager import ExpMan
import random
#from enum import Enum

VERSION = "0.1.5"
LAUNCH_DATE = "2025/07/13"


DEBUG = False #or True

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

#Window size
WIN_WIDTH = 128
WIN_HEIGHT = 128

#Sprite banks
TILE_BANK0 = 0
TILE_BANK1 = 1
TILE_BANK2 = 2

#State IDs
STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_PAUSE = 3
STATE_GAMECLEAR = 4  # ゲームクリア状態

GameState = STATE_TITLE

STATE_PLAYING_ENEMY_ENTRY = 0
STATE_PLAYING_ENEMY_SPAWN = 1
STATE_PLAYING_FIGHT = 2
STATE_PLAYING_STAGE_CLEAR = 3
GameStateSub = STATE_PLAYING_ENEMY_ENTRY

# ステージ管理
CURRENT_STAGE = 1
MAX_STAGE = 4

#Camera Shake
ShakeTimer = 0
ShakeStrength = 10
StopTimer = 0

#Stop Effect
STOP_TIME = 20  # Stop Time
SHAKE_TIME = 10  # Camera Shake Time

#Game System Timer
GameTimer = 0


#Score
HighScore = 0
Score = 0




# --------------------------------------------------
# Enemy spawn pattern (10x4 grid)
# --------------------------------------------------
ENEMY_MAP_STG01 = [
    [5, 3, 5, 5, 4, 4, 5, 5, 3, 5],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [1, 4, 4, 3, 3, 3, 3, 4, 4, 1],
    [1, 1, 1, 2, 2, 2, 2, 1, 1, 1],
]


ENEMY_MAP_STG02 = [
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [4, 4, 5, 5, 4, 4, 5, 5, 4, 4],
    [2, 2, 1, 1, 2, 2, 1, 1, 2, 2],
    [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
]

ENEMY_MAP_STG03 = [
    [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]

ENEMY_MAP_STG04 = [
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [5, 3, 5, 3, 5, 5, 3, 5, 3, 5],
    [2, 1, 2, 1, 2, 2, 1, 2, 1, 2],
    [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
]

#Sprite Collision List
enemy_list = []
enemy_bullet_list = []
player_bullet_list = []

# エネミーグループの移動方向
ENEMY_MOVE_RIGHT = 1
ENEMY_MOVE_LEFT = -1
enemy_move_direction = ENEMY_MOVE_RIGHT  # 初期方向は右
enemy_group_x = 0  # グループ全体のX座標オフセット

#パーティクル管理オブジェクト
explode_manager = ExpMan()

def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    # 各辺の位置を計算
    left1   = x1
    right1  = x1 + w1
    top1    = y1
    bottom1 = y1 + h1

    left2   = x2
    right2  = x2 + w2
    top2    = y2
    bottom2 = y2 + h2

    # 衝突しているかを確認
    is_collision = (
        left1   < right2 and
        right1  > left2 and
        top1    < bottom2 and
        bottom1 > top2
    )

    return is_collision


#Sprite Location List
# 8x8 sprites
SpIdx =  namedtuple("SprIdx", ["x", "y"])
SprList = {
    'NULL' : SpIdx(0, 0),  # NULL
    "TOP" : SpIdx(8, 0),  # TOP
    "LEFT" : SpIdx(16, 0),  # LEFT
    "RIGHT" : SpIdx(24, 0),  # RIGHT
    "NULL" : SpIdx(32, 0),   # NULL
    


    "BULLET01" : SpIdx(40, 0),  # BULLET
    "BULLET02" : SpIdx(48, 0),  

    "EXT01" : SpIdx(56, 0), # Ship Exhaust
    "EXT02" : SpIdx(64, 0), # Ship Exhaust
    "EXT03" : SpIdx(72, 0), # Ship Exhaust
    "EXT04" : SpIdx(80, 0), # Ship Exhaust

    "MUZL01" : SpIdx(88, 0),  #MuzzleFlash01
    "MUZL02" : SpIdx(96, 0),  #MuzzleFlash02
    "MUZL03" : SpIdx(104, 0),  #MuzzleFlash03
    "NULL" : SpIdx(112, 0),
    "ENEMY_BULLET" : SpIdx(120, 0),

    "NULL" : SpIdx(0, 8),    #NULL
    
    "ENEMY01_0" : SpIdx(8, 8),    #Enemy01_0
    "ENEMY01_1" : SpIdx(16, 8),   #Enemy01_1
    "ENEMY01_2" : SpIdx(24, 8),   #Enemy01_2
    "ENEMY01_3" : SpIdx(32, 8),   #Enemy01_3

    "ENEMY02_0" : SpIdx(40, 8),   #Enemy02_0
    "ENEMY02_1" : SpIdx(48, 8),   #Enemy02_0
    "ENEMY02_2" : SpIdx(56, 8),   #Enemy02_0
    "ENEMY02_3" : SpIdx(64, 8),   #Enemy02_0

    "ENEMY03_0" : SpIdx(72, 8),   #Enemy03_0
    "ENEMY03_1" : SpIdx(80, 8),   #Enemy03_1
    "ENEMY03_2" : SpIdx(88, 8),   #Enemy03_2
    "ENEMY03_3" : SpIdx(96, 8),   #Enemy03_3

    "ENEMY04_0" : SpIdx(104, 8),   #Enemy04_0
    "ENEMY04_1" : SpIdx(112, 8),   #Enemy04_1
    "ENEMY04_2" : SpIdx(120, 8),   #Enemy04_2
    "ENEMY04_3" : SpIdx(128, 8),   #Enemy04_3

    "ENEMY05_0" : SpIdx(136, 8),   #Enemy05_0
    "ENEMY05_1" : SpIdx(144, 8),   #Enemy05_1
    "ENEMY05_2" : SpIdx(152, 8),   #Enemy05_2
    "ENEMY05_3" : SpIdx(160, 8),   #Enemy05_3

}

# --------------------------------------------------
# Enemy sprite helper
# --------------------------------------------------
MAX_ENEMY_NUM = 5
MAX_ANIM_PAT = 4

def get_enemy_sprite(enemy_num: int, anim_pat: int) -> SpIdx:
    """Return ``SpIdx`` for given enemy number and animation pattern."""

    enemy_num = max(1, min(enemy_num, MAX_ENEMY_NUM))
    anim_pat = anim_pat % MAX_ANIM_PAT

    key = f"ENEMY{enemy_num:02d}_{anim_pat}"
    return SprList.get(key, SprList["NULL"])

def get_current_stage_map():
    """現在のステージの敵配置マップを返す"""
    if CURRENT_STAGE == 1:
        return ENEMY_MAP_STG01
    elif CURRENT_STAGE == 2:
        return ENEMY_MAP_STG02
    elif CURRENT_STAGE == 3:
        return ENEMY_MAP_STG03
    elif CURRENT_STAGE == 4:
        return ENEMY_MAP_STG04
    return ENEMY_MAP_STG01  # デフォルトはステージ1

def check_stage_clear():
    """敵が全滅したかチェックし、次のステージに移行する"""
    global CURRENT_STAGE, GameStateSub
    # デバッグ出力: エネミーの状態
    debug_print(f"[DEBUG] --- check_stage_clear ---")
    debug_print(f"[DEBUG] Active Enemy Count: {len([e for e in enemy_list if e.active])}")
    for idx, e in enumerate(enemy_list):
        debug_print(f"[DEBUG] Enemy[{idx}]: state={getattr(e, 'state', None)}, active={getattr(e, 'active', None)}")
    # アクティブな敵がいるかチェック
    active_enemies = [e for e in enemy_list if e.active]
    if not active_enemies:  # アクティブな敵がいない場合
        if CURRENT_STAGE < MAX_STAGE:
            GameStateSub = STATE_PLAYING_STAGE_CLEAR
            return True
        else:
            # 最終ステージクリア時
            import Common
            Common.GameState = Common.STATE_GAMECLEAR
            return True
    return False

# 攻撃ステート管理用の変数
attack_selection_timer = 0
ATTACK_SELECTION_INTERVAL = 240  # 攻撃選択間隔（フレーム：4秒）
ATTACK_CHANCE = 0.75  # 攻撃選択確率（75%で非常に頻繁に）

def update_enemy_attack_selection():
    """敵の攻撃ステート選択を管理する"""
    global attack_selection_timer
    
    # 攻撃選択タイマーの更新
    attack_selection_timer += 1
    
    # 一定間隔で攻撃する敵を選択
    if attack_selection_timer >= ATTACK_SELECTION_INTERVAL:
        attack_selection_timer = 0
        
        # 通常状態かつクールダウン中でない敵のみを対象に攻撃選択を行う
        normal_enemies = [e for e in enemy_list if e.active and e.state == 0 and e.attack_cooldown_timer == 0]  # ENEMY_STATE_NORMAL = 0
        
        if normal_enemies:
            # ランダムに敵を選択して攻撃準備状態にする
            if random.random() < ATTACK_CHANCE:
                selected_enemy = random.choice(normal_enemies)
                selected_enemy.state = 1  # ENEMY_STATE_PREPARE_ATTACK = 1
                selected_enemy.attack_timer = 0  # タイマーリセット
