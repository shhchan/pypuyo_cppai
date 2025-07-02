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
VIRTUAL_CELL_SIZE = 48  # 仮想セルサイズを大きめに
FIELD_WIDTH = 6
FIELD_HEIGHT = 14
VISIBLE_TOP_MARGIN = 2  # 上部に2行分余裕を持たせて表示
STATUS_BAR_HEIGHT = VIRTUAL_CELL_SIZE * 3 * 1.5  # スコア・連鎖数・モード表示用
NEXT_AREA_WIDTH = int(VIRTUAL_CELL_SIZE * 1.5)  # ネクストエリアの幅（フィールド1列分+余白）
VIRTUAL_SCREEN_WIDTH = VIRTUAL_CELL_SIZE * FIELD_WIDTH + NEXT_AREA_WIDTH
VIRTUAL_SCREEN_HEIGHT = VIRTUAL_CELL_SIZE * (FIELD_HEIGHT + VISIBLE_TOP_MARGIN) + STATUS_BAR_HEIGHT
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

def get_scale_and_offset(window_size):
    win_w, win_h = window_size
    scale_x = win_w / VIRTUAL_SCREEN_WIDTH
    scale_y = win_h / VIRTUAL_SCREEN_HEIGHT
    scale = min(scale_x, scale_y)
    # アスペクト比維持のため余白を計算
    draw_w = int(VIRTUAL_SCREEN_WIDTH * scale)
    draw_h = int(VIRTUAL_SCREEN_HEIGHT * scale)
    offset_x = (win_w - draw_w) // 2
    offset_y = (win_h - draw_h) // 2
    return scale, offset_x, offset_y

