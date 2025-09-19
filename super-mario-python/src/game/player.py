import pygame
import os
import time

class Player:
    def __init__(self, x, y):
        self.width = 48
        self.height = 55
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.facing_right = True

        # Thuộc tính khác
        self.vel_y = 0
        self.on_ground = False
        self.health = 100
        self.invincible = False
        self.invincible_start = 0
        self.hit_head = False
        self.last_head_platform = None
        self.direction = 1  # 1: phải, -1: trái
        self.projectiles = []
        self.energy = 0         # Thanh nộ, tối đa 100
        self.charging = False   # Đang gồng nộ
        self.charge_effect = 0  # Hiệu ứng gồng
        self.special_active = False
        self.special_timer = 0
        self.special_direction = 1

        # Sprite sheet
        self.sprites_walk = []
        self.sprites_stand = []
        self.bboxes_walk = []
        self.bboxes_stand = []
        self.frame_offsets_walk = []
        self.frame_offsets_stand = []
        self.sprite_jump = None
        self.sprite_fall = None
        self.bbox_jump = None
        self.bbox_fall = None
        self.frame_offset_jump = (0, 0)
        self.frame_offset_fall = (0, 0)

        self.load_sprites()
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_speed = 6
        self.is_walking = False

        # Mặc định là đứng yên
        self.image = self.sprites_stand[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hitbox = self.rect.copy()

    def load_sprites(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "Character")
        # Walk sheet
        walk_path = os.path.join(assets_dir, "Characters-walk.png")
        walk_sheet = pygame.image.load(walk_path).convert_alpha()
        # Stand sheet
        stand_path = os.path.join(assets_dir, "Characters-stand.png")
        stand_sheet = pygame.image.load(stand_path).convert_alpha()
        # Jump sprite
        jump_path = os.path.join(assets_dir, "Characters-jump.png")
        jump_img = pygame.image.load(jump_path).convert_alpha()
        # Fall sprite
        fall_path = os.path.join(assets_dir, "Characters-fall.png")
        fall_img = pygame.image.load(fall_path).convert_alpha()

        num_frames_walk = 6
        num_frames_stand = 6
        frame_width_walk = walk_sheet.get_width() // num_frames_walk
        frame_height_walk = walk_sheet.get_height()
        frame_width_stand = stand_sheet.get_width() // num_frames_stand
        frame_height_stand = stand_sheet.get_height()

        target_height = 55
        # Walk frames
        for i in range(num_frames_walk):
            crop_width = frame_width_walk - 20
            frame = walk_sheet.subsurface((i * frame_width_walk, 0, crop_width, frame_height_walk))
            mask = pygame.mask.from_surface(frame)
            rects = mask.get_bounding_rects()
            bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
            cropped_frame = frame.subsurface(bbox)
            scale_ratio = target_height / cropped_frame.get_height()
            new_width = int(cropped_frame.get_width() * scale_ratio)
            scaled_frame = pygame.transform.scale(cropped_frame, (new_width, target_height))
            self.sprites_walk.append(scaled_frame)
            scaled_bbox = pygame.Rect(0, 0, new_width, target_height)
            self.bboxes_walk.append(scaled_bbox)
            offset_x = (self.width - new_width) // 2
            offset_y = 0
            self.frame_offsets_walk.append((offset_x, offset_y))
        # Stand frames
        for i in range(num_frames_stand):
            crop_width = frame_width_stand - 20
            frame = stand_sheet.subsurface((i * frame_width_stand, 0, crop_width, frame_height_stand))
            mask = pygame.mask.from_surface(frame)
            rects = mask.get_bounding_rects()
            bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
            cropped_frame = frame.subsurface(bbox)
            scale_ratio = target_height / cropped_frame.get_height()
            new_width = int(cropped_frame.get_width() * scale_ratio)
            scaled_frame = pygame.transform.scale(cropped_frame, (new_width, target_height))
            self.sprites_stand.append(scaled_frame)
            scaled_bbox = pygame.Rect(0, 0, new_width, target_height)
            self.bboxes_stand.append(scaled_bbox)
            offset_x = (self.width - new_width) // 2
            offset_y = 0
            self.frame_offsets_stand.append((offset_x, offset_y))

        # Jump sprite
        mask = pygame.mask.from_surface(jump_img)
        rects = mask.get_bounding_rects()
        bbox = rects[0] if rects else pygame.Rect(0, 0, jump_img.get_width(), jump_img.get_height())
        cropped = jump_img.subsurface(bbox)
        scale_ratio = 55 / cropped.get_height()
        new_width = int(cropped.get_width() * scale_ratio)
        self.sprite_jump = pygame.transform.scale(cropped, (new_width, 55))
        self.bbox_jump = pygame.Rect(0, 0, new_width, 55)
        self.frame_offset_jump = ((self.width - new_width) // 2, 0)
        # Fall sprite
        mask = pygame.mask.from_surface(fall_img)
        rects = mask.get_bounding_rects()
        bbox = rects[0] if rects else pygame.Rect(0, 0, fall_img.get_width(), fall_img.get_height())
        cropped = fall_img.subsurface(bbox)
        scale_ratio = 55 / cropped.get_height()
        new_width = int(cropped.get_width() * scale_ratio)
        self.sprite_fall = pygame.transform.scale(cropped, (new_width, 55))
        self.bbox_fall = pygame.Rect(0, 0, new_width, 55)
        self.frame_offset_fall = ((self.width - new_width) // 2, 0)

        # Cập nhật rect ban đầu
        self.image = self.sprites_stand[0]
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.width = self.image.get_width()
        self.height = target_height
        self.bbox = self.bboxes_stand[0]
        self.hitbox = self.rect.copy()

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

        if keys[pygame.K_LEFT]:
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.direction = 1

        # Gồng nộ khi giữ phím X
        if keys[pygame.K_x]:
            self.charging = True
            if self.energy < 100:
                self.energy += 0.5
            self.charge_effect = (self.charge_effect + 1) % 30
            dx = 0  # Không di chuyển khi gồng nộ
        else:
            self.charging = False
            self.charge_effect = 0
            dx = 0
            if keys[pygame.K_LEFT]:
                dx -= 5
                self.direction = -1
            if keys[pygame.K_RIGHT]:
                dx += 5
                self.direction = 1

        if self.special_active:
            self.special_timer -= 1
            if self.special_timer <= 0:
                self.special_active = False

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
                if self.vel_y > 0 and old_y + self.rect.height <= plat.rect.top + 5:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0 and old_y >= plat.rect.bottom - 5:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0
                    self.hit_head = True
                    self.last_head_platform = plat

        # Hết bất tử sau 1 giây
        if self.invincible and (time.time() - self.invincible_start > 1):
            self.invincible = False

        # Cập nhật frame khi di chuyển
        moving = dx != 0
        self.is_walking = moving
        if moving:
            self.frame_speed = 6  # tốc độ mặc định khi đi bộ
            self.frame_counter += 1
            if self.frame_counter >= self.frame_speed:
                self.current_frame = (self.current_frame + 1) % len(self.sprites_walk)
                self.frame_counter = 0
        else:
            self.frame_speed = 7  # tăng lên để idle chậm hơn (gợi ý: 18 hoặc lớn hơn)
            self.frame_counter += 1
            if self.frame_counter >= self.frame_speed:
                self.current_frame = (self.current_frame + 1) % len(self.sprites_stand)
                self.frame_counter = 0

        # Xác định trạng thái nhảy/rơi
        self.is_jumping = self.vel_y < 0 and not self.on_ground
        self.is_falling = self.vel_y > 0 and not self.on_ground

        # Cập nhật hướng
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        # Giữ nguyên midbottom khi đổi frame
        old_midbottom = self.rect.midbottom
        if self.is_jumping:
            self.image = self.sprite_jump
            self.bbox = self.bbox_jump
            offset_x, offset_y = self.frame_offset_jump
        elif self.is_falling:
            self.image = self.sprite_fall
            self.bbox = self.bbox_fall
            offset_x, offset_y = self.frame_offset_fall
        elif self.is_walking:
            self.image = self.sprites_walk[self.current_frame]
            self.bbox = self.bboxes_walk[self.current_frame]
            offset_x, offset_y = self.frame_offsets_walk[self.current_frame]
        else:
            self.image = self.sprites_stand[self.current_frame]
            self.bbox = self.bboxes_stand[self.current_frame]
            offset_x, offset_y = self.frame_offsets_stand[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.midbottom = old_midbottom

        # Hitbox căn giữa sprite trên khung 48x55
        hitbox_x = self.rect.x + offset_x
        hitbox_y = self.rect.y + offset_y

        self.hitbox = pygame.Rect(
            hitbox_x,
            hitbox_y,
            self.bbox.width,
            self.bbox.height
        )

    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_start = time.time()

    def attack(self):
        from game.projectile import Projectile
        # Đạn xuất phát từ giữa nhân vật
        proj = Projectile(self.rect.centerx, self.rect.centery, self.direction)
        self.projectiles.append(proj)
    
    def special_attack(self):
        self.energy = 0  # Reset nộ
        self.special_active = True
        self.special_timer = 10  # Số frame hiệu ứng đặc biệt
        self.special_direction = self.direction  # Hướng chưởng

    def render(self, screen):
        # Vẽ frame hiện tại, lật nếu quay trái
        visible = True
        if self.invincible:
            # Nhấp nháy: ẩn 1 frame, hiện 1 frame
            if int((time.time() - self.invincible_start) * 10) % 2 == 0:
                visible = False
        if visible:
            if self.is_jumping:
                img = self.sprite_jump
                offset_x, offset_y = self.frame_offset_jump
            elif self.is_falling:
                img = self.sprite_fall
                offset_x, offset_y = self.frame_offset_fall
            elif self.is_walking:
                img = self.sprites_walk[self.current_frame]
                offset_x, offset_y = self.frame_offsets_walk[self.current_frame]
            else:
                img = self.sprites_stand[self.current_frame]
                offset_x, offset_y = self.frame_offsets_stand[self.current_frame]
            draw_x = self.rect.x + offset_x
            draw_y = self.rect.y + offset_y
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, (draw_x, draw_y))

        font = pygame.font.SysFont(None, 32)
        health_text = font.render(f'HP: {self.health}', True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

        # Vẽ các đạn chưởng
        for proj in self.projectiles:
            proj.render(screen)
        
        pygame.draw.rect(screen, (50, 50, 50), (10, 50, 100, 12))
        pygame.draw.rect(screen, (0, 200, 255), (10, 50, int(self.energy), 12))
        font = pygame.font.SysFont(None, 18)
        energy_text = font.render('NỘ', True, (255, 255, 255))
        screen.blit(energy_text, (115, 48))
        # Hiệu ứng gồng nộ
        if self.charging:
            for i in range(8, 0, -1):
                rx = self.rect.width // 2 + i * 2
                ry = self.rect.height // 2 + i * 2
                color = pygame.Color(0)
                color.hsva = ((self.charge_effect * 5 + i * 40) % 360, 100, 100, int(20 * (i / 8)))
                s = pygame.Surface((rx*2, ry*2), pygame.SRCALPHA)
                pygame.draw.ellipse(s, color, (0, 0, rx*2, ry*2), 0)
                screen.blit(s, (self.rect.centerx - rx, self.rect.centery - ry))
        if self.special_active:
            effect_color = (255, 255, 0)
            if self.special_direction == 1:
                start = (self.rect.right, self.rect.centery)
                end = (screen.get_width(), self.rect.centery)
                width = screen.get_width() - self.rect.right
                x_pos = self.rect.right
            else:
                start = (self.rect.left, self.rect.centery)
                end = (0, self.rect.centery)
                width = self.rect.left
                x_pos = 0
            pygame.draw.line(screen, effect_color, start, end, 16)
            for i in range(5):
                alpha = 120 - i * 20
                color = (255, 255 - i*40, 0, alpha)
                s = pygame.Surface((width, 32), pygame.SRCALPHA)
                pygame.draw.rect(s, color, (0, 8-i, width, 16+i*2))
                if self.special_direction == 1:
                    screen.blit(s, (x_pos, self.rect.centery - 16 + i*2))
                else:
                    screen.blit(pygame.transform.flip(s, True, False), (x_pos, self.rect.centery - 16 + i*2))

        # Vẽ hitbox để kiểm tra
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)