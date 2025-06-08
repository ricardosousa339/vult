import pygame

# Cores (se forem usadas apenas pela Character, podem ficar aqui ou em um config.py)
BLUE = (100, 150, 255) 

class Character:
    def __init__(self, name, color=BLUE, map_x=0, map_y=0, sprite_path=None):
        self.name = name
        self.color = color
        self.dialogue_sprite_original_width = 150
        self.dialogue_sprite_original_height = 200

        self.frames = []
        self.is_animated = False
        self.current_frame_index = 0
        self.animation_speed = 15
        self.animation_timer = 0
        self.is_moving = False

        if sprite_path:
            try:
                full_sprite_image = pygame.image.load(sprite_path).convert_alpha()
                spritesheet_width = full_sprite_image.get_width()
                spritesheet_height = full_sprite_image.get_height()
                frame_width = spritesheet_width // 2
                frame_height = spritesheet_height

                if frame_width > 0 and spritesheet_width >= frame_width * 2:
                    self.frames.append(full_sprite_image.subsurface(pygame.Rect(0, 0, frame_width, frame_height)))
                    self.frames.append(full_sprite_image.subsurface(pygame.Rect(frame_width, 0, frame_width, frame_height)))
                    self.is_animated = True
                    self.dialogue_sprite_original_width = frame_width
                    self.dialogue_sprite_original_height = frame_height
                else:
                    self.frames.append(full_sprite_image)
                    self.dialogue_sprite_original_width = spritesheet_width
                    self.dialogue_sprite_original_height = spritesheet_height
            except pygame.error as e:
                print(f"Cannot load sprite for {self.name} at {sprite_path}: {e}")

        self.story = None
        self.map_x = map_x
        self.map_y = map_y
        self.map_sprite_size = 48
        self.player_speed = 4

    def update_animation(self):
        if not self.is_animated or not self.frames or len(self.frames) <= 1:
            return
        if not self.is_moving:
            self.current_frame_index = 0
            self.animation_timer = 0
            return
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)

    def move(self, dx, dy, map_boundary_width, map_boundary_height):
        new_x = self.map_x + dx
        new_y = self.map_y + dy
        if 0 <= new_x <= map_boundary_width - self.map_sprite_size:
            self.map_x = new_x
        if 0 <= new_y <= map_boundary_height - self.map_sprite_size:
            self.map_y = new_y

    def draw_on_map(self, screen, map_pos_on_screen):
        if self.frames:
            current_frame_surface = self.frames[self.current_frame_index]
            scaled_sprite = pygame.transform.scale(current_frame_surface, (self.map_sprite_size, self.map_sprite_size))
            screen.blit(scaled_sprite, map_pos_on_screen)
        else:
            pygame.draw.rect(screen, self.color, (map_pos_on_screen[0], map_pos_on_screen[1], self.map_sprite_size, self.map_sprite_size))
