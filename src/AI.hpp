#pragma once

#include <utility>
#include <vector>
#include <array>
#include <cstdint>
#include "Field.hpp"
#include "AIContext.hpp"

namespace puyo {
	struct Move {
		int target_x;
		int rotation;
	};

	enum class AIType {
		Random,
		InitRuleBase,
	};

	class AI {
	public:
		static AI* create(AIType type);
		virtual ~AI() = default;
		virtual Move decide(const AIContext& ctx) = 0;
		// 配置可能なMoveのリストを返す
		virtual std::vector<Move> is_valid_move(const Field& field) const;
	protected:
		// 配置可能かどうか判定
		virtual bool can_place(const Field& field, int x, int r) const;
	};
}