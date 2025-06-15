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
        self.game_state = "map"  # Initial state, can be "playing", "dialogue", "map"
        
        # Carregar a fonte pixelizada
        try:
            # Substitua 'pixel_font.ttf' pelo nome do seu arquivo de fonte e 36 pelo tamanho desejado
            font_path = os.path.join("src", "assets", "depixel.ttf") # Caminho corrigido
            pixel_font_size = 16 # Ajuste o tamanho conforme necessário
            self.font = pygame.font.Font(font_path, pixel_font_size)
        except pygame.error as e:
            print(f"Erro ao carregar a fonte pixelizada: {e}. Usando fonte padrão.")
            self.font = pygame.font.Font(None, 24) # Fallback para a fonte padrão
        except FileNotFoundError:
            print(f"Arquivo da fonte pixelizada não encontrado em {font_path}. Usando fonte padrão.")
            self.font = pygame.font.Font(None, 24)

        self.dialogue_system = DialogueSystem(self.screen, self.font, WIDTH, HEIGHT)
        
        player_sprite_paths = {
            "frente": {"path": os.path.join("src", "assets", "sprite_knight_frente.png"), "frames": 2},
            "costas": {"path": os.path.join("src", "assets", "sprite_knight_costas.png"), "frames": 2},
            "esquerda": {"path": os.path.join("src", "assets", "sprite_knight_esquerda.png"), "frames": 2},
            "direita": {"path": os.path.join("src", "assets", "sprite_knight_direita.png"), "frames": 2},
        }
        # Player starting position will be relative to the first map's dimensions.
        self.player = Character("Cavaleiro", BLUE, map_x=0, map_y=0, sprite_paths=player_sprite_paths)
        # Using "protagonist" as a conventional ID for the player in story data
        self.player.id = "protagonist" 
        
        # NPCs will be loaded per map. This dictionary will hold NPCs for the CURRENT map.
        self.current_map_npcs = {}
        self.current_npc_in_dialogue = None # Stores the Character object of NPC in dialogue

        # Define stories globally, referenced by NPCs in map definitions
        self.stories = {}
        
        blacksmith_story = Story()
        blacksmith_story.scenes = [
            # Ensure "character" uses the NPC's ID as defined in map_definitions
            {"character": "blacksmith_mundo_principal", "text": "Olá, nobre cavaleiro! Precisa de uma espada afiada?"},
            {"character": "blacksmith_mundo_principal", "text": "Minhas forjas estão sempre quentes!"}
        ]
        
        guardiao_story = Story()
        guardiao_story.scenes = [
            {"character": "cave_guardian", "text": "Você não deveria estar aqui, forasteiro!"},
            {"character": "cave_guardian", "text": "A caverna guarda segredos que não são para os olhos curiosos."}
        ]
        self.stories["guardian_story"] = guardiao_story
        self.stories["blacksmith_story_generic"] = blacksmith_story

        merchant_story = Story()
        merchant_story.scenes = [
            {"character": "merchant_mundo_principal", "text": "Mercadorias raras, direto de terras distantes!"},
            {"character": "merchant_mundo_principal", "text": "Tenho poções e artefatos, se tiveres ouro."}
        ]
        self.stories["merchant_story_generic"] = merchant_story
        
        self.current_dialogue_story = None
        self.tile_size = 100 
        self.current_dialogue_background_surface = None

        # Define NPC sprite paths that can be reused or defined per NPC in map_definitions
        self.default_npc_sprite_paths = {
            "frente": {"path": os.path.join("src", "assets", "sprite_knight_frente.png"), "frames": 1} # Placeholder
        }

        self.map_definitions = {
            "mundo_principal": {
                "layout_file": os.path.join("src", "assets", "map_layout.map"),
                "background_image": os.path.join("src", "assets", "map_image.png"),
                "dialogue_background_image": os.path.join("src", "assets", "fundo_dialogo_castelo.png"),
                "pixel_width": 2000, 
                "pixel_height": 2000,
                "portals": {
                    (9, 11): {"target_map_key": "caverna_secreta", "target_player_pos": (150, 600)}, 
                    (10, 11): {"target_map_key": "caverna_secreta", "target_player_pos": (150, 600)},
                    (9, 12): {"target_map_key": "caverna_secreta", "target_player_pos": (150, 600)},
                    (10, 12): {"target_map_key": "caverna_secreta", "target_player_pos": (150, 600)},
                    (7, 7): {"target_map_key": "caverna_secreta", "target_player_pos": (100, 100)},
                },
                "npcs": [
                    {
                        "id": "blacksmith_mundo_principal",
                        "name": "Ferreiro",
                        "sprite_paths": { # Example for blacksmith, assuming single frame sprites
                            "frente": {"path": os.path.join("src", "assets", "sprite_knight_frente.png"), "frames": 1}
                        }, 
                        "map_x": 200, "map_y": 250, 
                        "story_key": "blacksmith_story_generic"
                    },
                    {
                        "id": "merchant_mundo_principal",
                        "name": "Mercador",
                        "sprite_paths": {
                            "frente": {"path": os.path.join("src", "assets", "sprite_knight_frente.png"), "frames": 1} # Example
                        },
                        "map_x": 1700, "map_y": 1700,
                        "story_key": "merchant_story_generic"
                    }
                ]
            },
            "caverna_secreta": {
                "layout_file": os.path.join("src", "assets", "map_caverna.map"),
                "background_image": os.path.join("src", "assets", "caverna_bg_animated.png"),
                "dialogue_background_image": os.path.join("src", "assets", "fundo_dialogo_castelo.png"),
                "background_animation_frames": 3,
                "pixel_width": 1000,
                "pixel_height": 342,
                "repeat_x": 3,
                "portals": {
                    (2, 1): {"target_map_key": "mundo_principal", "target_player_pos": (9 * self.tile_size + self.tile_size // 2, 13 * self.tile_size)},
                },
                "npcs": [
                     {
                         "id": "cave_guardian",
                         "name": "Guardião da Caverna",
                         "sprite_paths": {"frente": {"path": os.path.join("src", "assets", "cavaleiro2_animado.png"), "frames": 2}},
                         "map_x": 500, "map_y": 150,
                         "story_key": "guardian_story"
                     }
                ]
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
            "g0": pygame.image.load(os.path.join("src", "assets", "grama_tile_0.png")).convert_alpha(), #grama 0 graus
            "g90": pygame.image.load(os.path.join("src", "assets", "grama_tile_90.png")).convert_alpha(), #grama 90 graus
            "g180": pygame.image.load(os.path.join("src", "assets", "grama_tile_180.png")).convert_alpha(), #grama 180 graus
            "g270": pygame.image.load(os.path.join("src", "assets", "grama_tile_270.png")).convert_alpha(), #grama 270 graus
            "s": pygame.image.load(os.path.join("src", "assets", "areia.png")).convert_alpha(), # areia
            "p": pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA),
            "a": pygame.image.load(os.path.join("src", "assets", "porta_aberta.png")).convert_alpha(), # porta fechada
            "f": pygame.image.load(os.path.join("src", "assets", "porta_fechada.png")).convert_alpha(), # porta fechada (usada para portas de NPCs)
        }
        self.tiles["p"].fill((0,0,0,0))

        # Load the raw portal open image (unscaled)
        try:
            portal_open_image_path = os.path.join("src", "assets", "portao_aberto.png")
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

        # Load NPCs for the current map
        self.current_map_npcs.clear()
        npc_configs = self.current_map_info.get("npcs", [])
        for config in npc_configs:
            npc_id = config["id"]
            npc_name = config["name"]
            sprite_paths = config.get("sprite_paths", self.default_npc_sprite_paths) # Fallback to default
            map_x = config["map_x"]
            map_y = config["map_y"]
            story_key = config.get("story_key")

            new_npc = Character(name=npc_name, map_x=map_x, map_y=map_y, sprite_paths=sprite_paths)
            new_npc.id = npc_id # Assign the ID to the character object for story referencing

            if story_key and story_key in self.stories:
                new_npc.story = self.stories[story_key]
            else:
                new_npc.story = None # Or a default empty story
                if story_key:
                    print(f"Warning: Story key '{story_key}' for NPC '{npc_id}' not found in self.stories.")
            
            self.current_map_npcs[npc_id] = new_npc
            print(f"Loaded NPC: {npc_id} at ({map_x},{map_y}) for map {self.current_map_key}")


        # Load dialogue background for the current map
        self.current_dialogue_background_surface = None # Reset
        dialogue_bg_path = self.current_map_info.get("dialogue_background_image")
        if dialogue_bg_path:
            try:
                raw_dialogue_bg = pygame.image.load(dialogue_bg_path).convert()
                self.current_dialogue_background_surface = pygame.transform.scale(raw_dialogue_bg, (WIDTH, HEIGHT))
            except pygame.error as e:
                print(f"Error loading dialogue background for {self.current_map_key} at {dialogue_bg_path}: {e}")
            except FileNotFoundError:
                print(f"Dialogue background image file not found at {dialogue_bg_path}.")
        
        if self.current_dialogue_background_surface is None:
            # Fallback if loading failed or no path was provided
            print(f"Using fallback dialogue background for map {self.current_map_key}.")
            self.current_dialogue_background_surface = pygame.Surface((WIDTH, HEIGHT))
            self.current_dialogue_background_surface.fill(DARK_GRAY) # Default dialogue background

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
            # Use self.current_map_pixel_height which is an attribute of the Game class
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
                            if scene is None: 
                                self.game_state = "map" # Or "playing"
                                if self.current_npc_in_dialogue: # Clear dialogue state for the NPC
                                    self.current_npc_in_dialogue.is_in_dialogue = False
                                self.current_npc_in_dialogue = None
                                self.current_dialogue_story = None
                                self.dialogue_system.clear_dialogue()
                                self.dialogue_exit_active = True 
                            else:
                                speaker_id_from_scene = scene["character"]
                                speaker_object = None
                                if speaker_id_from_scene == self.player.id: # Check against player's assigned ID
                                    speaker_object = self.player
                                elif speaker_id_from_scene in self.current_map_npcs:
                                    speaker_object = self.current_map_npcs[speaker_id_from_scene]
                                
                                if speaker_object:
                                    self.dialogue_system.set_dialogue(speaker_object, scene["text"])
                                else:
                                    print(f"Error: Speaker ID '{speaker_id_from_scene}' in story not found.")
                                    # Potentially end dialogue or skip scene
                                    self.game_state = "map" # Or "playing"
                                    if self.current_npc_in_dialogue:
                                       self.current_npc_in_dialogue.is_in_dialogue = False
                                    self.current_npc_in_dialogue = None
                                    self.current_dialogue_story = None
                                    self.dialogue_system.clear_dialogue()

                    elif event.key == pygame.K_ESCAPE:
                        if self.game_state == "dialogue":
                            if self.current_npc_in_dialogue: # Clear dialogue state for the NPC
                                self.current_npc_in_dialogue.is_in_dialogue = False
                            self.current_npc_in_dialogue = None
                            self.dialogue_system.clear_dialogue() 
                            self.game_state = "map" # Changed from "playing" to "map" to match other dialogue exits
                            # self.current_npc_in_dialogue was already cleared by clear_dialogue if it sets self.current_character to None
                elif self.game_state == "map": # Assuming "map" is the state for free roaming
                    if event.key == pygame.K_e: # Example: 'E' to interact
                        # Check for NPC interaction
                        player_interaction_rect = self.player.get_interaction_rect()
                        for npc_id, npc_object in self.current_map_npcs.items():
                            # Use interaction_rect for both player and NPC for consistent detection
                            if player_interaction_rect.colliderect(npc_object.get_interaction_rect()):
                                self._handle_dialogue_interaction(npc_object)
                                break # Interact with the first NPC found
                    
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

    def _handle_dialogue_interaction(self, npc_character):
        if npc_character and npc_character.story:
            self.game_state = "dialogue"
            self.current_npc_in_dialogue = npc_character
            self.current_dialogue_story = npc_character.story
            self.current_dialogue_story.reset() # Start story from the beginning
            
            first_scene = self.current_dialogue_story.get_current_scene()
            if first_scene:
                speaker_id_from_scene = first_scene["character"]
                speaker_object = None
                if speaker_id_from_scene == self.player.id:
                    speaker_object = self.player
                elif speaker_id_from_scene in self.current_map_npcs:
                    speaker_object = self.current_map_npcs[speaker_id_from_scene]
                
                if speaker_object:
                    self.dialogue_system.set_dialogue(speaker_object, first_scene["text"])
                else:
                    print(f"Error: Speaker ID '{speaker_id_from_scene}' for first scene not found.")
                    self.game_state = "map" 
                    self.current_npc_in_dialogue = None
                    self.current_dialogue_story = None
            else: # Story has no scenes
                print(f"Warning: Story for NPC '{npc_character.name}' has no scenes.")
                self.game_state = "map"
                self.current_npc_in_dialogue = None
                self.current_dialogue_story = None
        else:
            if npc_character:
                 print(f"Info: NPC '{npc_character.name}' has no story to tell.")
            # No story or no NPC, remain in current state or switch to map/playing
            # self.game_state = "map" # Or "playing"

    def update(self):
        # Update animations regardless of game state for characters that might be on screen
        self.player.update_animation()
        for npc in self.current_map_npcs.values():
            npc.update_animation()
        
        if self.game_state == "dialogue":
            # Specific dialogue updates, like character in dialogue animation (already covered by above)
            if self.dialogue_system.current_character: # This is the character currently speaking
                 self.dialogue_system.current_character.update_animation() # Ensure speaker animates
            # Make sure the NPC being talked TO also updates its is_in_dialogue state if needed
            if self.current_npc_in_dialogue and not self.current_npc_in_dialogue.is_in_dialogue:
                self.current_npc_in_dialogue.is_in_dialogue = True


        if self.portal_is_activating:
            self.portal_activation_timer -= 1
            
            if self.portal_activation_timer <= 0:
                if self.portal_target_info:
                    # The f_portal_original_coords logic for changing the tile is removed from here,
                    # as the tile is now changed immediately upon portal activation.
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
            # self.player.update_animation() # Moved to top of update

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
                # Check if the player is on a portal tile ('p' or 'f')
                if current_tile_key == 'p' or current_tile_key == 'f':
                    # Check if this specific tile coordinate is defined as a portal in the current map's settings
                    if current_tile_coords_in_pattern in self.current_map_info.get("portals", {}):
                        portal_info = self.current_map_info["portals"][current_tile_coords_in_pattern]
                        if not self.portal_is_activating:
                            self.portal_is_activating = True
                            self.portal_activation_timer = self.portal_activation_delay
                            self.portal_target_info = portal_info
                            
                            # If it's an 'f' tile (NPC/special portal), change it to 'a' immediately
                            if current_tile_key == 'f':
                                self.map_data[tile_row][tile_col_in_pattern] = 'a'
                                # Ensure 'f' portals do not use the special opening background
                                self.scaled_portal_open_background_override = None 
                            elif self.raw_portal_open_image: # For 'p' tiles, use override
                                # Scale the portal open image to the base pattern width of the current map
                                base_map_width = self.current_map_info["pixel_width"]
                                base_map_height = self.current_map_info["pixel_height"]
                                self.scaled_portal_open_background_override = pygame.transform.scale(self.raw_portal_open_image, (base_map_width, base_map_height))
            
            # NPC updates (like movement, decisions, etc. - not just animation) could go here
            # For now, only animation is handled at the top of update()
            # Example: Check for player interaction (moved to events for key press)
            
            self.camera.update(self.player)

            # player_rect = pygame.Rect(self.player.map_x, self.player.map_y, self.player.map_sprite_width, self.player.map_sprite_height) # Not used


        # elif self.game_state == "dialogue": # Dialogue specific updates are now at the top or within events
            # pass
            

    def draw(self):
        self.screen.fill(BLACK) # Default background if others fail

        if self.game_state == "dialogue" and self.current_dialogue_background_surface:
            self.screen.blit(self.current_dialogue_background_surface, (0,0))
            # DialogueSystem's draw method will draw the character sprite and text box over this
        else: # "map" or "playing" state
            self.draw_background() # Draws map background and tiles
            
            # Draw player
            self.player.draw_on_map(self.screen, (self.player.map_x + self.camera.camera_rect.x, self.player.map_y + self.camera.camera_rect.y))

            # Draw NPCs for the current map
            for npc_id, npc_obj in self.current_map_npcs.items():
                npc_obj.draw_on_map(self.screen, (npc_obj.map_x + self.camera.camera_rect.x, npc_obj.map_y + self.camera.camera_rect.y))

        # If in dialogue state, draw dialogue UI on top of everything else for that state
        if self.game_state == "dialogue":
            self.dialogue_system.draw() 
            instruction_text = "Espaço: Avançar | ESC: Fechar Diálogo"
            self.screen.blit(self.font.render(instruction_text, True, WHITE), (10, HEIGHT - 30))
        
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