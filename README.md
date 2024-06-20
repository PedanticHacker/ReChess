# ReChess

## What is this?

This is a [GUI](https://en.wikipedia.org/wiki/Graphical_user_interface "Graphical User Interface")
application for playing chess against a [UCI](https://en.wikipedia.org/wiki/Universal_Chess_Interface "Universal Chess Interface")
chess engine.

## What programming language is this written in?

The source code of ReChess is written completely in **Python**.

## What version of Python are we talking about here?

ReChess should be launched with Python **3.12**.

## Why only 3.12?

I guarantee that using the 3.12 version, ReChess will work on Windows,
any Linux-based, and macOS platforms.

## What about other Python versions?

You may edit the source code to make it work with older Python versions.

## Are there any dependencies?

ReChess depends upon and extensively uses the **PySide6** GUI framework
and the **python-chess** library.

## Is there any 3rd-party software involved?

Yes. ReChess integrates **Stockfish** by default, which is the strongest
chess engine in the world.

## What do I get?

ReChess provides you with all the basic stuff for playing chess, so like
a nice [SVG](https://en.wikipedia.org/wiki/SVG "Simple Vector Graphics")
chessboard with good-looking chess pieces, two chess clocks, a [FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation "Forsyth-Edwards Notation") record editor, and a table for displaying
chess move notation in the [SAN](https://en.wikipedia.org/wiki/Algebraic_notation_(chess) "Standard Algebraic Notation")
format.

## Which chess variants are supported?

Only standard chess is supported. Chess variants are not supported.

## How do I move a chess piece on the chessboard?

To make a chess move, click a chess piece and then click one of its
legal squares.

## Can't I drag and then drop a chess piece?

Nope. Drag-and-drop functionality is not supported, just click-click.

## How do I know what's a legal square of a chess piece?

After you click a chess piece, its legal squares are marked with a dot.

## How does ReChess look?

The following screenshots show how ReChess looks.

![ReChess on Windows 11](link "ReChess on Windows 11")
*Changing the settings.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Selecting a move from the chess notation table.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Analyzing a position with the default chess engine.*

![ReChess on Windows 11](link "ReChess on Windows 11")
*Promoting a white pawn to a queen, a rook, a bishop, or a knight.*

## What's the default chess engine in ReChess?

The latest version of the **Stockfish** chess engine is the default. It
works on Windows, any Linux-based, and macOS platforms.

## What if I want to play against some other chess engine?

Custom chess engines can also be loaded and played against in ReChess,
but make sure that yours is a [UCI](https://en.wikipedia.org/wiki/Universal_Chess_Interface "Universal Chess Interface")
chess engine.

## Why is that?

Chess engines that are compatible only with the [CECP](https://www.chessprogramming.org/Chess_Engine_Communication_Protocol "Chess Engine Communication Protocol") protocol and designed for a [WinBoard](https://www.chessprogramming.org/WinBoard)
or an [XBoard](https://www.chessprogramming.org/XBoard) GUI cannot be
loaded and played against in ReChess, since there's no support for it,
unless your chess engine supports UCI as well, then you're in luck.

## Are there any requirements I must have for ReChess?

The requirements listed below must be installed on your platform before
you can successfully launch ReChess. Use the provided links to install
any requirement you might be missing.

1. Install the Python programming language:

    - [**Python 3.12.4**](https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe)

2. In a command-line interface with admin privileges, install these:

    - **PySide6**, by executing the command `pip install PySide6`
    - **python-chess**, by executing the command `pip install chess`

Alternatively, you can also install **PySide6** and **python-chess**
with the *pip* package manager in your command-line interface within
ReChess's top-level directory, then execute this command:

```bash
pip install -r requirements.txt
```

## How can I launch ReChess?

After installing ReChess's requirements, launch your favorite [IDE](https://en.wikipedia.org/wiki/Integrated_development_environment "Integrated Development Environment") (e.g., PyCharm, VSCode, Wing, Spyder, etc.) or
your favorite [source-code editor](https://en.wikipedia.org/wiki/Source-code_editor)
(e.g., Sublime Text, Notepad++, UltraEdit, Atom, etc.), then build the
`main.py` file found in ReChess's top-level directory.

Alternatively, you can also execute the `python main.py` command in your
command-line interface within ReChess's top-level directory.

## Who's to thank for all this?

1. Thanks goes to all developers for their dedicated work on the Python
programming language!

    - [Source code](https://github.com/python/cpython)
    - [Downloads page](https://www.python.org/downloads)

2. Thanks goes to all developers for their dedicated work on the PySide6
GUI framework!

    - [PyPI (Python Package Index) page](https://pypi.org/project/PySide6)

3. Thanks goes to developer Niklas Fiekas for his dedicated work on the
python-chess library!

    - [Source code](https://github.com/niklasf/python-chess)
    - [PyPI (Python Package Index) page](https://pypi.org/project/chess)

4. Last but not least, thanks also goes to all developers for their
dedicated work on the Stockfish chess engine!

    - [Source code](https://github.com/official-stockfish/Stockfish)
    - [Downloads page](https://stockfishchess.org/download)

## What license does ReChess use?

ReChess is licensed under the **MIT License**.

## Where can I see the license?

See the `LICENSE.txt` file in ReChess's top-level directory about the
permissions, limitations, and conditions of the license.

## What if I develop an application based on ReChess?

In that case, you are not obligated to use the same license, but you are
required to add the original author's copyright notice (i.e., mine).

Your copyright notice would then look like this:

```
Copyright 2024 Boštjan Mejak
Copyright 2024 John Doe
```

On the second line, change the year to the one when you are releasing
your application based on ReChess and also change the name and surname
to your actual legal name and your actual legal surname.
