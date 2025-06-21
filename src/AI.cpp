#include "AI.hpp"
#include <cstdlib>
#include <vector>
#include <array>
#include <stdexcept>
#include <iostream>

namespace puyo {
	// AI基底クラスのデフォルト実装
	bool AI::can_place(const Field& field, int x, int r) const {
		// ぷよの高さ情報を取得
		uint8_t heights[6] = {};
		for (int i = 0; i < 6; ++i) {
			heights[i] = 0;
			for (int y = field.get_height() - 1; y > 0; --y) {
				if (static_cast<int>(field.get_cell(i, y)) != 0) heights[i] = field.get_height() - y;
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

	std::vector<Move> AI::is_valid_move(const Field& field) const {
		std::vector<Move> moves;
		int w = field.get_width();
		for (int x = 0; x < w; ++x) {
			for (int r = 0; r < 4; ++r) {
				if (can_place(field, x, r)) {
					moves.push_back({x, r});
				}
			}
		}
		return moves;
	}

	class RandomAI : public AI {
	public:
		Move decide(const Field& field) override {
			auto moves = is_valid_move(field);
			// debug: moves の内容を表示
			std::cout << "Valid moves found: " << moves.size() << std::endl;
			for (const auto& move : moves) {
				std::cout << "(x=" << move.target_x << ", r=" << move.rotation << "), ";
			}
			std::cout << std::endl;
			// ぷよが配置できる場所がない場合はエラー
			if (moves.empty()) {
				throw std::runtime_error("No valid moves available.");
			}
			int idx = std::rand() % moves.size();
			return moves[idx];
		}
	};

	AI* create_random_AI() {
		return new RandomAI();
	}
}