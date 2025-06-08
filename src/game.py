import pygame
import sys
import os

from camera import Camera
from character import Character # Assuming BLUE is defined in character.py or a config.py
from dialogue_system import DialogueSystem # Assuming colors are in dialogue_system.py or config
from story import Story
from config import WIDTH, HEIGHT, FPS, MAP_WIDTH, MAP_HEIGHT, BLACK, BLUE, WHITE, DARK_GRAY


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Visual Novel - Demo Medieval")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "map"
        
        self.font = pygame.font.Font(None, 24)
        # Passa WIDTH e HEIGHT para DialogueSystem
        self.dialogue_system = DialogueSystem(self.screen, self.font, WIDTH, HEIGHT)
        
        player_sprite_path = os.path.join("src", "assets", "sprite_knight_frente.png")
        # Usar um caminho diferente ou o mesmo placeholder para NPCs
        npc_sprite_path = os.path.join("src", "assets", "sprite_knight_frente.png") 

        # Player starting position: Horizontally centered, bottom of the map
        player_start_x = MAP_WIDTH // 2
        # Assuming self.player.map_sprite_size is the height of the player on the map
        # We'll need to instantiate the player first to get this, or use a fixed value if known
        # For now, let's assume a known/typical sprite size for initial y calculation, then refine if needed
        # Or, better, calculate it based on player's actual map_sprite_size after instantiation.
        # Let's instantiate with a placeholder Y and then adjust, or use a known value.
        # player_start_y = MAP_HEIGHT - A_KNOWN_PLAYER_SPRITE_HEIGHT_ON_MAP 
        # For simplicity now, let's use a direct calculation, assuming player object is available or its size is known.
        # We will define player_start_y after player object is created to use its map_sprite_size.

        self.player = Character("Cavaleiro", BLUE, map_x=player_start_x, map_y=0, sprite_path=player_sprite_path) # Placeholder map_y
        player_start_y = MAP_HEIGHT - self.player.map_sprite_size 
        self.player.map_y = player_start_y # Set the correct map_y

        self.npcs = {
            "blacksmith": Character("Ferreiro", (100,100,100), map_x=100, map_y=100, sprite_path=npc_sprite_path),
            "merchant": Character("Mercador", (0,100,0), map_x=MAP_WIDTH - 150, map_y=MAP_HEIGHT -150, sprite_path=npc_sprite_path)
        }
        self.characters = {"protagonist": self.player}
        self.characters.update(self.npcs)

        # Configuração das histórias dos NPCs
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
        
        self.current_dialogue_story = None
        self.current_background = "floresta_medieval"
        self.camera = Camera(WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT)
        self.dialogue_exit_active = False # Flag to manage dialogue re-triggering

        # Load tiles
        self.tile_size = 100 # Or your desired tile size
        self.tiles = {
            "g0": pygame.image.load(os.path.join("src", "assets", "grama_tile_0.png")).convert_alpha(),
            "g90": pygame.image.load(os.path.join("src", "assets", "grama_tile_90.png")).convert_alpha(),
            "g180": pygame.image.load(os.path.join("src", "assets", "grama_tile_180.png")).convert_alpha(),
            "g270": pygame.image.load(os.path.join("src", "assets", "grama_tile_270.png")).convert_alpha(),
            "s": pygame.image.load(os.path.join("src", "assets", "areia.png")).convert_alpha(),
        }
        # Scale tiles if necessary
        for key in self.tiles:
            self.tiles[key] = pygame.transform.scale(self.tiles[key], (self.tile_size, self.tile_size))

        self.map_data = self.load_map_data(os.path.join("src", "assets", "map_layout.map"))
        self.collision_map_rects = []
        self.blocking_tile_keys = ['x', 'g0', 'g90', 'g180', 'g270'] # Define blocking tile keys including grass
        self._create_collision_rects()

    def _create_collision_rects(self):
        self.collision_map_rects = []
        for row_index, row_data in enumerate(self.map_data):
            for col_index, tile_key in enumerate(row_data):
                if tile_key in self.blocking_tile_keys: # Check if the tile_key is in the list of blocking keys
                    rect = pygame.Rect(col_index * self.tile_size, 
                                       row_index * self.tile_size, 
                                       self.tile_size, 
                                       self.tile_size)
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
            num_cols = MAP_WIDTH // self.tile_size
            num_rows = MAP_HEIGHT // self.tile_size
            map_data = [['0' for _ in range(num_cols)] for _ in range(num_rows)]
        return map_data

    def draw_background(self, background_name):
        # Load the map image
        map_image_path = os.path.join("src", "assets", "map_image.png")
        try:
            map_image = pygame.image.load(map_image_path).convert()
            map_image = pygame.transform.scale(map_image, (MAP_WIDTH, MAP_HEIGHT))
            # Blit the map image as the background
            self.screen.blit(map_image, (self.camera.camera_rect.x, self.camera.camera_rect.y))
        except pygame.error as e:
            print(f"Error loading base map image: {e}")
            self.screen.fill(BLACK) # Fallback to black background

        # Overlay tiles based on self.map_data
        for row_index, row_data in enumerate(self.map_data):
            for col_index, tile_key in enumerate(row_data):
                tile_image = self.tiles.get(tile_key)
                if tile_image:
                    x = col_index * self.tile_size + self.camera.camera_rect.x
                    y = row_index * self.tile_size + self.camera.camera_rect.y
                    
                    # Only draw if tile is on screen
                    tile_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    screen_rect = self.screen.get_rect()
                    if tile_rect.colliderect(screen_rect):
                         self.screen.blit(tile_image, (x, y))

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
        if self.game_state == "map":
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            any_key_pressed = (keys[pygame.K_LEFT] or keys[pygame.K_a] or
                               keys[pygame.K_RIGHT] or keys[pygame.K_d] or
                               keys[pygame.K_UP] or keys[pygame.K_w] or
                               keys[pygame.K_DOWN] or keys[pygame.K_s])
            self.player.is_moving = any_key_pressed

            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -self.player.player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = self.player.player_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -self.player.player_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = self.player.player_speed
            
            if dx != 0 or dy != 0: self.player.move(dx, dy, MAP_WIDTH, MAP_HEIGHT, self.collision_map_rects)
            self.player.update_animation()
            
            for npc in self.npcs.values():
                if npc.is_animated and len(npc.frames) > 1: npc.is_moving = True
                else: npc.is_moving = False
                npc.update_animation()
            self.camera.update(self.player)

            player_rect = pygame.Rect(self.player.map_x, self.player.map_y, self.player.map_sprite_size, self.player.map_sprite_size)
            
            # Check for NPC collision only if dialogue_exit_active is False
            if not self.dialogue_exit_active:
                for npc_name, npc in self.npcs.items():
                    npc_rect = pygame.Rect(npc.map_x, npc.map_y, npc.map_sprite_size, npc.map_sprite_size)
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
            elif not any(player_rect.colliderect(pygame.Rect(npc.map_x, npc.map_y, npc.map_sprite_size, npc.map_sprite_size)) for npc in self.npcs.values()):
                self.dialogue_exit_active = False

        elif self.game_state == "dialogue":
            # Lógica de animação para personagem em diálogo
            if self.dialogue_system.current_character and self.dialogue_system.current_character.is_animated:
                self.dialogue_system.current_character.is_moving = True # Força animação durante diálogo
                self.dialogue_system.current_character.update_animation()

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_background(self.current_background)

        if self.game_state == "map":
            player_map_pos_rect = pygame.Rect(self.player.map_x, self.player.map_y, self.player.map_sprite_size, self.player.map_sprite_size)
            self.player.draw_on_map(self.screen, self.camera.apply_to_rect(player_map_pos_rect).topleft)
            for npc in self.npcs.values():
                npc_map_pos_rect = pygame.Rect(npc.map_x, npc.map_y, npc.map_sprite_size, npc.map_sprite_size)
                npc.draw_on_map(self.screen, self.camera.apply_to_rect(npc_map_pos_rect).topleft)
            instruction_text = "WASD/Setas: Mover | ESC: Sair | Aproxime-se para interagir"
            self.screen.blit(self.font.render(instruction_text, True, WHITE), (10, 10))

        elif self.game_state == "dialogue":
            # Desenha personagem em diálogo e caixa de diálogo
            if self.current_dialogue_story and self.dialogue_system.current_character:
                char_in_dialogue = self.dialogue_system.current_character
                if char_in_dialogue.frames:
                    frame_to_draw = char_in_dialogue.frames[char_in_dialogue.current_frame_index]
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