#include "Field.hpp"
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <cstdint>
//#include "Cell.hpp"

namespace puyo {
	Field::Field(int h, int w) :
		height(h),
		width(w),
		grid(h, std::vector<CellType>(w, CellType::EMPTY)),
		next_tsumos{
			std::make_pair(CellType::EMPTY, CellType::EMPTY),
			std::make_pair(CellType::EMPTY, CellType::EMPTY)
		},
		active_tsumo{ 2, -1, 0, -1, 0, CellType::EMPTY, CellType::EMPTY },
		score(0),
		current_chain_size(0),
		game_over(false) {
		std::srand(static_cast<unsigned>(std::time(nullptr)));
	}


	void Field::set_cell(int x, int y, CellType type) {
		if (y >= 0 && y < height && x >= 0 && x < width) {
			grid[y][x] = type;
		}
	}

	CellType Field::get_cell(int x, int y) const {
		if (y >= 0 && y < height && x >= 0 && x < width) {
			return grid[y][x];
		}
		else {
			return CellType::WALL; // Out of bounds returns WALL
		}
	}

	void Field::set_next_tsumos(const std::pair<CellType, CellType>& next1, const std::pair<CellType, CellType>& next2) {
		next_tsumos[0] = next1;
		next_tsumos[1] = next2;
	}

	void Field::set_active_tsumo(CellType center, CellType sub, int x, int y, int dx, int dy, int rotation) {
		active_tsumo = { x, y, dx, dy, rotation, center, sub };
	}

	void Field::move_active_tsumo_left(void) {
		if (active_tsumo.x != 0 && active_tsumo.x + active_tsumo.dx != 0) {
			active_tsumo.x--;
		}
	}

	void Field::move_active_tsumo_right(void) {
		if (active_tsumo.x != width - 1 && active_tsumo.x + active_tsumo.dx != width - 1) {
			active_tsumo.x++;
		}
	}

	void Field::rotate_active_tsumo_left(void) {
		active_tsumo.rotation = (active_tsumo.rotation + 3) % 4;
		// up --> left
		if (active_tsumo.dy == -1) {
			active_tsumo.dy = 0;
			active_tsumo.dx = -1;
			if (active_tsumo.x == 0) {
				active_tsumo.x++;
			}
		}
		// left --> down
		else if (active_tsumo.dx == -1) {
			active_tsumo.dx = 0;
			active_tsumo.dy = 1;
			// The emulator displays the active tsumo at the top, so the center always moves up one position.
			active_tsumo.y--;  
		}
		// down --> right
		else if (active_tsumo.dy == 1) {
			active_tsumo.dy = 0;
			active_tsumo.dx = 1;
			// The emulator displays the active tsumo at the top, so the center always moves down one position.
			active_tsumo.y++;
			if (active_tsumo.x == width - 1) {
				active_tsumo.x--;
			}
		}
		// right --> up
		else if (active_tsumo.dx == 1) {
			active_tsumo.dx = 0;
			active_tsumo.dy = -1;
		}
	}

	void Field::rotate_active_tsumo_right(void) {
		active_tsumo.rotation = (active_tsumo.rotation + 1) % 4;
		// up --> right
		if (active_tsumo.dy == -1) {
			active_tsumo.dy = 0;
			active_tsumo.dx = 1;
			if (active_tsumo.x == width - 1) {
				active_tsumo.x--;
			}
		}
		// right --> down
		else if (active_tsumo.dx == 1) {
			active_tsumo.dx = 0;
			active_tsumo.dy = 1;
			// The emulator displays the active tsumo at the top, so the center always moves up one position.
			active_tsumo.y--;
		}
		// down --> left
		else if (active_tsumo.dy == 1) {
			active_tsumo.dy = 0;
			active_tsumo.dx = -1;
			// The emulator displays the active tsumo at the top, so the center always moves down one position.
			active_tsumo.y++;
			if (active_tsumo.x == 0) {
				active_tsumo.x++;
			}
		}
		// left --> up
		else if (active_tsumo.dx == -1) {
			active_tsumo.dx = 0;
			active_tsumo.dy = -1;
		}
	}

