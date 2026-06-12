import os
import sys
import random

import pygame


WIDTH, HEIGHT = 960, 540
FPS = 60


def load_image(name: str, fallback_color: tuple[int, int, int], size: tuple[int, int]) -> pygame.Surface:
    """画像ファイルがあればロード、なければ色付きの四角で代用"""
    if os.path.exists(name):
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf


def draw_pseudo_3d_background(screen: pygame.Surface) -> None:
    """簡単な擬似3D背景（空＋遠近感のある地面＋城）"""
    # 空のグラデーション
    top_color = pygame.Color(20, 30, 80)
    bottom_color = pygame.Color(80, 140, 220)
    for i in range(HEIGHT // 2):
        ratio = i / (HEIGHT // 2)
        r = top_color.r + (bottom_color.r - top_color.r) * ratio
        g = top_color.g + (bottom_color.g - top_color.g) * ratio
        b = top_color.b + (bottom_color.b - top_color.b) * ratio
        pygame.draw.line(screen, (int(r), int(g), int(b)), (0, i), (WIDTH, i))

    # 地面（遠近感のある台形）
    ground_color = (40, 100, 40)
    pygame.draw.polygon(
        screen,
        ground_color,
        [
            (0, HEIGHT // 2 + 20),
            (WIDTH, HEIGHT // 2 + 20),
            (WIDTH * 3 // 4, HEIGHT - 10),
            (WIDTH // 4, HEIGHT - 10),
        ],
    )

    # 道
    road_color = (130, 110, 80)
    pygame.draw.polygon(
        screen,
        road_color,
        [
            (WIDTH // 2 - 40, HEIGHT // 2 + 20),
            (WIDTH // 2 + 40, HEIGHT // 2 + 20),
            (WIDTH * 3 // 5, HEIGHT - 10),
            (WIDTH * 2 // 5, HEIGHT - 10),
        ],
    )

    # 遠くの城（擬似3D）
    castle_base_y = HEIGHT // 2 + 10
    castle_color = (200, 200, 220)
    pygame.draw.rect(screen, castle_color, (WIDTH // 2 - 70, castle_base_y - 80, 140, 80))
    pygame.draw.rect(screen, castle_color, (WIDTH // 2 - 40, castle_base_y - 120, 80, 40))
    # 塔
    pygame.draw.rect(screen, castle_color, (WIDTH // 2 - 90, castle_base_y - 70, 20, 70))
    pygame.draw.rect(screen, castle_color, (WIDTH // 2 + 70, castle_base_y - 70, 20, 70))
    # 旗
    pygame.draw.line(screen, (120, 120, 140), (WIDTH // 2, castle_base_y - 120), (WIDTH // 2, castle_base_y - 150), 3)
    pygame.draw.polygon(
        screen,
        (220, 60, 60),
        [
            (WIDTH // 2, castle_base_y - 150),
            (WIDTH // 2 + 30, castle_base_y - 140),
            (WIDTH // 2, castle_base_y - 130),
        ],
    )


class Fighter:
    def __init__(
        self,
        name: str,
        max_hp: int,
        atk: int,
        pos: tuple[int, int],
        image: pygame.Surface,
    ) -> None:
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.atk = atk
        self.pos = pos
        self.image = image

    def is_alive(self) -> bool:
        return self.hp > 0

    def attack(self, other: "Fighter") -> int:
        damage = max(1, self.atk + random.randint(-3, 3))
        other.hp = max(0, other.hp - damage)
        return damage


def draw_hp_bar(
    screen: pygame.Surface,
    x: int,
    y: int,
    w: int,
    h: int,
    current: int,
    maximum: int,
    color: tuple[int, int, int],
) -> None:
    pygame.draw.rect(screen, (0, 0, 0), (x - 2, y - 2, w + 4, h + 4))
    pygame.draw.rect(screen, (60, 60, 60), (x, y, w, h))
    ratio = max(0.0, min(1.0, current / maximum))
    inner_w = int(w * ratio)
    if inner_w > 0:
        pygame.draw.rect(screen, color, (x, y, inner_w, h))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("ちいさな冒険 - Pygame 版")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("meiryo", 32)
    font_small = pygame.font.SysFont("meiryo", 20)

    # 画像読み込み（無ければ色付き四角）
    hero_img = load_image("hero.png", (60, 180, 255), (140, 200))
    dragon_img = load_image("dragon.png", (200, 80, 80), (220, 220))

    hero = Fighter("ゆうしゃ", max_hp=120, atk=16, pos=(WIDTH // 4, HEIGHT // 2 + 40), image=hero_img)
    dragon = Fighter("ドラゴン", max_hp=200, atk=18, pos=(WIDTH * 3 // 4 - 160, HEIGHT // 2 - 20), image=dragon_img)

    turn = "player"  # "player" or "enemy"
    message_lines: list[str] = [
        "スペース: こうげき   S: とくぎ   Q: やめる",
        "ゆうしゃ と ドラゴン が あらわれた！",
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and turn == "player":
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE and hero.is_alive() and dragon.is_alive():
                    dmg = hero.attack(dragon)
                    message_lines = [f"ゆうしゃ の こうげき！ ドラゴン に {dmg} の ダメージ！"]
                    turn = "enemy"
                elif event.key == pygame.K_s and hero.is_alive() and dragon.is_alive():
                    # とくぎ：少し強い攻撃
                    dmg = hero.attack(dragon) + random.randint(5, 10)
                    dragon.hp = max(0, dragon.hp - dmg)
                    message_lines = ["ゆうしゃ の ひっさつぎわざ！", f"ドラゴン に {dmg} の 大ダメージ！"]
                    turn = "enemy"

        # 敵ターンの処理（自動）
        if turn == "enemy" and dragon.is_alive() and hero.is_alive():
            pygame.time.delay(400)
            dmg = dragon.attack(hero)
            message_lines = [f"ドラゴン の こうげき！ ゆうしゃ は {dmg} の ダメージ！"]
            turn = "player"

        if not dragon.is_alive():
            message_lines = ["ドラゴン を たおした！", "Fキー で 終了"]
        if not hero.is_alive():
            message_lines = ["ゆうしゃ は たおれた…", "Fキー で 終了"]

        keys = pygame.key.get_pressed()
        if (not hero.is_alive() or not dragon.is_alive()) and keys[pygame.K_f]:
            running = False

        # 描画
        draw_pseudo_3d_background(screen)

        # ドラゴン
        screen.blit(dragon.image, dragon.pos)
        draw_hp_bar(screen, WIDTH - 320, 40, 260, 18, dragon.hp, dragon.max_hp, (220, 60, 60))
        text_enemy = font_small.render(f"ドラゴン  HP {dragon.hp}/{dragon.max_hp}", True, (255, 255, 255))
        screen.blit(text_enemy, (WIDTH - 320, 10))

        # ヒーロー
        screen.blit(hero.image, hero.pos)
        draw_hp_bar(screen, 60, HEIGHT - 80, 260, 18, hero.hp, hero.max_hp, (60, 220, 60))
        text_hero = font_small.render(f"ゆうしゃ  HP {hero.hp}/{hero.max_hp}", True, (255, 255, 255))
        screen.blit(text_hero, (60, HEIGHT - 110))

        # メッセージウィンドウ
        msg_rect = pygame.Rect(40, HEIGHT - 150, WIDTH - 80, 100)
        pygame.draw.rect(screen, (0, 0, 0), msg_rect)
        pygame.draw.rect(screen, (255, 255, 255), msg_rect, 2)

        y = msg_rect.y + 10
        for line in message_lines[:3]:
            surf = font_small.render(line, True, (255, 255, 255))
            screen.blit(surf, (msg_rect.x + 14, y))
            y += 26

        title_surf = font_big.render("ちいさな冒険 - ドラゴン戦（Pygame版）", True, (255, 255, 0))
        screen.blit(title_surf, (40, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
