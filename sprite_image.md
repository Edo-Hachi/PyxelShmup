# スプライト画像管理の改善案

## 現状の問題点

現在の`SpriteManager.py`では、`my_resource.pyxres`内のビットマップスプライトデータに対して、ハードコードされた座標配列を使用している。

```python
# 現在の実装
SprList = {
    'NULL': SpIdx(0, 0),
    "TOP": SpIdx(8, 0),
    "LEFT": SpIdx(16, 0),
    "RIGHT": SpIdx(24, 0),
    "BULLET01": SpIdx(40, 0),
    "ENEMY01_0": SpIdx(8, 8),
    "ENEMY01_1": SpIdx(16, 8),
    # ... 以下続く
}
```

**課題:**
- `my_resource.pyxres`の内容が変更されても、座標を手動で更新する必要がある
- スプライトの配置を動的にトレースする仕組みがない
- 保守性が低い

## 改善案の比較

### アプローチ1: 設定ファイル方式

```python
# sprites.json または sprites.yaml
{
  "sprite_size": 8,
  "sheets": [
    {
      "name": "player",
      "row": 0,
      "sprites": ["top", "left", "right", "null"]
    },
    {
      "name": "weapons", 
      "row": 0,
      "start_col": 5,
      "sprites": ["bullet01", "bullet02"]
    },
    {
      "name": "enemies",
      "row": 1,
      "start_col": 1,
      "pattern": "enemy{type:02d}_{frame}",
      "types": 5,
      "frames": 4
    }
  ]
}
```

**メリット:**
- 設定とコードの分離
- 非プログラマーでも編集可能
- 柔軟な構成変更

**デメリット:**
- 設定ファイルの管理が必要
- JSONの構文エラーリスク

### アプローチ2: コンベンション方式

```python
class SpriteManager:
    def __init__(self, sprite_size=8):
        self.sprite_size = sprite_size
        self.sprites = {}
        
    def define_grid(self, name, start_x, start_y, cols, rows, names=None):
        """グリッド形式でスプライトを定義"""
        for row in range(rows):
            for col in range(cols):
                if names and row * cols + col < len(names):
                    sprite_name = names[row * cols + col]
                else:
                    sprite_name = f"{name}_{row}_{col}"
                
                self.sprites[sprite_name] = SpIdx(
                    start_x + col * self.sprite_size,
                    start_y + row * self.sprite_size
                )
    
    def define_sequence(self, pattern, start_x, start_y, count, direction='horizontal'):
        """連続スプライトを定義"""
        for i in range(count):
            name = pattern.format(i)
            if direction == 'horizontal':
                x = start_x + i * self.sprite_size
                y = start_y
            else:
                x = start_x
                y = start_y + i * self.sprite_size
            
            self.sprites[name] = SpIdx(x, y)

# 使用例:
sprite_manager = SpriteManager()
sprite_manager.define_grid("player", 8, 0, 4, 1, ["top", "left", "right", "null"])
sprite_manager.define_sequence("enemy01_{}", 8, 8, 4)
sprite_manager.define_sequence("enemy02_{}", 40, 8, 4)
```

**メリット:**
- プログラマティックな定義
- 動的な生成が可能
- パターンの自動化

**デメリット:**
- コードの複雑性増加
- 規則性がないスプライトには不向き

### アプローチ3: 自動検出方式（高度）

```python
import pyxel

class SmartSpriteManager:
    def __init__(self, resource_file):
        pyxel.load(resource_file)
        self.auto_detect_sprites()
    
    def auto_detect_sprites(self):
        """画像を解析してスプライト境界を自動検出"""
        # 透明度やカラーキーを使ってスプライト境界を検出
        # エッジ検出アルゴリズムでスプライトを分離
        pass
    
    def scan_pattern(self, pattern, start_pos, grid_size):
        """特定パターンでスプライトをスキャン"""
        pass
```

**メリット:**
- 完全自動化
- 手動設定不要

**デメリット:**
- 実装の複雑さ
- 検出精度の問題
- Pyxelの制限

## 推奨案: 分離されたリソース管理

スプライトデータを`my_resource.pyxres`で一括管理するのではなく、エンティティごとに分離する。

### ファイル構成
```
resources/
├── player.pyxres       # プレイヤー機体のスプライト
├── enemies.pyxres      # 全敵機のスプライト
├── bullets.pyxres      # 弾丸関連のスプライト
├── effects.pyxres      # エフェクト・爆発
├── ui.pyxres          # UI要素
└── sounds.pyxres      # 効果音（分離可能なら）
```

### 対応するスプライトマネージャー

