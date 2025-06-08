import pygame
import sys
import os

# Configurações
WIDTH = 1024
HEIGHT = 768
FPS = 60

MAP_WIDTH = WIDTH * 2  # O mapa é duas vezes mais largo que a tela
MAP_HEIGHT = HEIGHT * 2 # O mapa é duas vezes mais alto que a tela

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BLUE = (100, 150, 255)

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height

    def apply_to_rect(self, rect): # rect is a pygame.Rect on the map
        return rect.move(self.camera_rect.left, self.camera_rect.top)

    def apply_to_surface(self, surface_rect): # surface_rect is a pygame.Rect for a surface to be blitted
        return surface_rect.move(self.camera_rect.left, self.camera_rect.top)

    def update(self, target): # target is a Character object
        # Centraliza a câmera no alvo (target.map_x, target.map_y são o canto superior esquerdo do sprite do alvo)
        # Para centralizar o *centro* do alvo, ajustamos por metade do tamanho do alvo e metade do tamanho da câmera.
        x = -target.map_x + self.width // 2 - target.map_sprite_size // 2
        y = -target.map_y + self.height // 2 - target.map_sprite_size // 2

        # Limita o scroll aos limites do mapa
        x = min(0, x)  # Não deixa a câmera ir para a esquerda do início do mapa (0)
        y = min(0, y)  # Não deixa a câmera ir para cima do início do mapa (0)
        x = max(-(self.map_width - self.width), x)  # Não deixa a câmera ir para a direita do fim do mapa
        y = max(-(self.map_height - self.height), y) # Não deixa a câmera ir para baixo do fim do mapa
        
        self.camera_rect.topleft = (x, y)

class Character:
    def __init__(self, name, color=BLUE, map_x=0, map_y=0, sprite_path=None): # Added sprite_path
        self.name = name
        self.color = color
        # self.sprite = None # Sprite individual não é mais o primário, usamos self.frames
        self.dialogue_sprite_original_width = 150 # Default if no sprite
        self.dialogue_sprite_original_height = 200 # Default if no sprite

        self.frames = []
        self.is_animated = False
        self.current_frame_index = 0
        self.animation_speed = 15 # Ticks do jogo por frame da animação (60 FPS / 15 = 4 FPS de animação)
        self.animation_timer = 0
        self.is_moving = False # Novo atributo para controlar o estado de movimento

        if sprite_path:
            try:
                full_sprite_image = pygame.image.load(sprite_path).convert_alpha()
                
                spritesheet_width = full_sprite_image.get_width()
                spritesheet_height = full_sprite_image.get_height()
                
                # Assumindo dois frames lado a lado para animação
                frame_width = spritesheet_width // 2
                frame_height = spritesheet_height

                # Verifica se a imagem é larga o suficiente para conter dois frames
                if frame_width > 0 and spritesheet_width >= frame_width * 2: 
                    self.frames.append(full_sprite_image.subsurface(pygame.Rect(0, 0, frame_width, frame_height)))
                    self.frames.append(full_sprite_image.subsurface(pygame.Rect(frame_width, 0, frame_width, frame_height)))
                    self.is_animated = True
                    self.dialogue_sprite_original_width = frame_width # Largura de um único frame
                    self.dialogue_sprite_original_height = frame_height # Altura de um único frame
                else: # Trata como um sprite de frame único
                    self.frames.append(full_sprite_image)
                    # self.is_animated continua False
                    self.dialogue_sprite_original_width = spritesheet_width
                    self.dialogue_sprite_original_height = spritesheet_height
            except pygame.error as e:
                print(f"Cannot load sprite for {self.name} at {sprite_path}: {e}")
                # self.frames continua vazio, dimensões padrão serão usadas

        self.story = None # For NPC-specific dialogues
        self.map_x = map_x # Position on the map
        self.map_y = map_y # Position on the map
        self.map_sprite_size = 48 # Size of the character on the map (pixels)
        self.player_speed = 4 # Movement speed for map

    def update_animation(self):
        if not self.is_animated or not self.frames or len(self.frames) <= 1:
            return # Não animar se não for animado ou tiver só um frame

        if not self.is_moving: # Se não estiver se movendo
            self.current_frame_index = 0 # Volta para o primeiro frame (frame de "parado")
            self.animation_timer = 0
            return

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)

    def move(self, dx, dy, map_boundary_width, map_boundary_height):
        # Basic boundary checking for map movement
        new_x = self.map_x + dx
        new_y = self.map_y + dy

        if 0 <= new_x <= map_boundary_width - self.map_sprite_size:
            self.map_x = new_x
        if 0 <= new_y <= map_boundary_height - self.map_sprite_size:
            self.map_y = new_y

    def draw_on_map(self, screen, map_pos_on_screen):
        """Draws a scaled-down version of the character for the map view at a specific screen position."""
        if self.frames: # Verifica se existem frames carregados
            current_frame_surface = self.frames[self.current_frame_index]
            scaled_sprite = pygame.transform.scale(current_frame_surface, (self.map_sprite_size, self.map_sprite_size))
            screen.blit(scaled_sprite, map_pos_on_screen)
        else:
            # Fallback para um retângulo colorido se não houver frames
            pygame.draw.rect(screen, self.color, (map_pos_on_screen[0], map_pos_on_screen[1], self.map_sprite_size, self.map_sprite_size))

