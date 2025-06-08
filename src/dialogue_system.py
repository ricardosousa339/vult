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
        
    def draw_dialogue_box(self):
        box_rect = pygame.Rect(0, self.screen_height - self.dialogue_box_height, self.screen_width, self.dialogue_box_height)
        pygame.draw.rect(self.screen, DARK_GRAY, box_rect)
        pygame.draw.rect(self.screen, WHITE, box_rect, 3)
        
        if self.current_character:
            name_surface = self.font.render(self.current_character.name, True, WHITE)
            self.screen.blit(name_surface, (20, self.screen_height - self.dialogue_box_height + 10))
        
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
