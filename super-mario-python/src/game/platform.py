import pygame
import os

class Platform:
    chung_image = None
    mystery_image = None  # cache riêng cho mystery box

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

        # Tìm đường dẫn tuyệt đối dựa trên vị trí file platform.py
        base_path = os.path.dirname(__file__)  # .../src/game
        assets_path = os.path.normpath(os.path.join(base_path, "..", "assets", "other"))

        if width == 40 and height == 40:
            # Mystery Box
            if Platform.mystery_image is None:
                path = os.path.join(assets_path, "mystery-box.png")
                img = pygame.image.load(path).convert_alpha()
                Platform.mystery_image = img
            self.image = pygame.transform.scale(Platform.mystery_image, (width, height))
        else:
            # Chướng ngại
            if Platform.chung_image is None:
                path = os.path.join(assets_path, "ChuongNgai.png")
                img = pygame.image.load(path).convert_alpha()
                Platform.chung_image = img
            self.image = pygame.transform.scale(Platform.chung_image, (width, height))

    def render(self, screen):
        screen.blit(self.image, self.rect.topleft)
