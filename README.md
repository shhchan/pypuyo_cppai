# pypuyo_cppai

## Directory Structure

```
├── CMakeLists.txt
├── main.py                # Puyo Puyo game main (Python, using Pygame)
├── README.md              # This file
├── build/                 # C++ binaries and pybind11 build artifacts
│   └── puyo_core.cpython-***.so  # C++ extension module for Python
├── src/                   # C++ source code
│   ├── AI.cpp, AI.hpp
│   ├── Field.cpp, Field.hpp
│   ├── bindings.cpp       # pybind11 bindings
│   └── ...
├── tests/
│   └── test_puyo_core.py  # Python script for testing the C++ core
└── .venv/                 # Python virtual environment (recommended)
```

## Setup Instructions

### 1. Create and Activate Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install pygame
```

### 3. Build the C++ Core (pybind11)

```bash
cd build && cmake .. && make
```

- `puyo_core.cpython-***.so` will be generated in the `build/` directory.

### 4. Run the Game

```bash
python main.py
```

- The game window will appear, and you can control the puyos with your keyboard.
- The C++ core logic is used from Python.

## Controls

- `A`: Move left
- `D`: Move right
- `W`: Hard drop
- `↓`: Rotate left
- `→`: Rotate right
- `ESC` or close window: Exit

## Testing

You can run tests for the C++ core using `tests/test_puyo_core.py`:

```bash
python tests/test_puyo_core.py
```

## How to Add a New AI (e.g. InitRuleBaseAI) and Use It from Python

1. **C++でAIクラスを実装**
    - 例: `src/InitRuleBaseAI.hpp`, `src/InitRuleBaseAI.cpp` を作成し、`AI` を継承したクラスを実装。

2. **AIType列挙体に追加**
    - `src/AI.hpp` の `enum class AIType` に新しいAI（例: `InitRuleBase`）を追加。
    ```cpp
    enum class AIType {
        Random,
        InitRuleBase, // ← 追加
    };
    ```

3. **AI::create()に分岐を追加**
    - `src/AI.cpp` の `AI* AI::create(AIType type)` に新AIの生成分岐を追加。
    ```cpp
    #include "InitRuleBaseAI.hpp"
    // ...
    case AIType::InitRuleBase:
        return new InitRuleBaseAI();
    ```

4. **pybind11バインディングにAITypeを追加**
    - `src/bindings.cpp` の `py::enum_<puyo::AIType>` に `.value("INIT_RULE_BASE", puyo::AIType::InitRuleBase)` を追加。

5. **CMakeLists.txtにcppファイルを追加**
    - `CMakeLists.txt` の `pybind11_add_module` の引数に `src/InitRuleBaseAI.cpp` を追加。
    ```cmake
    pybind11_add_module(puyo_core src/bindings.cpp src/AI.cpp src/RandomAI.cpp src/Field.cpp src/InitRuleBaseAI.cpp)
    ```

6. **ビルドし直す**
    ```bash
    cd build && cmake .. && make && cd ../
    ```

7. **Python側でAITypeを指定して利用**
    - 例: `main.py` で `puyo_core.AIType.INIT_RULE_BASE` を指定してAIを生成。
    ```python
    ai = puyo_core.AI.create(puyo_core.AIType.INIT_RULE_BASE)
    ```

8. **実行**
    ```bash
    python main.py
    ```