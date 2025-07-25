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

---

# 敵機入場パターン追加開発記録

## 概要
2025年7月18日、敵機の入場パターンを拡張し、新たにジグザグパターンを追加した。

## 開発経緯

### 背景
- 既存の左右ループパターン（pattern 1, 2）に加えて、より多様な入場演出が必要
- ユーザーからの要望：「敵がステージに入ってくるときのパターンを増やしたい」
- 最初はSIN波を使った滑らかな軌道を試行したが、動きが速すぎて不自然

### 設計思想の変更
- **フレーム数制御からX座標制御へ**: より確実で理解しやすい制御方式
- **矩形軌道の採用**: 滑らかな曲線ではなく、きっちりした矩形の軌道
- **位置ベース判定**: X座標の値で移動状態を判定する仕組み

## 実装内容

### 新パターン: entry_pattern=3 (ジグザグパターン)

#### 軌道仕様
- **開始位置**: X=0, Y=64
- **移動パターン**: 24ピクセル右→36ピクセル上→24ピクセル右→36ピクセル下→24ピクセル右→36ピクセル上→24ピクセル右
- **終了条件**: X座標が96ピクセルを超えたらホームポジションへ移動開始
- **垂直移動**: X座標固定で真っ直ぐ上下移動（斜めではない）

#### 技術的特徴
```python
if self.x < 96:
    if self.x < 24:
        # 0-24ピクセル：右に移動
        self.x += 1.0
        self.y = 64
    elif self.x == 24 and self.y > 28:
        # X=24で上に移動中（64→28）
        self.y -= 1.0
    elif self.x < 48:
        # 24-48ピクセル：右に移動
        self.x += 1.0
        # Y座標は28で固定
    # ...以下同様のパターン
```

### 実装ファイル

#### Enemy.py
- **初期位置設定**: entry_pattern=3の場合、X=0, Y=64でスタート
- **移動ロジック**: X座標ベースの状態判定による矩形軌道制御
- **ホームポジション移動**: X≥96で従来の降下ロジックに移行

#### main.py
- **パターン割り当て**: 1行目の敵のみをジグザグパターンに設定
- **他パターン維持**: 2-4行目は従来の左右ループパターンを継続

```python
# 新しいジグザグパターンをテスト
if _y == 0:  # 1行目だけジグザグパターン
    pattern = 3
else:
    pattern = 1 if _x < 5 else 2
```

## 🎯 技術的成果

### 設計上の改善
1. **フレーム数依存の除去**: 時間ではなく位置で制御
2. **確実な状態遷移**: X座標の値で明確な判定
3. **矩形軌道の実現**: 斜めではない真っ直ぐな上下移動

### 拡張性の確保
- **パターン追加容易**: 新しいentry_patternの追加が簡単
- **微調整対応**: 移動距離や速度の調整が容易
- **独立性**: 他のパターンに影響しない

### 視覚的効果
- **差別化**: 1行目の敵だけが特別な軌道で登場
- **予測可能性**: 一定のパターンで動くため、プレイヤーが対策を立てやすい
- **演出効果**: 多様な入場パターンによるゲーム体験の向上

## 🔧 開発プロセス

### Phase 1: SIN波パターンの試行
- 左右からの波形軌道を実装
- ユーザーフィードバック：「動きが速すぎて不自然」
- 追い越し問題：左側の敵が後続に追い抜かれる現象

### Phase 2: 設計思想の転換
- フレーム数からX座標ベースへの変更
- 矩形軌道の採用
- 位置判定ロジックの実装

### Phase 3: 実装と調整
- entry_pattern=3の実装
- 移動距離の調整（X方向24px、Y方向36px）
- 真っ直ぐな上下移動の実現

## 💡 得られた知見

### 制御方式の重要性
- **フレーム数制御**: 時間ベースだが、完了タイミングが曖昧
- **位置ベース制御**: より確実で理解しやすい

### ユーザーフィードバックの価値
- 実際の動作を見たユーザーの感想が設計改善に直結
- 「速すぎる」「不自然」といった感覚的なフィードバックが重要

### 段階的開発の効果
- 最初のSIN波パターンは没になったが、設計思想転換のきっかけに
- 試行錯誤を通じて、より良いソリューションにたどり着いた

## 🚀 今後の予定

### 微調整項目
- **移動速度**: 現在1.0pixel/frameの調整検討
- **移動距離**: X方向24px、Y方向36pxの最適化
- **軌道形状**: より自然な見た目への調整

### 追加パターン案
- **三角軌道**: 上下に山型の軌道
- **ダブルループ**: 2回転する円弧軌道
- **スパイラル**: 螺旋状の軌道

