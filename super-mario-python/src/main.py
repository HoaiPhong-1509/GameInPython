import pygame
import sys
from game.player import Player
from game.enemies import Enemy
from game.levels import Level
from game.item import Item
import os


items = []
# Initialize Pygame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Super Mario Python")

# Load background clouds
base_path = os.path.join(os.path.dirname(__file__), "assets", "other")
cloud1_img = pygame.image.load(os.path.join(base_path, "cloud1.png")).convert_alpha()
cloud2_img = pygame.image.load(os.path.join(base_path, "cloud2.png")).convert_alpha()

# Resize nếu cần cho phù hợp
cloud1_img = pygame.transform.scale(cloud1_img, (100, 60))
cloud2_img = pygame.transform.scale(cloud2_img, (120, 70))

# Danh sách các đám mây có vị trí + tốc độ
clouds = [
    {"x": 100, "y": 100, "speed": 0.3, "img": cloud1_img},
    {"x": 500, "y": 80, "speed": 0.2, "img": cloud2_img},
    {"x": 200, "y": 250, "speed": 0.25, "img": cloud2_img},
    {"x": 550, "y": 300, "speed": 0.35, "img": cloud1_img},
]

# Game variables
clock = pygame.time.Clock()

# Danh sách các map (level)
level_data_list = [
    [
        {'type': 'platform', 'x': 0, 'y': 550, 'width': 800, 'height': 50},
        {'type': 'platform', 'x': 200, 'y': 450, 'width': 100, 'height': 20},
        {'type': 'platform', 'x': 400, 'y': 350, 'width': 400, 'height': 20},
        {'type': 'platform', 'x': 600, 'y': 250, 'width': 500, 'height': 20},
    ],
    [
        {'type': 'platform', 'x': 0, 'y': 550, 'width': 800, 'height': 50},      # Đất chính
        {'type': 'platform', 'x': 100, 'y': 450, 'width': 120, 'height': 20},    # Bậc trái
        {'type': 'platform', 'x': 300, 'y': 400, 'width': 100, 'height': 20},    # Bậc giữa
        {'type': 'platform', 'x': 500, 'y': 350, 'width': 180, 'height': 20},    # Bậc phải
        {'type': 'platform', 'x': 650, 'y': 250, 'width': 100, 'height': 20},    # Bậc cao phải
        {'type': 'platform', 'x': 250, 'y': 200, 'width': 120, 'height': 60},    # Bậc cao giữa
        {'type': 'platform', 'x': 450, 'y': 180, 'width': 120, 'height': 30},    
        {'type': 'platform', 'x': 250, 'y': 95, 'width': 40, 'height': 40},     # Hộp vật phẩm ?
    ]
]
current_level = 0
level = Level(level_data_list[current_level])

def reset_enemies_for_level(level_idx):
    if level_idx == 0:
        return [
            Enemy((200, 490), 100),
            Enemy((300, 490), 100),
            Enemy((500, 290), 100, move_range=(400, 800))
        ]
    elif level_idx == 1:
        return [
            Enemy((120, 390), 100, move_range=(100, 220)),   # Đứng trên bậc trái
            Enemy((550, 290), 100, move_range=(500, 680))    # Đứng trên bậc phải
        ]
    return []

player = Player(100, 400)  
enemies = reset_enemies_for_level(current_level)

def draw_game_over(screen):
    # Tạo lớp phủ mờ
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Màu đen, alpha 180/255
    screen.blit(overlay, (0, 0))

    # Hiện chữ GAME OVER
    font_big = pygame.font.SysFont(None, 80)
    font_small = pygame.font.SysFont(None, 48)
    text_game_over = font_big.render("GAME OVER", True, (255, 0, 0))
    text_retry = font_small.render("Again", True, (255, 255, 255))

    screen.blit(text_game_over, (screen.get_width()//2 - text_game_over.get_width()//2, 180))
    retry_rect = text_retry.get_rect(center=(screen.get_width()//2, 300))
    screen.blit(text_retry, retry_rect)
    return retry_rect

def main():
    global current_level, level, enemies, player
    game_over = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if retry_rect and retry_rect.collidepoint(mouse_pos):
                        # Reset lại game
                        current_level = 0
                        level = Level(level_data_list[current_level])
                        player = Player(100, 400)
                        enemies = reset_enemies_for_level(current_level)
                        game_over = False

        if not game_over:
            # Update game state
            player.update(level.platforms)

            # Update clouds
            for cloud in clouds:
                cloud["x"] += cloud["speed"]
                if cloud["x"] > screen_width:
                    cloud["x"] = -cloud["img"].get_width()

            # Kiểm tra va chạm đầu với hộp vật phẩm ?
            if player.hit_head and player.last_head_platform:
                plat = player.last_head_platform
                if plat.rect.width == 40 and plat.rect.height == 40:
                    # Chỉ sinh item nếu platform này chưa từng sinh item
                    if not hasattr(plat, "used") or not plat.used:
                        items.append(Item(plat.rect.centerx - 15, plat.rect.top +10))
                        plat.used = True

            # Update item
            for item in items:
                item.update()

            for enemy in enemies:
                enemy.update()
                if player.rect.colliderect(enemy.rect):
                    player.take_damage(20)

            level.update()

            # Chuyển map nếu player đi qua mép phải
            if player.rect.right > screen_width:
                current_level += 1
                if current_level >= len(level_data_list):
                    current_level = 0
                level = Level(level_data_list[current_level])
                player = Player(0, player.rect.y)
                enemies = reset_enemies_for_level(current_level)
            # Chỉ cho phép chuyển map trái nếu không phải map 1
            elif player.rect.left < 0 and current_level != 0:
                current_level -= 1
                if current_level < 0:
                    current_level = len(level_data_list) - 1
                level = Level(level_data_list[current_level])
                player = Player(screen_width - player.rect.width, player.rect.y)
                enemies = reset_enemies_for_level(current_level)
            # Chặn mép trái ở map 1
            if current_level == 0 and player.rect.left < 0:
                player.rect.left = 0
            
        # Render everything
        screen.fill((135, 206, 235))

        # Vẽ mây
        for cloud in clouds:
            screen.blit(cloud["img"], (cloud["x"], cloud["y"]))

        level.render(screen)
        for enemy in enemies:
            enemy.render(screen)
        player.render(screen)

        # Render item SAU CÙNG để luôn nổi lên trên
        for item in items:
            item.render(screen)
            if item.active and player.rect.colliderect(item.rect) and not item.rising:
                player.health = min(player.health + 50, 100)
                item.active = False

        retry_rect = None
        if player.health <= 0:
            game_over = True
            retry_rect = draw_game_over(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
