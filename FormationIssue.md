# Formation Movement Issue Analysis

## 問題の概要
敵が攻撃モードから隊列復帰する際に、正しい座標に戻らず、位置がずれるバグが発生している。

## 現在の座標管理システム

### 敵エンティティが持つ座標
```python
class Enemy:
    def __init__(self, x, y, ...):
        self.base_x = x      # 初期X座標（隊列復帰用）
        self.base_y = y      # 初期Y座標（隊列復帰用）
        self.x = x           # 現在の表示X座標
        self.y = y           # 現在の表示Y座標
        self.formation_x = x # 隊列内での現在のX位置
        self.formation_y = y # 隊列内での現在のY位置
```

### 問題点
1. **座標の重複管理**: `base_x`, `formation_x`, `x` の3つのX座標を管理
2. **更新タイミングの複雑さ**: 各状態で異なる更新ロジック
3. **一貫性の欠如**: 状態間で座標の意味が異なる

## 現在の隊列移動処理

### main.py での処理
```python
# グループ移動の更新
GameState.enemy_group_x += Enemy.MOVE_SPEED * GameState.enemy_move_direction

# 移動量が閾値を超えたら整数値で移動
if abs(GameState.enemy_group_x) >= Enemy.MOVE_THRESHOLD:
    move_amount = int(GameState.enemy_group_x)
    GameState.enemy_group_x -= move_amount
    
    # 画面端での方向転換チェック
    formation_enemies = [e for e in Common.enemy_list if e.active and (e.state == 0 or e.state == 1)]
    if formation_enemies:
        if GameState.enemy_move_direction == GameState.ENEMY_MOVE_RIGHT:
            rightmost_x = max(enemy.base_x for enemy in formation_enemies)
            if rightmost_x + 8 >= Config.WIN_WIDTH:
                GameState.enemy_move_direction = GameState.ENEMY_MOVE_LEFT
        else:
            leftmost_x = min(enemy.base_x for enemy in formation_enemies)
            if leftmost_x <= 0:
                GameState.enemy_move_direction = GameState.ENEMY_MOVE_RIGHT

# 各敵のupdateを呼び出す
for _e in Common.enemy_list:
    _e.update(move_amount)
```

### 問題点
1. **base_x基準の判定**: 方向転換判定が`base_x`を使用しているが、実際の位置は`x`
2. **グローバル状態依存**: `GameState.enemy_group_x`による累積誤差
3. **複雑な状態管理**: 各敵が個別に座標を更新

## 各状態での座標更新

### NORMAL状態
```python
def _update_normal(self, move_amount_x):
    self.x += move_amount_x
    self.base_x += move_amount_x
    self.formation_x += move_amount_x
```

### PREPARE_ATTACK状態
```python
def _update_prepare_attack(self, move_amount_x):
    self.x += move_amount_x
    self.base_x += move_amount_x
    self.formation_x += move_amount_x
```

### ATTACK状態
```python
def _update_attack(self, move_amount_x):
    self.x = self.base_x + sway_offset + move_amount_x
    self.formation_x += move_amount_x  # 最近追加
```

### DESCENDING状態（復帰処理）
```python
def _update_descending(self, move_amount_x):
    target_x = self.formation_x
    target_y = self.formation_y
    
    # 隊列位置に近づいたかチェック
    if distance_to_formation <= self.FORMATION_PROXIMITY:
        self.x = self.formation_x + move_amount_x
        self.y = target_y
        self.base_x = self.formation_x
        self.base_y = target_y
        self.state = ENEMY_STATE_NORMAL
```

## デバッグログから見つかった問題

### 具体的な問題例
```
[RETURN] Enemy 32: RETURNED TO FORMATION
  target_x: 54.0, target_y: 10.0
  move_amount_x: 0
  formation_x: 54.0, formation_y: 10.0
  x: 54.0 -> 54.0, base_x: 85.0 -> 54.0
```

### 問題の分析
1. **formation_x: 54.0** - 正しい隊列位置
2. **base_x: 85.0 -> 54.0** - 攻撃開始時の古い位置から急激に変更
3. **座標の不整合**: 攻撃中にformation_xは正しく更新されていたが、base_xは古い値のまま

## 根本的な設計問題

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

## 提案する解決策

### 1. 座標管理の単純化
```python
class Enemy:
    def __init__(self, x, y, ...):
        # 削除: base_x, base_y
        self.formation_x = x  # 隊列内の絶対位置
        self.formation_y = y  # 隊列内の絶対位置
        self.x = x           # 現在の表示位置
        self.y = y           # 現在の表示位置
```

### 2. 隊列移動の一元化
```python
def update_formation_movement():
    # 隊列にいる敵のみを対象
    formation_enemies = [e for e in Common.enemy_list 
                        if e.active and e.is_in_formation()]
    
    if formation_enemies:
        # リアルタイムで端点を取得
        leftmost_x = min(e.formation_x for e in formation_enemies)
        rightmost_x = max(e.formation_x for e in formation_enemies)
        
        # 移動方向決定
        if rightmost_x + 8 >= Config.WIN_WIDTH:
            direction = -1
        elif leftmost_x <= 0:
            direction = 1
        else:
            direction = current_direction
        
        # 全員の formation_x を一括更新
        for enemy in Common.enemy_list:
            if enemy.active:
                enemy.formation_x += direction * MOVE_SPEED
```

### 3. 状態処理の単純化
```python
def _update_normal(self):
    # 隊列位置にいるだけ
    self.x = self.formation_x
    self.y = self.formation_y

def _update_attack(self):
    # 攻撃中（formation_x/yは自動更新される）
    self.y += self.ATTACK_MOVE_SPEED
    # 左右の揺れ...

def _update_descending(self):
    # 隊列位置に戻るだけ
    if self.is_close_to_formation():
        self.x = self.formation_x
        self.y = self.formation_y
        self.state = NORMAL
```

## リファクタリングプラン

### Phase 1: 座標システム単純化
1. `base_x`, `base_y` の削除
2. `formation_x`, `formation_y` のみでの管理
3. 各状態での座標更新ロジック統一

### Phase 2: 隊列移動一元化
1. main.pyでの一括座標更新
2. グローバル状態からの脱却
3. リアルタイム端点検出

### Phase 3: 状態処理統一
1. 各状態での単純な位置制御
2. 復帰処理の簡略化
3. デバッグの簡素化

## 期待される効果

1. **バグの根絶**: 座標の不整合がなくなる
2. **保守性向上**: 理解しやすい単純な設計
3. **拡張性確保**: 新しい移動パターンの追加が容易
4. **パフォーマンス向上**: 不要な計算の削減

## 実装時の注意点

1. **段階的実装**: 一度に全てを変更せず、段階的に移行
2. **動作確認**: 各フェーズで動作テストを実施
3. **デバッグ支援**: 新しい座標系でのデバッグ情報整備
4. **後方互換性**: 既存のゲームプレイへの影響を最小化

---

*このドキュメントは現在の問題分析と解決策提案を含む。実装前に詳細な設計レビューを推奨。*