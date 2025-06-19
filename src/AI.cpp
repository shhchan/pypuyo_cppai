#include "AI.hpp"
#include <cstdlib>

namespace puyo {
	class RandomAI : public AI {
	public:
		Move decide(const Field& field) override {
			int w = field.get_width();
			// 0 から w-1 のランダム
			int x = std::rand() % w;
			int r = std::rand() % 4; // 0 から 3 のランダム（回転数）

			return { x, r };
		}
	};

	AI* create_random_AI() {
		return new RandomAI();
	}
}