	void Field::drop_active_tsumo(void) {
		int cx = active_tsumo.x;
		int sx = active_tsumo.x + active_tsumo.dx;
		int cy = 0;
		int sy = 0;

		// Case when the center is above sub
		if (active_tsumo.dy == 1) {
			// For sub
			bool can_fall_sub = false;
			for (int y = 0; y < height; y++) {
				if (get_cell(sx, y + 1) == CellType::EMPTY) {
					sy++;
				}
				else {
					can_fall_sub = get_cell(sx, y) == CellType::EMPTY;
					break;
				}
			}
			// Set sub temporarily
			CellType original_cell_for_sub = get_cell(sx, sy);
			if (can_fall_sub) {
				set_cell(sx, sy, active_tsumo.sub);
			}

			// For center
			bool can_fall_center = false;
			for (int y = 0; y < height; y++) {
				if (get_cell(cx, y + 1) == CellType::EMPTY) {
					cy++;
				}
				else {
					can_fall_center = get_cell(cx, y) == CellType::EMPTY;
					break;
				}
			}
			// If either one cannot drop, restore the grid
			if (!can_fall_center || !can_fall_sub) {
				set_cell(sx, sy, original_cell_for_sub);
			}
			// Else. set center
			else {
				set_cell(cx, cy, active_tsumo.center);
			}
		}

		// Case when the center is at the same position as or below sub
		else {
			// For center
			bool can_fall_center = false;
			for (int y = 0; y < height; y++) {
				if (get_cell(cx, y + 1) == CellType::EMPTY) {
					cy++;
				}
				else {
					can_fall_center = get_cell(cx, y) == CellType::EMPTY;
					break;
				}
			}
			// Set center temporarily
			CellType original_cell_for_center = get_cell(cx, cy);
			if (can_fall_center) {
				set_cell(cx, cy, active_tsumo.center);
			}

			// For sub
			bool can_fall_sub = false;
			for (int y = 0; y < height; y++) {
				if (get_cell(sx, y + 1) == CellType::EMPTY) {
					sy++;
				}
				else {
					can_fall_sub = get_cell(sx, y) == CellType::EMPTY;
					break;
				}
			}
			// If either one cannot drop, restore the grid
			if (!can_fall_center || !can_fall_sub) {
				set_cell(cx, cy, original_cell_for_center);
			}
			// Else, set sub
			else {
				set_cell(sx, sy, active_tsumo.sub);
			}
		}
	}

	int Field::get_height() const {
		return height;
	}

	int Field::get_width() const {
		return width;
	}

	CellType Field::get_grid_cell(int x, int y) const {
		return get_cell(x, y);
	}

	Field::ActiveTsumo Field::get_active_tsumo() const {
		return active_tsumo;
	}

	std::pair<CellType, CellType> Field::generate_random_tsumo(void) {
		const CellType types[] = {
			CellType::RED, CellType::GREEN, CellType::YELLOW, CellType::BLUE
		};

		return std::make_pair(types[rand() % 4], types[rand() % 4]);
	}

	void Field::generate_next_tsumo(void) {
		// next --> active_tsumo
		set_active_tsumo(next_tsumos[0].first, next_tsumos[0].second);
		// nextnext --> next, new tsumo --> nextnext
		set_next_tsumos(next_tsumos[1], generate_random_tsumo());
	}

	std::pair<std::pair<int, int>, std::pair<int, int>> Field::get_ghost_position() const {
		int cx = active_tsumo.x;
		int sx = active_tsumo.x + active_tsumo.dx;
		int cy = 0;
		int sy = 0;

		// コピーしたグリッドでシミュレートする
		std::vector<std::vector<CellType>> temp_grid = grid;

		// center が sub より上にある場合（dy == 1）
		if (active_tsumo.dy == 1) {
			// sub を落とす
			while (sy + 1 < height && temp_grid[sy + 1][sx] == CellType::EMPTY) {
				sy++;
			}
			// 仮に sub を置く
			temp_grid[sy][sx] = active_tsumo.sub;

			// center を落とす
			while (cy + 1 < height && temp_grid[cy + 1][cx] == CellType::EMPTY) {
				cy++;
			}
		}
		// center が sub と同じ高さまたは下にある
		else {
			// center を落とす
			while (cy + 1 < height && temp_grid[cy + 1][cx] == CellType::EMPTY) {
				cy++;
			}
			// 仮に center を置く
			temp_grid[cy][cx] = active_tsumo.center;

			// sub を落とす
			while (sy + 1 < height && temp_grid[sy + 1][sx] == CellType::EMPTY) {
				sy++;
			}
		}

		return { {cx, cy}, {sx, sy} };
	}

