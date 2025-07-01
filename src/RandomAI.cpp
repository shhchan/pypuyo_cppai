#include "RandomAI.hpp"
#include <iostream>

namespace puyo {
    Move RandomAI::decide(const AIContext& ctx) {
        auto moves = is_valid_move(ctx.field);
        // debug: moves の内容を表示
        std::cout << "Valid moves found: " << moves.size() << std::endl;
        std::cout << "(x, r) = ";
        for (const auto& move : moves) {
            std::cout << "(" << move.target_x << ", " << move.rotation << "), ";
        }
        std::cout << std::endl;
        // ぷよが配置できる場所がない場合はエラー
        if (moves.empty()) {
            throw std::runtime_error("No valid moves available.");
        }
        
        int idx = std::rand() % moves.size();
        return moves[idx];
    }
}