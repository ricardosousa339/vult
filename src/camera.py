import pygame

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
        # Assumes target has map_x, map_y, and map_sprite_size attributes
        x = -target.map_x + self.width // 2 - target.map_sprite_size // 2
        y = -target.map_y + self.height // 2 - target.map_sprite_size // 2

        # Limita o scroll aos limites do mapa
        x = min(0, x)  # Não deixa a câmera ir para a esquerda do início do mapa (0)
        y = min(0, y)  # Não deixa a câmera ir para cima do início do mapa (0)
        x = max(-(self.map_width - self.width), x)  # Não deixa a câmera ir para a direita do fim do mapa
        y = max(-(self.map_height - self.height), y) # Não deixa a câmera ir para baixo do fim do mapa
        
        self.camera_rect.topleft = (x, y)