class DialogueSystem:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.dialogue_box_height = 150
        self.current_text = ""
        self.current_character = None
        
    def draw_dialogue_box(self):
        """Desenha a caixa de diálogo"""
        box_rect = pygame.Rect(0, HEIGHT - self.dialogue_box_height, WIDTH, self.dialogue_box_height)
        pygame.draw.rect(self.screen, DARK_GRAY, box_rect)
        pygame.draw.rect(self.screen, WHITE, box_rect, 3)
        
        # Nome do personagem
        if self.current_character:
            name_surface = self.font.render(self.current_character.name, True, WHITE)
            self.screen.blit(name_surface, (20, HEIGHT - self.dialogue_box_height + 10))
        
        # Texto do diálogo
        if self.current_text:
            text_y = HEIGHT - self.dialogue_box_height + 50
            words = self.current_text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.font.size(test_line)[0] < WIDTH - 40:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for i, line in enumerate(lines[:3]):  # Máximo 3 linhas
                text_surface = self.font.render(line, True, WHITE)
                self.screen.blit(text_surface, (20, text_y + i * 25))
    
    def set_dialogue(self, character, text):
        self.current_character = character
        self.current_text = text

class Story:
    def __init__(self):
        # Aqui você pode definir sua história
        self.scenes = [
            {
                "background": "floresta_medieval", # Atualizado
                "character": "protagonist",
                "text": "Saudações! Eu sou um nobre cavaleiro. Bem-vindo ao meu reino!"
            },
            {
                "background": "floresta_medieval", # Atualizado
                "character": "protagonist",
                "text": "Esta é uma simples balada. Pressione ESPAÇO para desbravar a narrativa."
            },
            {
                "background": "floresta_medieval", # Atualizado
                "character": "protagonist", 
                "text": "Vós podeis substituir estes estandartes por vossas próprias tapeçarias mais tarde!"
            },
            {
                "background": "floresta_medieval", # Atualizado
                "character": "protagonist",
                "text": "Aqui podeis adicionar contendas, escolhas e grandes feitos. O que desejais?"
            },
            # Exemplo de "puzzle" simples - pode expandir depois
            {
                "background": "floresta_medieval", # Atualizado
                "character": "protagonist",
                "text": "Fim da jornada por ora! Pressione ESC para retirar-se ou ESPAÇO para reiniciar a aventura."
            }
        ]
        self.current_scene = 0
    
    def get_current_scene(self):
        if self.current_scene < len(self.scenes):
            return self.scenes[self.current_scene]
        return None
    
    def next_scene(self):
        self.current_scene += 1
        if self.current_scene >= len(self.scenes):
            self.current_scene = 0  # Recomeça
    
    def reset(self):
        self.current_scene = 0

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Visual Novel - Demo Medieval") # Atualizado
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "map" # Can be "map" or "dialogue"
        
        # Font
        self.font = pygame.font.Font(None, 24) # Considerar uma fonte mais temática depois
        
        # Sistema de diálogo
        self.dialogue_system = DialogueSystem(self.screen, self.font)
        
        # Personagens
        # Make sure the sprite paths are correct relative to your execution directory
        # or provide absolute paths.
        player_sprite_path = os.path.join("src", "assets", "sprite_knight_frente.png")
        blacksmith_sprite_path = os.path.join("src", "assets", "sprite_knight_frente.png") # Placeholder, replace with actual NPC sprite
        merchant_sprite_path = os.path.join("src", "assets", "sprite_knight_frente.png")   # Placeholder, replace with actual NPC sprite

        self.player = Character("Cavaleiro", BLUE, map_x=WIDTH//2, map_y=HEIGHT//2, sprite_path=player_sprite_path)
        self.npcs = {
            "blacksmith": Character("Ferreiro", (100,100,100), map_x=100, map_y=100, sprite_path=blacksmith_sprite_path),
            "merchant": Character("Mercador", (0,100,0), map_x=WIDTH - 150, map_y=HEIGHT -150, sprite_path=merchant_sprite_path)
        }
        self.characters = {"protagonist": self.player} # For dialogue system compatibility
        self.characters.update(self.npcs)

        # NPC Stories (simple examples)
        blacksmith_story = Story()
        blacksmith_story.scenes = [
            {"background": "floresta_medieval", "character": "blacksmith", "text": "Olá, nobre cavaleiro! Precisa de uma espada afiada?"},
            {"background": "floresta_medieval", "character": "blacksmith", "text": "Minhas forjas estão sempre quentes!"}
        ]
        self.npcs["blacksmith"].story = blacksmith_story

        merchant_story = Story()
        merchant_story.scenes = [
            {"background": "floresta_medieval", "character": "merchant", "text": "Mercadorias raras, direto de terras distantes!"},
            {"background": "floresta_medieval", "character": "merchant", "text": "Tenho poções e artefatos, se tiveres ouro."}
        ]
        self.npcs["merchant"].story = merchant_story
        
        # História principal (pode ser usada para quests ou introdução)
        self.main_story = Story()
        self.main_story.scenes = [
             {
                "background": "floresta_medieval", 
                "character": "protagonist",
                "text": "Vagueio por estas terras em busca de aventuras... e talvez um bom hidromel."
            }
        ]
        self.current_dialogue_story = None # Will point to the story being used in dialogue mode
        
        # Background atual (placeholder)
        self.current_background = "floresta_medieval" # Atualizado

        # Câmera
        self.camera = Camera(WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT)

    def draw_background(self, background_name):
        """Desenha o background - placeholder que pode ser substituído por imagens"""
        # Cria uma superfície para o mapa inteiro
        map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))

        if background_name == "floresta_medieval": # Nome atualizado
            # Céu (pode ser mais escuro ou nublado para um tom medieval)
            pygame.draw.rect(map_surface, (100, 100, 120), (0, 0, MAP_WIDTH, MAP_HEIGHT//2)) # Céu acinzentado
            # Chão (terra ou grama mais escura)
            pygame.draw.rect(map_surface, (50, 80, 50), (0, MAP_HEIGHT//2, MAP_WIDTH, MAP_HEIGHT//2)) # Verde escuro/terra
            
            # Árvores (mais robustas e escuras) - desenhadas em toda a extensão do mapa
            tree_trunk_color = (80, 50, 30) # Marrom escuro para troncos
            tree_foliage_color = (30, 70, 30) # Verde bem escuro para folhagem
            
            for i in range(10): # Aumentar o número de árvores para preencher o mapa maior
                x = i * (MAP_WIDTH // 10) + (MAP_WIDTH // 20) # Espaçamento ajustado para MAP_WIDTH
                trunk_width = 30
                trunk_height = HEIGHT//3 + 20 # Altura relativa à tela ainda pode fazer sentido
                foliage_radius = 50
                
                # Tronco
                pygame.draw.rect(map_surface, tree_trunk_color, (x - trunk_width//2, MAP_HEIGHT//2 - trunk_height + 50, trunk_width, trunk_height))
                # Folhagem (copa mais densa)
                pygame.draw.circle(map_surface, tree_foliage_color, (x, MAP_HEIGHT//2 - trunk_height + 50 - foliage_radius//2), foliage_radius)
                pygame.draw.circle(map_surface, tree_foliage_color, (x - foliage_radius//3, MAP_HEIGHT//2 - trunk_height + 20 - foliage_radius//2), foliage_radius -10)
                pygame.draw.circle(map_surface, tree_foliage_color, (x + foliage_radius//3, MAP_HEIGHT//2 - trunk_height + 20- foliage_radius//2), foliage_radius-10)

            # Opcional: Silhueta de um castelo distante no mapa
            castle_color = (70, 70, 70) # Cinza escuro para silhueta
            pygame.draw.rect(map_surface, castle_color, (MAP_WIDTH - 400, MAP_HEIGHT//2 - 100, 60, 100)) # Torre 1
            pygame.draw.rect(map_surface, castle_color, (MAP_WIDTH - 300, MAP_HEIGHT//2 - 120, 60, 120)) # Torre 2 (maior)
            pygame.draw.rect(map_surface, castle_color, (MAP_WIDTH - 200, MAP_HEIGHT//2 - 100, 60, 100)) # Torre 3
            pygame.draw.rect(map_surface, castle_color, (MAP_WIDTH - 400, MAP_HEIGHT//2 - 50, 200, 20)) # Muralha
        
        # Blit a porção visível do mapa na tela principal, deslocada pela câmera
        self.screen.blit(map_surface, (self.camera.camera_rect.x, self.camera.camera_rect.y))

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "dialogue":
                    if event.key == pygame.K_SPACE:
                        if self.current_dialogue_story:
                            self.current_dialogue_story.next_scene()
                            scene = self.current_dialogue_story.get_current_scene()
                            if not scene: # End of NPC dialogue
                                self.game_state = "map"
                                self.current_dialogue_story.reset() # Reset for next time
                                self.current_dialogue_story = None
                            else:
                                # Update dialogue system with the new scene from the current story
                                character_in_dialogue = self.characters.get(scene["character"])
                                if character_in_dialogue:
                                    self.dialogue_system.set_dialogue(character_in_dialogue, scene["text"])
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "map"
                        if self.current_dialogue_story:
                            self.current_dialogue_story.reset()
                            self.current_dialogue_story = None
                elif self.game_state == "map":
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    # Player movement will be handled in update based on pressed keys

    def update(self):
        if self.game_state == "map":
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            # Define is_moving baseado nas teclas pressionadas
            if keys[pygame.K_LEFT] or keys[pygame.K_a] or \
               keys[pygame.K_RIGHT] or keys[pygame.K_d] or \
               keys[pygame.K_UP] or keys[pygame.K_w] or \
               keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.is_moving = True
            else:
                self.player.is_moving = False

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -self.player.player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = self.player.player_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -self.player.player_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = self.player.player_speed
            
            if dx != 0 or dy != 0:
                self.player.move(dx, dy, MAP_WIDTH, MAP_HEIGHT)
            # else: # Se não houve movimento, garante que is_moving seja False
            #    self.player.is_moving = False # Esta linha é redundante devido à lógica acima

            self.player.update_animation() # Atualiza animação do jogador
            
            # NPCs podem continuar animando independentemente por enquanto
            # Se quiser que NPCs também só animem ao se mover, precisará de lógica similar para eles
            for npc in self.npcs.values():
                # Para este exemplo, vamos fazer os NPCs animarem continuamente se tiverem animação
                if npc.is_animated and len(npc.frames) > 1:
                    npc.is_moving = True # Faz os NPCs com animação sempre animarem
                else:
                    npc.is_moving = False
                npc.update_animation() 

            self.camera.update(self.player) # Atualiza a câmera para seguir o jogador

            # Check for NPC interaction
            player_rect = pygame.Rect(self.player.map_x, self.player.map_y, self.player.map_sprite_size, self.player.map_sprite_size)
            for npc_name, npc in self.npcs.items():
                npc_rect = pygame.Rect(npc.map_x, npc.map_y, npc.map_sprite_size, npc.map_sprite_size)
                if player_rect.colliderect(npc_rect):
                    if npc.story: # Check if NPC has a story to tell
                        self.game_state = "dialogue"
                        self.current_dialogue_story = npc.story
                        scene = self.current_dialogue_story.get_current_scene()
                        if scene:
                            character_in_dialogue = self.characters.get(scene["character"])
                            if character_in_dialogue:
                                self.dialogue_system.set_dialogue(character_in_dialogue, scene["text"])
                        break # Interact with one NPC at a time

        elif self.game_state == "dialogue":
            # Dialogue progression is handled in events for SPACE key
            pass # Potentially update animated character portraits or text effects here

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_background(self.current_background)

        if self.game_state == "map":
            # Player e NPCs são desenhados em suas posições no mapa, a câmera cuida do offset
            player_map_pos_rect = pygame.Rect(self.player.map_x, self.player.map_y, self.player.map_sprite_size, self.player.map_sprite_size)
            self.player.draw_on_map(self.screen, self.camera.apply_to_rect(player_map_pos_rect).topleft)
            
            for npc_name, npc in self.npcs.items():
                npc_map_pos_rect = pygame.Rect(npc.map_x, npc.map_y, npc.map_sprite_size, npc.map_sprite_size)
                npc.draw_on_map(self.screen, self.camera.apply_to_rect(npc_map_pos_rect).topleft)
            
            # Simple instruction for map mode
            instruction_text = "WASD/Setas: Mover | ESC: Sair | Aproxime-se de NPCs para interagir"
            instruction_surface = self.font.render(instruction_text, True, WHITE)
            self.screen.blit(instruction_surface, (10, 10))

        elif self.game_state == "dialogue":
            # Draw the full-size character for dialogue
            scene = self.current_dialogue_story.get_current_scene()
            if scene and scene["character"] in self.characters:
                character_in_dialogue = self.characters[scene["character"]]
                if character_in_dialogue.frames: # Verifica se há frames
                    current_frame_surface = character_in_dialogue.frames[character_in_dialogue.current_frame_index]
                    # Usa dialogue_sprite_original_width/height que agora refletem o tamanho de um frame
                    sprite_x = WIDTH // 2 - character_in_dialogue.dialogue_sprite_original_width // 2
                    sprite_y = HEIGHT // 2 - character_in_dialogue.dialogue_sprite_original_height // 2 - 50
                    self.screen.blit(current_frame_surface, (sprite_x, sprite_y))
                else:
                    # Fallback para um retângulo colorido se não houver frames
                    pygame.draw.rect(self.screen, character_in_dialogue.color, 
                                     (WIDTH//2 - character_in_dialogue.dialogue_sprite_original_width//2, 
                                      HEIGHT//2 - character_in_dialogue.dialogue_sprite_original_height//2 - 50, 
                                      character_in_dialogue.dialogue_sprite_original_width, 
                                      character_in_dialogue.dialogue_sprite_original_height))
            
            self.dialogue_system.draw_dialogue_box()
            
            # Instruções para diálogo
            instruction_text = "ESPAÇO: Próximo | ESC: Voltar ao Mapa"
            instruction_surface = self.font.render(instruction_text, True, WHITE)
            self.screen.blit(instruction_surface, (10, 10))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

game = Game()
game.run()
pygame.quit()
sys.exit()