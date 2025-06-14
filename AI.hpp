#pragma once

#include <utility>
#include "Field.hpp"

namespace puyo {
	struct Move {
		int target_x;
		int rotation;
	};

	class AI {
	public:
		virtual ~AI() = default;

		virtual Move decide(const Field& field) = 0;
	};

	// ランダム配置 AI
	AI* create_random_AI();
}