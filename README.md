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