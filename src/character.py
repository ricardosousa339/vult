import pygame

# Cores (se forem usadas apenas pela Character, podem ficar aqui ou em um config.py)
BLUE = (100, 150, 255) 

class Character:
    def __init__(self, name, color=BLUE, map_x=0, map_y=0, sprite_paths=None, map_sprite_static_path=None): 
        self.name = name
        self.color = color
        self.dialogue_sprite_original_width = 150 
        self.dialogue_sprite_original_height = 200

        self.directional_frames = {} 
        self.current_frame_index = 0
        self.animation_speed = 60 # Aumentado de 15 para 30 para diminuir a velocidade da animação
        self.animation_timer = 0
        self.is_moving = False
        self.current_direction = "frente" 
        self.is_in_dialogue = False 
        self.map_sprite_surface = None # For static map sprite

        if map_sprite_static_path:
            try:
                self.map_sprite_surface = pygame.image.load(map_sprite_static_path).convert_alpha()
                # Scale it to map_sprite_width, map_sprite_height if needed, or use original size
                # For now, let's assume it's pre-sized or we'll scale in draw_on_map
            except pygame.error as e:
                print(f"Cannot load static map sprite for {self.name} at {map_sprite_static_path}: {e}")

        if sprite_paths:
            for direction, sprite_info in sprite_paths.items():
                path = sprite_info["path"]
                num_frames = sprite_info.get("frames", 1) # Default to 1 frame if not specified
                try:
                    full_sprite_image = pygame.image.load(path).convert_alpha()
                    spritesheet_width = full_sprite_image.get_width()
                    spritesheet_height = full_sprite_image.get_height()
                    
                    frame_width = spritesheet_width // num_frames 
                    frame_height = spritesheet_height

                    current_direction_frames = []
                    if frame_width > 0 and num_frames > 0:
                        for i in range(num_frames):
                            frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                            current_direction_frames.append(full_sprite_image.subsurface(frame_rect))
                    else: # Should not happen if path and frames are correct
                        current_direction_frames.append(full_sprite_image) # Fallback to full image
                    
                    self.directional_frames[direction] = current_direction_frames
                    
                    if direction == "frente" and current_direction_frames:
                        first_frame_frente = current_direction_frames[0]
                        # Update dialogue sprite dimensions based on the actual first frame of 'frente'
                        # This ensures dialogue sprite scaling is based on the single frame, not the whole sheet
                        self.dialogue_sprite_original_width = first_frame_frente.get_width()
                        self.dialogue_sprite_original_height = first_frame_frente.get_height()

                except pygame.error as e:
                    print(f"Cannot load sprite for {self.name} direction {direction} at {path}: {e}")
                    self.directional_frames[direction] = [] 
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

        self.id = None # Added to store unique NPC ID if needed
        self.story = None # Added to store Story object

    def update_animation(self):
        frames_key_to_use = "frente"
        should_animate_continuously = False

        if self.is_in_dialogue:
            frames_key_to_use = "frente"
            should_animate_continuously = True # Animate idle in dialogue
        else:
            frames_key_to_use = self.current_direction
            should_animate_continuously = self.is_moving # Animate only if moving on map

        active_frames = self.directional_frames.get(frames_key_to_use, 
                                                   self.directional_frames.get("frente", [])) # Fallback to "frente"

        if not active_frames or len(active_frames) <= 1:
            self.current_frame_index = 0
            self.animation_timer = 0
            return

        if should_animate_continuously:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame_index = (self.current_frame_index + 1) % len(active_frames)
        else: # Not moving and not in dialogue (or single frame animation)
            self.current_frame_index = 0 # Reset to first frame
            self.animation_timer = 0

    def get_current_animated_frame(self) -> pygame.Surface | None:
        frames_key_to_use = "frente" if self.is_in_dialogue else self.current_direction
        
        active_frames = self.directional_frames.get(frames_key_to_use, 
                                                   self.directional_frames.get("frente", [])) # Fallback to "frente"

        if active_frames:
            idx = self.current_frame_index
            if idx >= len(active_frames): 
                idx = 0
            return active_frames[idx]
        return None

    def get_rect(self):
        """Returns the character's bounding box rectangle on the map."""
        return pygame.Rect(self.map_x, self.map_y, self.map_sprite_width, self.map_sprite_height)

    def get_interaction_rect(self, interaction_reach=10):
        """Returns a slightly larger rectangle for interaction detection."""
        # Center of the base rect
        base_rect = self.get_rect()
        center_x = base_rect.centerx
        center_y = base_rect.centery
        
        # Make it slightly larger for easier interaction
        interaction_width = base_rect.width + interaction_reach * 2
        interaction_height = base_rect.height + interaction_reach * 2
        
        return pygame.Rect(
            center_x - interaction_width // 2,
            center_y - interaction_height // 2,
            interaction_width,
            interaction_height
        )

    # Remove or comment out the old get_dialogue_sprite method

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
        if self.map_sprite_surface and not self.is_moving: # NPCs are typically not moving
            # Scale the static map sprite if it hasn't been scaled yet or if dimensions differ
            # For simplicity, let's assume it's either pre-scaled or we scale it here once
            # This could be optimized by scaling once in __init__ if dimensions are fixed
            scaled_map_sprite = pygame.transform.scale(self.map_sprite_surface, (self.map_sprite_width, self.map_sprite_height))
            screen.blit(scaled_map_sprite, position)
        else: # Fallback to animated sprite (e.g., for player or if static map sprite not set)
            active_frames = self.directional_frames.get(self.current_direction, self.directional_frames.get("frente", []))
            current_frame_surface = None
            if active_frames:
                if self.current_frame_index >= len(active_frames):
                    self.current_frame_index = 0 # Safety check
                current_frame_surface = active_frames[self.current_frame_index]
            
            if current_frame_surface:
                # Scale the frame to map_sprite_width and map_sprite_height
                scaled_frame = pygame.transform.scale(current_frame_surface, (self.map_sprite_width, self.map_sprite_height))
                screen.blit(scaled_frame, position)
            else:
                # Fallback: draw a simple rect if no sprite is available
                pygame.draw.rect(screen, self.color, (position[0], position[1], self.map_sprite_width, self.map_sprite_height))
