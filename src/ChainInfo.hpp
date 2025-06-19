#pragma once

#include <vector>
#include <set>
#include "CellType.hpp"

namespace puyo {
	struct ChainInfo {
		int chain_count;
		std::vector<int> group_sizes;
		std::set<CellType> colors;
		int total_erased;
		bool erased;

		ChainInfo() : chain_count(0), total_erased(0), erased(false) {};
	};
}