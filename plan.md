plan.md                                                                                                  │ │
│ │                                                                                                          │ │
│ │ # PyxelShmup JSON スプライト統合プラン                                                                   │ │
│ │                                                                                                          │ │
│ │ ## 🎯 目標                                                                                               │ │
│ │ SpriteDefiner.pyで作成したsprites.jsonをゲーム本体に統合し、ハードコーディングされたスプライト座標をJSON │ │
│ │ 駆動の動的システムに置き換える                                                                           │ │
│ │                                                                                                          │ │
│ │ ## 📋 段階的実行プラン                                                                                   │ │
│ │                                                                                                          │ │
│ │ ### Step 1: JSONローダー基盤構築                                                                         │ │
│ │ 1. **SpriteManager.pyにJSON読み込み機能追加**                                                            │ │
│ │    - sprites.json読み込み処理                                                                            │ │
│ │    - エラーハンドリング（ファイル未存在、形式不正等）                                                    │ │
│ │    - 起動時自動読み込み                                                                                  │ │
│ │                                                                                                          │ │
│ │ ### Step 2: プレイヤースプライト統合（最初の実証）                                                       │ │
│ │ 2. **プレイヤースプライト用新API実装**                                                                   │ │
│ │    ```python                                                                                             │ │
│ │    # 目標: get_player_sprite(direction="TOP"|"LEFT"|"RIGHT")                                             │ │
│ │    # 現在: SprList["PLAYER"] の固定座標から                                                              │ │
│ │    # 新形式: sprites.jsonの"PLAYER"グループから動的取得                                                  │ │
│ │    ```                                                                                                   │ │
│ │                                                                                                          │ │
│ │ 3. **Player.pyでのスプライト参照更新**                                                                   │ │
│ │    - ハードコーディングされた座標を新API呼び出しに変更                                                   │ │
│ │    - 既存の描画ロジックは維持                                                                            │ │
│ │                                                                                                          │ │
│ │ ### Step 3: 動作確認・デバッグ                                                                           │ │
│ │ 4. **プレイヤー表示テスト**                                                                              │ │
│ │    - ゲーム起動でプレイヤーが正常表示されるか確認                                                        │ │
│ │    - 移動時の LEFT/RIGHT スプライト切り替え動作確認                                                      │ │
│ │    - エラー発生時の適切な処理確認                                                                        │ │
│ │                                                                                                          │ │
│ │ ### Step 4: 他スプライトへの展開準備                                                                     │ │
│ │ 5. **成功パターンの確立**                                                                                │ │
│ │    - プレイヤースプライトで確立したパターンを他に適用                                                    │ │
│ │    - PBULLET, EXHST, MZLFLSH等への展開方針決定                                                           │ │
│ │                                                                                                          │ │
│ │ ## 🔧 技術設計                                                                                           │ │
│ │                                                                                                          │ │
│ │ ### JSON読み込み構造                                                                                     │ │
│ │ ```python                                                                                                │ │
│ │ class SpriteManager:                                                                                     │ │
│ │     def __init__(self):                                                                                  │ │
│ │         self.json_sprites = {}  # sprites.jsonデータ                                                     │ │
│ │         self.load_sprites_json()                                                                         │ │
│ │                                                                                                          │ │
│ │     def get_player_sprite(self, direction="TOP"):                                                        │ │
│ │         # "PLAYER"グループからdirectionタグで検索                                                        │ │
│ │         for key, sprite in self.json_sprites.items():                                                    │ │
│ │             if sprite["name"] == "PLAYER" and direction in sprite["tags"]:                               │ │
│ │                 return (sprite["x"], sprite["y"])                                                        │ │
│ │ ```                                                                                                      │ │
│ │                                                                                                          │ │
│ │ ### 既存互換性                                                                                           │ │
│ │ - 既存のSprList辞書は当面維持                                                                            │ │
│ │ - 段階的移行でゲーム動作を保証                                                                           │ │
│ │ - 問題発生時は即座にロールバック可能                                                                     │ │
│ │                                                                                                          │ │
│ │ ## 📊 Step 1での期待効果                                                                                 │ │
│ │                                                                                                          │ │
│ │ 1. **即座の価値実証**: プレイヤー表示でJSON統合の実効性確認                                              │ │
│ │ 2. **リスク最小化**: 影響範囲を限定した安全な実装                                                        │ │
│ │ 3. **学習効果**: 実装パターン確立で後続作業の効率化                                                      │ │
│ │ 4. **デバッグ容易性**: 問題箇所の特定と修正が簡単                                                        │ │
│ │                                                                                                          │ │
│ │ このステップバイステップアプローチで、まずプレイヤースプライトからスタートしましょうか？    