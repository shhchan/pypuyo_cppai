# CMakeの最低バージョンを指定
cmake_minimum_required(VERSION 3.10)

# プロジェクト名の扱いに関するポリシーを設定
cmake_policy(SET CMP0148 NEW)

# プロジェクト名を設定
project(pypuyo_cppai)

# C++の標準バージョンを指定
set(CMAKE_CXX_STANDARD 17)

# ソースファイルのリスト
set(SOURCES
    src/AI.cpp
    src/bindings.cpp
    src/Field.cpp
)

# pybind11をサブモジュールとして追加した場合の設定
# add_subdirectory(pybind11)

find_package(pybind11 CONFIG REQUIRED)

# Pythonモジュールとしてビルド
pybind11_add_module(puyo_core src/bindings.cpp src/AI.cpp src/RandomAI.cpp src/Field.cpp)
target_include_directories(puyo_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

# 静的ライブラリを作成（必要なら残す）
# add_library(pypuyo_cppai STATIC ${SOURCES})
# target_include_directories(pypuyo_cppai PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# 実行ファイルを作成したい場合は以下を有効化
# add_executable(main main.cpp)  # main.cppからmainという実行ファイルを作成
# target_link_libraries(main pypuyo_cppai)  # mainにpypuyo_cppaiライブラリをリンク
