#pragma once
#include "AI.hpp"
#include "AIContext.hpp"


namespace puyo {
    class InitRuleBaseAI : public AI {
    public:
        Move decide(const AIContext& context) override;
    };
}