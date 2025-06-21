#pragma once

#include <vector>
#include <array>
#include "CellType.hpp"
#include "ChainInfo.hpp"

namespace puyo {
	class Field {
	public:
		Field(int h = 14, int w = 6);

		int height, width;
		std::vector<std::vector<CellType>> grid;
		std::array<std::pair<CellType, CellType>, 2> next_tsumos;
		struct ActiveTsumo {
			int x, y;
			int dx, dy;
			CellType center, sub;
		} active_tsumo;
		int score;
		int current_chain_size;
		bool game_over;

		void set_cell(int x, int y, CellType type);
		CellType get_cell(int x, int y) const;

		void set_next_tsumos(const std::pair<CellType, CellType>&, const std::pair<CellType, CellType>&);
		void set_active_tsumo(CellType center, CellType sub, int x = 2, int y = -1, int dx = 0, int dy = -1);
		void move_active_tsumo_left();
		void move_active_tsumo_right();
		void rotate_active_tsumo_left();
		void rotate_active_tsumo_right();
		void drop_active_tsumo();

		std::pair<std::pair<int, int>, std::pair<int, int>> get_ghost_position() const;
		ChainInfo analyze_and_erase_chains(int chain_count = 1);
		void apply_gravity();

		int calculate_score(const ChainInfo&);
		void update_score(const ChainInfo&);
		int get_score() const;
		int get_current_chain_size() const;
		void set_current_chain_size(int);
		void draw(bool should_show_ghost = true) const;
		void generate_next_tsumo();

		int get_height() const;
		int get_width() const;
		CellType get_grid_cell(int x, int y) const;
		ActiveTsumo get_active_tsumo() const;
		std::array<std::pair<CellType, CellType>, 2> get_next_tsumos() const;

		// 追加: ぷよ配置可能判定
		bool can_place(int x, int r) const;

	private:
		std::pair<CellType, CellType> generate_random_tsumo();
		int get_chain_bonus(int);
		int get_link_bonus(int);
		int get_color_bonus(int);
	};
}