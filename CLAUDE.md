# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Game
```bash
python main.py
```

### Prerequisites
- Python 3.7 or higher
- Pyxel game engine: `pip install pyxel`

### Virtual Environment
The project includes a `venv/` directory. Activate it with:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

## Code Architecture

### Core Structure
This is a 2D shoot-em-up game built with the Pyxel game engine featuring:

- **Main Game Loop**: `main.py` - Contains the main `App` class with game states (Title, Playing, Game Over)
- **Modular Architecture**: Refactored into specialized modules for better maintainability
  - `Config.py` - Centralized configuration constants
  - `GameState.py` - Game state management and progression
  - `SpriteManager.py` - Sprite definitions and utilities
  - `StageManager.py` - Stage management and enemy patterns
  - `Common.py` - Core utilities (collision detection, entity lists)
- **Entity System**: Object-oriented approach with separate classes for game entities

### Key Components

#### Game States
- `STATE_TITLE`: Title screen with star field background
- `STATE_PLAYING`: Main gameplay with sub-states for enemy spawning, fighting, and stage clear
- `STATE_GAMEOVER`: Game over screen
- `STATE_PAUSE`: Pause functionality

#### Entity Classes
- **Player** (`Player.py`): Player ship with movement, shooting, collision, and invincibility mechanics
- **Enemy** (`Enemy.py`): Enemy entities with AI, group movement, multi-stage attack behavior, and shooting patterns
- **Bullet** (`Bullet.py`): Player projectiles
- **EnemyBullet** (`EnemyBullet.py`): Enemy projectiles
- **ExplodeManager** (`ExplodeManager.py`): Particle system for explosions
- **StarManager** (`StarManager.py`): Background star field animation

#### Core Game Systems
- **Collision Detection**: AABB collision system in `Common.check_collision()`
- **Stage Management**: 4 stages with different enemy spawn patterns defined in `StageManager.py`
- **Group Enemy Movement**: Enemies move as a cohesive group with direction changes at screen edges
- **Multi-Stage Enemy Attack System**: Enemies can transition between formation movement and individual attack behavior
- **Hit Effects**: Screen shake, hit-stop timing, and particle explosions
- **Scoring System**: Points awarded for enemy destruction

### Important Constants & Configuration

#### Game Settings
- Window size: 128x128 pixels
- Frame rate: 60 FPS  
- Display scale: 5x
- Sprite banks: 0, 1, 2

#### Sprite Management
- Sprites defined in `SpriteManager.SprList` dictionary using `SpIdx` namedtuple
- Enemy sprites support 4-frame animation cycles
- `get_enemy_sprite()` function handles sprite indexing for 5 enemy types

#### Stage Data
- Enemy spawn patterns stored as 10x4 grids in `ENEMY_MAP_STG01` through `ENEMY_MAP_STG04` in `StageManager.py`
- Numbers 1-5 represent different enemy types
- `get_current_stage_map()` returns appropriate pattern for current stage

### Audio Resources
- Sound effects stored in `my_resource.pyxres` Pyxel resource file
- Channel 0 used for player shooting and enemy destruction sounds

### Enemy Attack System
The game features a sophisticated multi-stage enemy attack system with the following states:

#### Attack States
- **NORMAL** (0): Standard formation movement with the group
- **PREPARE_ATTACK** (1): Pre-attack preparation with visual shaking effects
- **ATTACK** (2): Individual attack descent with swaying movement
- **RETURNING** (3): Waiting state at screen bottom before returning
- **DESCENDING** (4): Returning to formation position

#### Attack Mechanics
- Enemies break formation individually to perform attack dives
- Preparation phase includes visual feedback (shaking) to telegraph attacks
- Attack descent features swaying movement for dynamic challenge
- Enemies return to formation after completing attack runs
- Cooldown system prevents immediate repeat attacks

#### Configuration Constants
- `PREPARE_ATTACK_DURATION`: 180 frames (3 seconds) preparation time
- `ATTACK_MOVE_SPEED`: 0.8 pixels per frame descent speed
- `ATTACK_SWAY_AMPLITUDE`: 1.5 pixels left-right sway range
- `RETURN_DELAY`: 120 frames (2 seconds) before returning
- `ATTACK_COOLDOWN`: 300 frames (5 seconds) post-attack cooldown

