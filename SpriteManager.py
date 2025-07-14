# Sprite Management
# Handles sprite definitions and sprite-related utilities

from collections import namedtuple
import Config

# Sprite Location Definition
SpIdx = namedtuple("SprIdx", ["x", "y"])

# Sprite Dictionary - 8x8 sprites
SprList = {
    'NULL': SpIdx(0, 0),  # NULL
    "TOP": SpIdx(8, 0),  # TOP
    "LEFT": SpIdx(16, 0),  # LEFT
    "RIGHT": SpIdx(24, 0),  # RIGHT
    "NULL": SpIdx(32, 0),   # NULL

    "BULLET01": SpIdx(40, 0),  # BULLET
    "BULLET02": SpIdx(48, 0),  

    "EXT01": SpIdx(56, 0),  # Ship Exhaust
    "EXT02": SpIdx(64, 0),  # Ship Exhaust
    "EXT03": SpIdx(72, 0),  # Ship Exhaust
    "EXT04": SpIdx(80, 0),  # Ship Exhaust

    "MUZL01": SpIdx(88, 0),  # MuzzleFlash01
    "MUZL02": SpIdx(96, 0),  # MuzzleFlash02
    "MUZL03": SpIdx(104, 0),  # MuzzleFlash03
    "NULL": SpIdx(112, 0),
    "ENEMY_BULLET": SpIdx(120, 0),

    "NULL": SpIdx(0, 8),    # NULL
    
    "ENEMY01_0": SpIdx(8, 8),    # Enemy01_0
    "ENEMY01_1": SpIdx(16, 8),   # Enemy01_1
    "ENEMY01_2": SpIdx(24, 8),   # Enemy01_2
    "ENEMY01_3": SpIdx(32, 8),   # Enemy01_3

    "ENEMY02_0": SpIdx(40, 8),   # Enemy02_0
    "ENEMY02_1": SpIdx(48, 8),   # Enemy02_1
    "ENEMY02_2": SpIdx(56, 8),   # Enemy02_2
    "ENEMY02_3": SpIdx(64, 8),   # Enemy02_3

    "ENEMY03_0": SpIdx(72, 8),   # Enemy03_0
    "ENEMY03_1": SpIdx(80, 8),   # Enemy03_1
    "ENEMY03_2": SpIdx(88, 8),   # Enemy03_2
    "ENEMY03_3": SpIdx(96, 8),   # Enemy03_3

    "ENEMY04_0": SpIdx(104, 8),   # Enemy04_0
    "ENEMY04_1": SpIdx(112, 8),   # Enemy04_1
    "ENEMY04_2": SpIdx(120, 8),   # Enemy04_2
    "ENEMY04_3": SpIdx(128, 8),   # Enemy04_3

    "ENEMY05_0": SpIdx(136, 8),   # Enemy05_0
    "ENEMY05_1": SpIdx(144, 8),   # Enemy05_1
    "ENEMY05_2": SpIdx(152, 8),   # Enemy05_2
    "ENEMY05_3": SpIdx(160, 8),   # Enemy05_3
}

# Enemy Sprite Helper
MAX_ENEMY_NUM = 5
MAX_ANIM_PAT = 4

def get_enemy_sprite(enemy_num: int, anim_pat: int) -> SpIdx:
    """Return SpIdx for given enemy number and animation pattern."""
    enemy_num = max(1, min(enemy_num, MAX_ENEMY_NUM))
    anim_pat = anim_pat % MAX_ANIM_PAT
    
    key = f"ENEMY{enemy_num:02d}_{anim_pat}"
    return SprList.get(key, SprList["NULL"])