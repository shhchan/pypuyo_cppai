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
STATUS_BAR_HEIGHT = CELL_SIZE * 3 * 1.5  # スコア・連鎖数・モード表示用（1.5倍で余裕を持たせる）
# 画面サイズの計算
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
            # 窒息点(3列目12段目, x=2, y=2)に赤いバツ印をセルいっぱいに描画
            if x == 2 and y == 2:
                cx = x * CELL_SIZE
                cy = (y + VISIBLE_TOP_MARGIN) * CELL_SIZE
                margin = int(CELL_SIZE * 0.18)
                pygame.draw.line(
                    screen, (255, 0, 0),
                    (cx + margin, cy + margin),
                    (cx + CELL_SIZE - margin, cy + CELL_SIZE - margin),
                    width=max(2, CELL_SIZE // 8)
                )
                pygame.draw.line(
                    screen, (255, 0, 0),
                    (cx + CELL_SIZE - margin, cy + margin),
                    (cx + margin, cy + CELL_SIZE - margin),
                    width=max(2, CELL_SIZE // 8)
                )
                continue
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

def draw_status(screen, field, is_ai_mode):
    # スコアと連鎖数をフィールド下部に2行で表示＋モード表示（CHAINの下に）
    font = pygame.font.SysFont(None, 32)
    score = field.get_score()
    chain = field.get_current_chain_size()
    score_label = font.render(f"SCORE: {score}", True, (255, 255, 255))
    chain_label = font.render(f"CHAIN: {chain}", True, (255, 255, 255))
    mode_label = font.render(f"MODE: {'AI' if is_ai_mode else 'PLAYER'}", True, (255, 255, 0))
    base_x = 16
    base_y = (FIELD_HEIGHT + VISIBLE_TOP_MARGIN) * CELL_SIZE + 16
    screen.blit(score_label, (base_x, base_y))
    screen.blit(chain_label, (base_x, base_y + 36))
    screen.blit(mode_label, (base_x, base_y + 72))

def draw(screen, field, is_ai_mode, targets=None):
    screen.fill((0, 0, 0))
    draw_funcs = {
        "field": lambda: draw_field(screen, field),
        "active_tsumo": lambda: draw_active_tsumo(screen, field),
        "nexts": lambda: draw_nexts(screen, field),
        "status": lambda: draw_status(screen, field, is_ai_mode),
    }
    if targets is None:
        for func in draw_funcs.values():
            func()
    else:
        for key in targets:
            if key in draw_funcs:
                draw_funcs[key]()
    pygame.display.flip()

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

    # ランダムAIのインスタンス生成
    ai = puyo_core.AI.create(puyo_core.AIType.RANDOM)
    is_ai_mode = False
    running = True
    while running:
        drop_flag = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    is_ai_mode = not is_ai_mode  # モード切替
                if not is_ai_mode:
                    if event.key == pygame.K_a:
                        field.move_active_tsumo_left()
                    elif event.key == pygame.K_d:
                        field.move_active_tsumo_right()
                    elif event.key == pygame.K_w:
                        drop_flag = field.can_place(field.get_active_tsumo().x, field.get_active_tsumo().rotation)
                    elif event.key == pygame.K_DOWN:
                        field.rotate_active_tsumo_left()
                    elif event.key == pygame.K_RIGHT:
                        field.rotate_active_tsumo_right()
        # AIモードの自動操作
        if is_ai_mode:
            move = ai.decide(field)
            # rotation: 0=上, 1=右, 2=下, 3=左
            for _ in range(move.rotation):
                field.rotate_active_tsumo_right()
                draw(screen, field, is_ai_mode)
                pygame.time.wait(100)
            # x座標を合わせる（最大FIELD_WIDTH回まで）
            max_move = FIELD_WIDTH
            move_count = 0
            while field.get_active_tsumo().x < move.target_x and move_count < max_move:
                field.move_active_tsumo_right()
                move_count += 1
                draw(screen, field, is_ai_mode)
                pygame.time.wait(100)
            while field.get_active_tsumo().x > move.target_x and move_count < max_move:
                field.move_active_tsumo_left()
                move_count += 1
                draw(screen, field, is_ai_mode)
                pygame.time.wait(100)
            drop_flag = True
        # 落下処理
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
                draw(screen, field, is_ai_mode, targets=["field", "nexts", "status"])
                pygame.time.wait(800)
            field.generate_next_tsumo()  # 操作ぷよ・ネクスト・ネクネクをC++側で更新
        # 連鎖が終了したら field の連鎖数をリセット
        field.set_current_chain_size(0)
        draw(screen, field, is_ai_mode)
        # 窒息判定
        if field.is_game_over():
            # シンプルなゲームオーバー画面を3行で表示
            font = pygame.font.SysFont(None, 36)
            messages = ["GAME OVER!", "R: Retry", "Q: Quit"]
            screen.fill((0, 0, 0))
            total_height = sum(font.size(msg)[1] for msg in messages) + 16  # 行間8px
            start_y = SCREEN_HEIGHT // 2 - total_height // 2
            for i, msg in enumerate(messages):
                text_surface = font.render(msg, True, (255, 0, 0))
                x = (SCREEN_WIDTH + 80) // 2 - text_surface.get_width() // 2
                y = start_y + i * (font.get_height() + 8)
                screen.blit(text_surface, (x, y))
            pygame.display.flip()
            waiting_for_retry = True
            while waiting_for_retry:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting_for_retry = False
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            field = puyo_core.Field(FIELD_HEIGHT, FIELD_WIDTH)
                            field.generate_next_tsumo()
                            field.generate_next_tsumo()  # 操作ぷよをセット
                            waiting_for_retry = False
                            is_ai_mode = False
                        elif event.key == pygame.K_q:
                            waiting_for_retry = False
                            running = False
        clock.tick(FPS)
    pygame.quit()

if __name__ == '__main__':
    main()