### Debug Features
- `Config.DEBUG` flag enables collision box visualization
- Green boxes for player, red boxes for enemies when enabled

## Development Notes

### Code Style
- Japanese comments mixed with English
- Modular state management through specialized modules
- Entity lists stored globally in `Common.py`: `enemy_list`, `player_bullet_list`, `enemy_bullet_list`
- Configuration constants centralized in `Config.py`
- Game state variables managed in `GameState.py`

### ⚠️ **重要開発方針** - JSON設定の優先
- **JSONファイル（sprites.json）のアニメーション設定が最優先**
- ハードコーディングされたフレーム数よりもJSON設定を優先する
- JSON の tags[2] がアニメーション持続フレーム数を定義
- 新機能追加時は必ずJSON設定に対応したタイマー制御を実装
- 例：エグゾースト、弾丸、エフェクト等の全アニメーション

### Game Balance
- Enemy shooting probability increases as fewer enemies remain
- Player has invincibility frames after being hit with visual feedback
- Screen shake and hit-stop effects for impact feedback
- Enemy attack behavior includes preparation phase with visual feedback (shaking)
- Multi-stage enemy attack patterns with formation breaking and returning

### Resource Management
- Automatic garbage collection of inactive bullets and enemies
- Particle system manages explosion effects independently
- Virtual environment included for dependency isolation

---

# PyxelShmup リファクタリング記録

## 概要
2025年7月14日実施の大規模リファクタリングにより、コードの保守性と可読性を大幅に向上させた。

## 主な成果

### 📊 数値的改善
- **Common.py**: 261行 → 43行 (83%削減)
- **変更ファイル数**: 21ファイル
- **コード行数**: +1,050行追加、-418行削除
- **新規作成モジュール**: 5つ

### 🏗️ アーキテクチャ改善

#### Before (問題点)
```
Common.py (261行)
├── 設定定数 (40+項目)
├── ゲーム状態管理
├── スプライト定義
├── ステージ管理
├── 衝突判定
├── 敵攻撃管理
└── その他ユーティリティ
```

#### After (改善後)
```
Config.py (設定定数の一元管理)
├── ゲーム基本設定
├── プレイヤー設定
├── 敵設定
├── 弾丸設定
├── エフェクト設定
└── オーディオ設定

GameState.py (ゲーム状態管理)
├── 現在のゲーム状態
├── ステージ進行
├── スコア管理
├── カメラエフェクト
└── デバッグ機能

SpriteManager.py (スプライト管理)
├── スプライト座標定義
├── 敵スプライト取得
└── アニメーション管理

StageManager.py (ステージ管理)
├── 敵配置パターン
├── ステージクリア判定
└── ステージ進行管理

Common.py (コアユーティリティ)
├── エンティティリスト
├── 衝突判定
├── 敵攻撃選択
└── 爆発管理
```

## 🔧 実施した改善作業

### Phase 1: 分析と計画
- 既存コードの構造分析
- 問題点の特定
- リファクタリング戦略の策定

### Phase 2: モジュール分割
1. **Config.py作成** - 全設定定数を集約
2. **GameState.py作成** - ゲーム状態管理を分離
3. **SpriteManager.py作成** - スプライト定義を独立化
4. **StageManager.py作成** - ステージ管理を分離
5. **Common.py再設計** - コアユーティリティのみに絞り込み

### Phase 3: 全ファイル更新
- import文の新構造対応
- 定数参照の修正
- 関数呼び出しの更新
- エラー修正と動作確認

## 📁 作成されたファイル

### Config.py
- 全設定定数の集約 (VERSION, WIN_WIDTH, PLAYER_SPEED, etc.)
- ゲーム基本設定からオーディオ設定まで40+項目

### GameState.py
- ゲーム状態管理 (GameState, GameStateSub, CURRENT_STAGE)
- スコア管理とカメラエフェクト
- デバッグ機能とリセット機能

### SpriteManager.py
- スプライト定義と管理 (SprList辞書)
- 敵スプライト取得機能 (get_enemy_sprite)
- アニメーションパターン管理

### StageManager.py
- ステージ管理 (ENEMY_MAP_STG01-04)
- ステージクリア判定 (check_stage_clear)
- ステージ進行管理

