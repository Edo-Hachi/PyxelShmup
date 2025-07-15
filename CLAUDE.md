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