	ChainInfo Field::analyze_and_erase_chains(int chain_count) {
		ChainInfo chain_info;

		bool erased = false;
		std::vector<std::vector<bool>> visited(height, std::vector<bool>(width, false));

		const int dx[4] = { 1, 0, -1, 0 };
		const int dy[4] = { 0, 1, 0, -1 };

		for (int y = 0; y < height; y++) {
			for (int x = 0; x < width; x++) {
				// 探索不要な箇所はスキップ
				if (visited[y][x] || grid[y][x] == CellType::EMPTY || grid[y][x] == CellType::GARBAGE) {
					continue;
				}

				CellType target_type = grid[y][x];
				std::vector<std::pair<int, int>> connected;
				std::vector<std::pair<int, int>> stack = { {x, y} };
				std::vector<std::pair<int, int>> garbages;
				visited[y][x] = true;

				while (!stack.empty()) {
					std::pair<int, int> cell = stack.back(); 
					stack.pop_back(); 
					int cx = cell.first; 
					int cy = cell.second;
					connected.push_back({ cx, cy });

					for (int dir = 0; dir < 4; dir++) {
						int nx = cx + dx[dir];
						int ny = cy + dy[dir];
						// 通常のぷよ
						if (nx >= 0 && nx < width && ny >= 0 && ny < height
							&& !visited[ny][nx] && grid[ny][nx] == target_type) {
							visited[ny][nx] = true;
							stack.emplace_back(nx, ny);
						}
						// おじゃまぷよ
						else if (nx >= 0 && nx < width && ny >= 0 && ny < height
							&& !visited[ny][nx] && grid[ny][nx] == CellType::GARBAGE) {
							visited[ny][nx] = true;
							garbages.push_back({ nx, ny });
						}
					}
				}

				if (connected.size() >= 4) {
					for (std::pair<int, int> erasable_cell : connected) {
						grid[erasable_cell.second][erasable_cell.first] = CellType::EMPTY;
					}
					for (std::pair<int, int> erasable_cell : garbages) {
						grid[erasable_cell.second][erasable_cell.first] = CellType::EMPTY;
					}

					// 連鎖の情報を格納
					chain_info.group_sizes.push_back(connected.size());
					chain_info.colors.insert(target_type);
					chain_info.total_erased += connected.size();

					erased = true;
				}
			}
		}

		chain_info.erased = erased;

		chain_info.chain_count = chain_info.erased ? chain_count + 1 : chain_count;

		return chain_info;
	}

	void Field::apply_gravity(void) {
		for (int x = 0; x < width; x++) {
			int write_y = height - 1;
			for (int y = height - 1; y >= 1; y--) {
				if (grid[y][x] != CellType::EMPTY) {
					grid[write_y][x] = grid[y][x];
					if (write_y != y) {
						grid[y][x] = CellType::EMPTY;
					}
					write_y--;
				}
			}
		}
	}

	int Field::get_chain_bonus(int chain) {
		static const int chain_bonuses[] = {
			0, 8, 16, 32, 64, 96, 128, 160,
			192, 224, 256, 288, 320, 352, 384, 416, 448, 480, 512
		};

		return chain <= 0 ? 0 : chain <= 19 ? chain_bonuses[chain - 1] : 512;
	}

	int Field::get_link_bonus(int size) {
		if (size < 5) return 0;
		if (size == 5) return 2;
		if (size == 6) return 3;
		if (size == 7) return 4;
		if (size == 8) return 5;
		if (size == 9) return 6;
		if (size == 10) return 7;
		return 10;  // size >= 11
	}

	int Field::get_color_bonus(int color_count) {
		switch (color_count) {
			case 1: return 0;
			case 2: return 3;
			case 3: return 6;
			case 4: return 12;
			case 5: return 24;
			default: return 0;
		}
	}

	int Field::calculate_score(const ChainInfo& chain_info) {
		int chain_bonus = get_chain_bonus(chain_info.chain_count);
		int link_bonus = 0;
		for (int size : chain_info.group_sizes) {
			link_bonus += get_link_bonus(size);
		}
		int color_bonus = get_color_bonus(chain_info.colors.size());

		int bonus = chain_bonus + link_bonus + color_bonus;
		if (bonus == 0) {
			bonus = 1;
		}

		return chain_info.total_erased * bonus * 10;
	}

	void Field::update_score(const ChainInfo& chain_info) {
		score += calculate_score(chain_info);
	}

	// score の getter
	int Field::get_score() const {
		return score;
	}
	// current_chain_size の getter
	int Field::get_current_chain_size() const {
		return current_chain_size;
	}

	void Field::set_current_chain_size(int chain_count) {
		current_chain_size = chain_count;
	}

	// next_tsumosのgetter
	std::array<std::pair<CellType, CellType>, 2> Field::get_next_tsumos() const {
		return next_tsumos;
	}

