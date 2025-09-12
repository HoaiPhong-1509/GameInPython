import pygame
import time
import os



def load_walk_frames(base_path, prefix, count, size=(48, 55)):
    frames = []
    for i in range(1, count + 1):
        file = f"{prefix}{i}-removebg.png"
        path = os.path.join(base_path, file)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)  # ép về 48×48
            frames.append(img)
    return frames



class Player:
    def __init__(self, x, y):
        base_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Character')

        # Walk frames (phải)
        self.walk_right_frames = load_walk_frames(base_path, "NV-right-walk", 3)

        # Flip sang trái
        self.walk_left_frames = [pygame.transform.flip(img, True, False) for img in self.walk_right_frames]

        # Jump frame
        img_jump = pygame.image.load(os.path.join(base_path, "NV-jump-removebg.png")).convert_alpha()
        img_jump = pygame.transform.scale(img_jump, (48, 48))  # ép 48×48 luôn
        self.img_jump = img_jump



        # Animation state
        self.image = self.walk_right_frames[0]

        # --- Hitbox dựa theo bounding box pixel thật ---
        mask = pygame.mask.from_surface(self.image)
        bbox = mask.get_bounding_rects()[0]  # lấy rect bao quanh pixel không trong suốt

        # rect (hitbox) khớp với phần nhân vật, bỏ nền trong suốt
        self.rect = pygame.Rect(x, y, bbox.width, bbox.height)
        self.rect.bottomleft = (x, y + bbox.height)

        # Ảnh căn theo hitbox
        self.image_rect = self.image.get_rect(midbottom=self.rect.midbottom)

        # Animation info
        self.facing_right = True
        self.current_frame = 0
        self.animation_timer = 0

        # Thuộc tính khác
        self.vel_y = 0
        self.on_ground = False
        self.health = 100
        self.invincible = False
        self.invincible_start = 0
        self.hit_head = False
        self.last_head_platform = None

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        moving = False

        if keys[pygame.K_LEFT]:
            dx -= 5
            moving = True
            self.facing_right = False

        if keys[pygame.K_RIGHT]:
            dx += 5
            moving = True
            self.facing_right = True

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False
            self.image = self.img_jump

        # --- Di chuyển ngang ---
        self.rect.x += dx
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if dx > 0:
                    self.rect.right = plat.rect.left
                elif dx < 0:
                    self.rect.left = plat.rect.right

        # --- Gravity + Di chuyển dọc ---
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        old_y = self.rect.y
        self.rect.y += self.vel_y

        self.on_ground = False
        self.hit_head = False
        self.last_head_platform = None

        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                # rơi xuống đất
                if self.vel_y > 0 and old_y + self.rect.height <= plat.rect.top + 5:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                # đụng trần
                elif self.vel_y < 0 and old_y >= plat.rect.bottom - 5:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0
                    self.hit_head = True
                    self.last_head_platform = plat

        # --- Animation ---
        if self.on_ground:
            if moving:
                self.animate_walk()
            else:
                self.image = self.walk_right_frames[0] if self.facing_right else self.walk_left_frames[0]

        if self.invincible and (time.time() - self.invincible_start > 3):
            self.invincible = False

        # Cập nhật vị trí ảnh theo hitbox
        self.image_rect.midbottom = self.rect.midbottom

    def animate_walk(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.walk_right_frames)

        if self.facing_right:
            self.image = self.walk_right_frames[self.current_frame]
        else:
            self.image = self.walk_left_frames[self.current_frame]

    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_start = time.time()

    def render(self, screen):
        draw_player = True
        if self.invincible:
            if int((time.time() - self.invincible_start) * 10) % 2 == 0:
                draw_player = False
        if draw_player:
            screen.blit(self.image, self.image_rect)

        font = pygame.font.SysFont(None, 32)
        health_text = font.render(f'HP: {self.health}', True, (255, 255, 255))
        screen.blit(health_text, (10, 10))