## 🎯 具体的な改善内容

### 1. 責任の分離
- 各モジュールが単一責任を持つ
- 機能ごとの明確な境界

### 2. 依存関係の改善
- 循環依存の解消
- 必要な部分のみをimport

### 3. 設定の一元化
- 全ての定数をConfig.pyに集約
- 設定変更が一箇所で完結

### 4. コードの保守性向上
- 新機能追加時の影響範囲限定
- デバッグとテストの容易化

## 🚀 今後の拡張可能性

### 検討された追加改善案
1. **BaseBullet class** - 弾丸システムの統一
2. **BaseParticle class** - 爆発エフェクトの統一
3. **分離されたリソース管理** - スプライトファイルの分割

### スプライト管理の将来構想
```
resources/
├── player.pyxres       # プレイヤー専用
├── enemies.pyxres      # 敵機専用
├── bullets.pyxres      # 弾丸専用
├── effects.pyxres      # エフェクト専用
└── ui.pyxres          # UI専用
```

## 💡 学んだ教訓

### 設計原則の重要性
- **単一責任の原則**: 各モジュールが一つの責任を持つ
- **関心事の分離**: 機能ごとの明確な境界
- **設定の外部化**: ハードコーディングの回避

### リファクタリングの進め方
1. **現状分析**: 問題点の特定
2. **計画策定**: 段階的なアプローチ
3. **段階的実装**: 小さな変更の積み重ね
4. **継続的テスト**: 各段階での動作確認

## 🎉 最終結果

### 技術的成果
- **可読性**: コードの理解が容易
- **保守性**: 変更の影響範囲が限定
- **拡張性**: 新機能追加が簡単
- **テスト容易性**: 個別モジュールのテストが可能

### 開発効率の向上
- 設定変更が一箇所で完結
- 機能追加時の影響範囲が明確
- デバッグ時の問題箇所特定が容易
- 複数人での並行開発が可能

## 🔚 まとめ

大規模なリファクタリングにより、PyxelShmupプロジェクトの技術的負債を大幅に削減し、将来の開発に向けた堅牢な基盤を構築した。特にCommon.pyの83%削減により、コードの見通しが大幅に改善され、保守性が向上した。

今後はこの新しいアーキテクチャを基盤として、より効率的な開発が可能になる。

---

# SpriteDefiner開発記録

## 概要
2025年7月15日、スプライト管理の改善を目的として、ビジュアルなスプライト定義ツール「SpriteDefiner」を開発・完成させた。

## 開発経緯

### 課題
- ゲーム本体のスプライト座標がハードコーディングされていた
- 新しいスプライトの追加や変更時の工数が大きい
- 設定ファイル化による保守性向上が必要

### 解決方針
JSON形式の設定ファイルを基盤とした、ビジュアルなスプライト定義システムの構築

## 開発プロセス

### Phase 1: 基本コンセプト設計
- 単純なJSON設定アプローチから開始
- ビジュアル編集ツールのコンセプト確立
- SpriteDefiner.py（v1）の実装

### Phase 2: 機能拡張と改善
- SpriteDefiner_v2.pyへの大幅機能強化
- 編集履歴システムの実装
- 安全性機能の追加

## 🎯 SpriteDefiner_v2.py の主要機能

### コア機能
- **ビジュアルスプライトシート表示**: 8x8グリッドオーバーレイ付き
- **マウス・キーボード操作**: 直感的な操作インターフェース
- **モード切替システム**: VIEW/EDITモードによる安全な編集
- **拡張タグシステム**: DIC1-3 + EXT1-5 による柔軟なメタデータ管理

### 安全性機能
- **F-keyコントロール**: F1(EDIT), F2(VIEW), F10(SAVE), F11(LOAD), F12(QUIT)
- **Y/N確認ダイアログ**: 上書き保存・終了時の確認プロンプト
- **ESC/Q無効化**: 誤操作防止のためのキー無効化
- **編集ロック機能**: EDITモード中のスプライト位置固定

### 編集履歴システム
- **シンプルな名前リスト**: 複雑な操作ログではなく、編集したスプライト名の履歴
- **重複除去**: 同じ名前の重複を自動除去して最新を末尾に移動
- **6件表示**: 最新6件の編集履歴を常時表示
- **最適配置**: 画面右端での常時表示により編集効率向上

