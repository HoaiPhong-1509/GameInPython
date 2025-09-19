import os
import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, health, move_range=None):
        super().__init__()
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

        # Physics
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms=None):
        # Xử lý knockback trước khi di chuyển bình thường
        if self.knockback > 0:
            self.rect.x += self.knockback_dir * 6
            self.knockback -= 1
        else:
            # CHỈ di chuyển ngang và kiểm tra move_range khi đang đứng trên platform
            if self.on_ground:
                self.rect.x += self.direction * self.speed

                if self.move_range:
                    # Nếu vượt ra khỏi move_range thì đảo hướng, KHÔNG ép vị trí
                    if self.rect.left < self.move_range[0]:
                        self.direction = 1
                    elif self.rect.right > self.move_range[1]:
                        self.direction = -1
                else:
                    # Nếu không có move_range, chỉ đảo hướng khi chạm mép màn hình
                    if self.rect.left < 0:
                        self.direction = 1
                    elif self.rect.right > 800:
                        self.direction = -1

        # Áp dụng trọng lực
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.y += int(self.vel_y)
        self.on_ground = False

        # Xác định platform đất chính (y lớn nhất, width >= 800)
        ground_platform = None
        if platforms:
            for plat in platforms:
                if plat.rect.width >= 800:
                    ground_platform = plat
                    break

        # Kiểm tra va chạm với platform
        standing_on_ground = False
        if platforms:
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    if self.vel_y > 0 and self.rect.bottom - plat.rect.top < 20:
                        self.rect.bottom = plat.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        # Nếu đứng trên platform đất chính thì bỏ move_range
                        if ground_platform and plat == ground_platform:
                            standing_on_ground = True
                        break  # Đã đứng trên 1 platform thì không cần kiểm tra tiếp

        # Nếu đang đứng trên đất chính thì bỏ move_range, cho đi tự do
        if standing_on_ground:
            self.move_range = None
        else:
            # Nếu enemy có move_range gốc thì giữ lại, tránh bị mất khi nhảy lên lại platform
            if hasattr(self, "original_move_range"):
                self.move_range = self.original_move_range
            else:
                self.original_move_range = self.move_range

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
