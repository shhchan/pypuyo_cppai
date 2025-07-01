#pragma once
#include "Field.hpp"

namespace puyo {
    struct AIContext {
        const Field& field;
        // 今後必要な情報があればここに追加
        // 例: int turn; std::vector<int> opponent_scores; など
        AIContext(const Field& f) : field(f) {}
    };
}