## 📁 出力形式

### sprites.json構造
```json
{
  "meta": {
    "sprite_size": 8,
    "resource_file": "my_resource.pyxres",
    "created_by": "SpriteDefiner v2",
    "version": "2.0"
  },
  "sprites": {
    "position_key": {
      "x": coordinate,
      "y": coordinate,
      "name": "GROUP_NAME",
      "tags": ["DIC1", "DIC2", "DIC3", "EXT1", "EXT2"]
    }
  }
}
```

### タグシステム設計
- **DIC1 (ACT_NAME)**: アクション名定義
- **DIC2 (FRAME_NUM)**: フレーム番号
- **DIC3 (ANIM_SPEED)**: アニメーション速度
- **EXT1-EXT5**: 将来の拡張用タグ

## 🔧 技術的特徴

### グループベース命名
- 複数のスプライトが同じNAMEを持てる設計
- position_keyによる一意性確保
- 同じグループ内での異なるDICタグ設定が可能

### UIデザイン
- **リアルタイムフィードバック**: カーソル位置の即座反映
- **色分けされた表示**: モード別の視覚的フィードバック
- **情報密度最適化**: 必要な情報の効率的配置

### 操作安全性
- **データ損失防止**: 確認ダイアログによる誤操作防止
- **自動保存**: EDITモード終了時の自動セーブ
- **状態管理**: 編集中の状態を明確に表示

## 💾 成果物

### 作成されたスプライト定義
現在のsprites.jsonには以下のスプライトが定義済み：
- **PLAYER**: TOP, LEFT, RIGHT (3フレーム)
- **PBULLET**: プレイヤー弾丸 (2種類)
- **EXHST**: 排気エフェクト (4フレーム)
- **MZLFLSH**: マズルフラッシュ (2フレーム)
- **ENMYBLT**: 敵弾丸

## 🚀 次回開発予定

### ゲーム本体統合
1. **JSON読み込み機能**: sprites.jsonからのデータ読み込み
2. **スプライト展開処理**: ゲーム内でのスプライトデータ活用
3. **既存ハードコーディング置換**: SpriteManager.pyの更新
4. **動的スプライト管理**: 実行時でのスプライト切り替え

### 期待される効果
- **開発効率向上**: スプライト変更の簡略化
- **保守性向上**: 設定ファイルによる管理
- **拡張性確保**: 新スプライトの容易な追加
- **チーム開発支援**: ビジュアルツールによる共同作業

## 💡 開発で得られた知見

### ツール設計の重要性
- **ユーザビリティファースト**: 開発者が使いやすいツール設計
- **安全性の重要性**: データ損失防止機能の必要性
- **フィードバックの価値**: リアルタイムな視覚的フィードバック

### インクリメンタル開発
- **段階的機能追加**: 基本機能から始めて段階的に高機能化
- **ユーザーフィードバック反映**: 実際の使用経験からの改善
- **継続的な改善**: 使いやすさの追求

SpriteDefinerの開発により、PyxelShmupプロジェクトのスプライト管理が大幅に改善され、次の段階であるゲーム本体統合への準備が整った。

---

# SpriteDefinerリファクタリング・UI改善記録

## 概要
2025年7月15日、SpriteDefiner.pyの大規模リファクタリングと多言語対応の改善を実施した。

## 実施内容

### Phase 1: コードリファクタリング
- **問題点の特定**: 743行の巨大な単一クラスによる保守性の低下
- **単一責任の原則適用**: 各メソッドが単一の責任を持つよう分割
- **状態管理の改善**: AppStateのEnumを使用したクリーンな状態管理
- **共通処理の抽出**: テキスト入力処理の共通化

### Phase 2: 機能改善
- **バグ修正**: EDITモードでのDIC変更時の状態遷移問題を解決
- **視覚的一貫性**: EDIT/COMMAND_INPUTモードでの一貫したグリッド色表示
- **起動時自動読み込み**: sprites.jsonの自動読み込み機能追加
- **エラーハンドリング**: ファイル読み込み時の適切なエラー処理

