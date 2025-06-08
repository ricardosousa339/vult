import pygame

# Cores (se forem usadas apenas pela Character, podem ficar aqui ou em um config.py)
BLUE = (100, 150, 255) 

class Character:
    def __init__(self, name, color=BLUE, map_x=0, map_y=0, sprite_paths=None): # Changed sprite_path to sprite_paths
        self.name = name
        self.color = color
        # Default dialogue sprite size, can be overridden by 'frente' sprite
        self.dialogue_sprite_original_width = 150 
        self.dialogue_sprite_original_height = 200

        self.directional_frames = {} # Stores lists of frames for each direction
        self.current_frame_index = 0
        self.animation_speed = 15 
        self.animation_timer = 0
        self.is_moving = False
        self.current_direction = "frente" # Default direction

        if sprite_paths:
            for direction, path in sprite_paths.items():
                try:
                    full_sprite_image = pygame.image.load(path).convert_alpha()
                    spritesheet_width = full_sprite_image.get_width()
                    spritesheet_height = full_sprite_image.get_height()
                    # Assuming 2 frames horizontally for animation if spritesheet is wide enough
                    frame_width = spritesheet_width // 2 
                    frame_height = spritesheet_height

                    current_direction_frames = []
                    if frame_width > 0 and spritesheet_width >= frame_width * 2: # Check if it's a 2-frame sheet
                        current_direction_frames.append(full_sprite_image.subsurface(pygame.Rect(0, 0, frame_width, frame_height)))
                        current_direction_frames.append(full_sprite_image.subsurface(pygame.Rect(frame_width, 0, frame_width, frame_height)))
                    else: # Single frame sprite
                        current_direction_frames.append(full_sprite_image)
                    
                    self.directional_frames[direction] = current_direction_frames
                    
                    # If this is the 'frente' sprite, set dialogue dimensions from its first frame
                    if direction == "frente" and current_direction_frames:
                        first_frame_frente = current_direction_frames[0]
                        self.dialogue_sprite_original_width = first_frame_frente.get_width()
                        self.dialogue_sprite_original_height = first_frame_frente.get_height()

                except pygame.error as e:
                    print(f"Cannot load sprite for {self.name} direction {direction} at {path}: {e}")
                    self.directional_frames[direction] = [] # Store empty list if loading fails
        self.map_x = map_x
        self.map_y = map_y
        # New dimensions based on 28x34 aspect ratio, aiming for height ~102
        self.map_sprite_width = 58
        self.map_sprite_height = 81
        self.player_speed = 4

        # Collision hitbox properties (feet area)
        self.collision_box_width_ratio = 0.7  # 70% of sprite width
        self.collision_box_height_ratio = 0.3 # 30% of sprite height (feet)

        self.collision_box_width = int(self.map_sprite_width * self.collision_box_width_ratio)
        self.collision_box_height = int(self.map_sprite_height * self.collision_box_height_ratio)
        
        # Offset to center the collision box horizontally and place it at the bottom
        self.collision_box_offset_x = (self.map_sprite_width - self.collision_box_width) // 2
        self.collision_box_offset_y = self.map_sprite_height - self.collision_box_height


    def update_animation(self):
        active_frames = self.directional_frames.get(self.current_direction, self.directional_frames.get("frente", []))

        if not active_frames or len(active_frames) <= 1: # Not animated if no frames or just a single frame
            self.current_frame_index = 0 # Reset to first frame if available (or stay at 0 if no frames)
            self.animation_timer = 0
            return

        if not self.is_moving:
            self.current_frame_index = 0
            self.animation_timer = 0
            return
        
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(active_frames)

    def move(self, dx, dy, map_width, map_height, collision_rects=None):
        # Attempt X movement
        potential_map_x = self.map_x + dx
        # Define the collision rectangle for X movement check
        player_collision_rect_x = pygame.Rect(
            potential_map_x + self.collision_box_offset_x,
            self.map_y + self.collision_box_offset_y,
            self.collision_box_width,
            self.collision_box_height
        )

        collided_x = False
        if collision_rects and dx != 0:
            for rect in collision_rects:
                if player_collision_rect_x.colliderect(rect):
                    if dx > 0:  # Moving right
                        # Adjust map_x so collision_box right edge touches rect left edge
                        self.map_x = rect.left - self.collision_box_width - self.collision_box_offset_x
                    elif dx < 0:  # Moving left
                        # Adjust map_x so collision_box left edge touches rect right edge
                        self.map_x = rect.right - self.collision_box_offset_x
                    collided_x = True
                    break
        
        if not collided_x:
            self.map_x = potential_map_x

        # Attempt Y movement
        potential_map_y = self.map_y + dy
        # Define the collision rectangle for Y movement check (using potentially updated self.map_x)
        player_collision_rect_y = pygame.Rect(
            self.map_x + self.collision_box_offset_x,
            potential_map_y + self.collision_box_offset_y,
            self.collision_box_width,
            self.collision_box_height
        )

        collided_y = False
        if collision_rects and dy != 0:
            for rect in collision_rects:
                if player_collision_rect_y.colliderect(rect):
                    if dy > 0:  # Moving down
                        # Adjust map_y so collision_box bottom edge touches rect top edge
                        self.map_y = rect.top - self.collision_box_height - self.collision_box_offset_y
                    elif dy < 0:  # Moving up
                        # Adjust map_y so collision_box top edge touches rect bottom edge
                        self.map_y = rect.bottom - self.collision_box_offset_y
                    collided_y = True
                    break
        
        if not collided_y:
            self.map_y = potential_map_y

        # Boundary checks for map limits (based on the full sprite)
        self.map_x = max(0, min(self.map_x, map_width - self.map_sprite_width))
        self.map_y = max(0, min(self.map_y, map_height - self.map_sprite_height))

    def draw_on_map(self, screen, position):
        active_frames = self.directional_frames.get(self.current_direction, self.directional_frames.get("frente", []))

        if active_frames:
            # Ensure current_frame_index is valid for the current set of frames
            if self.current_frame_index >= len(active_frames):
                self.current_frame_index = 0
            
            current_frame_surface = active_frames[self.current_frame_index]
            scaled_sprite = pygame.transform.scale(current_frame_surface, (self.map_sprite_width, self.map_sprite_height))
            screen.blit(scaled_sprite, position)
        else:
            pygame.draw.rect(screen, self.color, (position[0], position[1], self.map_sprite_width, self.map_sprite_height))
