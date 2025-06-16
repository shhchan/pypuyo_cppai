import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(script_dir, 'build')
sys.path.append(build_dir)

import puyo_core

# AIインスタンス生成
aio = puyo_core.create_random_AI()

# フィールド生成（デフォルトサイズ）
field = puyo_core.Field()

# セルをセット
field.set_cell(0, 0, puyo_core.CellType.RED)
field.set_cell(1, 0, puyo_core.CellType.GREEN)

# フィールドの状態を取得
cell = field.get_cell(0, 0)
print(f"cell(0,0): {cell}")

# AIで手を決定
decision = aio.decide(field)
print(f"AI decision: target_x={decision.target_x}, rotation={decision.rotation}")

# 連鎖解析
chain_info = field.analyze_and_erase_chains()
print(f"ChainInfo: {chain_info}")
