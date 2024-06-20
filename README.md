# ReChess

A GUI app for playing chess against a UCI chess engine.

### Source Code

ReChess's source code is written in the **Python** programming language.
ReChess should be launched with the Python interpreter version 3.12.

You may edit the source code to make it work with older versions of the
Python interpreter, but note that using version 3.12 guarantees that
ReChess will work on Windows, Linux-based, and macOS platforms.

### Dependencies

ReChess depends upon and extensively uses the **PySide6** GUI framework
and the **python-chess** library.

### 3rd-Party Software

ReChess integrates the **Stockfish** chess engine.

### UI Components

ReChess provides all the UI components for playing chess, which include
an SVG board with pieces, chess clocks, a FEN record editor, and a table
for displaying chess move notation in SAN (Standard Algebraic Notation)
format.

### Game Rules

ReChess adheres only to the rules of standard chess.

> [!NOTE]
> Chess variants are not supported.

### Chess Moves

To make a chess move, click the origin square of a chess piece and then
click its legal square.

> [!NOTE]
> Drag-and-drop functionality for making chess moves is not supported.

### Legal Square Markers

After you click a chess piece, its legal squares are marked with a dot.

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

## Chess Engine Integration & Protocol Compatibility

The Stockfish chess engine is integrated in ReChess by default and works
on Windows, Linux-based, and macOS platforms.

Custom chess engines can also be loaded and played against in ReChess,
provided they are compatible with the UCI protocol.

## CECP Protocol Compatibility

The chess engines, compatible only with the CECP protocol and designed
for a WinBoard or an XBoard GUI cannot be loaded and played against in
ReChess. It is required that all chess engines are compatible with the
UCI protocol for proper integration and gameplay availability.

## Requirements

The requirements listed below must be installed on your platform before
you can successfully launch ReChess. Use the provided links to install
any requirement you might be missing.

1. Install the Python programming language:

    - [**Python 3.12.4**](https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe)

2. In a command-line interface with admin privileges, install these:

    - **PySide6**, by executing the command `pip install PySide6`
    - **python-chess**, by executing the command `pip install chess`

Alternatively, install **PySide6** and **python-chess** with the pip
package manager in your command-line interface with admin privileges
within ReChess's top-level directory by executing this command:

```bash
pip install -r requirements.txt
```

## How to Launch ReChess

After installing all of ReChess' requirements, launch your favorite IDE
(e.g., PyCharm, VSCode, Wing, Spyder, etc.) or your favorite code editor
(e.g., Sublime Text, Notepad++, UltraEdit, Atom, etc.), then build the
`main.py` file found in ReChess's top-level directory.

Alternatively, execute the `python main.py` command in your command-line
interface within ReChess's top-level directory.

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

4. Thanks to all developers for their dedicated work on the Stockfish
chess engine!

    - [Source code](https://github.com/official-stockfish/Stockfish)
    - [Downloads page](https://stockfishchess.org/download)

## License

ReChess is licensed under the **MIT License**.

See the `LICENSE.txt` file in ReChess's top-level directory about the
permissions, limitations, and conditions of the license.

If you develop software based on ReChess, you are not obligated to use
the same license, but you are required to add the original author's
copyright notice.

Your copyright notice should look like below. On the second line, change
the example year to the year when you are releasing your ReChess-based
software and also change the example name and surname to your legal name
and your legal surname.

```
Copyright 2024 Boštjan Mejak
Copyright 2024 John Doe
```