### 技術的発展
- **パターン設定の外部化**: JSON設定での軌道パラメータ管理
- **エディタ機能**: 軌道パターンの視覚的編集ツール

## 🎉 現在の状態

### 実装完了
✅ **ジグザグパターン**: X座標ベースの矩形軌道  
✅ **1行目専用**: 特別な演出効果  
✅ **位置制御**: 確実な状態遷移  
✅ **矩形軌道**: 真っ直ぐな上下移動  

### 次回作業
- X,Y移動距離の微調整
- 視覚的効果の最適化
- 他パターンとの調和

**実施日時**: 2025年7月18日 19:00-21:00  
**状態**: ジグザグパターン基本実装完了、微調整待ち

---

# 敵機座標管理問題発見・分析記録

## 概要
2025年7月18日深夜、敵機の攻撃→復帰サイクルにおいて、座標ずれのバグが発生していることが判明。詳細な分析により、複雑な座標管理システムが原因であることが明らかになった。

## 発見された問題

### 症状
- 敵機が攻撃モードから隊列復帰する際、正しい位置に戻らない
- 復帰位置が攻撃開始時の古い座標になってしまう
- 隊列移動中の座標同期が適切に行われていない

### 根本原因
現在の座標管理システムは**3つの座標（base_x, formation_x, x）**を管理しており、各状態で異なる更新ロジックを持つため、整合性を保つのが困難。

```python
# 問題のある設計
class Enemy:
    def __init__(self, x, y, ...):
        self.base_x = x      # 初期X座標（隊列復帰用）
        self.formation_x = x # 隊列内での現在のX位置
        self.x = x           # 現在の表示X座標
        # 3つの座標を管理 = 複雑性の温床
```

## 実施した調査・修正

### Phase 1: デバッグログシステム構築
- `debug_enemy.log`ファイルによる詳細な座標追跡
- 各状態での座標変化を記録
- 復帰時の座標計算プロセスを可視化

### Phase 2: 座標更新ロジック修正
各状態で`formation_x`の更新を統一：
- `_update_normal`: ✅ 修正済み
- `_update_prepare_attack`: ✅ 修正済み  
- `_update_attack`: ✅ 修正実施
- `_update_returning`: ✅ 修正実施
- `_update_continuous_attack`: ✅ 修正実施

### Phase 3: 復帰座標計算の改善
```python
# Before: 問題のある計算
self.x = target_x + move_amount_x
self.base_x = target_x

# After: 統一された計算
self.x = self.formation_x + move_amount_x
self.base_x = self.formation_x
```

## 発見された設計上の問題

### 1. 座標の責任分散
- `base_x`: 初期位置＋グループ移動の累積
- `formation_x`: 隊列内の理論位置  
- `x`: 実際の表示位置

### 2. 状態間の整合性
- 各状態で異なる座標更新ロジック
- 状態遷移時の座標同期処理が複雑

### 3. グループ移動の複雑さ
- main.pyでのグローバル移動量計算
- 各敵での個別座標更新
- 累積誤差の可能性

## 問題分析文書

### FormationIssue.md作成
現在の問題を包括的に分析し、解決策を提案：
- 現在の座標管理システムの問題点
- デバッグログから見つかった具体的な問題
- 提案する座標システム単純化アプローチ
- 段階的リファクタリングプラン

## 提案されている解決策

### 座標管理の単純化
```python
# 新しい設計案
class Enemy:
    def __init__(self, x, y, ...):
        self.formation_x = x  # 隊列内の絶対位置
        self.formation_y = y  # 隊列内の絶対位置
        self.x = x           # 現在の表示位置
        self.y = y           # 現在の表示位置
        # base_x, base_y は削除
```

### 隊列移動の一元化
```python
def update_formation_movement():
    # 隊列にいる敵のみを対象
    formation_enemies = [e for e in Common.enemy_list 
                        if e.active and e.is_in_formation()]
    
    if formation_enemies:
        # リアルタイムで端点を取得
        leftmost_x = min(e.formation_x for e in formation_enemies)
        rightmost_x = max(e.formation_x for e in formation_enemies)
        
        # 移動方向決定と全員の formation_x 一括更新
        for enemy in Common.enemy_list:
            if enemy.active:
                enemy.formation_x += direction * MOVE_SPEED
```

## 技術的価値

### 現在の修正による改善
- 座標ずれの大幅な改善
- デバッグの容易性向上
- 座標追跡の透明性確保

### 将来のリファクタリング効果
- **バグの根絶**: 座標の不整合がなくなる
- **保守性向上**: 理解しやすい単純な設計  
- **拡張性確保**: 新しい移動パターンの追加が容易
- **パフォーマンス向上**: 不要な計算の削減

## 次回作業予定

