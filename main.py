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
except Exception as e:
    print(e)
    sys.exit(1)
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
            # 窒息点(3列目12段目, x=2, y=2)に赤いバツ印をセルいっぱいに描画
            if x == 2 and y == 2:
                cx = int(x * VIRTUAL_CELL_SIZE * scale) + ox
                cy = int((y + VISIBLE_TOP_MARGIN) * VIRTUAL_CELL_SIZE * scale) + oy
                cell_size = int(VIRTUAL_CELL_SIZE * scale)
                margin = int(cell_size * 0.18)
                pygame.draw.line(
                    screen, (255/3*2, 0, 0),
                    (cx + margin, cy + margin),
                    (cx + cell_size - margin, cy + cell_size - margin),
                    width=max(2, cell_size // 8)
                )
                pygame.draw.line(
                    screen, (255/3*2, 0, 0),
                    (cx + cell_size - margin, cy + margin),
                    (cx + margin, cy + cell_size - margin),
                    width=max(2, cell_size // 8)
                )
                continue

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

def draw_status(screen, field, ai_mode_idx, scale, ox, oy):
    # スコアと連鎖数をフィールド下部に2行で表示＋モード表示（AI名も表示）
    font = pygame.font.SysFont(None, int(32 * scale))
    score = field.get_score()
    chain = field.get_current_chain_size()
    score_label = font.render(f"SCORE: {score}", True, (255, 255, 255))
    chain_label = font.render(f"CHAIN: {chain}", True, (255, 255, 255))
    mode_name = AI_MODES[ai_mode_idx][0]
    mode_label = font.render(f"MODE: {mode_name}", True, (255, 255, 0))
    base_x = ox + int(16 * scale)
    base_y = oy + int((FIELD_HEIGHT + VISIBLE_TOP_MARGIN) * VIRTUAL_CELL_SIZE * scale) + int(16 * scale)
    screen.blit(score_label, (base_x, base_y))
    screen.blit(chain_label, (base_x, base_y + int(36 * scale)))
    screen.blit(mode_label, (base_x, base_y + int(72 * scale)))

def draw(screen, field, is_ai_mode, ai_mode_idx=0, targets=None):
    win_size = screen.get_size()
    scale, ox, oy = get_scale_and_offset(win_size)
    screen.fill((0, 0, 0))
    draw_funcs = {
        "field": lambda: draw_field(screen, field, scale, ox, oy),
        "active_tsumo": lambda: draw_active_tsumo(screen, field, scale, ox, oy),
        "nexts": lambda: draw_nexts(screen, field, scale, ox, oy),
        "status": lambda: draw_status(screen, field, ai_mode_idx, scale, ox, oy),
    }
    if targets is None:
        for func in draw_funcs.values():
            func()
    else:
        for key in targets:
            if key in draw_funcs:
                draw_funcs[key]()
    pygame.display.flip()

AI_MODES = [
    ("PLAYER", None),
    ("RANDOM AI", lambda: puyo_core.AI.create(puyo_core.AIType.RANDOM)),
    ("INIT RULE BASE AI", lambda: puyo_core.AI.create(puyo_core.AIType.INIT_RULE_BASE)),
]

# モード選択UI描画
# フィールドを半透明で重ねて表示

def draw_mode_select(screen, selected_idx, field=None, is_ai_mode=False):
    # まずフィールドを描画（サーフェスに描画してから半透明化）
    if field is not None:
        # 1回だけ暗くする（毎回新しいsurfaceを作る）
        field_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        draw(field_surface, field, is_ai_mode, selected_idx)
        # 半透明化（アルファ値180/255）
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0,0,0,75))  # 薄暗くする
        field_surface.blit(overlay, (0,0))
        screen.blit(field_surface, (0,0))
    else:
        screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 28)
    win_size = screen.get_size()
    title = font.render("Select Mode", True, (255,255,0))
    screen.blit(title, (win_size[0]//2 - title.get_width()//2, 80))
    for i, (name, _) in enumerate(AI_MODES):
        color = (255,255,255) if i != selected_idx else (0,255,0)
        label = font.render(name, True, color)
        x = win_size[0]//2 - label.get_width()//2
        y = 180 + i*70
        screen.blit(label, (x, y))
        # 選択中の行だけ矢印を表示
        if i == selected_idx:
            marker = small_font.render("-->", True, (0,255,0))
            screen.blit(marker, (x - 60, y + 10))
    info = small_font.render("Tab: Next  Enter: Select", True, (200,200,200))
    screen.blit(info, (win_size[0]//2 - info.get_width()//2, 180 + len(AI_MODES)*70 + 20))
    pygame.display.flip()

def main():
    pygame.init()
    # デフォルトウィンドウサイズを大きめに
    default_size = (int(VIRTUAL_SCREEN_WIDTH * 1.5), int(VIRTUAL_SCREEN_HEIGHT * 1.5))
    screen = pygame.display.set_mode(default_size, pygame.RESIZABLE)
    pygame.display.set_caption('PuyoPuyo')
    clock = pygame.time.Clock()
    field = puyo_core.Field(FIELD_HEIGHT, FIELD_WIDTH)
    field.generate_next_tsumo()
    field.generate_next_tsumo()

    # --- ここからAIインスタンス管理の改修 ---
    ai_instances = [None] * len(AI_MODES)
    ai_mode_idx = 0  # 0: player, 1: random, 2: init rule base
    is_ai_mode = False
    running = True
    mode_selecting = False
    selected_mode_idx = 0
    # --- ここまで ---

    while running:
        drop_flag = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if mode_selecting:
                    if event.key == pygame.K_TAB:
                        selected_mode_idx = (selected_mode_idx + 1) % len(AI_MODES)
                        draw_mode_select(screen, selected_mode_idx, field, is_ai_mode)
                    elif event.key == pygame.K_RETURN:
                        ai_mode_idx = selected_mode_idx
                        is_ai_mode = ai_mode_idx != 0
                        mode_selecting = False
                        if ai_mode_idx != 0 and ai_instances[ai_mode_idx] is None:
                            ai_instances[ai_mode_idx] = AI_MODES[ai_mode_idx][1]()
                        draw(screen, field, is_ai_mode, ai_mode_idx)
                else:
                    if event.key == pygame.K_TAB:
                        mode_selecting = True
                        selected_mode_idx = ai_mode_idx
                        draw_mode_select(screen, selected_mode_idx, field, is_ai_mode)
                        continue
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
        if mode_selecting:
            pygame.time.wait(30)
            continue
        if is_ai_mode:
            ai = ai_instances[ai_mode_idx]
            move = ai.decide(field)
            for _ in range(move.rotation):
                field.rotate_active_tsumo_right()
                draw(screen, field, is_ai_mode, ai_mode_idx)
                pygame.time.wait(100)
            max_move = FIELD_WIDTH
            move_count = 0
            while field.get_active_tsumo().x < move.target_x and move_count < max_move:
                field.move_active_tsumo_right()
                move_count += 1
                draw(screen, field, is_ai_mode, ai_mode_idx)
                pygame.time.wait(100)
            while field.get_active_tsumo().x > move.target_x and move_count < max_move:
                field.move_active_tsumo_left()
                move_count += 1
                draw(screen, field, is_ai_mode, ai_mode_idx)
                pygame.time.wait(100)
            drop_flag = True
        if drop_flag:
            field.drop_active_tsumo()
            chain_count = 0
            while True:
                chain_info = field.analyze_and_erase_chains(chain_count)
                if not getattr(chain_info, 'erased', False):
                    break
                chain_count += 1
                field.set_current_chain_size(chain_count)
                field.update_score(chain_info)
                field.apply_gravity()
                draw(screen, field, is_ai_mode, ai_mode_idx, targets=["field", "nexts", "status"])
                pygame.time.wait(800)
            field.generate_next_tsumo()
        field.set_current_chain_size(0)
        draw(screen, field, is_ai_mode, ai_mode_idx)
        if field.is_game_over():
            # 背景にフィールドを半透明で描画
            field_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            draw(field_surface, field, is_ai_mode, ai_mode_idx)
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0,0,0,120))  # ゲームオーバー時はやや濃いめ
            field_surface.blit(overlay, (0,0))
            screen.blit(field_surface, (0,0))
            font = pygame.font.SysFont(None, 36)
            messages = ["GAME OVER!", "R: Retry", "Q: Quit"]
            win_size = screen.get_size()
            scale, ox, oy = get_scale_and_offset(win_size)
            total_height = sum(font.size(msg)[1] for msg in messages) + 16
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
                            field.generate_next_tsumo()
                            waiting_for_retry = False
                            is_ai_mode = False
                            ai_mode_idx = 0
                        elif event.key == pygame.K_q:
                            waiting_for_retry = False
                            running = False
        clock.tick(FPS)
    pygame.quit()

if __name__ == '__main__':
    main()
