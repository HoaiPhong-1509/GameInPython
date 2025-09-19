import os
import pygame

class Enemy:
    def __init__(self, position, health, move_range=None):
        self.rect = pygame.Rect(position[0], position[1], 60, 60)
        self.direction = 1
        self.move_range = move_range
        self.health = health
        

        # Vận tốc di chuyển
        self.speed = 2  

        # Load frames
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "enemies")
        base_path = os.path.abspath(base_path)

        self.frames_right = [
            pygame.image.load(os.path.join(base_path, "enemy-walk1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "enemy-walk2.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "enemy-walk3.png")).convert_alpha(),
        ]
        self.frames_right = [pygame.transform.scale(frame, (self.rect.width, self.rect.height)) for frame in self.frames_right]
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in self.frames_right]

        # Hoạt ảnh
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.05  # chỉnh nhỏ hơn thì hoạt ảnh chậm hơn

        # Trạng thái bất tử
        self.invincible = False
        self.invincible_timer = 0

        # Knockback
        self.knockback = 0  # Số pixel bị đẩy lùi còn lại
        self.knockback_dir = 0  # Hướng đẩy lùi

    def update(self):
        # Xử lý knockback trước khi di chuyển bình thường
        if self.knockback > 0:
            self.rect.x += self.knockback_dir * 6  # tốc độ đẩy lùi, chỉnh tùy ý
            self.knockback -= 1
        else:
            # Di chuyển kẻ địch bình thường
            self.rect.x += self.direction * self.speed
            if self.move_range:
                if self.rect.left < self.move_range[0] or self.rect.right > self.move_range[1]:
                    self.direction *= -1
            else:
                if self.rect.left < 0 or self.rect.right > 800:
                    self.direction *= -1

        # Cập nhật hoạt ảnh (chậm, cố định)
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames_right)
        
        # Cập nhật trạng thái bất tử
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def render(self, screen):
        if self.direction > 0:
            frame = self.frames_right[self.current_frame]
        else:
            frame = self.frames_left[self.current_frame]
        screen.blit(frame, self.rect)

    def take_damage(self, amount, knockback_dir=0):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_timer = 10  # bất tử 10 frame sau khi bị đánh
            if knockback_dir != 0:
                self.knockback = 8  # số frame bị đẩy lùi, chỉnh tùy ý
                self.knockback_dir = knockback_dir
