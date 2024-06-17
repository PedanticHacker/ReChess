# ReChess

A GUI app for playing chess against a UCI chess engine.

### Source Code

ReChess' source code is written in the **Python** programming language.
ReChess must be launched with Python interpreter's 3.12 version.

You may edit the source code to make it work with older interpreter's
versions, but note that using version 3.12 guarantees that ReChess will
work on Windows, Linux-based, and macOS platforms.

### Dependencies

ReChess depends upon and extensively uses the **PySide6** GUI framework
and the **python-chess** library.

### 3rd-Party Software

ReChess integrates the **Stockfish** UCI chess engine.

### UI Components

ReChess provides all the UI components for playing chess, which include
an SVG board with pieces, chess clocks, a FEN record editor, and a table
for displaying chess move notation in SAN (Standard Algebraic Notation)
format.

### Piece Movement

Moving the pieces on the board adheres to the rules of standard chess.

To move a piece from one square to another, click the piece and then
click its target square.

Note: Drag-and-drop functionality for moving pieces is not supported.

### Move Legality Indication

After clicking a piece, its legal squares become marked with a dot.

### Appearance

The following screenshots show how ReChess looks.

![ReChess on Windows 11](link "ReChess on Windows 11")
*Changing the settings.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Selecting a move from the chess notation table.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Analyzing a position with the integrated chess engine.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Promoting a white pawn to a queen, a rook, a bishop, or a knight.*

## UCI Chess Engine Integration & Protocol Compatibility

The latest official version of the Stockfish UCI chess engine is
integrated for Windows, Linux-based, and macOS platforms.

Custom chess engines can also be loaded and played against in ReChess,
provided they are compatible with the UCI protocol.

## CECP Protocol Compatibility

Chess engines compatible only with the CECP protocol and designed for
either a WinBoard or an XBoard GUI cannot be loaded and played against
in ReChess. It is required that all chess engines are compatible with
the UCI protocol for proper integration and gameplay availability.

## Requirements

The requirements listed below must be installed on your platform before
you can successfully launch ReChess. Use the provided links to install
any requirement that you might be missing.

1. Install the Python programming language:

- [**Python 3.12.4**](https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe)

2. In a command-line interface with admin privileges, install these:

- **PySide6**, by executing the command `pip install PySide6`
- **python-chess**, by executing the command `pip install chess`

Alternatively, install **PySide6** and **python-chess** with the pip
package manager in your command-line interface with admin privileges
within ReChess' top-level directory by executing this command:

```bash
pip install -r requirements.txt
```

## How to Launch ReChess

After installing all of ReChess' requirements, launch your favorite IDE
(e.g., PyCharm, VSCode, Wing, Spyder, etc.) or your favorite code editor
(e.g., Sublime Text, Notepad++, UltraEdit, Atom, etc.), then build the
`main.py` file found in ReChess' top-level directory.

Alternatively, execute the command `python main.py` in your command-line
interface within ReChess' top-level directory.

## Credits and Links

1. Thanks to all developers for their dedicated work on the Python
programming language!

- [Source code](https://github.com/python/cpython)
- [Downloads page](https://www.python.org/downloads)

2. Thanks to all developers for their dedicated work on the PySide6
GUI framework!

- [PyPI (Python Package Index) page](https://pypi.org/project/PySide6)

3. Thanks to developer Niklas Fiekas for his dedicated work on the
python-chess library!

- [Source code](https://github.com/niklasf/python-chess)
- [PyPI (Python Package Index) page](https://pypi.org/project/chess)

4. Thanks to all developers for their dedicated work on the
Stockfish chess engine!

- [Source code](https://github.com/official-stockfish/Stockfish)
- [Downloads page](https://stockfishchess.org/download)

## License

ReChess is licensed under the MIT License.

The contents of the license can be found in the `LICENSE.txt` file in
the top-level directory of ReChess. The file provides all information
about the permissions, limitations, and conditions of the license.
