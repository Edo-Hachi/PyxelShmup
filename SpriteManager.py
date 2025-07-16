# Sprite Management
# Handles sprite definitions and sprite-related utilities

from collections import namedtuple
import Config
import json
import os

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


# JSON-based Sprite Management
class SpriteManager:
    """JSON-based sprite management system."""
    
    def __init__(self):
        self.json_sprites = {}  # sprites.jsonから読み込んだデータ
        self.json_file_path = "sprites.json"
        self.load_sprites_json()
    
    def load_sprites_json(self):
        """sprites.jsonファイルを読み込み、スプライトデータを初期化する。"""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, "r", encoding="utf-8") as f:
                    sprite_data = json.load(f)
                
                # スプライトデータを取得
                if "sprites" in sprite_data:
                    self.json_sprites = sprite_data["sprites"]
                    print(f"[SpriteManager] Loaded {len(self.json_sprites)} sprites from JSON")
                else:
                    print("[SpriteManager] Warning: No 'sprites' key found in JSON")
                    self.json_sprites = {}
            else:
                print(f"[SpriteManager] Warning: {self.json_file_path} not found, using fallback")
                self.json_sprites = {}
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"[SpriteManager] Error loading sprites.json: {e}")
            self.json_sprites = {}
    
    def get_player_sprite(self, direction="TOP"):
        """プレイヤースプライトの座標を取得する。
        
        Args:
            direction (str): "TOP", "LEFT", "RIGHT"のいずれか
            
        Returns:
            SpIdx: スプライトの座標 (x, y)
        """
        # JSONからPLAYERグループを検索（新フォーマット: ACT_NAMEフィールド）
        for key, sprite in self.json_sprites.items():
            if sprite.get("NAME") == "PLAYER" and sprite.get("ACT_NAME") == direction:
                return SpIdx(sprite["x"], sprite["y"])
        
        # JSONにない場合は既存のSprListから取得（フォールバック）
        print(f"[SpriteManager] Warning: Player sprite '{direction}' not found in JSON, using fallback")
        return SprList.get(direction, SprList["NULL"])
    
    def get_sprite_by_name_and_tag(self, name, tag=None):
        """名前とタグでスプライトを取得する汎用メソッド。
        
        Args:
            name (str): スプライト名
            tag (str, optional): 検索するタグ
            
        Returns:
            SpIdx: スプライトの座標 (x, y)
        """
        for key, sprite in self.json_sprites.items():
            if sprite.get("NAME") == name:
                if tag is None or tag in sprite.get("tags", []):
                    return SpIdx(sprite["x"], sprite["y"])
        
        # 見つからない場合はNULLを返す
        print(f"[SpriteManager] Warning: Sprite '{name}' with tag '{tag}' not found")
        return SprList["NULL"]
    
    def get_sprite_group(self, name):
        """指定された名前のスプライトグループを全て取得する。
        
        Args:
            name (str): スプライト名
            
        Returns:
            list: スプライトのリスト [(x, y, tags), ...]
        """
        sprites = []
        for key, sprite in self.json_sprites.items():
            if sprite.get("NAME") == name:
                sprites.append({
                    "x": sprite["x"],
                    "y": sprite["y"],
                    "tags": sprite.get("tags", []),
                    "key": key
                })
        return sprites
    
    def get_bullet_sprite(self, frame_number):
        """プレイヤー弾丸のスプライト座標を取得する。
        
        Args:
            frame_number (int): フレーム番号 (0 または 1)
            
        Returns:
            SpIdx: スプライトの座標 (x, y)
        """
        # フレーム番号を文字列に変換
        frame_str = str(frame_number % 2)  # 0 または 1
        
        # JSONからPBULLETグループを検索（新フォーマット: FRAME_NUMフィールド）
        for key, sprite in self.json_sprites.items():
            if sprite.get("NAME") == "PBULLET" and sprite.get("FRAME_NUM") == frame_str:
                return SpIdx(sprite["x"], sprite["y"])
        
        # JSONにない場合は既存のSprListからフォールバック
        print(f"[SpriteManager] Warning: PBULLET frame {frame_number} not found in JSON, using fallback")
        if frame_number == 0:
            return SprList.get("BULLET01", SprList["NULL"])
        else:
            return SprList.get("BULLET02", SprList["NULL"])
    
    def get_bullet_animation_duration(self):
        """JSONからプレイヤー弾丸のアニメーション持続時間を取得する。
        
        Returns:
            int: アニメーション持続フレーム数（デフォルト3）
        """
        # JSONからPBULLETの最初のスプライトの持続時間を取得（新フォーマット: ANIM_SPDフィールド）
        for key, sprite in self.json_sprites.items():
            if sprite.get("NAME") == "PBULLET":
                anim_spd = sprite.get("ANIM_SPD")
                if anim_spd:
                    try:
                        return int(anim_spd)
                    except ValueError:
                        pass
        
        # デフォルト値
        return 3
    
    def get_exhaust_sprite(self, frame_number):
        """エグゾーストスプライトの座標を取得する。
        
        Args:
            frame_number (int): フレーム番号 (0-3)
            
        Returns:
            SpIdx: スプライトの座標 (x, y)
        """
        # フレーム番号を文字列に変換
        frame_str = str(frame_number % 4)  # 0-3の循環
        
        # JSONからEXHSTグループを検索（新フォーマット: FRAME_NUMフィールド）
        for key, sprite in self.json_sprites.items():
            if sprite.get("NAME") == "EXHST" and sprite.get("FRAME_NUM") == frame_str:
                return SpIdx(sprite["x"], sprite["y"])
        
        # JSONにない場合は既存のSprListからフォールバック
        print(f"[SpriteManager] Warning: EXHST frame {frame_number} not found in JSON, using fallback")
        fallback_keys = ["EXT01", "EXT02", "EXT03", "EXT04"]
        if 0 <= frame_number < len(fallback_keys):
            return SprList.get(fallback_keys[frame_number], SprList["NULL"])
        return SprList["NULL"]
    
    def get_exhaust_animation_duration(self):
        """JSONからエグゾーストアニメーションの持続時間を取得する。
        
        Returns:
            int: アニメーション持続フレーム数（デフォルト1）
        """
        # JSONからEXHSTの最初のスプライトの持続時間を取得（新フォーマット: ANIM_SPDフィールド）
        for key, sprite in self.json_sprites.items():
            if sprite.get("NAME") == "EXHST":
                anim_spd = sprite.get("ANIM_SPD")
                if anim_spd:
                    try:
                        return int(anim_spd)
                    except ValueError:
                        pass
        
        # デフォルト値
        return 1


# グローバルインスタンス
sprite_manager = SpriteManager()

# プレイヤー弾丸のアニメーション管理用のヘルパー関数
def get_bullet_animation_frame(game_timer, animation_speed=None):
    """ゲームタイマーに基づいて弾丸のアニメーションフレームを計算する。
    パターン0をNフレーム→パターン1をNフレーム→パターン0に戻る...
    
    Args:
        game_timer (int): ゲームタイマー
        animation_speed (int, optional): 各パターンの持続フレーム数。
                                       Noneの場合はJSONから取得（デフォルト3）
        
    Returns:
        int: アニメーションフレーム (0 または 1)
    """
    # animation_speedが指定されていない場合はJSONから取得
    if animation_speed is None:
        animation_speed = sprite_manager.get_bullet_animation_duration()
    
    # 2N フレーム周期 (パターン0:Nフレーム + パターン1:Nフレーム)
    cycle_position = game_timer % (animation_speed * 2)
    return 0 if cycle_position < animation_speed else 1