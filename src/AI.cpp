#include "AI.hpp"
#include <cstdlib>
#include <vector>
#include <array>
#include <stdexcept>
#include <iostream>

namespace puyo {
	// AI基底クラスのデフォルト実装
	bool AI::can_place(const Field& field, int x, int r) const {
		return field.can_place(x, r);
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