### Phase 3: 多言語対応の適正化
- **問題認識**: Pyxelの日本語フォント非対応による表示問題
- **UI表示の英語化**: 全てのユーザー向けメッセージを英語に変更
- **内部コメントの日本語保持**: 開発者向けコメントは日本語で維持
- **バイリンガルコメント構造**: 将来の多言語対応に向けた構造化

## 🔧 技術的改善詳細

### リファクタリング成果
```python
# Before: 巨大な単一メソッド
def update(self):
    # 200行以上の複雑な処理...

# After: 責任分離されたメソッド群
def update(self):
    if self.app_state == AppState.SAVE_CONFIRM:
        self._handle_save_confirmation()
    elif self.app_state == AppState.QUIT_CONFIRM:
        self._handle_quit_confirmation()
    # ...

def _handle_cursor_movement(self):
    # カーソル移動専用処理

def _handle_selection_input(self):
    # 選択処理専用
```

### 状態管理の改善
```python
# Before: 複数のbooleanフラグ
self.edit_mode = False
self.input_mode = False
self.save_confirm_mode = False
self.quit_confirm_mode = False

# After: Enumによる明確な状態管理
class AppState(Enum):
    VIEW = "view"
    EDIT = "edit"
    COMMAND_INPUT = "command_input"
    LEGACY_INPUT = "legacy_input"
    SAVE_CONFIRM = "save_confirm"
    QUIT_CONFIRM = "quit_confirm"
```

### 共通処理の抽出
```python
# Before: 重複したテキスト入力コード
def _handle_command_input(self):
    # 文字入力処理のコード重複...

def _handle_text_input(self):
    # 同じ文字入力処理の重複...

# After: 共通処理メソッド
def _handle_text_input_common(self, input_text):
    # 統一された文字入力処理
    return input_text

def _handle_command_input(self):
    self.command_input = self._handle_text_input_common(self.command_input)

def _handle_text_input(self):
    self.input_text = self._handle_text_input_common(self.input_text)
```

## 🌐 多言語対応の適正化

### 発見した問題
- Pyxelエンジンは日本語フォントをサポートしていない
- 日本語メッセージが正しく表示されない
- ユーザー体験の大幅な低下

### 解決策の実装
```python
# Before: 日本語UI表示
self.message = "スプライト名を入力 (レガシーモード):"

# After: 英語UI表示
self.message = "Enter sprite name (legacy mode):"

# 内部コメントは日本語で保持
def _handle_legacy_input_trigger(self):
    """レガシー命名モードのトリガー処理（意図的使用のためShift+Enter）"""
```

### バイリンガルコメント構造
```python
#ソースコードの中のコメントは日本語、英語を併記してください
##例
# :jp この関数はスプライトを表示します
# :en This function displays the sprite
# #画面に出力する文字列は英語にしてください。pyxelは日本語フォントを表示できません
```

## 📊 改善結果

### コード品質向上
- **保守性**: 各メソッドが単一責任を持つ
- **可読性**: 状態管理が明確
- **拡張性**: 新機能追加が容易
- **テスト容易性**: 個別メソッドのテスト可能

### ユーザー体験向上
- **表示問題解決**: 全てのメッセージが正しく表示
- **操作の安定性**: 状態遷移のバグ修正
- **視覚的一貫性**: UI表示の改善
- **起動時利便性**: 自動読み込み機能

### 開発体験向上
- **デバッグ容易性**: 問題箇所の特定が簡単
- **コード理解**: 構造が明確
- **機能追加**: 影響範囲が限定的
- **多言語対応**: 将来の拡張に対応

## 💡 得られた知見

### リファクタリングの重要性
1. **段階的アプローチ**: 一度に全てを変更せず、段階的に実施
2. **動作確認**: 各段階での動作テストが重要
3. **ユーザーフィードバック**: 実際の使用感からの改善点発見

### 多言語対応の注意点
1. **技術的制約の理解**: フレームワークの制限を事前に把握
2. **表示テスト**: 実際の表示確認が必須
3. **段階的導入**: 内部コメントから始めて段階的に対応

### 開発ツール設計の原則
1. **使いやすさ優先**: 開発者の作業効率を最優先
2. **エラー防止**: 誤操作を防ぐ仕組みの重要性
3. **視覚的フィードバック**: 状態の明確な表示

