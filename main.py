import sys
import os
import random
import pygame
import importlib

script_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(script_dir, 'build')
sys.path.append(build_dir)

# pybind11でビルドされたC++モジュールをインポート
try:
    puyo_core = importlib.import_module('puyo_core')
except ImportError:
    print('puyo_core モジュールが見つかりません。ビルド済みか確認してください。')
    sys.exit(1)

# ゲーム設定
CELL_SIZE = 32
FIELD_WIDTH = 6
FIELD_HEIGHT = 12
VISIBLE_TOP_MARGIN = 2  # 上部に2行分余裕を持たせて表示
SCREEN_WIDTH = CELL_SIZE * FIELD_WIDTH
SCREEN_HEIGHT = CELL_SIZE * (FIELD_HEIGHT + VISIBLE_TOP_MARGIN)
FPS = 60
PUYO_COLORS = ["red", "green", "blue", "yellow"]
COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (160, 32, 240),
    "garbage": (192, 192, 192),
}

# C++ CellType enum との対応
CELLTYPE_MAP = {
    0: None,  # EMPTY
    2: "red",
    3: "green",
    4: "yellow",
    5: "blue",
    6: "purple",
    7: "garbage",
}
REVERSE_CELLTYPE_MAP = {
    "red": puyo_core.CellType.RED,
    "green": puyo_core.CellType.GREEN,
    "yellow": puyo_core.CellType.YELLOW,
    "blue": puyo_core.CellType.BLUE,
    "purple": puyo_core.CellType.PURPLE,
    "garbage": puyo_core.CellType.GARBAGE,
}

def draw_field(screen, field):
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            cell = field.get_cell(x, y)
            color_name = CELLTYPE_MAP.get(int(cell), None)
            if color_name:
                pygame.draw.rect(screen, COLOR_MAP[color_name], (x*CELL_SIZE, (y+VISIBLE_TOP_MARGIN)*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_active_tsumo(screen, field):
    tsumo = field.get_active_tsumo()
    for dx, dy, color in [
        (0, 0, tsumo.center),
        (tsumo.dx, tsumo.dy, tsumo.sub),
    ]:
        x = tsumo.x + dx
        y = tsumo.y + dy
        if 0 <= x < FIELD_WIDTH and y >= -VISIBLE_TOP_MARGIN - 1 and y < FIELD_HEIGHT:
            color_name = CELLTYPE_MAP.get(int(color), None)
            if color_name:
                pygame.draw.rect(
                    screen,
                    COLOR_MAP[color_name],
                    (x * CELL_SIZE, (y + VISIBLE_TOP_MARGIN) * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('PuyoPuyo')
    clock = pygame.time.Clock()
    field = puyo_core.Field(FIELD_HEIGHT, FIELD_WIDTH)

    # C++側のgenerate_next_tsumoでネクスト・ネクネク・操作ぷよを管理
    field.generate_next_tsumo()  # ネクスト・ネクネク初期化
    field.generate_next_tsumo()  # 操作ぷよをセット

    running = True
    while running:
        drop_flag = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    field.move_active_tsumo_left()
                elif event.key == pygame.K_d:
                    field.move_active_tsumo_right()
                elif event.key == pygame.K_w:
                    drop_flag = True
                elif event.key == pygame.K_DOWN:
                    field.rotate_active_tsumo_left()
                elif event.key == pygame.K_RIGHT:
                    field.rotate_active_tsumo_right()
        # 自動落下機能を削除
        if drop_flag:
            field.drop_active_tsumo()
            # 1連鎖ずつ描画しながら連鎖処理
            while True:
                chain_info = field.analyze_and_erase_chains()
                if not getattr(chain_info, 'erased', False):
                    break
                field.apply_gravity()
                # 1連鎖ごとに描画・少し待つ
                screen.fill((0, 0, 0))
                draw_field(screen, field)
                pygame.display.flip()
                pygame.time.wait(800)  # 400ms待機
            field.generate_next_tsumo()  # 操作ぷよ・ネクスト・ネクネクをC++側で更新
        screen.fill((0, 0, 0))
        draw_field(screen, field)
        draw_active_tsumo(screen, field)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == '__main__':
    main()