	bool Field::can_place(int x, int r) const {
		// ぷよの高さ情報を取得
		uint8_t heights[6] = {};
		for (int i = 0; i < 6; ++i) {
			heights[i] = 0;
			for (int y = get_height() - 1; y > 0; --y) {
				if (static_cast<int>(get_cell(i, y)) != 0) heights[i] = get_height() - y;
			}
		}
		// 14段目の情報（bit列）
		uint8_t row14 = 0;
		for (int i = 0; i < 6; ++i) {
			if (heights[i] == 14) row14 |= (1 << i);
		}
		// 回転方向のオフセット
		static const int dx[4] = {0, 1, 0, -1}; // UP, RIGHT, DOWN, LEFT
		static const int dy[4] = {-1, 0, 1, 0};
		// 0:UP, 1:RIGHT, 2:DOWN, 3:LEFT
		int dir = r;
		// 軸ぷよが14段目
		if (heights[x] + (dir == 2) > 12) return false;
		int child_x = x + dx[dir];
		if (child_x < 0 || child_x >= 6) return false;
		int child_y = heights[child_x] + (dir == 0);
		if (child_y == 13 && ((row14 >> child_x) & 1)) return false;
		// チェックリスト
		static const int check[6][4] = {
			{1, 0, -1, -1}, {1, -1, -1, -1}, {-1, -1, -1, -1}, {3, -1, -1, -1}, {3, 4, -1, -1}, {3, 4, 5, -1}
		};
		static const int check_12[6][6] = {
			{1, 2, 3, 4, 5, -1}, {2, 3, 4, 5, -1, -1}, {-1, -1, -1, -1, -1, -1}, {2, 1, 0, -1, -1, -1}, {3, 2, 1, 0, -1, -1}, {4, 3, 2, 1, 0, -1}
		};
		int check_x = x;
		if (dir == 1 && x >= 2) check_x += 1;
		else if (dir == 3 && x <= 2) check_x -= 1;
		int height_12_idx = -1;
		for (int i = 0; check[check_x][i] != -1; ++i) {
			if (heights[check[check_x][i]] > 12) return false;
			if (heights[check[check_x][i]] == 12 && height_12_idx == -1) height_12_idx = check[check_x][i];
		}
		if (height_12_idx == -1) return true;
		if (heights[1] > 11 && heights[3] > 11) return true;
		for (int i = 0; check_12[height_12_idx][i] != -1; ++i) {
			if (heights[check_12[height_12_idx][i]] > 11) break;
			if (heights[check_12[height_12_idx][i]] == 11) return true;
		}
		return false;
	}

/* 	void Field::draw(bool should_show_ghost) const {
		// Calc ghost
		auto ghost = get_ghost_position();
		int gcx = ghost.first.first;
		int gcy = ghost.first.second;
		int gsx = ghost.second.first;
		int gsy = ghost.second.second;

		// Draw active tsumo
		for (int y = -2; y < 0; y++) {
			// Draw left space
			Cell(CellType::EMPTY).draw();
			for (int x = 0; x < width; x++) {
				if (x == active_tsumo.x && y == active_tsumo.y) {
					Cell(active_tsumo.center).draw();
				}
				else if (x == active_tsumo.x + active_tsumo.dx && y == active_tsumo.y + active_tsumo.dy) {
					Cell(active_tsumo.sub).draw();
				}
				else {
					Cell(CellType::EMPTY).draw();
				}
			}
			// Draw right space
			Cell(CellType::EMPTY).draw();
			std::cout << std::endl;
		}

		// Draw field
		for (int y = 0; y < height; y++) {
			// Draw left WALL
			if (y >= 1) {
				Cell(CellType::WALL).draw();
			}
			else {
				Cell(CellType::EMPTY).draw();
			}
			
			// Draw grid
			for (int x = 0; x < width; x++) {
				// Draw if ghost exists
				if (should_show_ghost && x == gcx && y == gcy) {
					Cell(active_tsumo.center).draw(true);
				}
				else if (should_show_ghost && x == gsx && y == gsy) {
					Cell(active_tsumo.sub).draw(true);
				}
				else {
					Cell(grid[y][x]).draw();
				}
			}

			// Draw right WALL
			if (y >= 1) {
				Cell(CellType::WALL).draw();
			}

			// Draw next tsumos
			if (y == 1) {
				Cell(next_tsumos[0].second).draw();
			}
			else if (y == 2) {
				Cell(next_tsumos[0].first).draw();
				Cell(next_tsumos[1].second).draw();
			}
			else if (y == 3) {
				Cell(CellType::EMPTY).draw();
				Cell(next_tsumos[1].first).draw();
			}

			std::cout << std::endl;
		}

		// Draw under WALL
		for (int x = 0; x < width + 2; x++) {
			Cell(CellType::WALL).draw();
		}

		// Draw score
		std::cout << "\n" << std::setfill('0') << std::setw(8) << score << std::endl;
		std::cout << current_chain_size << "連鎖" << std::endl;
	} */
}
