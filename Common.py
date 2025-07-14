# Common Utilities
# Core game utilities and shared functionality

import random
from ExplodeManager import ExpMan
import Config
import GameState

# Entity Lists - global game object containers
enemy_list = []
enemy_bullet_list = []
player_bullet_list = []

# Particle System
explode_manager = ExpMan()

def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    """AABB collision detection"""
    left1 = x1
    right1 = x1 + w1
    top1 = y1
    bottom1 = y1 + h1

    left2 = x2
    right2 = x2 + w2
    top2 = y2
    bottom2 = y2 + h2

    is_collision = (
        left1 < right2 and
        right1 > left2 and
        top1 < bottom2 and
        bottom1 > top2
    )

    return is_collision

def update_enemy_attack_selection():
    """Manage enemy attack state selection"""
    GameState.attack_selection_timer += 1
    
    if GameState.attack_selection_timer >= Config.ATTACK_SELECTION_INTERVAL:
        GameState.attack_selection_timer = 0
        
        # Select enemies in normal state without cooldown
        normal_enemies = [e for e in enemy_list if e.active and e.state == 0 and e.attack_cooldown_timer == 0]
        
        if normal_enemies:
            if random.random() < Config.ATTACK_CHANCE:
                selected_enemy = random.choice(normal_enemies)
                selected_enemy.state = 1  # ENEMY_STATE_PREPARE_ATTACK
                selected_enemy.attack_timer = 0