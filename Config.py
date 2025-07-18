#ソースコードの中のコメントは日本語にしましょう
# #画面に出力する文字列は英語にしてください。pyxelは日本語フォントを表示できません
# CLAUDE.md を書き込むときは英語にしてください
# 変数の型は宣言してください

# Game Configuration Constants
# All hardcoded values centralized here for easy modification

# Game Information
VERSION = "0.1.6"
LAUNCH_DATE = "2025/07/17"

# Development Settings
DEBUG = False

# Window Settings
WIN_WIDTH = 128
WIN_HEIGHT = 128
DISPLAY_SCALE = 5
FPS = 60

# Sprite Banks
TILE_BANK0 = 0
TILE_BANK1 = 1
TILE_BANK2 = 2

# Game State Constants
STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_PAUSE = 3
STATE_GAMECLEAR = 4

# Playing Sub-States
STATE_PLAYING_ENEMY_ENTRY = 0
STATE_PLAYING_ENEMY_SPAWN = 1
STATE_PLAYING_FIGHT = 2
STATE_PLAYING_STAGE_CLEAR = 3

# Stage Management
MAX_STAGE = 4

# Visual Effects
STOP_TIME = 20
SHAKE_TIME = 10
SHAKE_STRENGTH = 10



# Audio Settings
# (Audio channels are hardcoded in each class for simplicity)