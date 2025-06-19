#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

// Puyo Puyo Core Library
#include "CellType.hpp"
#include "ChainInfo.hpp"
#include "Field.hpp"
#include "AI.hpp"

namespace py = pybind11;
using namespace puyo;

PYBIND11_MODULE(puyo_core, m) {
  m.doc() = "Puyto Puyo Core Library Bindings";

  // --- CellType enum ---
  py::enum_<CellType>(m, "CellType")
    .value("EMPTY", CellType::EMPTY)
    .value("WALL", CellType::WALL)
    .value("RED", CellType::RED)
    .value("GREEN", CellType::GREEN)
    .value("YELLOW", CellType::YELLOW)
    .value("BLUE", CellType::BLUE)
    .value("PURPLE", CellType::PURPLE)
    .value("GARBAGE", CellType::GARBAGE)
    .export_values();

  // --- ChainInfo struct ---
  py::class_<ChainInfo>(m, "ChainInfo")
    .def(py::init<>())
    .def_readwrite("chain_count", &ChainInfo::chain_count)
    .def_readwrite("group_sizes", &ChainInfo::group_sizes)
    .def_readwrite("colors", &ChainInfo::colors)
    .def_readwrite("total_erased", &ChainInfo::total_erased)
    .def_readwrite("erased", &ChainInfo::erased)
    .def("__repr__", [](const ChainInfo &info) {
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
  py::class_<Field::ActiveTsumo>(m, "ActiveTsumo")
    .def_readonly("x", &Field::ActiveTsumo::x)
    .def_readonly("y", &Field::ActiveTsumo::y)
    .def_readonly("dx", &Field::ActiveTsumo::dx)
    .def_readonly("dy", &Field::ActiveTsumo::dy)
    .def_readonly("center", &Field::ActiveTsumo::center)
    .def_readonly("sub", &Field::ActiveTsumo::sub)
    .def("__repr__", [](const Field::ActiveTsumo &tsumo) {
      return "<ActiveTsumo x=" + std::to_string(tsumo.x)
        + " y=" + std::to_string(tsumo.y)
        + " dx=" + std::to_string(tsumo.dx)
        + " dy=" + std::to_string(tsumo.dy)
        + " center=" + std::to_string(static_cast<int>(tsumo.center))
        + " sub=" + std::to_string(static_cast<int>(tsumo.sub)) + ">";
    });

  // --- Field class ---
  py::class_<Field>(m, "Field")
    .def(py::init<int, int>(), py::arg("height") = 14, py::arg("width") = 6)
    .def("set_cell", &Field::set_cell, py::arg("x"), py::arg("y"), py::arg("type"))
    .def("get_cell", &Field::get_cell, py::arg("x"), py::arg("y"))
    .def("set_next_tsumos", &Field::set_next_tsumos, py::arg("next1"), py::arg("next2"))
    .def("set_active_tsumo", &Field::set_active_tsumo, py::arg("center"), py::arg("sub"), py::arg("x") = 2, py::arg("y") = -1, py::arg("dx") = 0, py::arg("dy") = -1)
    .def("move_active_tsumo_left", &Field::move_active_tsumo_left)
    .def("move_active_tsumo_right", &Field::move_active_tsumo_right)
    .def("rotate_active_tsumo_left", &Field::rotate_active_tsumo_left)
    .def("rotate_active_tsumo_right", &Field::rotate_active_tsumo_right)
    .def("drop_active_tsumo", &Field::drop_active_tsumo)
    .def("get_ghost_position", &Field::get_ghost_position)
    .def("analyze_and_erase_chains", &Field::analyze_and_erase_chains, py::arg("chain_count") = 1)
    .def("apply_grabity", &Field::apply_gravity)
    .def("calculate_score", &Field::calculate_score, py::arg("chain_info"))
    .def("update_score", &Field::update_score, py::arg("chain_info"))
    .def("set_current_chain_size", &Field::set_current_chain_size, py::arg("chain_count"))
    .def("generate_next_tsumo", &Field::generate_next_tsumo)
    .def("get_height", &Field::get_height)
    .def("get_width", &Field::get_width)
    .def("get_grid_cell", &Field::get_grid_cell, py::arg("x"), py::arg("y"))
    .def("get_active_tsumo", &Field::get_active_tsumo)
    .def("__repr__", [](const Field &field) {
      return "<Field height=" + std::to_string(field.get_height())
        + " width=" + std::to_string(field.get_width()) + ">";
    });

    // -- Move struct
    py::class_<Move>(m, "Move")
      .def_readonly("target_x", &Move::target_x)
      .def_readonly("rotation", &Move::rotation)
      .def("__repr__", [](const Move &move) {
        return "<Move target_x=" + std::to_string(move.target_x)
          + " rotation=" + std::to_string(move.rotation) + ">";
      });

    // AI class and factory
    py::class_<AI, std::shared_ptr<AI>>(m, "AI")
      .def("decide", &AI::decide, py::arg("field"));

    m.def("create_random_AI", &puyo::create_random_AI, py::return_value_policy::take_ownership, 
          "Create a random AI instance that makes random decisions.");
}