```python
# SpriteManager.py の改良版
@dataclass
class SpriteInfo:
    x: int
    y: int
    sheet: int  # どのスプライトシートか

class ModularSpriteManager:
    def __init__(self):
        self.sprite_sheets = {}
        self.sprites = {}
        self._load_resources()
    
    def _load_resources(self):
        # プレイヤー専用リソース
        self.sprite_sheets['player'] = 0
        pyxel.load("resources/player.pyxres", tilemap=False, sound=False)
        self._define_player_sprites()
        
        # 敵専用リソース  
        self.sprite_sheets['enemies'] = 1
        pyxel.load("resources/enemies.pyxres", tilemap=False, sound=False)
        self._define_enemy_sprites()
        
        # 弾丸専用リソース
        self.sprite_sheets['bullets'] = 2
        pyxel.load("resources/bullets.pyxres", tilemap=False, sound=False)
        self._define_bullet_sprites()
    
    def _define_player_sprites(self):
        """プレイヤー機体のスプライト定義"""
        player_sprites = {
            'top': (0, 0),
            'left': (8, 0), 
            'right': (16, 0),
            'exhaust_1': (0, 8),
            'exhaust_2': (8, 8),
            'exhaust_3': (16, 8),
            'exhaust_4': (24, 8),
            'muzzle_1': (0, 16),
            'muzzle_2': (8, 16),
            'muzzle_3': (16, 16),
        }
        
        for name, (x, y) in player_sprites.items():
            self.sprites[name] = SpriteInfo(
                x, y, self.sprite_sheets['player']
            )
    
    def _define_enemy_sprites(self):
        """敵機のスプライト定義 - 整理された配置"""
        for enemy_type in range(1, 6):
            for frame in range(4):
                name = f"enemy{enemy_type:02d}_{frame}"
                # 敵専用シートなので0から配置可能
                x = frame * 8
                y = (enemy_type - 1) * 8
                self.sprites[name] = SpriteInfo(
                    x, y, self.sprite_sheets['enemies']
                )
    
    def _define_bullet_sprites(self):
        """弾丸のスプライト定義"""
        bullet_sprites = {
            'player_bullet': (0, 0),
            'enemy_bullet': (8, 0),
            'power_bullet': (16, 0),
        }
        
        for name, (x, y) in bullet_sprites.items():
            self.sprites[name] = SpriteInfo(
                x, y, self.sprite_sheets['bullets']
            )

    def draw_sprite(self, sprite_name, x, y):
        """スプライトを描画"""
        sprite = self.sprites[sprite_name]
        pyxel.blt(x, y, sprite.sheet, sprite.x, sprite.y, 8, 8, pyxel.COLOR_BLACK)
```

### 使用時の改良

```python
# Player.py での使用例
def draw(self):
    sprite = sprite_manager.sprites[self.sprite_name]
    pyxel.blt(self.x, self.y, sprite.sheet, sprite.x, sprite.y, 8, 8, pyxel.COLOR_BLACK)
```

## 分離されたリソース管理のメリット

1. **関心事の分離**: 各エンティティが自分のリソースを持つ
2. **並行開発**: アーティストが独立してスプライトを作成可能
3. **メモリ効率**: 必要なリソースのみロード可能
4. **保守性**: 敵を追加する時は`enemies.pyxres`だけ更新
5. **テスト容易**: 個別のスプライトシートでテスト可能
6. **ファイル管理**: 責任の所在が明確

## 段階的移行計画

1. **Phase 1**: 現在の`my_resource.pyxres`から分離
2. **Phase 2**: 各ファイルに対応するスプライト定義クラス作成
3. **Phase 3**: 動的ロードシステムの実装

## 結論

ファイル数は増えるが、各リソースの責任が明確になり、保守性が大幅に向上する。特に複数人での開発や長期的なメンテナンスにおいて、この分離アプローチが最も適している。

## 即座に実装可能な改善案

現在のコードを少し改良するだけでも改善可能：

```python
# SpriteManager.py の改良版
class SpriteLayout:
    def __init__(self, sprite_size=8):
        self.size = sprite_size
        self.sprites = {}
        self._build_layout()
    
    def _build_layout(self):
        # プレイヤー関連 (Row 0)
        self._add_row(0, ['null', 'top', 'left', 'right', 'null', 
                         'bullet01', 'bullet02', 'ext01', 'ext02', 'ext03', 'ext04',
                         'muzl01', 'muzl02', 'muzl03', 'null', 'enemy_bullet'])
        
        # 敵スプライト (Row 1) - 自動生成
        self._add_enemy_sprites(1)
    
    def _add_row(self, row, names):
        for col, name in enumerate(names):
            if name != 'null':
                self.sprites[name] = SpIdx(col * self.size, row * self.size)
    
    def _add_enemy_sprites(self, row):
        for enemy_type in range(1, 6):
            for frame in range(4):
                name = f"enemy{enemy_type:02d}_{frame}"
                col = (enemy_type - 1) * 4 + frame + 1
                self.sprites[name] = SpIdx(col * self.size, row * self.size)
```

この方法により、スプライトレイアウトの変更に対してより柔軟に対応できるようになる。