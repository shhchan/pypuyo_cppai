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
FIELD_HEIGHT = 14
VISIBLE_TOP_MARGIN = 2  # 上部に2行分余裕を持たせて表示
# ステータス表示用の高さを2行分確保（例: 80px）
STATUS_BAR_HEIGHT = 80
SCREEN_WIDTH = CELL_SIZE * FIELD_WIDTH
SCREEN_HEIGHT = CELL_SIZE * (FIELD_HEIGHT + VISIBLE_TOP_MARGIN) + STATUS_BAR_HEIGHT
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
    # ゴースト位置の取得
    ghost = field.get_ghost_position()
    (gcx, gcy), (gsx, gsy) = ghost
    # ゴーストぷよの描画（小さい半透明四角形、セル中央）
    ghost_size = int(CELL_SIZE * 0.5)
    ghost_offset = (CELL_SIZE - ghost_size) // 2
    for dx, dy, color, gx, gy in [
        (0, 0, tsumo.center, gcx, gcy),
        (tsumo.dx, tsumo.dy, tsumo.sub, gsx, gsy),
    ]:
        color_name = CELLTYPE_MAP.get(int(color), None)
        if color_name:
            ghost_rect = pygame.Rect(
                gx * CELL_SIZE + ghost_offset,
                (gy + VISIBLE_TOP_MARGIN) * CELL_SIZE + ghost_offset,
                ghost_size,
                ghost_size
            )
            ghost_surface = pygame.Surface((ghost_size, ghost_size), pygame.SRCALPHA)
            ghost_surface.fill(COLOR_MAP[color_name] + (150,))  # 透明度50
            screen.blit(ghost_surface, ghost_rect)
    # 操作中ぷよの描画（通常）
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

def draw_nexts(screen, field):
    # ネクスト・ネクネクをフィールド右側に描画
    nexts = field.get_next_tsumos()  # get_next_tsumos()で取得
    base_x = FIELD_WIDTH * CELL_SIZE + 16  # フィールド右端+余白
    base_y = VISIBLE_TOP_MARGIN * CELL_SIZE + 32
    for i, (center, sub) in enumerate(nexts):
        # 上がsub, 下がcenterとして縦に描画
        y_offset = base_y + i * 3 * CELL_SIZE
        for j, color in enumerate([sub, center]):
            color_name = CELLTYPE_MAP.get(int(color), None)
            if color_name:
                pygame.draw.rect(
                    screen,
                    COLOR_MAP[color_name],
                    (base_x, y_offset + j * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )
        # ラベル
        font = pygame.font.SysFont(None, 24)
        label = font.render("NEXT" if i == 0 else "NEXT2", True, (255,255,255))
        screen.blit(label, (base_x, y_offset - 24))

def draw_status(screen, field):
    # スコアと連鎖数をフィールド下部に2行で表示
    font = pygame.font.SysFont(None, 32)
    score = field.get_score()
    chain = field.get_current_chain_size()
    score_label = font.render(f"SCORE: {score}", True, (255, 255, 255))
    chain_label = font.render(f"CHAIN: {chain}", True, (255, 255, 255))
    base_x = 16
    # ステータスバーの中央寄せ（フィールド下端＋余白）
    base_y = (FIELD_HEIGHT + VISIBLE_TOP_MARGIN) * CELL_SIZE + 16
    screen.blit(score_label, (base_x, base_y))
    screen.blit(chain_label, (base_x, base_y + 36))

def main():
    pygame.init()
    # 画面サイズをネクスト表示分拡張
    screen = pygame.display.set_mode((SCREEN_WIDTH + 80, SCREEN_HEIGHT))
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
            chain_count = 0  # 連鎖数を初期化
            # 1連鎖ずつ描画しながら連鎖処理
            while True:
                chain_info = field.analyze_and_erase_chains(chain_count)
                if not getattr(chain_info, 'erased', False):
                    break
                # 連鎖が発生した場合は連鎖数を更新
                chain_count += 1
                field.set_current_chain_size(chain_count)
                # スコア計算
                field.update_score(chain_info)
                field.apply_gravity()
                # 1連鎖ごとに描画・少し待つ
                screen.fill((0, 0, 0))
                draw_field(screen, field)
                draw_nexts(screen, field)
                draw_status(screen, field)
                pygame.display.flip()
                pygame.time.wait(800)  # 400ms待機
            field.generate_next_tsumo()  # 操作ぷよ・ネクスト・ネクネクをC++側で更新
        # 連鎖が終了したら field の連鎖数をリセット（本当は field のメンバに current_chain_size があるので，それを使うようにすべき）
        field.set_current_chain_size(0)
        screen.fill((0, 0, 0))
        draw_field(screen, field)
        draw_active_tsumo(screen, field)
        draw_nexts(screen, field)
        draw_status(screen, field)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == '__main__':
    main()
