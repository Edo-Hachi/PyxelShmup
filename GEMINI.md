# Gemini CLI Agent Development Log for PyxelShmup Project

This document details the development process, including features implemented, issues encountered, and the trial-and-error steps taken to resolve them, as guided by the Gemini CLI agent.

## Implemented Features

### 1. Galaga-style Enemy Entry Animation
**Goal:** Implement a dynamic enemy entrance sequence where enemies fly in from off-screen, perform acrobatic maneuvers, and then smoothly transition into their formation positions.

**Implementation Details:**
*   Introduced new enemy states: `ENEMY_STATE_ENTERING` (for the initial flight path) and `ENEMY_STATE_FORMATION_READY` (for waiting in position before group movement begins).
*   Modified `Enemy.py` to handle complex, time-based movement paths using trigonometric functions (`sin`, `cos`) for looping maneuvers.
*   Implemented two distinct entry patterns (`entry_pattern=1` for left-side loop, `entry_pattern=2` for right-side loop).
*   Updated `main.py` to manage the `STATE_PLAYING_ENEMY_ENTRY` sub-state, spawning enemies sequentially with assigned entry patterns and their final formation coordinates.
*   Ensured a synchronized transition from `ENEMY_STATE_FORMATION_READY` to `ENEMY_STATE_NORMAL` (group movement) once all enemies have arrived at their formation spots.

## Issues and Resolutions (Trial & Error Process)

### Issue 1: Initial Prototype Movement (Single Enemy)
*   **Problem:** The first attempt at the looping movement for a single enemy was visually "interesting" but didn't smoothly transition into a static formation position. The enemy would loop, then abruptly settle.
*   **Trial & Error:**
    *   Initial `ENEMY_STATE_ENTERING` logic in `Enemy.py` focused solely on the loop.
    *   Attempted to transition the enemy's state to `ENEMY_STATE_DESCENDING` after the loop duration. This caused issues because `DESCENDING` was designed for post-attack return, not initial entry, leading to unpredictable final positioning.
*   **Resolution:** Modified `Enemy.py` to keep the enemy in `ENEMY_STATE_ENTERING` but introduce a second phase within this state. After the initial loop duration, the enemy's movement logic shifts to a "descending" phase, directly guiding it from its current position to its `formation_pos` using linear interpolation, ensuring a smooth and accurate arrival.

### Issue 2: Premature Stage Clear During Entry Animation
*   **Problem:** When implementing the full stage entry with sequential enemy spawning, the game would immediately trigger "Stage Clear" upon starting. This happened because `Common.check_stage_clear()` was called before all enemies were spawned, finding `Common.enemy_list` temporarily empty.
*   **Trial & Error:** `Common.check_stage_clear()` was initially called unconditionally in `main.py`'s `update_playing` function.
*   **Resolution:** Modified `main.py` to restrict the call to `Common.check_stage_clear()` only when `Common.GameStateSub` is `STATE_PLAYING_FIGHT`. This ensures the stage clear condition is only evaluated during active combat.

### Issue 3: Enemies Not Moving as a Cohesive Formation After Entry
*   **Problem:** After all enemies completed their entry animation and were supposed to form a cohesive unit, they either remained static or moved erratically, not as a synchronized formation.
*   **Trial & Error:**
    *   Introduced `ENEMY_STATE_FORMATION_READY` in `Enemy.py` and `main.py`. Enemies would transition to this state upon reaching their formation spot, waiting for all others. Once all 40 enemies were `FORMATION_READY`, `main.py` would transition them all to `ENEMY_STATE_NORMAL` simultaneously. This fixed the "scattered" individual movement but the *entire group* still didn't move horizontally.
    *   **Root Cause Identification:** The group horizontal movement logic (`Common.enemy_group_x` updates and its application to `enemy.formation_x`) in `main.py` was being executed even when `Common.GameStateSub` was `STATE_PLAYING_ENEMY_ENTRY`. This caused the target `formation_x` for enemies still in their entry animation to constantly shift, preventing them from accurately reaching their intended final positions for the formation.
*   **Resolution:** Wrapped the entire group horizontal movement logic in `main.py` within an `if Common.GameStateSub == Common.STATE_PLAYING_FIGHT:` block. This ensured that the `formation_x` of enemies remained static and predictable during the entry phase, allowing them to correctly settle into their designated spots.

### Issue 4: Player Bullet Speed Increased Dramatically
*   **Problem:** After previous fixes, player bullets started moving at an extremely high speed.
*   **Trial & Error:**
    *   Checked `Bullet.py` for any changes to `self.speed` or its `update` method (no issues found).
    *   Suspected that `Bullet.update()` was being called multiple times per frame.
    *   **Root Cause Identification:** The `for _b in Common.player_bullet_list: _b.update()` call was inadvertently duplicated in `main.py`'s `update_playing` function during a previous refactoring step (when moving bullet updates outside the `Common.StopTimer` block). This resulted in each bullet's `update` method being called twice per frame, effectively doubling its speed.
*   **Resolution:** Removed the duplicate `_b.update()` calls for both player and enemy bullets in `main.py`, ensuring each bullet's `update` method was called only once per frame.

### Issue 5: Enemies Not Moving as a Formation (Again) / Hitstop Interaction
*   **Problem:** After fixing the bullet speed, the enemy formation stopped moving horizontally again, particularly when hitstop occurred.
*   **Trial & Error:**
    *   Realized that while individual enemy `update()` calls were correctly placed outside the `Common.StopTimer` return, the *group movement calculation* (`Common.enemy_group_x` update and `move_amount` calculation) was still being skipped if it was *below* the `return` statement. Also, there was a potential for `move_amount` to be applied inconsistently between `main.py` and `Enemy.py`.
*   **Resolution:**
    1.  **Refactored `Enemy.py`'s `update` method:** Modified `Enemy.py`'s `update` method to accept `move_amount_x` as an argument. All `self.x` and `self.base_x` updates related to group movement were centralized within `Enemy.update()` for all relevant states (`NORMAL`, `PREPARE_ATTACK`, `ATTACK`, `RETURNING`, `DESCENDING`, `CONTINUOUS_ATTACK`). The `if Common.StopTimer > 0: return` was removed from `Enemy.update()` as hitstop is now managed globally in `main.py`.
    2.  **Refactored `main.py`'s `update_playing` function:**
        *   The `move_amount` calculation (including `Common.enemy_group_x` updates and direction changes) was moved to occur *before* the `for _e in Common.enemy_list: _e.update(move_amount)` loop. This ensures `move_amount` is always calculated for the current frame.
        *   The `for _e in Common.enemy_list: _e.update(move_amount)` loop was placed *before* the `if Common.StopTimer > 0: return` statement. This guarantees that individual enemy updates (including their internal application of `move_amount_x`) always run, regardless of hitstop.
        *   The direct application of `move_amount` to `enemy.x` and `enemy.base_x` within the `STATE_PLAYING_FIGHT` block was removed, as this is now handled by `Enemy.update()`.

This comprehensive refactoring of the update loop and hitstop logic ensures that all game elements behave as expected, with enemy formation movement and bullet trajectories remaining consistent even during hitstop events.
