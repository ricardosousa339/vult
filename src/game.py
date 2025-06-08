import pygame
import sys
import os

from camera import Camera
from character import Character
from dialogue_system import DialogueSystem
from story import Story
# Import global MAP_WIDTH, MAP_HEIGHT as fallbacks or for initial setup if needed
from config import WIDTH, HEIGHT, FPS, MAP_WIDTH as DEFAULT_MAP_WIDTH, MAP_HEIGHT as DEFAULT_MAP_HEIGHT, BLACK, BLUE, WHITE, DARK_GRAY


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Vult Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "map"
        
        self.font = pygame.font.Font(None, 24)
        self.dialogue_system = DialogueSystem(self.screen, self.font, WIDTH, HEIGHT)
        
        player_sprite_paths = {
            "frente": os.path.join("src", "assets", "sprite_knight_frente.png"),
            "costas": os.path.join("src", "assets", "sprite_knight_costas.png"),
            "esquerda": os.path.join("src", "assets", "sprite_knight_esquerda.png"),
            "direita": os.path.join("src", "assets", "sprite_knight_direita.png"),
        }
        npc_sprite_paths = {
            "frente": os.path.join("src", "assets", "sprite_knight_frente.png")
        }

        # Player starting position will be relative to the first map's dimensions
        # We'll set it properly after loading the first map's info.
        self.player = Character("Cavaleiro", BLUE, map_x=0, map_y=0, sprite_paths=player_sprite_paths)
        
        self.npcs = {
            "blacksmith": Character("Ferreiro", (100,100,100), map_x=100, map_y=100, sprite_paths=npc_sprite_paths),
            "merchant": Character("Mercador", (0,100,0), map_x=DEFAULT_MAP_WIDTH - 250, map_y=DEFAULT_MAP_HEIGHT -250, sprite_paths=npc_sprite_paths) # Initial pos, might need adjustment per map
        }
        self.characters = {"protagonist": self.player}
        self.characters.update(self.npcs)

        blacksmith_story = Story()
        blacksmith_story.scenes = [
            {"character": "blacksmith", "text": "Olá, nobre cavaleiro! Precisa de uma espada afiada?"},
            {"character": "blacksmith", "text": "Minhas forjas estão sempre quentes!"}
        ]
        self.npcs["blacksmith"].story = blacksmith_story

        merchant_story = Story()
        merchant_story.scenes = [
            {"character": "merchant", "text": "Mercadorias raras, direto de terras distantes!"},
            {"character": "merchant", "text": "Tenho poções e artefatos, se tiveres ouro."}
        ]
        self.npcs["merchant"].story = merchant_story
        
        self.current_dialogue_story = None
        self.tile_size = 100 # Define tile_size before map_definitions if used in target_player_pos calculations

        self.map_definitions = {
            "mundo_principal": {
                "layout_file": os.path.join("src", "assets", "map_layout.map"),
                "background_image": os.path.join("src", "assets", "map_image.png"),
                "pixel_width": 2000, 
                "pixel_height": 2000,
                "portals": {
                    (9, 11): {"target_map_key": "caverna_secreta", "target_player_pos": (150, 600)}, 
                    (10, 11): {"target_map_key": "caverna_secreta", "target_player_pos": (150, 600)},
                    (9, 12): {"target_map_key": "caverna_secreta", "target_player_pos": (150, 600)},
                    (10, 12): {"target_map_key": "caverna_secreta", "target_player_pos": (150, 600)},
                }
            },
            "caverna_secreta": {
                "layout_file": os.path.join("src", "assets", "map_caverna.map"),
                "background_image": os.path.join("src", "assets", "caverna_bg_animated.png"), # Updated
                "background_animation_frames": 4, # Added
                "pixel_width": 1000,  # Largura do padrão original da caverna
                "pixel_height": 342, # Altura da caverna
                "repeat_x": 3, # Repetir o padrão da caverna 3 vezes horizontalmente
                "portals": {
                    # Portal na primeira instância do padrão
                    (5, 3): {"target_map_key": "mundo_principal", "target_player_pos": (9 * self.tile_size + self.tile_size // 2, 13 * self.tile_size)},
                    # Se houver um portal de saída em cada repetição, eles podem ser definidos dinamicamente ou
                    # a lógica de detecção de portal precisará considerar repeat_x.
                    # Por simplicidade, vamos assumir que a lógica de detecção de portal lidará com isso.
                }
            }
        }
        self.current_map_key = "mundo_principal"
        self.current_map_info = self.map_definitions[self.current_map_key]
        
        # Calcular a largura efetiva do mapa atual (considerando a repetição)
        self.current_map_effective_pixel_width = self.current_map_info.get("pixel_width", DEFAULT_MAP_WIDTH) * self.current_map_info.get("repeat_x", 1)
        self.current_map_pixel_height = self.current_map_info.get("pixel_height", DEFAULT_MAP_HEIGHT)


        # Set initial player position based on the first map
        # initial_map_pixel_width = self.current_map_info["pixel_width"] # Use effective width for camera
        self.player.map_x = self.current_map_effective_pixel_width // 2
        self.player.map_y = self.current_map_pixel_height - self.player.map_sprite_height
        
        # Initialize camera with the dimensions of the first loaded map
        self.camera = Camera(WIDTH, HEIGHT, self.current_map_effective_pixel_width, self.current_map_pixel_height)
        self.dialogue_exit_active = False

        # Background animation attributes
        self.background_animation_frames_surfaces = []
        self.current_background_animation_frame_index = 0
        self.background_animation_timer = 0
        self.background_animation_speed = 15 # Adjust for desired animation speed (e.g., 15 ticks per frame)

        # Portal activation and background override attributes
        self.portal_is_activating = False
        self.portal_activation_delay = FPS * 1  # 1-second delay (FPS is from config)
        self.portal_activation_timer = 0
        self.portal_target_info = None 
        self.raw_portal_open_image = None # Will hold the unscaled porta_aberta.png
        self.scaled_portal_open_background_override = None # porta_aberta.png scaled to current map pattern size

        self.tiles = {
            "g0": pygame.image.load(os.path.join("src", "assets", "grama_tile_0.png")).convert_alpha(),
            "g90": pygame.image.load(os.path.join("src", "assets", "grama_tile_90.png")).convert_alpha(),
            "g180": pygame.image.load(os.path.join("src", "assets", "grama_tile_180.png")).convert_alpha(),
            "g270": pygame.image.load(os.path.join("src", "assets", "grama_tile_270.png")).convert_alpha(),
            "s": pygame.image.load(os.path.join("src", "assets", "areia.png")).convert_alpha(),
            "p": pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        }
        self.tiles["p"].fill((0,0,0,0))

        # Load the raw portal open image (unscaled)
        try:
            portal_open_image_path = os.path.join("src", "assets", "porta_aberta.png")
            self.raw_portal_open_image = pygame.image.load(portal_open_image_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading raw portal open image {portal_open_image_path}: {e}.")
            self.raw_portal_open_image = None 
        except FileNotFoundError:
            print(f"Raw portal open image file not found at {portal_open_image_path}.")
            self.raw_portal_open_image = None

        for key in self.tiles:
            self.tiles[key] = pygame.transform.scale(self.tiles[key], (self.tile_size, self.tile_size))

        self.map_data = []
        self.collision_map_rects = []
        self.blocking_tile_keys = ['x', 'g0', 'g90', 'g180', 'g270'] 
        
        self._load_current_map_assets()

    def _load_current_map_assets(self):
        # Largura do padrão original do mapa
        base_map_pixel_width = self.current_map_info["pixel_width"]
        # Altura do mapa
        current_map_pixel_height = self.current_map_info["pixel_height"]
        # Fator de repetição
        repeat_x = self.current_map_info.get("repeat_x", 1)
        # Largura efetiva total do mapa
        self.current_map_effective_pixel_width = base_map_pixel_width * repeat_x

        # Reset background animation frames
        self.background_animation_frames_surfaces = []
        self.current_background_animation_frame_index = 0
        self.background_animation_timer = 0

        num_anim_frames = self.current_map_info.get("background_animation_frames")

        try:
            if num_anim_frames and num_anim_frames > 0:
                spritesheet = pygame.image.load(self.current_map_info["background_image"]).convert_alpha()
                spritesheet_width = spritesheet.get_width()
                spritesheet_height = spritesheet.get_height()
                frame_width = spritesheet_width // num_anim_frames

                for i in range(num_anim_frames):
                    frame_surface = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, spritesheet_height))
                    scaled_frame = pygame.transform.scale(frame_surface, (base_map_pixel_width, current_map_pixel_height))
                    self.background_animation_frames_surfaces.append(scaled_frame)
                
                if self.background_animation_frames_surfaces:
                    self.current_background_image_pattern = self.background_animation_frames_surfaces[0] # Set initial pattern
                else: # Fallback if slicing failed
                    self.current_background_image_pattern = pygame.Surface((base_map_pixel_width, current_map_pixel_height))
                    self.current_background_image_pattern.fill(BLACK)

            else: # Static background
                self.current_background_image_pattern = pygame.image.load(self.current_map_info["background_image"]).convert()
                self.current_background_image_pattern = pygame.transform.scale(self.current_background_image_pattern, (base_map_pixel_width, current_map_pixel_height))
        
        except pygame.error as e:
            print(f"Error loading background for {self.current_map_key}: {e}")
            self.current_background_image_pattern = pygame.Surface((base_map_pixel_width, current_map_pixel_height))
            self.current_background_image_pattern.fill(BLACK)
            self.background_animation_frames_surfaces = [] # Ensure it's cleared on error

        self.map_data = self.load_map_data(self.current_map_info["layout_file"])
        self._create_collision_rects()

    def switch_map(self, new_map_key, player_start_pos):
        print(f"Switching map to {new_map_key}, player to {player_start_pos}")
        self.current_map_key = new_map_key
        self.current_map_info = self.map_definitions[self.current_map_key]
        
        # Recalcular dimensões efetivas para o novo mapa
        base_map_pixel_width = self.current_map_info["pixel_width"]
        self.current_map_pixel_height = self.current_map_info["pixel_height"]
        repeat_x = self.current_map_info.get("repeat_x", 1)
        self.current_map_effective_pixel_width = base_map_pixel_width * repeat_x

        self._load_current_map_assets() 
        
        self.player.map_x, self.player.map_y = player_start_pos
        
        self.camera.map_width = self.current_map_effective_pixel_width
        self.camera.map_height = self.current_map_pixel_height
        self.camera.update(self.player)

    def _create_collision_rects(self):
        self.collision_map_rects = []
        base_map_pixel_width = self.current_map_info["pixel_width"] # Largura do padrão
        repeat_x = self.current_map_info.get("repeat_x", 1)

        for i in range(repeat_x): # Para cada repetição do padrão
            offset_x = i * base_map_pixel_width
            for row_index, row_data in enumerate(self.map_data):
                for col_index, tile_key in enumerate(row_data):
                    if tile_key in self.blocking_tile_keys:
                        rect = pygame.Rect(
                            col_index * self.tile_size + offset_x, 
                            row_index * self.tile_size, 
                            self.tile_size, 
                            self.tile_size
                        )
                        self.collision_map_rects.append(rect)

    def load_map_data(self, map_file_path):
        map_data = []
        try:
            with open(map_file_path, "r") as map_file:
                for line in map_file.readlines():
                    map_data.append(line.strip().split())
        except FileNotFoundError:
            print(f"Error: Map file not found at {map_file_path}")
            # Create a default empty map or handle error as needed
            # For now, let's assume a map that's 10x10 of '0' if file not found
            num_cols = DEFAULT_MAP_WIDTH // self.tile_size
            num_rows = DEFAULT_MAP_HEIGHT // self.tile_size
            map_data = [['0' for _ in range(num_cols)] for _ in range(num_rows)]
        return map_data

    def draw_background(self): 
        base_map_pixel_width = self.current_map_info["pixel_width"]
        repeat_x = self.current_map_info.get("repeat_x", 1)

        pattern_to_draw = None

        if self.portal_is_activating and self.scaled_portal_open_background_override:
            pattern_to_draw = self.scaled_portal_open_background_override
        elif self.background_animation_frames_surfaces:
            pattern_to_draw = self.background_animation_frames_surfaces[self.current_background_animation_frame_index]
        elif hasattr(self, 'current_background_image_pattern') and self.current_background_image_pattern:
            pattern_to_draw = self.current_background_image_pattern
        
        if pattern_to_draw is None: # Fallback if no pattern is available
            pattern_to_draw = pygame.Surface((base_map_pixel_width, self.current_map_pixel_height))
            pattern_to_draw.fill(BLACK)

        # Desenhar a imagem de fundo repetida
        for i in range(repeat_x):
            try:
                self.screen.blit(
                    pattern_to_draw, 
                    (i * base_map_pixel_width + self.camera.camera_rect.x, self.camera.camera_rect.y)
                )
            except pygame.error as e:
                print(f"Error blitting background part for {self.current_map_key}: {e}")
                # Desenhar um placeholder preto para a parte do fundo que falhou
                placeholder_rect = pygame.Rect(
                    i * base_map_pixel_width + self.camera.camera_rect.x, 
                    self.camera.camera_rect.y,
                    base_map_pixel_width,
                    self.current_map_pixel_height 
                )
                pygame.draw.rect(self.screen, BLACK, placeholder_rect)


        # Overlay tiles based on self.map_data, considerando a repetição
        tiles_in_pattern_width = base_map_pixel_width // self.tile_size
        
        # Determinar o range de colunas de tiles visíveis na tela para otimizar o desenho
        # Isso considera a posição da câmera e a largura da tela
        # Coordenada X do início da câmera no mundo do jogo
        camera_world_x = -self.camera.camera_rect.x
        # Coluna do tile inicial visível (no mapa grande/repetido)
        start_col_on_screen = camera_world_x // self.tile_size
        # Coluna do tile final visível (no mapa grande/repetido)
        end_col_on_screen = (camera_world_x + WIDTH) // self.tile_size + 1 # +1 para garantir que tiles parciais sejam desenhados

        for row_index, row_data in enumerate(self.map_data):
            # Itera apenas sobre as colunas que podem estar visíveis
            for col_on_large_map in range(int(start_col_on_screen), int(end_col_on_screen) +1):
                # Mapeia a coluna do mapa grande de volta para a coluna no padrão original
                col_in_pattern = col_on_large_map % tiles_in_pattern_width
                
                if 0 <= col_in_pattern < len(row_data): # Verifica se col_in_pattern é válido para row_data
                    tile_key = row_data[col_in_pattern]
                    tile_image = self.tiles.get(tile_key)
                    
                    # tile_image_to_draw = tile_image # Default to the static tile image
                    # Removed specific logic for changing 'p' tile appearance during portal activation
                    # The background itself is now changed via scaled_portal_open_background_override
                    
                    if tile_image: # Was tile_image_to_draw
                        # Posição X do tile no mapa grande/repetido
                        x = col_on_large_map * self.tile_size + self.camera.camera_rect.x
                        y = row_index * self.tile_size + self.camera.camera_rect.y
                        
                        tile_rect_on_screen = pygame.Rect(x, y, self.tile_size, self.tile_size)
                        # Verifica se o tile está realmente na tela antes de desenhar (dupla checagem, mas útil)
                        if self.screen.get_rect().colliderect(tile_rect_on_screen):
                             self.screen.blit(tile_image, (x, y)) # Was tile_image_to_draw

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
                            if scene is None: # Checa se get_current_scene retornou None
                                self.game_state = "map"
                                self.current_dialogue_story = None # Limpa a história atual
                                self.dialogue_system.current_character = None # Limpa o personagem no sistema de diálogo
                                self.dialogue_system.current_text = "" # Limpa o texto no sistema de diálogo
                                self.dialogue_exit_active = True # Activate flag
                            else:
                                character_in_dialogue = self.characters.get(scene["character"])
                                if character_in_dialogue:
                                    self.dialogue_system.set_dialogue(character_in_dialogue, scene["text"])
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "map"
                        if self.current_dialogue_story:
                            # self.current_dialogue_story.reset() # Reset is handled when starting new dialogue
                            self.current_dialogue_story = None
                        self.dialogue_system.current_character = None
                        self.dialogue_system.current_text = ""
                        self.dialogue_exit_active = True # Activate flag to prevent immediate re-trigger
                elif self.game_state == "map":
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

    def update(self):
        if self.portal_is_activating:
            self.portal_activation_timer -= 1
            
            if self.portal_activation_timer <= 0:
                if self.portal_target_info:
                    self.switch_map(self.portal_target_info["target_map_key"], self.portal_target_info["target_player_pos"])
                # Reset portal state
                self.portal_is_activating = False
                self.portal_target_info = None
                self.scaled_portal_open_background_override = None # Clear the override
            return # Skip other updates (like player movement) during portal activation

        if self.game_state == "map":
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            any_key_pressed = (keys[pygame.K_LEFT] or keys[pygame.K_a] or
                               keys[pygame.K_RIGHT] or keys[pygame.K_d] or
                               keys[pygame.K_UP] or keys[pygame.K_w] or
                               keys[pygame.K_DOWN] or keys[pygame.K_s])
            self.player.is_moving = any_key_pressed

            if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
                dx = -self.player.player_speed
                self.player.current_direction = "esquerda"
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
                dx = self.player.player_speed
                self.player.current_direction = "direita"
            if keys[pygame.K_UP] or keys[pygame.K_w]: 
                dy = -self.player.player_speed
                self.player.current_direction = "costas"
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: 
                dy = self.player.player_speed
                self.player.current_direction = "frente"
            
            # Background animation update
            if self.background_animation_frames_surfaces and len(self.background_animation_frames_surfaces) > 1:
                self.background_animation_timer += 1
                if self.background_animation_timer >= self.background_animation_speed:
                    self.background_animation_timer = 0
                    self.current_background_animation_frame_index = (self.current_background_animation_frame_index + 1) % len(self.background_animation_frames_surfaces)

            if not any_key_pressed: pass 
            elif dx != 0 and dy != 0: pass 
            elif dx == 0 and dy == 0: pass

            # Use current map's dimensions for player movement boundaries
            # current_map_pixel_width = self.current_map_info["pixel_width"] # Isso foi movido para self.current_map_effective_pixel_width
            # current_map_pixel_height = self.current_map_info["pixel_height"]
            if dx != 0 or dy != 0: self.player.move(dx, dy, self.current_map_effective_pixel_width, self.current_map_pixel_height, self.collision_map_rects)
            self.player.update_animation()

            player_feet_x = self.player.map_x + self.player.collision_box_offset_x + self.player.collision_box_width // 2
            player_feet_y = self.player.map_y + self.player.collision_box_offset_y + self.player.collision_box_height // 2
            
            # Coordenada da coluna do tile no mapa grande/repetido
            tile_col_on_large_map = int(player_feet_x // self.tile_size)
            tile_row = int(player_feet_y // self.tile_size) # Linha não é afetada pela repetição horizontal

            # Largura do padrão original em tiles
            base_pattern_width_tiles = self.current_map_info["pixel_width"] // self.tile_size
            
            # Mapeia a coluna do tile no mapa grande de volta para a coluna no padrão original
            tile_col_in_pattern = tile_col_on_large_map % base_pattern_width_tiles
            
            current_tile_coords_in_pattern = (tile_col_in_pattern, tile_row)
            
            # Verifica se as coordenadas no padrão são válidas antes de acessar map_data
            if 0 <= tile_row < len(self.map_data) and \
               0 <= tile_col_in_pattern < (len(self.map_data[tile_row]) if self.map_data and tile_row < len(self.map_data) else 0) :
                current_tile_key = self.map_data[tile_row][tile_col_in_pattern]
                if current_tile_key == 'p':
                    # A chave do portal em self.current_map_info[\\\"portals\\\"] deve ser a coordenada no padrão
                    if current_tile_coords_in_pattern in self.current_map_info.get("portals", {}):
                        portal_data = self.current_map_info["portals"][current_tile_coords_in_pattern]
                        
                        if self.raw_portal_open_image: # Check if the base image was loaded
                            current_map_pattern_width = self.current_map_info["pixel_width"]
                            current_map_pattern_height = self.current_map_info["pixel_height"]
                            self.scaled_portal_open_background_override = pygame.transform.scale(
                                self.raw_portal_open_image, 
                                (current_map_pattern_width, current_map_pattern_height)
                            )
                        else: # Fallback if raw_portal_open_image failed to load
                            self.scaled_portal_open_background_override = None

                        self.portal_is_activating = True
                        self.portal_activation_timer = self.portal_activation_delay
                        self.portal_target_info = portal_data
                        # self.portal_tile_animating_coords removed
                        return 
            
            for npc in self.npcs.values():
                # NPCs can also have directions, but for now, they face "frente" and animate if set
                if npc.directional_frames.get("frente"): # Check if NPC has 'frente' frames
                    npc.current_direction = "frente"
                    if len(npc.directional_frames["frente"]) > 1: # If NPC has animation frames
                        npc.is_moving = True # Make NPCs animate if they have multiple frames
                    else:
                        npc.is_moving = False
                else: # No 'frente' frames, maybe a static sprite or error
                    npc.is_moving = False
                npc.update_animation()
            self.camera.update(self.player)

            player_rect = pygame.Rect(self.player.map_x, self.player.map_y, self.player.map_sprite_width, self.player.map_sprite_height)
            
            # Check for NPC collision only if dialogue_exit_active is False
            if not self.dialogue_exit_active:
                for npc_name, npc in self.npcs.items():
                    npc_rect = pygame.Rect(npc.map_x, npc.map_y, npc.map_sprite_width, npc.map_sprite_height)
                    if player_rect.colliderect(npc_rect) and npc.story:
                        self.game_state = "dialogue"
                        self.current_dialogue_story = npc.story
                        self.current_dialogue_story.reset() # Reseta a história do NPC para começar do início
                        scene = self.current_dialogue_story.get_current_scene()
                        if scene: # Deve haver uma cena após o reset
                            character_in_dialogue = self.characters.get(scene["character"])
                            if character_in_dialogue:
                                self.dialogue_system.set_dialogue(character_in_dialogue, scene["text"])
                        break # Interage com um NPC de cada vez
            # If player is not colliding with any NPC, reset the flag
            elif not any(player_rect.colliderect(pygame.Rect(npc.map_x, npc.map_y, npc.map_sprite_width, npc.map_sprite_height)) for npc in self.npcs.values()):
                self.dialogue_exit_active = False

        elif self.game_state == "dialogue":
            # Lógica de animação para personagem em diálogo
            current_char_in_dialogue = self.dialogue_system.current_character
            if current_char_in_dialogue:
                # Check if the character has 'frente' frames and more than one frame for animation
                frente_frames = current_char_in_dialogue.directional_frames.get("frente", [])
                if len(frente_frames) > 1:
                    current_char_in_dialogue.is_moving = True # Força animação durante diálogo
                    current_char_in_dialogue.update_animation()
                else:
                    current_char_in_dialogue.is_moving = False # No animation if single frame or no 'frente' frames
                    current_char_in_dialogue.update_animation() # Still call to reset frame index if needed

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_background() # No longer needs background_name

        if self.game_state == "map":
            player_map_pos_rect = pygame.Rect(self.player.map_x, self.player.map_y, self.player.map_sprite_width, self.player.map_sprite_height)
            self.player.draw_on_map(self.screen, self.camera.apply_to_rect(player_map_pos_rect).topleft)
            for npc in self.npcs.values():
                npc_map_pos_rect = pygame.Rect(npc.map_x, npc.map_y, npc.map_sprite_width, npc.map_sprite_height)
                npc.draw_on_map(self.screen, self.camera.apply_to_rect(npc_map_pos_rect).topleft)
            instruction_text = "WASD/Setas: Mover | ESC: Sair | Aproxime-se para interagir"
            self.screen.blit(self.font.render(instruction_text, True, WHITE), (10, 10))

        elif self.game_state == "dialogue":
            # Desenha personagem em diálogo e caixa de diálogo
            if self.current_dialogue_story and self.dialogue_system.current_character:
                char_in_dialogue = self.dialogue_system.current_character
                # Use 'frente' frames for dialogue, or fallback to any available frames
                dialogue_frames = char_in_dialogue.directional_frames.get("frente", list(char_in_dialogue.directional_frames.values())[0] if char_in_dialogue.directional_frames else [])

                if dialogue_frames:
                    # Ensure current_frame_index is valid for dialogue_frames
                    if char_in_dialogue.current_frame_index >= len(dialogue_frames):
                        char_in_dialogue.current_frame_index = 0

                    frame_to_draw = dialogue_frames[char_in_dialogue.current_frame_index]
                    # Use the character's dialogue_sprite_original_width/height for consistent dialogue sprite sizing
                    sprite_x = WIDTH // 2 - char_in_dialogue.dialogue_sprite_original_width // 2
                    sprite_y = HEIGHT // 2 - char_in_dialogue.dialogue_sprite_original_height // 2 - 50
                    self.screen.blit(frame_to_draw, (sprite_x, sprite_y))
                else: # Fallback se não houver frames
                    pygame.draw.rect(self.screen, char_in_dialogue.color, 
                                     (WIDTH//2 - char_in_dialogue.dialogue_sprite_original_width//2, 
                                      HEIGHT//2 - char_in_dialogue.dialogue_sprite_original_height//2 - 50, 
                                      char_in_dialogue.dialogue_sprite_original_width, 
                                      char_in_dialogue.dialogue_sprite_original_height))
            self.dialogue_system.draw_dialogue_box()
            instruction_text = "ESPAÇO: Próximo | ESC: Voltar ao Mapa"
            self.screen.blit(self.font.render(instruction_text, True, WHITE), (10, 10))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# Ponto de entrada principal
if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()