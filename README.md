# ReChess

## App Description

ReChess is a GUI app for playing chess against a UCI-based engine.

### About Source Code

The source code of ReChess is written in the **Python** programming
language, primarily to be executed with its 3.12 version, but you are
free to make it work on one of its older versions. Note, though, that
by using the 3.12 version, it is guaranteed that ReChess will work on
Windows, Linux or macOS.

### Third-Party Software

ReChess uses the **PySide6** GUI framework, the **python-chess** library
and the **Stockfish 16.1** engine.

### Components

ReChess provides all the standard components to play chess, which are an
SVG board with pieces, chess clocks, a FEN record editor and a table for
showing move notation in the SAN (Standard Algebraic Notation) format.

### Piece Movement

Moving the pieces on the board is bound to the rules of standard chess.

To move a piece from one square to another is by clicking the piece and
then clicking its target square.

Note: The drag-and-drop ability to move the pieces is not supported.

### Move Legality Indication

After clicking a piece, its legal squares become marked with a dot.

### Appearance

The following screenshots reveal how ReChess looks like.

![ReChess on Windows 11](link "ReChess on Windows 11")
*Changing the settings.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Selecting a move from the chess notation table.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Analyzing a position with the default Stockfish 16.1 engine.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Promoting a white pawn to a queen, a rook, a bishop or a knight.*

## UCI Engine Integration

By default, ReChess integrates the UCI-based Stockfish 16.1 engine for
either the Windows, a Linux-based or the macOS operating system.

A non-default engine can also be loaded and played against, but it must
support the UCI protocol.

## Requirements

The requirements listed below must be installed on your operating system
before you can successfully launch ReChess. Use the provided links to
install any requirement that you might be missing.

(1) Firstly, install the Python programming language:

- [**Python 3.12.2**](https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe)

(2) Secondly, in a command-line interface with admin privileges, install
the following:

- **PySide6**, by executing the command `pip install PySide6`
- **python-chess**, by executing the command `pip install chess`

Alternatively, install **PySide6** and **python-chess** with the `pip`
package manager in your command-line interface with admin privileges
within the top-level directory of ReChess and then execute the command
`pip install -r requirements.txt`.

## How to Launch ReChess

To launch ReChess after installing all of its requirements, launch your
favorite IDE (e.g., PyCharm, VSCode, Wing, Spyder, etc.) or perhaps your
code editor (e.g., Sublime Text, Notepad++, UltraEdit, Atom, etc.) and
build the `main.py` file, found in the top-level directory of ReChess.

Alternatively, execute the command `python main.py` in your command-line
interface within the top-level directory of ReChess.

## Credits and Links

**(1)** Thanks to all developers for their dedicated work on the Python
programming language!

- [Source code](https://github.com/python/cpython)
- [Downloads page](https://www.python.org/downloads)

**(2)** Thanks to all developers for their dedicated work on the PySide6
GUI framework!

- [PyPI (Python Package Index) page](https://pypi.org/project/PySide6)

**(3)** Thanks to developer Niklas Fiekas for his dedicated work on the
python-chess library!

- [Source code](https://github.com/niklasf/python-chess)
- [PyPI (Python Package Index) page](https://pypi.org/project/chess)

**(4)** Thanks to all developers for their dedicated work on the
Stockfish chess engine!

- [Source code](https://github.com/official-stockfish/Stockfish)
- [Downloads page](https://stockfishchess.org/download)

## License

ReChess is licensed under the MIT License.

The contents of the license can be found in the `LICENSE.txt` file in
the top-level directory of ReChess. The file provides all information
about the permissions, limitations and conditions of the license.
