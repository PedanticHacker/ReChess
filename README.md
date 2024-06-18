# ReChess

A GUI app for playing chess against a UCI chess engine.

### Source Code

ReChess' source code is written in the **Python** programming language.
ReChess should be launched with the Python interpreter version 3.12.

You may edit the source code to make it work with older versions of the
Python interpreter, but note that using version 3.12 guarantees that
ReChess will work on Windows, Linux-based, and macOS platforms.

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

Upon clicking a chess piece, its legal squares are marked with a dot.

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

```
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
Stockfish UCI chess engine!

    - [Source code](https://github.com/official-stockfish/Stockfish)
    - [Downloads page](https://stockfishchess.org/download)

## License

ReChess is licensed under the **MIT License**.

See the `LICENSE.txt` file in ReChess' top-level directory about the
permissions, limitations, and conditions of the license.

If you develop software based on ReChess, you are not obligated to use
the same license, but you are required to add the original author's
copyright notice.

So, your copyright notice would look like this:

```
Copyright 2024 Boštjan Mejak
Copyright <year> <name and surname>
```

On the second line, fill out the year in which you are releasing your
ReChess-based software and then fill out your name and surname, without
the `<` and `>` characters.
