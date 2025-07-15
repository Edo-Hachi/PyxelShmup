#!/usr/bin/env python3
"""
SpriteDefiner v2 - Enhanced Visual Sprite Definition Tool for Pyxel
"""

import pyxel
import json
from collections import namedtuple

class SpriteDefiner:
    def __init__(self):
        # Window settings
        self.WIDTH = 320
        self.HEIGHT = 240  # Increased height for status area
        
        # Resource settings
        self.RESOURCE_FILE = "my_resource.pyxres"
        self.SPRITE_SIZE = 8
        
        # UI settings
        self.GRID_COLOR_VIEW = pyxel.COLOR_WHITE
        self.GRID_COLOR_EDIT = pyxel.COLOR_RED
        self.SELECT_COLOR = pyxel.COLOR_RED
        self.CURSOR_COLOR_VIEW = pyxel.COLOR_GREEN
        self.CURSOR_COLOR_EDIT = pyxel.COLOR_RED
        self.HOVER_COLOR = pyxel.COLOR_CYAN
        self.SPRITE_AREA_WIDTH = 128
        self.SPRITE_AREA_HEIGHT = 128
        
        # State
        self.sprites = {}  # {name: {'x': x, 'y': y, 'tags': []}}
        self.selected_sprite = None  # (x, y)
        self.cursor_sprite = (0, 0)  # Current cursor position (x, y)
        self.hover_sprite = None  # Mouse hover position (x, y)
        
        # Edit history - simple list of sprite names
        self.edited_sprite_names = []  # List of recently edited sprite names
        
        # Input modes
        self.input_mode = False  # Legacy naming mode
        self.input_text = ""
        
        # Edit system
        self.edit_mode = False  # EDIT/VIEW mode
        self.command_mode = None  # Current command: None, 'NAME', 'DIC_1', 'DIC_2', 'DIC_3'
        self.command_input = ""  # Input text for current command
        self.edit_locked_sprite = None  # Sprite position locked during edit
        
        # Confirmation modes
        self.save_confirm_mode = False  # Y/N confirmation for F10 save
        self.quit_confirm_mode = False  # Y/N confirmation for F12 quit
        
        self.message = "Use arrow keys to move (auto-select), F1 for EDIT, F2 for VIEW"
        
        # UI positions
        self.sprite_display_x = 12
        self.sprite_display_y = 12
        
        # Initialize cursor and selection to same position
        self.selected_sprite = self.cursor_sprite  # Auto-select initial position
        
        # Initialize Pyxel
        pyxel.init(self.WIDTH, self.HEIGHT, title="SpriteDefiner v2", quit_key=pyxel.KEY_NONE)
        pyxel.load(self.RESOURCE_FILE)
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        """Update game logic"""
        if self.save_confirm_mode:
            self._handle_save_confirmation()
        elif self.quit_confirm_mode:
            self._handle_quit_confirmation()
        elif self.input_mode:
            self._handle_text_input()
        elif self.command_mode:
            self._handle_command_input()
        else:
            self._handle_normal_input()
        
        # Save functionality (F10 - VIEW mode only) - now with confirmation
        if pyxel.btnp(pyxel.KEY_F10) and not self.edit_mode and not self.save_confirm_mode and not self.quit_confirm_mode:
            self.save_confirm_mode = True
            self.message = "Save to sprites.json? Press Y to confirm, N to cancel"
        
        # Load functionality (F11 - VIEW mode only)
        if pyxel.btnp(pyxel.KEY_F11) and not self.edit_mode and not self.save_confirm_mode and not self.quit_confirm_mode:
            self._load_from_json()
        
        # Quit (F12 only - VIEW mode only) - now with confirmation
        if pyxel.btnp(pyxel.KEY_F12) and not self.edit_mode and not self.save_confirm_mode and not self.quit_confirm_mode:
            self.quit_confirm_mode = True
            self.message = "Really quit? Press Y to confirm, N to cancel"
        
        # Disabled ESC/Q quit for safety
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            if self.edit_mode:
                self.message = "Cannot quit in EDIT mode - press F2 to exit EDIT first"
            else:
                self.message = "Use F12 to quit (ESC/Q disabled for safety)"
    
    def _handle_normal_input(self):
        """Handle normal input (cursor movement, mode switching)"""
        # Handle keyboard cursor movement (disabled in EDIT mode)
        if not self.edit_mode:
            old_cursor = self.cursor_sprite
            
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.cursor_sprite = (max(0, self.cursor_sprite[0] - self.SPRITE_SIZE), self.cursor_sprite[1])
            if pyxel.btnp(pyxel.KEY_RIGHT):
                self.cursor_sprite = (min(self.SPRITE_AREA_WIDTH - self.SPRITE_SIZE, self.cursor_sprite[0] + self.SPRITE_SIZE), self.cursor_sprite[1])
            if pyxel.btnp(pyxel.KEY_UP):
                self.cursor_sprite = (self.cursor_sprite[0], max(0, self.cursor_sprite[1] - self.SPRITE_SIZE))
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.cursor_sprite = (self.cursor_sprite[0], min(self.SPRITE_AREA_HEIGHT - self.SPRITE_SIZE, self.cursor_sprite[1] + self.SPRITE_SIZE))
            
            # Auto-select sprite when cursor moves
            if old_cursor != self.cursor_sprite:
                self.selected_sprite = self.cursor_sprite
                self.message = f"Auto-selected sprite at {self.cursor_sprite}"
        
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
        
        # Handle mouse click (disabled in EDIT mode)
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.hover_sprite and not self.edit_mode:
            self.selected_sprite = self.hover_sprite
            self.cursor_sprite = self.hover_sprite
            self.message = f"Selected sprite at {self.hover_sprite}"
        
        # Manual select with SPACE (now optional since auto-select is active)
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.edit_mode:
            self.selected_sprite = self.cursor_sprite
            self.message = f"Manually selected sprite at {self.cursor_sprite}"
        
        # Enter EDIT mode with F1
        if pyxel.btnp(pyxel.KEY_F1) and not self.edit_mode:
            self.edit_mode = True
            self.edit_locked_sprite = self.cursor_sprite
            self.message = f"EDIT mode LOCKED on sprite ({self.cursor_sprite[0]}, {self.cursor_sprite[1]}) - Use commands: N, 1, 2, 3"
        
        # Exit EDIT mode with F2
        if pyxel.btnp(pyxel.KEY_F2) and self.edit_mode:
            # Auto-save when exiting EDIT mode
            self._save_to_json()
            self.edit_mode = False
            self.edit_locked_sprite = None
            self.message = "VIEW mode - Auto-saved changes"
        
        # Handle edit mode commands
        if self.edit_mode:
            # F3 for manual save in EDIT mode
            if pyxel.btnp(pyxel.KEY_F3):
                self._save_to_json()
            
            if pyxel.btnp(pyxel.KEY_N):
                self.command_mode = 'NAME'
                self.command_input = ""
                self.message = "Enter sprite name:"
            elif pyxel.btnp(pyxel.KEY_1):
                self.command_mode = 'DIC_1'
                self.command_input = ""
                self.message = "Enter ACT_NAME:"
            elif pyxel.btnp(pyxel.KEY_2):
                self.command_mode = 'DIC_2'
                self.command_input = ""
                self.message = "Enter FRAME_NUM:"
            elif pyxel.btnp(pyxel.KEY_3):
                self.command_mode = 'DIC_3'
                self.command_input = ""
                self.message = "Enter ANIM_SPEED:"
            # Extension tags (4-8 keys)
            elif pyxel.btnp(pyxel.KEY_4):
                self.command_mode = 'EXT_1'
                self.command_input = ""
                self.message = "Enter EXT1:"
            elif pyxel.btnp(pyxel.KEY_5):
                self.command_mode = 'EXT_2'
                self.command_input = ""
                self.message = "Enter EXT2:"
            elif pyxel.btnp(pyxel.KEY_6):
                self.command_mode = 'EXT_3'
                self.command_input = ""
                self.message = "Enter EXT3:"
            elif pyxel.btnp(pyxel.KEY_7):
                self.command_mode = 'EXT_4'
                self.command_input = ""
                self.message = "Enter EXT4:"
            elif pyxel.btnp(pyxel.KEY_8):
                self.command_mode = 'EXT_5'
                self.command_input = ""
                self.message = "Enter EXT5:"
        
        # Legacy naming mode
        if pyxel.btnp(pyxel.KEY_RETURN) and self.selected_sprite and not self.edit_mode:
            self.input_mode = True
            self.input_text = ""
            self.message = "Enter sprite name (legacy mode):"
    
    def _handle_command_input(self):
        """Handle command input mode"""
        # Handle character input
        for i in range(26):  # A-Z
            if pyxel.btnp(pyxel.KEY_A + i):
                if pyxel.btn(pyxel.KEY_SHIFT):
                    self.command_input += chr(ord('A') + i)
                else:
                    self.command_input += chr(ord('a') + i)
        
        # Numbers
        for i in range(10):
            if pyxel.btnp(pyxel.KEY_0 + i):
                self.command_input += str(i)
        
        # Underscore
        if pyxel.btnp(pyxel.KEY_MINUS) and pyxel.btn(pyxel.KEY_SHIFT):
            self.command_input += "_"
        
        # Backspace
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            if self.command_input:
                self.command_input = self.command_input[:-1]
        
        # Confirm input
        if pyxel.btnp(pyxel.KEY_RETURN):
            self._process_command()
        
        # Cancel input
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.command_mode = None
            self.command_input = ""
            self.message = "Command cancelled"
    
    def _handle_text_input(self):
        """Handle legacy text input for sprite naming"""
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
                sprite_key = f"{self.selected_sprite[0]}_{self.selected_sprite[1]}"
                self.sprites[sprite_key] = {
                    'x': self.selected_sprite[0],
                    'y': self.selected_sprite[1],
                    'name': self.input_text,
                    'tags': ['UNDEF']
                }
                self.message = f"Added sprite '{self.input_text}'"
                self.selected_sprite = None
            self.input_mode = False
            self.input_text = ""
        
        # Cancel input
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.input_mode = False
            self.input_text = ""
            self.message = "Cancelled"
    
    def _handle_save_confirmation(self):
        """Handle Y/N confirmation for save"""
        if pyxel.btnp(pyxel.KEY_Y):
            self.save_confirm_mode = False
            self._save_to_json()
        elif pyxel.btnp(pyxel.KEY_N) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.save_confirm_mode = False
            self.message = "Save cancelled"
    
    def _handle_quit_confirmation(self):
        """Handle Y/N confirmation for quit"""
        if pyxel.btnp(pyxel.KEY_Y):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_N) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.quit_confirm_mode = False
            self.message = "Quit cancelled"
    
    def _process_command(self):
        """Process the completed command"""
        # Use locked sprite position in EDIT mode
        x, y = self.edit_locked_sprite if self.edit_locked_sprite else self.cursor_sprite
        
        if self.command_mode == 'NAME':
            if self.command_input:
                # Find existing sprite at this position and preserve its tags
                existing_tags = ['UNDEF']
                sprite_key = f"{x}_{y}"  # Use position as unique key
                
                for key, data in list(self.sprites.items()):
                    if data['x'] == x and data['y'] == y:
                        existing_tags = data['tags']  # Preserve existing tags
                        del self.sprites[key]
                        break
                
                # Add sprite with position-based key to allow same names
                self.sprites[sprite_key] = {
                    'x': x,
                    'y': y,
                    'name': self.command_input,  # Group name (can be same for multiple sprites)
                    'tags': existing_tags
                }
                
                # Add to edited sprite names list
                self._add_edited_sprite_name(self.command_input)
                self.message = f"Set group name '{self.command_input}' for sprite at ({x}, {y})"
            
        elif self.command_mode in ['DIC_1', 'DIC_2', 'DIC_3', 'EXT_1', 'EXT_2', 'EXT_3', 'EXT_4', 'EXT_5']:
            # Find existing sprite at cursor position
            sprite_key = None
            for key, data in self.sprites.items():
                if data['x'] == x and data['y'] == y:
                    sprite_key = key
                    break
            
            if sprite_key:
                # Calculate tag index (DIC_1-3 → 0-2, EXT_1-5 → 3-7)
                if self.command_mode.startswith('DIC_'):
                    tag_index = int(self.command_mode.split('_')[1]) - 1
                elif self.command_mode.startswith('EXT_'):
                    tag_index = int(self.command_mode.split('_')[1]) + 2  # EXT_1 → index 3
                
                if self.command_input:
                    # Ensure tags list has enough slots
                    while len(self.sprites[sprite_key]['tags']) <= tag_index:
                        self.sprites[sprite_key]['tags'].append('UNDEF')
                    
                    # Remove UNDEF if it's the only tag
                    if self.sprites[sprite_key]['tags'] == ['UNDEF']:
                        self.sprites[sprite_key]['tags'] = []
                    
                    # Set the tag
                    if tag_index < len(self.sprites[sprite_key]['tags']):
                        self.sprites[sprite_key]['tags'][tag_index] = self.command_input
                    else:
                        self.sprites[sprite_key]['tags'].append(self.command_input)
                    
                    # Add to edited sprite names list (get current sprite name)
                    sprite_name = self.sprites[sprite_key].get('name', 'NONAME')
                    self._add_edited_sprite_name(sprite_name)
                    self.message = f"Set {self.command_mode} to '{self.command_input}'"
                else:
                    self.message = "Tag cannot be empty"
            else:
                # Create new sprite if none exists at this position
                sprite_key = f"{x}_{y}"
                self.sprites[sprite_key] = {
                    'x': x,
                    'y': y,
                    'name': 'NONAME',
                    'tags': ['UNDEF']
                }
                self.message = "Created new sprite - set NAME first"
        
        # Reset command mode
        self.command_mode = None
        self.command_input = ""
    
    def _add_edited_sprite_name(self, sprite_name):
        """Add sprite name to recently edited list"""
        # Remove if already exists to avoid duplicates
        if sprite_name in self.edited_sprite_names:
            self.edited_sprite_names.remove(sprite_name)
        
        # Add to end
        self.edited_sprite_names.append(sprite_name)
        
        # Keep only last 6 entries
        if len(self.edited_sprite_names) > 6:
            self.edited_sprite_names = self.edited_sprite_names[-6:]
    
    def _save_to_json(self):
        """Save sprites to JSON file"""
        sprite_data = {
            "meta": {
                "sprite_size": self.SPRITE_SIZE,
                "resource_file": self.RESOURCE_FILE,
                "created_by": "SpriteDefiner v2",
                "version": "2.0"
            },
            "sprites": {}
        }
        
        for key, data in self.sprites.items():
            sprite_data["sprites"][key] = {
                "x": data['x'], 
                "y": data['y'],
                "name": data.get('name', 'NONAME'),
                "tags": data['tags']
            }
        
        try:
            with open("sprites.json", "w", encoding="utf-8") as f:
                json.dump(sprite_data, f, indent=2, ensure_ascii=False)
            
            # Different messages based on context
            if self.edit_mode:
                self.message = f"Saved {len(self.sprites)} sprites (EDIT mode active)"
            else:
                self.message = f"F10: Saved {len(self.sprites)} sprites to sprites.json"
        except Exception as e:
            self.message = f"Error saving: {e}"
    
    def _load_from_json(self):
        """Load sprites from JSON file"""
        try:
            with open("sprites.json", "r", encoding="utf-8") as f:
                sprite_data = json.load(f)
            
            # Clear existing sprites
            self.sprites = {}
            
            # Load sprites from JSON
            if "sprites" in sprite_data:
                for key, data in sprite_data["sprites"].items():
                    self.sprites[key] = {
                        'x': data['x'],
                        'y': data['y'], 
                        'name': data.get('name', 'NONAME'),
                        'tags': data.get('tags', ['UNDEF'])
                    }
                    
            self.message = f"F11: Loaded {len(self.sprites)} sprites from sprites.json"
        except FileNotFoundError:
            self.message = "F11: No sprites.json file found"
        except Exception as e:
            self.message = f"Error loading: {e}"
    
    def draw(self):
        """Draw the application"""
        pyxel.cls(pyxel.COLOR_BLACK)
        
        # Draw sprite sheet
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
        
        # Draw status area below grid
        status_y = self.sprite_display_y + self.SPRITE_AREA_HEIGHT + 10
        self._draw_status_area(status_y)
        
        # Draw right panel
        sprite_list_x = self.sprite_display_x + self.SPRITE_AREA_WIDTH + 20
        self._draw_dynamic_info(sprite_list_x)
        
        # Draw recent edited sprite names (always visible at far right)
        recent_names_x = sprite_list_x + 100  # Position at far right (moved 20px left)
        self._draw_recent_sprite_names(recent_names_x)
        
        # Controls (bottom)
        controls_y = self.HEIGHT - 25
        if self.edit_mode:
            pyxel.text(10, controls_y, "EDIT MODE ACTIVE - Movement LOCKED | F2: Exit+Save | F3: Save", pyxel.COLOR_RED)
        else:
            pyxel.text(10, controls_y, "Arrow Keys: Auto-Select | F1: EDIT | F10: Save | F11: Load | F12: Quit", pyxel.COLOR_PINK)
        pyxel.text(10, controls_y + 8, f"Cursor: ({self.cursor_sprite[0]}, {self.cursor_sprite[1]})", pyxel.COLOR_GRAY)
    
    def _draw_sprite_sheet(self):
        """Draw the sprite sheet from image bank 0"""
        pyxel.blt(self.sprite_display_x, self.sprite_display_y, 
                 0, 0, 0, 
                 self.SPRITE_AREA_WIDTH, self.SPRITE_AREA_HEIGHT)
    
    def _draw_grid(self):
        """Draw grid lines over the sprite sheet"""
        # Choose grid color based on mode
        grid_color = self.GRID_COLOR_EDIT if self.edit_mode else self.GRID_COLOR_VIEW
        
        # Vertical lines
        for x in range(0, self.SPRITE_AREA_WIDTH + 1, self.SPRITE_SIZE):
            line_x = self.sprite_display_x + x
            pyxel.line(
                line_x, self.sprite_display_y,
                line_x, self.sprite_display_y + self.SPRITE_AREA_HEIGHT,
                grid_color
            )
        
        # Horizontal lines
        for y in range(0, self.SPRITE_AREA_HEIGHT + 1, self.SPRITE_SIZE):
            line_y = self.sprite_display_y + y
            pyxel.line(
                self.sprite_display_x, line_y,
                self.sprite_display_x + self.SPRITE_AREA_WIDTH, line_y,
                grid_color
            )
    
    def _draw_hover(self):
        """Draw hover highlight"""
        if self.hover_sprite:
            x, y = self.hover_sprite
            rect_x = self.sprite_display_x + x
            rect_y = self.sprite_display_y + y
            pyxel.rectb(rect_x, rect_y, self.SPRITE_SIZE, self.SPRITE_SIZE, self.HOVER_COLOR)
    
    def _draw_cursor(self):
        """Draw keyboard cursor"""
        # Choose cursor color based on mode
        cursor_color = self.CURSOR_COLOR_EDIT if self.edit_mode else self.CURSOR_COLOR_VIEW
        
        # In EDIT mode, show locked sprite position; in VIEW mode, show current cursor
        if self.edit_mode and self.edit_locked_sprite:
            x, y = self.edit_locked_sprite
            # Draw thicker cursor for locked sprite
            rect_x = self.sprite_display_x + x
            rect_y = self.sprite_display_y + y
            pyxel.rectb(rect_x, rect_y, self.SPRITE_SIZE, self.SPRITE_SIZE, cursor_color)
            pyxel.rectb(rect_x + 1, rect_y + 1, self.SPRITE_SIZE - 2, self.SPRITE_SIZE - 2, cursor_color)
            pyxel.rectb(rect_x + 2, rect_y + 2, self.SPRITE_SIZE - 4, self.SPRITE_SIZE - 4, cursor_color)
        else:
            x, y = self.cursor_sprite
            rect_x = self.sprite_display_x + x
            rect_y = self.sprite_display_y + y
            pyxel.rectb(rect_x, rect_y, self.SPRITE_SIZE, self.SPRITE_SIZE, cursor_color)
            pyxel.rectb(rect_x + 1, rect_y + 1, self.SPRITE_SIZE - 2, self.SPRITE_SIZE - 2, cursor_color)
    
    def _draw_selection(self):
        """Draw selection highlight"""
        if self.selected_sprite:
            x, y = self.selected_sprite
            rect_x = self.sprite_display_x + x
            rect_y = self.sprite_display_y + y
            pyxel.rectb(rect_x, rect_y, self.SPRITE_SIZE, self.SPRITE_SIZE, self.SELECT_COLOR)
    
    def _draw_mouse_cursor(self):
        """Draw custom mouse cursor"""
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        pyxel.line(mouse_x - 3, mouse_y, mouse_x + 3, mouse_y, pyxel.COLOR_WHITE)
        pyxel.line(mouse_x, mouse_y - 3, mouse_x, mouse_y + 3, pyxel.COLOR_WHITE)
        pyxel.pset(mouse_x, mouse_y, pyxel.COLOR_RED)
    
    def _draw_status_area(self, y_pos):
        """Draw status area below the grid"""
        # Mode indicator with clear next action
        if self.edit_mode:
            if self.edit_locked_sprite:
                lock_info = f" LOCKED ({self.edit_locked_sprite[0]}, {self.edit_locked_sprite[1]})"
                pyxel.text(10, y_pos, f"F2>VIEW [EDIT{lock_info}]", pyxel.COLOR_RED)
            else:
                pyxel.text(10, y_pos, "F2>VIEW [EDIT]", pyxel.COLOR_RED)
        else:
            pyxel.text(10, y_pos, "F1>EDIT [VIEW]", pyxel.COLOR_GREEN)
        
        # Command options (only in EDIT mode)
        if self.edit_mode and not self.command_mode:
            pyxel.text(10, y_pos + 12, "Commands: [N:NAME] [1-3:DIC] [4-8:EXT] [F3:SAVE]", pyxel.COLOR_CYAN)
        
        # Command input prompt
        if self.command_mode:
            prompt_text = f"{self.command_mode}> {self.command_input}_"
            pyxel.text(10, y_pos + 24, prompt_text, pyxel.COLOR_YELLOW)
        
        # Save confirmation prompt
        if self.save_confirm_mode:
            pyxel.text(10, y_pos + 24, "Save to sprites.json? [Y]es / [N]o / [ESC]ape", pyxel.COLOR_YELLOW)
        
        # Quit confirmation prompt
        if self.quit_confirm_mode:
            pyxel.text(10, y_pos + 24, "Really quit? [Y]es / [N]o / [ESC]ape", pyxel.COLOR_RED)
        
        # Message
        message_color = pyxel.COLOR_YELLOW if self.save_confirm_mode or self.quit_confirm_mode else pyxel.COLOR_WHITE
        pyxel.text(10, y_pos + 36, self.message, message_color)
    
    def _draw_dynamic_info(self, x_pos):
        """Draw dynamic sprite information based on cursor position"""
        # Show locked sprite info in EDIT mode, cursor info in VIEW mode
        if self.edit_mode and self.edit_locked_sprite:
            x, y = self.edit_locked_sprite
        else:
            x, y = self.cursor_sprite
        sprite_number = self._get_sprite_number(x, y)
        
        # Find sprite data by cursor position
        sprite_name = "NONAME"
        sprite_tags = ["UNDEF"]
        
        for key, data in self.sprites.items():
            if data['x'] == x and data['y'] == y:
                sprite_name = data.get('name', 'NONAME')
                sprite_tags = data['tags']
                break
        
        # Header - always visible
        pyxel.text(x_pos, self.sprite_display_y, "SPRITE DETAILS", pyxel.COLOR_CYAN)
        pyxel.text(x_pos, self.sprite_display_y + 12, f"Position: ({x}, {y})", pyxel.COLOR_WHITE)
        pyxel.text(x_pos, self.sprite_display_y + 22, f"Number: #{sprite_number}", pyxel.COLOR_WHITE)
        pyxel.text(x_pos, self.sprite_display_y + 32, f"N]Name: {sprite_name}", pyxel.COLOR_YELLOW)
        
        # DIC information
        act_name = sprite_tags[0] if len(sprite_tags) > 0 and sprite_tags[0] != 'UNDEF' else "NO_ACT"
        frame_num = sprite_tags[1] if len(sprite_tags) > 1 else "NO_FRAME"
        anim_speed = sprite_tags[2] if len(sprite_tags) > 2 else "NO_SPEED"
        
        pyxel.text(x_pos, self.sprite_display_y + 42, f"1]ACT_NAME: {act_name}", pyxel.COLOR_GREEN)
        pyxel.text(x_pos, self.sprite_display_y + 52, f"2]FRAME_NUM: {frame_num}", pyxel.COLOR_GREEN)
        pyxel.text(x_pos, self.sprite_display_y + 62, f"3]ANIM_SPEED: {anim_speed}", pyxel.COLOR_GREEN)
        
        # EXT information
        ext1 = sprite_tags[3] if len(sprite_tags) > 3 else "NO_EXT"
        ext2 = sprite_tags[4] if len(sprite_tags) > 4 else "NO_EXT"
        ext3 = sprite_tags[5] if len(sprite_tags) > 5 else "NO_EXT"
        ext4 = sprite_tags[6] if len(sprite_tags) > 6 else "NO_EXT"
        ext5 = sprite_tags[7] if len(sprite_tags) > 7 else "NO_EXT"
        
        pyxel.text(x_pos, self.sprite_display_y + 72, f"4]EXT1: {ext1}", pyxel.COLOR_GRAY)
        pyxel.text(x_pos, self.sprite_display_y + 82, f"5]EXT2: {ext2}", pyxel.COLOR_GRAY)
        pyxel.text(x_pos, self.sprite_display_y + 92, f"6]EXT3: {ext3}", pyxel.COLOR_GRAY)
        pyxel.text(x_pos, self.sprite_display_y + 102, f"7]EXT4: {ext4}", pyxel.COLOR_GRAY)
        pyxel.text(x_pos, self.sprite_display_y + 112, f"8]EXT5: {ext5}", pyxel.COLOR_GRAY)
        
        # Mode indicator
        mode_text = "EDIT" if self.edit_mode else "VIEW"
        mode_color = pyxel.COLOR_RED if self.edit_mode else pyxel.COLOR_GREEN
        pyxel.text(x_pos, self.sprite_display_y + 124, f"Mode: {mode_text}", mode_color)
        
        # Content based on mode
        if self.edit_mode:
            self._draw_edit_content(x_pos, sprite_tags)
        else:
            self._draw_view_content(x_pos)
    
    def _draw_edit_content(self, x_pos, sprite_tags):
        """Draw edit mode content"""
        start_y = self.sprite_display_y + 138  # Moved down to accommodate DIC+EXT display
        
        pyxel.text(x_pos, start_y, "Current Tags:", pyxel.COLOR_WHITE)
        
        tag_y = 12
        if sprite_tags and sprite_tags != ['UNDEF']:
            for i, tag in enumerate(sprite_tags[:3]):  # Show max 3 tags
                tag_name = f"DIC_{i+1}: {tag}"
                pyxel.text(x_pos, start_y + tag_y, tag_name, pyxel.COLOR_GREEN)
                tag_y += 10
        else:
            pyxel.text(x_pos, start_y + tag_y, "No tags defined", pyxel.COLOR_GRAY)
    
    def _draw_view_content(self, x_pos):
        """Draw view mode content - simple status"""
        start_y = self.sprite_display_y + 138  # Moved down to accommodate DIC+EXT display
        
        pyxel.text(x_pos, start_y, f"Total sprites: {len(self.sprites)}", pyxel.COLOR_CYAN)
        pyxel.text(x_pos, start_y + 12, "Press F1 to edit mode", pyxel.COLOR_GRAY)
    
    def _draw_recent_sprite_names(self, x_pos):
        """Draw recently edited sprite names at far right (always visible)"""
        start_y = self.sprite_display_y
        
        # Header with edit mode indicator
        if self.edit_mode:
            pyxel.text(x_pos, start_y, "RECENT EDITS", pyxel.COLOR_RED)
        else:
            pyxel.text(x_pos, start_y, "Recent Edits", pyxel.COLOR_CYAN)
        
        pyxel.text(x_pos, start_y + 10, f"({len(self.edited_sprite_names)})", pyxel.COLOR_GRAY)
        
        if self.edited_sprite_names:
            # Show last 6 sprite names
            y_offset = 22
            for i, sprite_name in enumerate(self.edited_sprite_names[-6:]):
                # Highlight most recent in yellow, others in white
                color = pyxel.COLOR_YELLOW if i == len(self.edited_sprite_names[-6:]) - 1 else pyxel.COLOR_WHITE
                
                # Truncate long names to fit
                display_name = sprite_name[:8] + "..." if len(sprite_name) > 8 else sprite_name
                pyxel.text(x_pos, start_y + y_offset, display_name, color)
                y_offset += 10
        else:
            pyxel.text(x_pos, start_y + 22, "None yet", pyxel.COLOR_GRAY)
    
    def _get_sprite_number(self, x, y):
        """Calculate sprite number based on position"""
        grid_x = x // self.SPRITE_SIZE
        grid_y = y // self.SPRITE_SIZE
        return grid_y * (self.SPRITE_AREA_WIDTH // self.SPRITE_SIZE) + grid_x


if __name__ == "__main__":
    SpriteDefiner()