#pragma once
#include "AI.hpp"
#include "AIContext.hpp"

namespace puyo {
    class RandomAI : public AI {
    public:
        Move decide(const AIContext& ctx) override;
    };
}