import pygame

# Cores (se forem usadas apenas pelo DialogueSystem, podem ficar aqui ou em um config.py)
WHITE = (255, 255, 255)
DARK_GRAY = (64, 64, 64)

class DialogueSystem:
    def __init__(self, screen, font, screen_width, screen_height):
        self.screen = screen
        self.font = font
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dialogue_box_height = 150
        self.current_text = ""
        self.current_character = None
        
    def draw(self): # Renomeado de draw_dialogue_box para draw
        box_rect = pygame.Rect(0, self.screen_height - self.dialogue_box_height, self.screen_width, self.dialogue_box_height)
        pygame.draw.rect(self.screen, DARK_GRAY, box_rect)
        pygame.draw.rect(self.screen, WHITE, box_rect, 3)

        if self.current_character: 
            animated_frame = self.current_character.get_current_animated_frame()
            if animated_frame:
                # Use animated_frame directly for calculations and scaling
                sprite_original_width = animated_frame.get_width()
                sprite_original_height = animated_frame.get_height()

                if sprite_original_height > 0: # Avoid division by zero
                    # --- Scaling Logic ---
                    # Define padding around the sprite
                    padding_above_dialogue_box = 20  # Space between sprite and dialogue box
                    padding_top_screen = 30          # Min space from top of screen
                    
                    # Calculate available height for the sprite
                    available_height = self.screen_height - self.dialogue_box_height - padding_above_dialogue_box - padding_top_screen
                    
                    # Target sprite height (e.g., 80% of available space, or 2.5x original, whichever is smaller but positive)
                    target_height = min(max(sprite_original_height * 2.5, available_height * 0.8), available_height)
                    if target_height <= 0 and available_height > 0 : # Ensure target_height is positive if space available
                        target_height = available_height * 0.5 # Fallback to 50% if calculation leads to non-positive

                    if target_height > 0 :
                        scale_ratio = target_height / sprite_original_height
                        scaled_width = int(sprite_original_width * scale_ratio)
                        scaled_height = int(target_height)
                        scaled_sprite = pygame.transform.scale(animated_frame, (scaled_width, scaled_height))
                    else: # Fallback if target_height is still not positive (e.g. very small screen)
                        scaled_sprite = animated_frame # Draw original size
                        scaled_width = sprite_original_width
                        scaled_height = sprite_original_height
                else:
                    scaled_sprite = animated_frame # Fallback for zero height original
                    scaled_width = sprite_original_width
                    scaled_height = sprite_original_height


                # --- Positioning Logic ---
                # Center horizontally
                sprite_x = (self.screen_width - scaled_width) // 2
                # Position above the dialogue box
                sprite_y = self.screen_height - self.dialogue_box_height - scaled_height - padding_above_dialogue_box
                
                # Ensure it doesn't go off the top of the screen
                sprite_y = max(padding_top_screen, sprite_y)

                self.screen.blit(scaled_sprite, (sprite_x, sprite_y))
        
        if self.current_text:
            text_y = self.screen_height - self.dialogue_box_height + 50
            words = self.current_text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.font.size(test_line)[0] < self.screen_width - 40:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for i, line in enumerate(lines[:3]):
                text_surface = self.font.render(line, True, WHITE)
                self.screen.blit(text_surface, (20, text_y + i * 25))
    
    def set_dialogue(self, character, text):
        self.current_character = character
        self.current_text = text
        # self.dialogue_character_sprite = None # Reset sprite
        if character:
            character.is_in_dialogue = True # Set dialogue flag
            # self.dialogue_character_sprite = character.get_dialogue_sprite() # Get the sprite
        # else:
            # self.dialogue_character_sprite = None

    def clear_dialogue(self):
        if self.current_character:
            self.current_character.is_in_dialogue = False # Reset dialogue flag
        self.current_character = None
        self.current_text = ""
        # self.dialogue_character_sprite = None
