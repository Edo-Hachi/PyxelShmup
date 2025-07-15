#!/usr/bin/env python3
"""
SpriteDefiner - Visual Sprite Definition Tool for Pyxel
ビジュアルなスプライト定義ツール

Usage:
    python SpriteDefiner.py
"""

import pyxel
import json
from collections import namedtuple

# Sprite data structure
SpriteInfo = namedtuple("SpriteInfo", ["name", "x", "y"])

class SpriteDefiner:
    def __init__(self):
        # Window settings
        self.WIDTH = 320  # Wider for sprite list
        self.HEIGHT = 200
        
        # Resource settings
        self.RESOURCE_FILE = "my_resource.pyxres"
        self.SPRITE_SIZE = 8
        self.SCALE = 1  # No scaling for simplicity
        
        # UI settings
        self.GRID_COLOR = pyxel.COLOR_WHITE
        self.SELECT_COLOR = pyxel.COLOR_RED
        self.CURSOR_COLOR = pyxel.COLOR_YELLOW
        self.HOVER_COLOR = pyxel.COLOR_CYAN
        self.SPRITE_AREA_WIDTH = 128  # Original sprite area width
        self.SPRITE_AREA_HEIGHT = 128  # Original sprite area height
        
        # State
        self.sprites = {}  # {name: {'x': x, 'y': y, 'tags': []}}
        self.selected_sprite = None  # (x, y)
        self.cursor_sprite = (0, 0)  # Current cursor position (x, y)
        self.hover_sprite = None  # Mouse hover position (x, y)
        self.input_mode = False
        self.input_text = ""
        self.show_details = True  # Always show sprite details
        self.edit_mode = False  # Edit mode for current sprite
        self.message = "Use arrow keys or click to select sprite, press ENTER to name it"
        
        # UI positions
        self.sprite_display_x = 12  # +2 offset
        self.sprite_display_y = 12  # +2 offset
        
        # Initialize Pyxel
        pyxel.init(self.WIDTH, self.HEIGHT, title="SpriteDefiner")
        pyxel.load(self.RESOURCE_FILE)
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        """Update game logic"""
        if self.input_mode:
            self._handle_text_input()
        else:
            self._handle_sprite_selection()
        
        # Save functionality
        if pyxel.btnp(pyxel.KEY_S):
            self._save_to_json()
        
        # Quit
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def _handle_sprite_selection(self):
        """Handle sprite selection with mouse and keyboard"""
        # Handle keyboard cursor movement
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.cursor_sprite = (max(0, self.cursor_sprite[0] - self.SPRITE_SIZE), self.cursor_sprite[1])
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.cursor_sprite = (min(self.SPRITE_AREA_WIDTH - self.SPRITE_SIZE, self.cursor_sprite[0] + self.SPRITE_SIZE), self.cursor_sprite[1])
        if pyxel.btnp(pyxel.KEY_UP):
            self.cursor_sprite = (self.cursor_sprite[0], max(0, self.cursor_sprite[1] - self.SPRITE_SIZE))
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.cursor_sprite = (self.cursor_sprite[0], min(self.SPRITE_AREA_HEIGHT - self.SPRITE_SIZE, self.cursor_sprite[1] + self.SPRITE_SIZE))
        
        # Update hover position
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        if (self.sprite_display_x <= mouse_x < self.sprite_display_x + self.SPRITE_AREA_WIDTH and
            self.sprite_display_y <= mouse_y < self.sprite_display_y + self.SPRITE_AREA_HEIGHT):
            rel_x = mouse_x - self.sprite_display_x
            rel_y = mouse_y - self.sprite_display_y
            hover_x = (rel_x // self.SPRITE_SIZE) * self.SPRITE_SIZE
            hover_y = (rel_y // self.SPRITE_SIZE) * self.SPRITE_SIZE
            self.hover_sprite = (hover_x, hover_y)
        else:
            self.hover_sprite = None
        
        # Handle mouse click
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.hover_sprite:
            self.selected_sprite = self.hover_sprite
            self.cursor_sprite = self.hover_sprite
            self.message = f"Selected sprite at ({self.hover_sprite[0]}, {self.hover_sprite[1]}). Press ENTER to name it."
        
        # Select current cursor position with SPACE
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.selected_sprite = self.cursor_sprite
            self.message = f"Selected sprite at ({self.cursor_sprite[0]}, {self.cursor_sprite[1]}). Press ENTER to name it."
        
        # Toggle edit mode with E
        if pyxel.btnp(pyxel.KEY_E):
            self.edit_mode = not self.edit_mode
            if self.edit_mode:
                self.message = "Edit mode ON. Press E to return to view mode."
            else:
                self.message = "View mode ON. Press E to enter edit mode."
        
        # Enter naming mode
        if pyxel.btnp(pyxel.KEY_RETURN) and self.selected_sprite:
            self.input_mode = True
            self.input_text = ""
            self.message = "Enter sprite name (press ENTER to confirm, ESC to cancel):"    
    
    def _handle_text_input(self):
        """Handle text input for sprite naming"""
        # Handle character input
        for i in range(26):  # A-Z
            if pyxel.btnp(pyxel.KEY_A + i):
                if pyxel.btn(pyxel.KEY_SHIFT):
                    self.input_text += chr(ord('A') + i)
                else:
                    self.input_text += chr(ord('a') + i)
        
        # Numbers
        for i in range(10):
            if pyxel.btnp(pyxel.KEY_0 + i):
                self.input_text += str(i)
        
        # Underscore
        if pyxel.btnp(pyxel.KEY_MINUS) and pyxel.btn(pyxel.KEY_SHIFT):
            self.input_text += "_"
        
        # Backspace
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            if self.input_text:
                self.input_text = self.input_text[:-1]
        
        # Confirm input
        if pyxel.btnp(pyxel.KEY_RETURN):
            if self.input_text and self.selected_sprite:
                self.sprites[self.input_text] = {
                    'x': self.selected_sprite[0],
                    'y': self.selected_sprite[1],
                    'tags': ['UNDEF']  # Default tag
                }
                self.message = f"Added sprite '{self.input_text}' at {self.selected_sprite}"
                self.selected_sprite = None
            self.input_mode = False
            self.input_text = ""
        
        # Cancel input
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.input_mode = False
            self.input_text = ""
            self.message = "Cancelled. Click on sprite to select."
    
    def _save_to_json(self):
        """Save sprites to JSON file"""
        sprite_data = {
            "meta": {
                "sprite_size": self.SPRITE_SIZE,
                "resource_file": self.RESOURCE_FILE,
                "created_by": "SpriteDefiner",
                "version": "1.0"
            },
            "sprites": {}
        }
        
        for name, data in self.sprites.items():
            sprite_data["sprites"][name] = {
                "x": data['x'], 
                "y": data['y'],
                "tags": data['tags']
            }
        
        try:
            with open("sprites.json", "w", encoding="utf-8") as f:
                json.dump(sprite_data, f, indent=2, ensure_ascii=False)
            self.message = f"Saved {len(self.sprites)} sprites to sprites.json"
        except Exception as e:
            self.message = f"Error saving: {e}"
    
    def draw(self):
        """Draw the application"""
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # Draw sprite sheet with scale
        self._draw_sprite_sheet()
        
        # Draw grid
        self._draw_grid()
        
        # Draw hover highlight
        self._draw_hover()
        
        # Draw cursor
        self._draw_cursor()
        
        # Draw selection highlight
        self._draw_selection()
        
        # Draw mouse cursor
        self._draw_mouse_cursor()
        
        # Draw UI
        self._draw_ui()
    
    def _draw_sprite_sheet(self):
        """Draw the sprite sheet from image bank 0"""
        # Draw full sprite sheet at original size first
        pyxel.blt(self.sprite_display_x, self.sprite_display_y, 
                 0, 0, 0, 
                 self.SPRITE_AREA_WIDTH, self.SPRITE_AREA_HEIGHT)
    
    def _draw_grid(self):
        """Draw grid lines over the sprite sheet"""
        # Vertical lines
        for x in range(0, self.SPRITE_AREA_WIDTH + 1, self.SPRITE_SIZE):
            line_x = self.sprite_display_x + x
            pyxel.line(
                line_x, self.sprite_display_y,
                line_x, self.sprite_display_y + self.SPRITE_AREA_HEIGHT,
                self.GRID_COLOR
            )
        
        # Horizontal lines
        for y in range(0, self.SPRITE_AREA_HEIGHT + 1, self.SPRITE_SIZE):
            line_y = self.sprite_display_y + y
            pyxel.line(
                self.sprite_display_x, line_y,
                self.sprite_display_x + self.SPRITE_AREA_WIDTH, line_y,
                self.GRID_COLOR
            )
    
    def _draw_hover(self):
        """Draw hover highlight"""
        if self.hover_sprite:
            x, y = self.hover_sprite
            rect_x = self.sprite_display_x + x
            rect_y = self.sprite_display_y + y
            # Draw subtle hover rectangle
            pyxel.rectb(rect_x, rect_y, self.SPRITE_SIZE, self.SPRITE_SIZE, self.HOVER_COLOR)
    
    def _draw_cursor(self):
        """Draw keyboard cursor"""
        x, y = self.cursor_sprite
        rect_x = self.sprite_display_x + x
        rect_y = self.sprite_display_y + y
        # Draw cursor rectangle
        pyxel.rectb(rect_x, rect_y, self.SPRITE_SIZE, self.SPRITE_SIZE, self.CURSOR_COLOR)
        pyxel.rectb(rect_x + 1, rect_y + 1, self.SPRITE_SIZE - 2, self.SPRITE_SIZE - 2, self.CURSOR_COLOR)
    
    def _draw_selection(self):
        """Draw selection highlight"""
        if self.selected_sprite:
            x, y = self.selected_sprite
            rect_x = self.sprite_display_x + x
            rect_y = self.sprite_display_y + y
            # Draw simple selection rectangle (same as grid)
            pyxel.rectb(rect_x, rect_y, self.SPRITE_SIZE, self.SPRITE_SIZE, self.SELECT_COLOR)
    
    def _draw_mouse_cursor(self):
        """Draw custom mouse cursor"""
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        # Draw crosshair cursor
        pyxel.line(mouse_x - 3, mouse_y, mouse_x + 3, mouse_y, pyxel.COLOR_WHITE)
        pyxel.line(mouse_x, mouse_y - 3, mouse_x, mouse_y + 3, pyxel.COLOR_WHITE)
        pyxel.pset(mouse_x, mouse_y, pyxel.COLOR_RED)
    
    def _draw_ui(self):
        """Draw user interface"""
        ui_start_y = self.sprite_display_y + self.SPRITE_AREA_HEIGHT + 10
        
        # Message
        pyxel.text(10, ui_start_y, self.message, pyxel.COLOR_WHITE)
        
        # Input text (if in input mode)
        if self.input_mode:
            pyxel.text(10, ui_start_y + 10, f"Name: {self.input_text}_", pyxel.COLOR_YELLOW)
        
        # Right panel content
        sprite_list_x = self.sprite_display_x + self.SPRITE_AREA_WIDTH + 20
        self._draw_dynamic_info(sprite_list_x)
        
        # Controls
        controls_y = self.HEIGHT - 40
        pyxel.text(10, controls_y, "Controls:", pyxel.COLOR_YELLOW)
        pyxel.text(10, controls_y + 8, "Arrow Keys: Move cursor | Space/Click: Select", pyxel.COLOR_WHITE)
        pyxel.text(10, controls_y + 16, "Enter: Name sprite | S: Save | Q/ESC: Quit", pyxel.COLOR_WHITE)
        
        # Current cursor position and mode info
        # Current cursor position and mode info
        mode_text = "EDIT" if self.edit_mode else "VIEW"
        pyxel.text(10, controls_y + 24, f"Cursor: ({self.cursor_sprite[0]}, {self.cursor_sprite[1]}) | Mode: {mode_text} | E: Toggle", pyxel.COLOR_GRAY)
    
    def _draw_sprite_list(self, x_pos):
        """Draw the list of defined sprites"""
        pyxel.text(x_pos, self.sprite_display_y, f"Defined sprites ({len(self.sprites)}):", pyxel.COLOR_CYAN)
        
        y_offset = 10
        max_display = 12
        for i, (name, data) in enumerate(list(self.sprites.items())[:max_display]):
            sprite_pos = (data['x'], data['y'])
            color = pyxel.COLOR_YELLOW if sprite_pos == self.selected_sprite else pyxel.COLOR_WHITE
            pyxel.text(x_pos, self.sprite_display_y + y_offset, f"{name}: ({data['x']},{data['y']})", color)
            y_offset += 8
        
        if len(self.sprites) > max_display:
            pyxel.text(x_pos, self.sprite_display_y + y_offset, f"... +{len(self.sprites) - max_display} more", pyxel.COLOR_GRAY)
    
    def _draw_dynamic_info(self, x_pos):
        """Draw dynamic sprite information based on cursor position"""
        # Always show current cursor sprite info
        x, y = self.cursor_sprite
        sprite_number = self._get_sprite_number(x, y)
        
        # Find sprite data by cursor position
        sprite_name = "NONAME"
        sprite_tags = ["UNDEF"]
        
        for name, data in self.sprites.items():
            if data['x'] == x and data['y'] == y:
                sprite_name = name
                sprite_tags = data['tags']
                break
        
        # Header - always visible
        pyxel.text(x_pos, self.sprite_display_y, "SPRITE DETAILS", pyxel.COLOR_CYAN)
        pyxel.text(x_pos, self.sprite_display_y + 12, f"Position: ({x}, {y})", pyxel.COLOR_WHITE)
        pyxel.text(x_pos, self.sprite_display_y + 22, f"Number: #{sprite_number}", pyxel.COLOR_WHITE)
        pyxel.text(x_pos, self.sprite_display_y + 32, f"Name: {sprite_name}", pyxel.COLOR_YELLOW)
        
        # Mode indicator
        mode_text = "EDIT" if self.edit_mode else "VIEW"
        mode_color = pyxel.COLOR_RED if self.edit_mode else pyxel.COLOR_GREEN
        pyxel.text(x_pos, self.sprite_display_y + 44, f"Mode: {mode_text}", mode_color)
        
        # Content based on mode
        if self.edit_mode:
            self._draw_edit_content(x_pos, sprite_tags)
        else:
            self._draw_view_content(x_pos)
    
    def _draw_edit_content(self, x_pos, sprite_tags):
        """Draw edit mode content"""
        start_y = self.sprite_display_y + 58
        
        pyxel.text(x_pos, start_y, "Tags:", pyxel.COLOR_WHITE)
        
        tag_y = 10
        for i, tag in enumerate(sprite_tags):
            pyxel.text(x_pos + 10, start_y + tag_y, f"- {tag}", pyxel.COLOR_GREEN)
            tag_y += 10
        
        # Edit instructions
        pyxel.text(x_pos, start_y + tag_y + 10, "Edit Controls:", pyxel.COLOR_CYAN)
        pyxel.text(x_pos, start_y + tag_y + 20, "T: Add tag", pyxel.COLOR_GRAY)
        pyxel.text(x_pos, start_y + tag_y + 30, "D: Delete tag", pyxel.COLOR_GRAY)
        pyxel.text(x_pos, start_y + tag_y + 40, "R: Rename sprite", pyxel.COLOR_GRAY)
    
    def _draw_view_content(self, x_pos):
        """Draw view mode content - sprite list"""
        start_y = self.sprite_display_y + 58
        
        pyxel.text(x_pos, start_y, f"All sprites ({len(self.sprites)}):", pyxel.COLOR_CYAN)
        
        y_offset = 12
        max_display = 8  # Reduced to fit in remaining space
        for i, (name, data) in enumerate(list(self.sprites.items())[:max_display]):
            sprite_pos = (data['x'], data['y'])
            color = pyxel.COLOR_YELLOW if sprite_pos == self.cursor_sprite else pyxel.COLOR_WHITE
            pyxel.text(x_pos, start_y + y_offset, f"{name}: ({data['x']},{data['y']})", color)
            y_offset += 8
        
        if len(self.sprites) > max_display:
            pyxel.text(x_pos, start_y + y_offset, f"... +{len(self.sprites) - max_display}", pyxel.COLOR_GRAY)
    
    def _get_sprite_number(self, x, y):
        """Calculate sprite number based on position"""
        grid_x = x // self.SPRITE_SIZE
        grid_y = y // self.SPRITE_SIZE
        return grid_y * (self.SPRITE_AREA_WIDTH // self.SPRITE_SIZE) + grid_x


if __name__ == "__main__":
    SpriteDefiner()