1. **現在の修正効果確認**: 座標ずれ問題の解決状況チェック
2. **リファクタリング計画策定**: FormationIssue.mdベースの詳細設計
3. **段階的実装**: 大規模リファクタリングの安全な実行

## 学んだ教訓

### 複雑性の危険性
- 座標管理という基本的な処理でも、複雑性が積み重なると深刻なバグの原因となる
- 3つの座標を管理するシステムは、人間の理解限界を超えている

### デバッグの重要性
- 詳細なログシステムが問題特定に不可欠
- 座標の変化を追跡することで、問題の根本原因を特定できた

### 設計の単純化
- 「シンプルで確実」が「複雑で高機能」に勝る
- リファクタリングによる単純化は、技術的負債の解消に直結

**実施日時**: 2025年7月18日 深夜 24:00-02:00  
**状態**: 座標管理問題分析完了、リファクタリング計画策定済み

---

# EntryPattern統合と射撃システム実装完了記録

## 概要
2025年7月19日、EntryPatternの完全統合とシンプルな射撃システムの実装を完了した。

## 実施内容

### Phase 1: EntryPattern統合による登場システム完全リファクタリング
- **座標管理の単純化**: base_x/formation_x/x の3座標システムから formation_x/x の2座標システムへ
- **EntryPatterns.py統合**: LeftLoopPattern、RightLoopPattern、ZigzagPatternを新Enemy.pyに完全統合
- **状態管理統一**: ENTRY_SEQUENCE → MOVING_TO_HOME → HOME_REACHED → NORMAL の明確な状態フロー
- **変数名衝突解決**: entry_pattern_obj/entry_pattern_str分離による'str' object エラー修正

### Phase 2: 敵機射撃システム実装
- **EnemyBullet連携**: 既存EnemyBulletクラスとの完全統合
- **確率的射撃**: 基本10%から最大30%までの動的射撃確率
- **残り敵数調整**: 敵が減るほど射撃確率が上昇する戦略的バランス
- **デバッグ対応**: 射撃時の詳細ログ出力とトレーサビリティ確保

### Phase 3: ステージクリア後の操作性改善
- **プレイヤー移動不能バグ修正**: 処理順序の改善により、ステージクリア中でもプレイヤー移動可能
- **ヒットストップ制御**: 適切なタイミングでのプレイヤー更新処理

## 技術的成果

### アーキテクチャの美しさ
```
EntryPattern → 状態管理 → 隊列移動 → 射撃システム
     ↓           ↓         ↓         ↓
独立クラス   明確な状態   単純座標   確率制御
```

### AIペアプログラミングの効果的パターン確立
- **段階的アプローチ**: 探索 → 分析 → 再構築の3段階プロセス
- **既存コード活用**: EnemyOld.pyを参考にした機能移植
- **クリーン実装**: スパゲッティコードを美しいアーキテクチャに変換

## 動作確認済み機能
✅ 4種類の登場パターン（LeftLoop/RightLoop/Zigzag/水平移動）  
✅ 確率的敵弾射撃システム  
✅ 残り敵数による射撃頻度調整  
✅ ステージクリア後のプレイヤー操作性  
✅ デバッグモードでの詳細ログ出力  

## 次回開発予定（2025年7月20日）

### 🎯 エネミー降下攻撃システム実装
EnemyOld.pyの攻撃システムを参考に、新しいクリーンアーキテクチャで実装予定：

#### 実装予定機能
1. **攻撃状態追加**
   - `ENEMY_STATE_PREPARE_ATTACK`: 攻撃準備（プルプル震え演出）
   - `ENEMY_STATE_ATTACK`: 個別降下攻撃（フラフラ揺れ動作）
   - `ENEMY_STATE_RETURNING`: 画面下での復帰待機
   - `ENEMY_STATE_DESCENDING`: 隊列への復帰降下

2. **攻撃AI管理**
   - 攻撃選択アルゴリズム
   - クールダウン管理システム
   - 複数敵の協調行動制御

3. **連続攻撃モード**
   - 最後の1機になった敵の永続攻撃
   - ランダム位置からの再出現システム

#### 開発方針
- **参考実装**: EnemyOld.pyの攻撃システム（PREPARE_ATTACK_DURATION、ATTACK_MOVE_SPEED等の定数）
- **クリーン設計**: 現在の美しい状態管理システムに自然に統合
- **段階的実装**: 攻撃準備 → 降下攻撃 → 復帰 → 連続攻撃の順で実装

この攻撃システム実装により、PyxelShmupは完全な縦スクロールシューティングゲームとして完成する予定。

**実施日時**: 2025年7月19日 22:00-24:00  
**状態**: EntryPattern統合・射撃システム完了、明日は降下攻撃実装予定