def draw_field(screen, field, scale, ox, oy):
    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            # 窒息点(3列目12段目, x=2, y=2)に赤いバツ印をセルいっぱいに描画
            if x == 2 and y == 2:
                cx = int(x * VIRTUAL_CELL_SIZE * scale) + ox
                cy = int((y + VISIBLE_TOP_MARGIN) * VIRTUAL_CELL_SIZE * scale) + oy
                cell_size = int(VIRTUAL_CELL_SIZE * scale)
                margin = int(cell_size * 0.18)
                pygame.draw.line(
                    screen, (255, 0, 0),
                    (cx + margin, cy + margin),
                    (cx + cell_size - margin, cy + cell_size - margin),
                    width=max(2, cell_size // 8)
                )
                pygame.draw.line(
                    screen, (255, 0, 0),
                    (cx + cell_size - margin, cy + margin),
                    (cx + margin, cy + cell_size - margin),
                    width=max(2, cell_size // 8)
                )
                continue
            cell = field.get_cell(x, y)
            color_name = CELLTYPE_MAP.get(int(cell), None)
            if color_name:
                rect = pygame.Rect(
                    int(x * VIRTUAL_CELL_SIZE * scale) + ox,
                    int((y + VISIBLE_TOP_MARGIN) * VIRTUAL_CELL_SIZE * scale) + oy,
                    int(VIRTUAL_CELL_SIZE * scale),
                    int(VIRTUAL_CELL_SIZE * scale)
                )
                pygame.draw.rect(screen, COLOR_MAP[color_name], rect)

def draw_active_tsumo(screen, field, scale, ox, oy):
    tsumo = field.get_active_tsumo()
    # ゴースト位置の取得
    ghost = field.get_ghost_position()
    (gcx, gcy), (gsx, gsy) = ghost
    # ゴーストぷよの描画（小さい半透明四角形、セル中央）
    ghost_size = int(VIRTUAL_CELL_SIZE * 0.5 * scale)
    ghost_offset = int((VIRTUAL_CELL_SIZE * scale - ghost_size) // 2)
    for dx, dy, color, gx, gy in [
        (0, 0, tsumo.center, gcx, gcy),
        (tsumo.dx, tsumo.dy, tsumo.sub, gsx, gsy),
    ]:
        color_name = CELLTYPE_MAP.get(int(color), None)
        if color_name:
            ghost_rect = pygame.Rect(
                int(gx * VIRTUAL_CELL_SIZE * scale) + ox + ghost_offset,
                int((gy + VISIBLE_TOP_MARGIN) * VIRTUAL_CELL_SIZE * scale) + oy + ghost_offset,
                ghost_size, ghost_size
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
                rect = pygame.Rect(
                    int(x * VIRTUAL_CELL_SIZE * scale) + ox,
                    int((y + VISIBLE_TOP_MARGIN) * VIRTUAL_CELL_SIZE * scale) + oy,
                    int(VIRTUAL_CELL_SIZE * scale),
                    int(VIRTUAL_CELL_SIZE * scale)
                )
                pygame.draw.rect(screen, COLOR_MAP[color_name], rect)

def draw_nexts(screen, field, scale, ox, oy):
    # ネクスト・ネクネクをフィールド右側に描画
    nexts = field.get_next_tsumos()  # get_next_tsumos()で取得
    # フィールド本体の右端＋余白
    field_right = ox + int(FIELD_WIDTH * VIRTUAL_CELL_SIZE * scale)
    margin = int(VIRTUAL_CELL_SIZE * 0.25 * scale)
    base_x = field_right + margin
    base_y = int(VISIBLE_TOP_MARGIN * VIRTUAL_CELL_SIZE * scale) + oy + int(32 * scale)
    for i, (sub, center) in enumerate(nexts):
        # 上がcenter, 下がsubとして縦に描画
        y_offset = base_y + i * int(3 * VIRTUAL_CELL_SIZE * scale)
        for j, color in enumerate([center, sub]):
            color_name = CELLTYPE_MAP.get(int(color), None)
            if color_name:
                rect = pygame.Rect(
                    base_x,
                    y_offset + j * int(VIRTUAL_CELL_SIZE * scale),
                    int(VIRTUAL_CELL_SIZE * scale),
                    int(VIRTUAL_CELL_SIZE * scale)
                )
                pygame.draw.rect(screen, COLOR_MAP[color_name], rect)
        # ラベル
        font = pygame.font.SysFont(None, int(24 * scale))
        label = font.render("NEXT" if i == 0 else "NEXT2", True, (255,255,255))
        screen.blit(label, (base_x, y_offset - int(24 * scale)))

def draw_status(screen, field, is_ai_mode, scale, ox, oy):
    # スコアと連鎖数をフィールド下部に2行で表示＋モード表示（CHAINの下に）
    font = pygame.font.SysFont(None, int(32 * scale))
    score = field.get_score()
    chain = field.get_current_chain_size()
    score_label = font.render(f"SCORE: {score}", True, (255, 255, 255))
    chain_label = font.render(f"CHAIN: {chain}", True, (255, 255, 255))
    mode_label = font.render(f"MODE: {'AI' if is_ai_mode else 'PLAYER'}", True, (255, 255, 0))
    base_x = ox + int(16 * scale)
    base_y = oy + int((FIELD_HEIGHT + VISIBLE_TOP_MARGIN) * VIRTUAL_CELL_SIZE * scale) + int(16 * scale)
    screen.blit(score_label, (base_x, base_y))
    screen.blit(chain_label, (base_x, base_y + int(36 * scale)))
    screen.blit(mode_label, (base_x, base_y + int(72 * scale)))

def draw(screen, field, is_ai_mode, targets=None):
    win_size = screen.get_size()
    scale, ox, oy = get_scale_and_offset(win_size)
    screen.fill((0, 0, 0))
    draw_funcs = {
        "field": lambda: draw_field(screen, field, scale, ox, oy),
        "active_tsumo": lambda: draw_active_tsumo(screen, field, scale, ox, oy),
        "nexts": lambda: draw_nexts(screen, field, scale, ox, oy),
        "status": lambda: draw_status(screen, field, is_ai_mode, scale, ox, oy),
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
    # デフォルトウィンドウサイズを大きめに
    default_size = (int(VIRTUAL_SCREEN_WIDTH * 1.5), int(VIRTUAL_SCREEN_HEIGHT * 1.5))
    screen = pygame.display.set_mode(default_size, pygame.RESIZABLE)
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
            elif event.type == pygame.VIDEORESIZE:
                # ウィンドウリサイズ時に再設定
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
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
            win_size = screen.get_size()
            scale, ox, oy = get_scale_and_offset(win_size)
            total_height = sum(font.size(msg)[1] for msg in messages) + 16  # 行間8px
            start_y = win_size[1] // 2 - total_height // 2
            for i, msg in enumerate(messages):
                text_surface = font.render(msg, True, (255, 0, 0))
                x = win_size[0] // 2 - text_surface.get_width() // 2
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
