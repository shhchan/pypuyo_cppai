#include "AI.hpp"
#include "RandomAI.hpp"
#include "InitRuleBaseAI.hpp"
#include <vector>
#include "AIContext.hpp"

namespace puyo {
	// AI基底クラスのデフォルト実装

	AI* AI::create(AIType type) {
		switch (type) {
			case AIType::Random:
				return new RandomAI();
			case AIType::InitRuleBase:
				return new InitRuleBaseAI();
			default:
				return nullptr; // 未実装のAIタイプ
		}
	}

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
}