#include "InitRuleBaseAI.hpp"
#include "CellType.hpp"
#include "ChainInfo.hpp"
#include <iostream>

namespace puyo {
    // 評価関数: 連結数・連鎖数でスコアを決定
    int evaluate_field(const Field& field) {
        // 連鎖情報を取得
        Field tmp = field;
        ChainInfo info = tmp.analyze_and_erase_chains();
        int score = 0;
        // 連鎖が発生していれば高スコア
        if (info.chain_count > 1) score += 10000 * info.chain_count;
        // 連結数（消えたぷよ数）も加点
        score += 100 * info.total_erased;
        // 盤面の連結グループ数も加点
        for (int sz : info.group_sizes) {
            if (sz >= 4) score += sz * 10;
        }
        // TODO: 今の実装だとすべて左にぷよが積まれてしまうので，改善が必要
        return score;
    }

    Move InitRuleBaseAI::decide(const AIContext& ctx) {
        auto moves = is_valid_move(ctx.field);
        auto active_tsumo = ctx.field.get_active_tsumo();
        auto next_tsumos = ctx.field.get_next_tsumos();

        int best_score = -1e9;
        Move best_move = moves[0];
        for (const auto& move1 : moves) {
            Field f1 = ctx.field;
            // 1手目をセット
            f1.set_active_tsumo(active_tsumo.center, active_tsumo.sub, move1.target_x, 0, 0, -1, move1.rotation);
            f1.drop_active_tsumo();
            f1.apply_gravity();
            f1.analyze_and_erase_chains();

            // 2手目候補
            std::vector<Move> moves2 = is_valid_move(f1);
            for (const auto& move2 : moves2) {
                Field f2 = f1;
                f2.set_active_tsumo(next_tsumos[0].first, next_tsumos[0].second, move2.target_x, 0, 0, -1, move2.rotation);
                f2.drop_active_tsumo();
                f2.apply_gravity();
                f2.analyze_and_erase_chains();

                // 3手目候補
                std::vector<Move> moves3 = is_valid_move(f2);
                for (const auto& move3 : moves3) {
                    Field f3 = f2;
                    f3.set_active_tsumo(next_tsumos[1].first, next_tsumos[1].second, move3.target_x, 0, 0, -1, move3.rotation);
                    f3.drop_active_tsumo();
                    f3.apply_gravity();
                    f3.analyze_and_erase_chains();

                    int score = evaluate_field(f3);
                    if (score > best_score) {
                        best_score = score;
                        best_move = move1;
                    }
                }
            }

            // debug
            std::cout << "[debug] best_move: (" << best_move.target_x << ", " << best_move.rotation << ") with score: " << best_score << std::endl;
            std::cout << "[debug] current move: (" << move1.target_x << ", " << move1.rotation << ") with score: " << evaluate_field(f1) << std::endl;
        }
        return best_move;
    }
}