## 🚀 今後の展望

### 短期的改善
- SpriteDefinerとゲーム本体の統合
- JSON形式スプライトデータの活用
- 動的スプライト管理機能の実装

### 中期的発展
- より高度なスプライト編集機能
- アニメーション設定の視覚化
- チーム開発支援機能

### 長期的ビジョン
- 完全なビジュアルゲーム開発環境
- 多言語開発支援
- 拡張可能なツールチェーン

## 🎯 まとめ

SpriteDefinerのリファクタリングと多言語対応改善により、以下の成果を達成した：

1. **技術的負債の解消**: 743行の巨大クラスを保守性の高い構造に改善
2. **ユーザー体験の向上**: 表示問題の解決と操作性の改善
3. **開発効率の向上**: デバッグとメンテナンスの容易化
4. **将来への準備**: 多言語対応とツール拡張の基盤構築

この改善により、PyxelShmupプロジェクトの開発ツールチェーンが大幅に強化され、より効率的で持続可能な開発体制が確立された。

---

# JSON駆動スプライト統合完了記録

## 概要
2025年7月16日深夜、JSON駆動スプライト管理システムの完全統合を達成した。

## 実施内容

### Phase 1: データ構造の大転換
- **tags配列形式からキーワードフィールド形式への移行**
  - 旧: `"tags": ["NO_ACT", "0", "20"]`
  - 新: `"NAME": "PBULLET", "ACT_NAME": "NO_ACT", "FRAME_NUM": "0", "ANIM_SPD": "20"`
- **可読性と保守性の大幅向上**

### Phase 2: ゲーム本体の完全JSON対応
- **Player.py**: プレイヤースプライト＋エグゾーストアニメーションをJSON制御
- **Bullet.py**: 弾丸アニメーションタイミングをJSON制御
- **SpriteManager.py**: 新キーワードフィールド形式の完全対応

### Phase 3: SpriteDefinerツールの対応
- **SPRITE_FIELDSシステム**: キーワードフィールドの動的管理
- **コマンド処理更新**: 新フィールド形式での編集機能
- **データ整合性確保**: 新旧形式の互換性維持

### Phase 4: フィールド名統一
- **大文字統一**: 'name' → 'NAME' でフィールド名の一貫性確保
- **全ファイル一括更新**: sprites.json, SpriteManager.py, SpriteDefiner.py

## 🎯 技術的成果

### JSON設定優先の確立
```python
# JSON設定値が最優先される設計
def get_bullet_animation_duration(self):
    for key, sprite in self.json_sprites.items():
        if sprite.get("NAME") == "PBULLET":
            anim_spd = sprite.get("ANIM_SPD")
            if anim_spd:
                return int(anim_spd)
    return 3  # フォールバック値
```

### アニメーション制御の統一
- **プレイヤー弾丸**: ANIM_SPD設定でフレーム切り替え制御
- **エグゾースト**: JSON駆動の4フレーム循環アニメーション  
- **ハードコーディング排除**: 全タイミング値をJSON外部化

### 開発ツールの完全対応
- **SpriteDefiner**: 新フィールド形式での直感的編集
- **リアルタイム反映**: JSON編集→ゲーム動作確認の高速サイクル
- **データ整合性**: 型安全性とエラーハンドリング

## 📊 実装状況

### 完了済み機能
✅ プレイヤースプライト（TOP/LEFT/RIGHT）のJSON制御  
✅ プレイヤー弾丸の2フレームアニメーション  
✅ エグゾーストの4フレーム循環アニメーション  
✅ SpriteDefinerでの新フィールド編集  
✅ JSON優先設計の確立  
✅ フィールド名統一（NAME, ACT_NAME, FRAME_NUM, ANIM_SPD）

### sprites.json現在の定義
```json
{
  "sprites": {
    "40_0": {"x": 40, "y": 0, "NAME": "PBULLET", "FRAME_NUM": "0", "ANIM_SPD": "20"},
    "48_0": {"x": 48, "y": 0, "NAME": "PBULLET", "FRAME_NUM": "1", "ANIM_SPD": "25"},
    "56_0": {"x": 56, "y": 0, "NAME": "EXHST", "FRAME_NUM": "0", "ANIM_SPD": "10"},
    // ... エグゾースト4フレーム、敵機5種類×4フレーム等
  }
}
```

