import pygame
import os # Adicionado para os.path.join

# Cores (se forem usadas apenas pelo DialogueSystem, podem ficar aqui ou em um config.py)
WHITE = (255, 255, 255)
DARK_GRAY = (64, 64, 64)
BLACK = (0, 0, 0)

class DialogueSystem:
    def __init__(self, screen, font, screen_width, screen_height):
        self.screen = screen
        self.font = font
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Define a altura desejada para a caixa de diálogo.
        # Este valor será usado para escalar a imagem e para o fallback.
        self.dialogue_box_height = 100  # Altura reduzida (era 150)
        self.current_text = ""
        self.current_character = None

        # Carregar a imagem da caixa de diálogo pixelizada
        try:
            # Substitua 'dialogue_box_pixel.png' pelo nome real do seu arquivo
            dialogue_box_path = os.path.join("src", "assets", "dialogue_box.png") 
            self.dialogue_box_image_original = pygame.image.load(dialogue_box_path).convert_alpha()
            
            scaled_width = self.screen_width
            # Usar a altura definida em self.dialogue_box_height para o escalonamento vertical
            scaled_height = self.dialogue_box_height 
            
            # Remover cálculo de aspect_ratio e a linha original de scaled_height:
            # aspect_ratio = self.dialogue_box_image_original.get_width() / self.dialogue_box_image_original.get_height()
            # scaled_height = int(scaled_width / aspect_ratio) 

            self.dialogue_box_image = pygame.transform.scale(self.dialogue_box_image_original, (scaled_width, scaled_height))
            # self.dialogue_box_height já está com o valor desejado (100).
            # A linha abaixo apenas confirmaria isso, mas pode ser mantida para clareza se preferir.
            # self.dialogue_box_height = self.dialogue_box_image.get_height() 
            self.dialogue_box_rect = self.dialogue_box_image.get_rect(bottomleft=(0, self.screen_height))

        except pygame.error as e:
            print(f"Erro ao carregar a imagem da caixa de diálogo: {e}")
            self.dialogue_box_image = None # Fallback para desenho retangular
            # self.dialogue_box_height já está definido com o valor desejado (ex: 100)
            self.dialogue_box_rect = pygame.Rect(0, self.screen_height - self.dialogue_box_height, self.screen_width, self.dialogue_box_height)
        except FileNotFoundError:
            print(f"Arquivo da caixa de diálogo não encontrado em {dialogue_box_path}")
            self.dialogue_box_image = None
            # self.dialogue_box_height já está definido com o valor desejado (ex: 100)
            self.dialogue_box_rect = pygame.Rect(0, self.screen_height - self.dialogue_box_height, self.screen_width, self.dialogue_box_height)

    def draw(self):
        if self.dialogue_box_image:
            self.screen.blit(self.dialogue_box_image, self.dialogue_box_rect.topleft)
        else: # Fallback para o desenho antigo se a imagem não carregar
            pygame.draw.rect(self.screen, DARK_GRAY, self.dialogue_box_rect)
            pygame.draw.rect(self.screen, WHITE, self.dialogue_box_rect, 3)

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
            # Ajustar o posicionamento do texto para dentro da nova caixa de diálogo
            # Esses valores (padding_x, padding_y_top) podem precisar de ajuste fino
            # dependendo do design da sua dialogue_box_pixel.png
            text_padding_x = 80  # Espaçamento das bordas laterais da caixa
            text_padding_y_top = 25 # Espaçamento do topo da caixa de diálogo para a primeira linha

            text_start_x = self.dialogue_box_rect.left + text_padding_x
            text_start_y = self.dialogue_box_rect.top + text_padding_y_top
            
            available_text_width = self.dialogue_box_rect.width - (text_padding_x * 2)

            words = self.current_text.split(' ') # Dividir por espaço para melhor controle
            lines = []
            current_line = ""
            
            for word in words:
                # Adiciona espaço antes da palavra, exceto se a linha estiver vazia
                word_to_add = (" " if current_line else "") + word 
                test_line = current_line + word_to_add
                
                if self.font.size(test_line)[0] <= available_text_width:
                    current_line += word_to_add
                else:
                    if current_line: # Se current_line não estiver vazia, adiciona à lista
                        lines.append(current_line)
                    current_line = word # Começa nova linha com a palavra atual
            
            if current_line: # Adiciona a última linha formada
                lines.append(current_line)
            
            line_height = self.font.get_linesize() # Usa o espaçamento padrão da fonte
            max_lines_to_display = 3 # Ou calcule com base na altura da caixa e line_height

            for i, line in enumerate(lines[:max_lines_to_display]):
                text_surface = self.font.render(line, True, BLACK) # True para antialiasing (pode desligar para pixel puro)
                self.screen.blit(text_surface, (text_start_x, text_start_y + i * line_height))
    
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
