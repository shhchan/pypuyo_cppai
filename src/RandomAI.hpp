#pragma once
#include "AI.hpp"

namespace puyo {
    class RandomAI : public AI {
    public:
		Move decide(const Field& field) override;
    };
}