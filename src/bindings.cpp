#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

// Puyo Puyo Core Library
#include "CellType.hpp"
#include "ChainInfo.hpp"
#include "Field.hpp"
#include "AI.hpp"
#include "AIContext.hpp"

namespace py = pybind11;

PYBIND11_MODULE(puyo_core, m) {
  m.doc() = "Puyto Puyo Core Library Bindings";

  // --- CellType enum ---
  py::enum_<puyo::CellType>(m, "CellType")
    .value("EMPTY", puyo::CellType::EMPTY)
    .value("WALL", puyo::CellType::WALL)
    .value("RED", puyo::CellType::RED)
    .value("GREEN", puyo::CellType::GREEN)
    .value("YELLOW", puyo::CellType::YELLOW)
    .value("BLUE", puyo::CellType::BLUE)
    .value("PURPLE", puyo::CellType::PURPLE)
    .value("GARBAGE", puyo::CellType::GARBAGE)
    .export_values();

  // --- AIType enum ---
  py::enum_<puyo::AIType>(m, "AIType")
    .value("RANDOM", puyo::AIType::Random)
    .export_values();

  // --- ChainInfo struct ---
  py::class_<puyo::ChainInfo>(m, "ChainInfo")
    .def(py::init<>())
    .def_readwrite("chain_count", &puyo::ChainInfo::chain_count)
    .def_readwrite("group_sizes", &puyo::ChainInfo::group_sizes)
    .def_readwrite("colors", &puyo::ChainInfo::colors)
    .def_readwrite("total_erased", &puyo::ChainInfo::total_erased)
    .def_readwrite("erased", &puyo::ChainInfo::erased)
    .def("__repr__", [](const puyo::ChainInfo &info) {
      std::string colors_str = "{";
      for (const auto& c : info.colors) colors_str += std::to_string(static_cast<int>(c)) + ",";
      colors_str += "}";
      std::string group_sizes_str = "[";
      for (const auto& g : info.group_sizes) group_sizes_str += std::to_string(g) + ",";
      group_sizes_str += "]";
      return "<ChainInfo chain_count=" + std::to_string(info.chain_count)
        + " group_sizes=" + group_sizes_str
        + " colors=" + colors_str
        + " total_erased=" + std::to_string(info.total_erased)
        + " erased=" + (info.erased ? "true" : "false") + ">";
    });

  // -- Field::ActiveTsumo struct ---
  py::class_<puyo::Field::ActiveTsumo>(m, "ActiveTsumo")
    .def_readonly("x", &puyo::Field::ActiveTsumo::x)
    .def_readonly("y", &puyo::Field::ActiveTsumo::y)
    .def_readonly("dx", &puyo::Field::ActiveTsumo::dx)
    .def_readonly("dy", &puyo::Field::ActiveTsumo::dy)
    .def_readonly("rotation", &puyo::Field::ActiveTsumo::rotation)
    .def_readonly("center", &puyo::Field::ActiveTsumo::center)
    .def_readonly("sub", &puyo::Field::ActiveTsumo::sub)
    .def("__repr__", [](const puyo::Field::ActiveTsumo &tsumo) {
      return "<ActiveTsumo x=" + std::to_string(tsumo.x)
        + " y=" + std::to_string(tsumo.y)
        + " dx=" + std::to_string(tsumo.dx)
        + " dy=" + std::to_string(tsumo.dy)
        + " rotation=" + std::to_string(tsumo.rotation)
        + " center=" + std::to_string(static_cast<int>(tsumo.center))
        + " sub=" + std::to_string(static_cast<int>(tsumo.sub)) + ">";
    });

  // --- Field class ---
  py::class_<puyo::Field>(m, "Field")
    .def(py::init<int, int>(), py::arg("height") = 14, py::arg("width") = 6)
    .def("set_cell", &puyo::Field::set_cell, py::arg("x"), py::arg("y"), py::arg("type"))
    .def("get_cell", &puyo::Field::get_cell, py::arg("x"), py::arg("y"))
    .def("set_next_tsumos", &puyo::Field::set_next_tsumos, py::arg("next1"), py::arg("next2"))
    .def("set_active_tsumo", &puyo::Field::set_active_tsumo, py::arg("center"), py::arg("sub"), py::arg("x") = 2, py::arg("y") = -1, py::arg("dx") = 0, py::arg("dy") = -1, py::arg("rotation") = 0)
    .def("move_active_tsumo_left", &puyo::Field::move_active_tsumo_left)
    .def("move_active_tsumo_right", &puyo::Field::move_active_tsumo_right)
    .def("rotate_active_tsumo_left", &puyo::Field::rotate_active_tsumo_left)
    .def("rotate_active_tsumo_right", &puyo::Field::rotate_active_tsumo_right)
    .def("drop_active_tsumo", &puyo::Field::drop_active_tsumo)
    .def("get_ghost_position", &puyo::Field::get_ghost_position)
    .def("analyze_and_erase_chains", &puyo::Field::analyze_and_erase_chains, py::arg("chain_count") = 1)
    .def("apply_gravity", &puyo::Field::apply_gravity)
    .def("calculate_score", &puyo::Field::calculate_score, py::arg("chain_info"))
    .def("update_score", &puyo::Field::update_score, py::arg("chain_info"))
    .def("get_score", &puyo::Field::get_score)
    .def("get_current_chain_size", &puyo::Field::get_current_chain_size)
    .def("set_current_chain_size", &puyo::Field::set_current_chain_size, py::arg("chain_count"))
    .def("generate_next_tsumo", &puyo::Field::generate_next_tsumo)
    .def("get_height", &puyo::Field::get_height)
    .def("get_width", &puyo::Field::get_width)
    .def("get_grid_cell", &puyo::Field::get_grid_cell, py::arg("x"), py::arg("y"))
    .def("get_active_tsumo", &puyo::Field::get_active_tsumo)
    .def("get_next_tsumos", &puyo::Field::get_next_tsumos)
    .def("can_place", &puyo::Field::can_place, py::arg("x"), py::arg("r"))
    .def("is_game_over", &puyo::Field::is_game_over)
    .def("__repr__", [](const puyo::Field &field) {
      return "<Field height=" + std::to_string(field.get_height())
        + " width=" + std::to_string(field.get_width()) + ">";
    });

    // -- Move struct
    py::class_<puyo::Move>(m, "Move")
      .def_readonly("target_x", &puyo::Move::target_x)
      .def_readonly("rotation", &puyo::Move::rotation)
      .def("__repr__", [](const puyo::Move &move) {
        return "<Move target_x=" + std::to_string(move.target_x)
          + " rotation=" + std::to_string(move.rotation) + ">";
      });

    // AIContext struct
    py::class_<puyo::AIContext>(m, "AIContext")
      .def(py::init<const puyo::Field&>());

    // AI class and factory
    py::class_<puyo::AI, std::shared_ptr<puyo::AI>>(m, "AI")
      .def("decide", [](puyo::AI& self, const puyo::Field& field) {
        puyo::AIContext ctx(field);
        return self.decide(ctx);
      }, py::arg("field"))
      .def_static("create", &puyo::AI::create, py::arg("type"), py::return_value_policy::take_ownership,
           "Create an AI instance of the specified type.")
      .def("is_valid_move", &puyo::AI::is_valid_move, py::arg("field"))
      .def("__repr__", [](const puyo::AI &ai) {
        return "<AI>";
      });
}