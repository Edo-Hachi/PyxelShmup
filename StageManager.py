# Stage Management
# Handles enemy spawn patterns and stage progression


#ソースコードの中のコメントは日本語にしましょう
# #画面に出力する文字列は英語にしてください。pyxelは日本語フォントを表示できません
# CLAUDE.md を書き込むときは英語にしてください
# 変数の型は宣言してください

import Config
import GameState

# Enemy spawn patterns (10x4 grid)
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

def get_current_stage_map():
    """Get enemy spawn pattern for current stage"""
    stage_maps = {
        1: ENEMY_MAP_STG01,
        2: ENEMY_MAP_STG02,
        3: ENEMY_MAP_STG03,
        4: ENEMY_MAP_STG04,
    }
    return stage_maps.get(GameState.CURRENT_STAGE, ENEMY_MAP_STG01)

def check_stage_clear(enemy_list):
    """Check if all enemies are defeated and handle stage progression"""
    # Check if any active enemies remain
    active_enemies = [e for e in enemy_list if e.active]
    
    # デバッグ出力を大幅削減（初回のみ、または変化があった時のみ）
    if Config.DEBUG and not hasattr(check_stage_clear, 'last_count'):
        check_stage_clear.last_count = len(active_enemies)
        GameState.debug_print(f"[DEBUG] check_stage_clear: {len(active_enemies)} enemies remaining")
    elif Config.DEBUG and len(active_enemies) != check_stage_clear.last_count:
        check_stage_clear.last_count = len(active_enemies)
        GameState.debug_print(f"[DEBUG] Enemy count changed: {len(active_enemies)} enemies remaining")
    
    if not active_enemies:
        GameState.debug_print(f"[DEBUG] Stage Clear! No enemies remaining")
        if GameState.CURRENT_STAGE < Config.MAX_STAGE:
            GameState.GameStateSub = Config.STATE_PLAYING_STAGE_CLEAR
            return True
        else:
            # Final stage clear
            GameState.GameState = Config.STATE_GAMECLEAR
            return True
    return False