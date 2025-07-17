# プレイヤー弾丸とエグゾーストのJSON制御 - コードレビュー

プレイヤー弾丸とエグゾーストのJSON制御について詳しく説明します。

## 1. プレイヤー弾丸のJSON制御

### データ構造（sprites.json）
```json
"40_0": {
  "NAME": "PBULLET",
  "FRAME_NUM": "0",
  "ANIM_SPD": "20"
},
"48_0": {
  "NAME": "PBULLET", 
  "FRAME_NUM": "1",
  "ANIM_SPD": "25"
}
```

### 処理の流れ

**1. Bullet.py:28** - アニメーションフレーム計算
```python
anim_frame = get_bullet_animation_frame(GameState.GameTimer)
```

**2. SpriteManager.py:253-271** - フレーム計算ロジック
```python
def get_bullet_animation_frame(game_timer, animation_speed=None):
    if animation_speed is None:
        animation_speed = sprite_manager.get_bullet_animation_duration()
    
    cycle_position = game_timer % (animation_speed * 2)
    return 0 if cycle_position < animation_speed else 1
```

**3. SpriteManager.py:186-203** - JSON持続時間取得
```python
def get_bullet_animation_duration(self):
    for key, sprite in self.json_sprites.items():
        if sprite.get("NAME") == "PBULLET":
            anim_spd = sprite.get("ANIM_SPD")
            if anim_spd:
                return int(anim_spd)
    return 3  # デフォルト値
```

**4. SpriteManager.py:162-184** - スプライト座標取得
```python
def get_bullet_sprite(self, frame_number):
    frame_str = str(frame_number % 2)
    for key, sprite in self.json_sprites.items():
        if sprite.get("NAME") == "PBULLET" and sprite.get("FRAME_NUM") == frame_str:
            return SpIdx(sprite["x"], sprite["y"])
```

## 2. エグゾーストのJSON制御

### データ構造（sprites.json）
```json
"56_0": {"NAME": "EXHST", "FRAME_NUM": "0", "ANIM_SPD": "10"},
"64_0": {"NAME": "EXHST", "FRAME_NUM": "1", "ANIM_SPD": "10"},
"72_0": {"NAME": "EXHST", "FRAME_NUM": "2", "ANIM_SPD": "10"},
"80_0": {"NAME": "EXHST", "FRAME_NUM": "3", "ANIM_SPD": "10"}
```

### 処理の流れ

**1. Player.py:61-68** - JSON駆動のタイマー制御
```python
exhaust_duration = sprite_manager.get_exhaust_animation_duration()
self.ExtTimer += 1

if self.ExtTimer >= exhaust_duration:
    self.ExtTimer = 0
    self.ExtIndex += 1
    if self.ExtIndex >= ExtMax:
        self.ExtIndex = 0
```

**2. Player.py:138-140** - JSON駆動のスプライト描画
```python
exhaust_sprite = sprite_manager.get_exhaust_sprite(self.ExtIndex)
pyxel.blt(self.x, self.y+8, Config.TILE_BANK0,
    exhaust_sprite.x, exhaust_sprite.y, self.width, self.height, pyxel.COLOR_BLACK)
```

**3. SpriteManager.py:205-227** - スプライト座標取得
```python
def get_exhaust_sprite(self, frame_number):
    frame_str = str(frame_number % 4)
    for key, sprite in self.json_sprites.items():
        if sprite.get("NAME") == "EXHST" and sprite.get("FRAME_NUM") == frame_str:
            return SpIdx(sprite["x"], sprite["y"])
```

## 3. JSON読み込み・管理システム

### 初期化（SpriteManager.py:79-82）
```python
def __init__(self):
    self.json_sprites = {}
    self.json_file_path = "sprites.json"
    self.load_sprites_json()
```

### 読み込み処理（SpriteManager.py:84-103）
```python
def load_sprites_json(self):
    try:
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                sprite_data = json.load(f)
            
            if "sprites" in sprite_data:
                self.json_sprites = sprite_data["sprites"]
```

## 技術的特徴

1. **JSON優先設計**: ハードコーディングよりJSON設定を優先
2. **フォールバック機能**: JSON読み込み失敗時は従来のSprListを使用
3. **動的アニメーション**: ANIM_SPDフィールドで速度調整可能
4. **統一フィールド**: NAME, FRAME_NUM, ANIM_SPD, ACT_NAMEで構造化

これにより、コードを再コンパイルすることなくsprites.jsonを編集するだけでアニメーション速度やスプライト位置を変更できます。