## 🚀 次回開発予定

### 明日のテスト項目
1. **詳細動作確認**
   - 各アニメーション速度の体感テスト
   - JSON設定変更の即座反映確認
   - エラーハンドリングの動作確認

2. **パフォーマンス検証**  
   - JSON読み込み処理の負荷測定
   - フレームレート安定性確認
   - メモリ使用量チェック

3. **拡張性テスト**
   - 新スプライト追加の手順確認
   - 複雑なアニメーションパターンのテスト
   - SpriteDefinerでの編集効率検証

### 中期的発展
- **敵機アニメーション**: 同様のJSON制御導入
- **エフェクトシステム**: 爆発・マズルフラッシュのJSON化
- **オーディオ管理**: サウンド設定のJSON外部化

## 💡 開発で得られた知見

### JSON駆動設計の価値
- **設定の可視化**: 数値調整が直感的
- **デバッグ効率**: 問題箇所の特定が容易
- **チーム開発**: 非プログラマーでも設定可能

### ツール統合の重要性
- **SpriteDefiner**: ビジュアル編集による生産性向上
- **即座フィードバック**: 編集→確認のサイクル高速化
- **品質保証**: 型安全性とエラー防止

## 🎉 プロジェクト現在地

PyxelShmupプロジェクトは、堅牢なアーキテクチャとJSON駆動の柔軟な設定システムを備えた、高品質なゲーム開発基盤として完成した。

今後の機能拡張や調整作業は、この基盤の上で効率的に進行できる状態となっている。

**現在時刻**: 2025年7月16日 深夜1時  
**状態**: JSON駆動スプライト統合完了、次回詳細テスト予定

---

# 自己完結型スプライト管理リファクタリング完了記録

## 概要
2025年7月17日、スプライト管理システムの最終的なリファクタリングを実施し、完全な自己完結型アーキテクチャへの移行を完了した。

## 実施内容

### Phase 1: アーキテクチャ問題の発見
- **問題認識**: コードレビュー中に発見されたSpriteManagerの責任過多
- **設計上の課題**: 各エンティティ専用メソッドの乱立
- **拡張性の問題**: 新エンティティ追加時のSpriteManager変更が必要

### Phase 2: 自己完結型設計への移行
- **SpriteManager純粋化**: データ提供者としての単一責任に集約
- **エンティティ自立化**: Player, Bullet, Enemy, EnemyBullet全てが自己完結
- **汎用メソッド統一**: `get_sprite_by_name_and_field()`, `get_sprite_metadata()`, `get_sprite_group()`

### Phase 3: レガシーコード完全削除
- **SprList辞書**: 完全にコメントアウト
- **専用ヘルパー関数**: 全削除（get_player_sprite, get_bullet_sprite等）
- **古い定数**: MAX_ENEMY_NUM, MAX_ANIM_PAT削除

## 🎯 技術的成果

### 責任の完全分離
```python
# Before: SpriteManagerが全てを知っている
def get_player_sprite(self, direction="TOP"):
def get_bullet_sprite(self, frame_number):
def get_enemy_sprite(self, enemy_num, anim_pat):

# After: 各エンティティが自己完結
class Player:
    def _get_player_sprite(self):
        return sprite_manager.get_sprite_by_name_and_field("PLAYER", "ACT_NAME", self.SprName)

class Bullet:
    def _get_bullet_sprite(self, frame_number):
        return sprite_manager.get_sprite_by_name_and_field("PBULLET", "FRAME_NUM", str(frame_number % 2))
```

### JSON駆動アニメーション完全統一
- **プレイヤー**: スプライト＋エグゾースト＋マズルフラッシュ
- **弾丸**: 2フレームアニメーション（ANIM_SPD: 20フレーム）
- **敵**: 種類別差別化アニメーション速度
  - ENEMY01: 10フレーム（標準）
  - ENEMY02: 12フレーム（少し遅め）
  - ENEMY03: 8フレーム（速め）
  - ENEMY04: 15フレーム（遅め）
  - ENEMY05: 6フレーム（最速）
- **敵弾**: JSONスプライト取得

