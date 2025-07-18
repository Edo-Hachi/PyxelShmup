#ソースコードの中のコメントは日本語にしましょう
# #画面に出力する文字列は英語にしてください。pyxelは日本語フォントを表示できません
# CLAUDE.md を書き込むときは英語にしてください
# 変数の型は宣言してください

import math
import Config

# 敵の入場パターンを管理するクラス群
# 新パターンを追加する際は、EntryPatternBaseを継承した新クラスを作成し、
# EntryPatternFactoryに登録するだけで済む設計

class EntryPatternBase:
    """入場パターンの基底クラス"""
    
    def __init__(self):
        self.formation_proximity = 8  # ホームポジション到達判定距離
        self.descend_speed = 1.5      # ホームポジション移動速度
    
    def update(self, enemy):
        """入場パターンの更新処理（サブクラスで実装）"""
        raise NotImplementedError("update method must be implemented")
    
    def is_completed(self, enemy):
        """入場パターンの完了判定（サブクラスで実装）"""
        raise NotImplementedError("is_completed method must be implemented")
    
    def _move_to_formation(self, enemy):
        """ホームポジションへの移動処理（共通処理）"""
        target_x = enemy.formation_x
        target_y = enemy.formation_y
        
        # Y軸方向の移動
        enemy.y += self.descend_speed
        
        # X軸方向の移動
        x_diff = target_x - enemy.x
        if abs(x_diff) > 1:
            enemy.x += math.copysign(min(abs(x_diff), 2), x_diff)
        else:
            enemy.x = target_x
        
        # 到達判定
        distance_to_formation = math.sqrt((enemy.x - target_x)**2 + (enemy.y - target_y)**2)
        if distance_to_formation <= self.formation_proximity or enemy.y > target_y:
            enemy.x = target_x
            enemy.y = target_y
            enemy.base_x = target_x
            enemy.base_y = target_y
            return True
        return False


class ZigzagPattern(EntryPatternBase):
    """ジグザグパターン（X座標ベースの矩形軌道）"""
    
    def __init__(self):
        super().__init__()
        self.completion_x = 96  # X座標がこの値を超えたらホームポジション移動開始
    
    def update(self, enemy):
        """ジグザグパターンの更新処理"""
        enemy.entry_timer += 1
        
        if enemy.x < self.completion_x:
            # ジグザグパターン実行中
            if enemy.x < 24:
                # 0-24ピクセル：右に移動
                enemy.x += 1.0
                enemy.y = 64
            elif enemy.x == 24 and enemy.y > 28:
                # X=24で上に移動中（64→28）
                enemy.y -= 1.0
            elif enemy.x < 48:
                # 24-48ピクセル：右に移動
                enemy.x += 1.0
                # Y座標は28で固定
            elif enemy.x == 48 and enemy.y < 64:
                # X=48で下に移動中（28→64）
                enemy.y += 1.0
            elif enemy.x < 72:
                # 48-72ピクセル：右に移動
                enemy.x += 1.0
                # Y座標は64で固定
            elif enemy.x == 72 and enemy.y > 28:
                # X=72で上に移動中（64→28）
                enemy.y -= 1.0
            else:
                # 72-96ピクセル：右に移動
                enemy.x += 1.0
                # Y座標は28で固定
        else:
            # ホームポジションへ移動
            return self._move_to_formation(enemy)
        
        return False
    
    def is_completed(self, enemy):
        """ジグザグパターンの完了判定"""
        # ホームポジションに到達したかチェック
        distance_to_formation = math.sqrt((enemy.x - enemy.formation_x)**2 + (enemy.y - enemy.formation_y)**2)
        return distance_to_formation <= self.formation_proximity


class LeftLoopPattern(EntryPatternBase):
    """左側からのループパターン"""
    
    def __init__(self):
        super().__init__()
        self.entry_duration = 120  # 2秒間のループ
        self.loop_center_x = Config.WIN_WIDTH / 4
        self.loop_center_y = Config.WIN_HEIGHT / 2
        self.radius = 40
        self.moving_to_formation = False
    
    def update(self, enemy):
        """左ループパターンの更新処理"""
        enemy.entry_timer += 1
        
        if enemy.entry_timer <= self.entry_duration:
            # ループ描画中
            angle = (enemy.entry_timer / self.entry_duration) * 2 * math.pi - math.pi / 2
            progress = enemy.entry_timer / self.entry_duration
            current_radius = progress * self.radius
            enemy.x = self.loop_center_x + math.cos(angle) * current_radius
            enemy.y = self.loop_center_y + math.sin(angle) * current_radius
        else:
            # ループ完了後、ホームポジションへ移動
            self.moving_to_formation = True
            return self._move_to_formation(enemy)
        
        return False
    
    def is_completed(self, enemy):
        """左ループパターンの完了判定"""
        return self.moving_to_formation and enemy.entry_timer > self.entry_duration


class RightLoopPattern(EntryPatternBase):
    """右側からのループパターン"""
    
    def __init__(self):
        super().__init__()
        self.entry_duration = 120  # 2秒間のループ
        self.loop_center_x = Config.WIN_WIDTH * 3 / 4
        self.loop_center_y = Config.WIN_HEIGHT / 2
        self.radius = 40
        self.moving_to_formation = False
    
    def update(self, enemy):
        """右ループパターンの更新処理"""
        enemy.entry_timer += 1
        
        if enemy.entry_timer <= self.entry_duration:
            # ループ描画中
            angle = (enemy.entry_timer / self.entry_duration) * 2 * math.pi - math.pi / 2
            progress = enemy.entry_timer / self.entry_duration
            current_radius = progress * self.radius
            enemy.x = self.loop_center_x - math.cos(angle) * current_radius  # X方向反転
            enemy.y = self.loop_center_y + math.sin(angle) * current_radius
        else:
            # ループ完了後、ホームポジションへ移動
            self.moving_to_formation = True
            return self._move_to_formation(enemy)
        
        return False
    
    def is_completed(self, enemy):
        """右ループパターンの完了判定"""
        return self.moving_to_formation and enemy.entry_timer > self.entry_duration


class EntryPatternFactory:
    """入場パターンのファクトリークラス"""
    
    @staticmethod
    def create(pattern_id):
        """パターンIDに応じて適切な入場パターンを生成"""
        if pattern_id == 1:
            return LeftLoopPattern()
        elif pattern_id == 2:
            return RightLoopPattern()
        elif pattern_id == 3:
            return ZigzagPattern()
        else:
            # デフォルトパターン（直線降下）
            return None
    
    @staticmethod
    def get_initial_position(pattern_id):
        """パターンIDに応じた初期位置を返す"""
        if pattern_id == 1:
            return (-16, Config.WIN_HEIGHT - 20)
        elif pattern_id == 2:
            return (Config.WIN_WIDTH + 16, Config.WIN_HEIGHT - 20)
        elif pattern_id == 3:
            return (0, 64)
        else:
            return (0, -16)  # デフォルト位置