# Game State Management
# Centralized state variables and game progression logic

#ソースコードの中のコメントは日本語にしましょう
# #画面に出力する文字列は英語にしてください。pyxelは日本語フォントを表示できません
# CLAUDE.md を書き込むときは英語にしてください
# 変数の型は宣言してください

import Config

# Current Game State
GameState = Config.STATE_TITLE
GameStateSub = Config.STATE_PLAYING_ENEMY_ENTRY

# Stage Management
CURRENT_STAGE = 1

# Camera Effects
ShakeTimer = 0
StopTimer = 0

# Game System Timer
GameTimer = 0

# Score Management
HighScore = 0
Score = 0

# Enemy Movement
ENEMY_MOVE_RIGHT = 1
ENEMY_MOVE_LEFT = -1
enemy_move_direction = ENEMY_MOVE_RIGHT
enemy_group_x = 0

# Attack Selection Management
attack_selection_timer = 0

def debug_print(*args, **kwargs):
    """Debug output function"""
    if Config.DEBUG:
        print(*args, **kwargs)

def reset_game_state():
    """Reset all game state variables for new game"""
    global GameState, GameStateSub, CURRENT_STAGE, ShakeTimer, StopTimer
    global GameTimer, Score, enemy_move_direction, enemy_group_x, attack_selection_timer
    
    GameState = Config.STATE_TITLE
    GameStateSub = Config.STATE_PLAYING_ENEMY_ENTRY
    CURRENT_STAGE = 1
    ShakeTimer = 0
    StopTimer = 0
    GameTimer = 0
    Score = 10  # Starting score
    enemy_move_direction = ENEMY_MOVE_RIGHT
    enemy_group_x = 0
    attack_selection_timer = 0