### クリーンアップ完了
```python
# 削除されたレガシーコード
- SprList辞書（47行の定義）
- get_player_sprite()
- get_bullet_sprite()
- get_bullet_animation_duration()
- get_exhaust_sprite()
- get_exhaust_animation_duration()
- get_bullet_animation_frame()
- get_enemy_sprite()
- MAX_ENEMY_NUM, MAX_ANIM_PAT定数
- __pycache__ファイル群
```

## 📊 実装状況

### 完了済み全エンティティ
✅ **Player**: 自己完結型スプライト管理（プレイヤー・エグゾースト・マズルフラッシュ）  
✅ **Bullet**: 自己完結型アニメーション管理  
✅ **Enemy**: 自己完結型アニメーション管理（種類別速度設定）  
✅ **EnemyBullet**: 自己完結型スプライト管理  

### SpriteManager汎用メソッド
```python
def get_sprite_by_name_and_field(self, name, field_name, field_value):
    """名前と指定フィールドの値でスプライトを取得する汎用メソッド"""

def get_sprite_metadata(self, name, field_name, default_value=None):
    """指定されたスプライトの特定フィールドの値を取得する"""

def get_sprite_group(self, name):
    """指定された名前のスプライトグループを全て取得する"""
```

## 🔧 開発プロセスの改善

### 段階的リファクタリング
1. **SpriteManager汎用化**: 純粋なデータ提供者へ
2. **Player自立化**: 最初のエンティティ変更でパターン確立
3. **Bullet自立化**: パターンの検証と改善
4. **Enemy自立化**: 複雑なアニメーション管理の統一
5. **EnemyBullet自立化**: 最終的な完全統一
6. **レガシー削除**: 古いコードの完全撤廃

### 動作確認とテスト
- **各段階での動作確認**: リファクタリング後の即座テスト
- **JSON設定検証**: sprites.jsonの名前修正とエラー対応
- **__pycache__クリーンアップ**: git管理の適正化

## 💡 設計の優秀性

### アーキテクチャの美しさ
```
エンティティ群 → SpriteManager → sprites.json
      ↓              ↓              ↓
  自己完結型      汎用メソッド    設定ファイル
```

### 拡張性の確保
- **新エンティティ追加**: SpriteManager変更不要
- **アニメーション調整**: sprites.json編集のみ
- **独立した責任**: 各エンティティが自分の処理を管理

### 保守性の向上
- **影響範囲限定**: 変更が他のエンティティに影響しない
- **デバッグ容易**: 問題箇所の特定が簡単
- **テスト可能**: 個別エンティティのテスト実装可能

## 🚀 今後の発展

### 確立されたパターン
新しいエンティティ（例：ボス、アイテム等）を追加する際：
1. エンティティクラス内に`_get_xxx_sprite()`メソッド実装
2. sprites.jsonに必要なスプライト定義追加
3. SpriteManagerは一切変更不要

### 技術的基盤の完成
- **JSON駆動**: 完全な外部設定管理
- **責任分離**: クリーンなアーキテクチャ
- **拡張準備**: 将来機能への対応完了

## 🎉 最終成果

### Git履歴
```
4a8c22c Refactor sprite management to self-contained entity architecture
e2ebb39 Remove __pycache__ files from git tracking
```

### コードメトリクス
- **削除されたコード**: レガシー関数群とSprList辞書
- **追加されたコード**: 各エンティティの自己完結メソッド
- **統一されたアーキテクチャ**: 全エンティティが同じパターンに従う

### 開発効率の向上
- **設定変更**: sprites.jsonのみで完結
- **新機能追加**: パターンが確立済み
- **デバッグ**: 責任箇所が明確

## 🔚 総合評価

このリファクタリングにより、PyxelShmupプロジェクトは技術的に非常に優秀なアーキテクチャを獲得した。特に：

1. **完全な責任分離**: 各コンポーネントが明確な役割を持つ
2. **JSON駆動設計**: 外部設定による柔軟性
3. **自己完結型エンティティ**: 独立性と保守性の確保
4. **レガシーコード完全削除**: 技術的負債の解消

今後の開発は、この堅牢な基盤の上で効率的に進行できる状態となった。

**実施日時**: 2025年7月17日 16:38-18:00  
**状態**: 自己完結型スプライト管理アーキテクチャ完全移行完了