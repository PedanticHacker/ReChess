# ReChess

## What is this?

ReChess is an app for playing chess against a chess engine.

## In what programming language is ReChess written?

That would be **Python**.

### What version of Python are we talking about here?

It would be best if you launch ReChess using Python **3.12**.

### Why 3.12?

By using Python 3.12, ReChess will work on all major platforms, so
Windows, Linux, and macOS.

### What about other Python versions?

Modifying the source code is quite simple if you're using an older
version of Python and want to adapt it.

## Are there any dependencies?

ReChess depends upon and extensively uses the **PySide6** GUI framework
and the **python-chess** library.

### Is there any 3rd-party software involved?

Yes. ReChess integrates **Stockfish**, a powerful chess engine for
playing and analyzing.

## What do I get?

With ReChess, you get all the basic stuff for playing chess:

- SVG chessboard
- chess clocks
- FEN record editor
- table that displays chess move notation in SAN format

### Can I do a chessboard position analysis?

Yes. You can analyze a chessboard position with the default chess engine
or the one you load yourself.

## Which chess variants are supported?

Only standard chess is supported. Chess variants are not supported.

## How do I move a piece on the chessboard?

Making a move in ReChess is as simple as a click. Just click a piece and
then click one of its legal squares to make your move.

### Can I drag and then drop a piece?

No. Drag-and-drop functionality is not supported.

### How can I know what's the legal square of a piece?

After you click a piece, all of its legal squares get marked with a dot.

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
works on Windows, Linux, and macOS platforms.

### What if I want to play against some other chess engine?

You can load and play against any chess engine in ReChess, but make sure
it is a UCI chess engine.

### Why does it have to be UCI?

Chess engines, compatible only with CECP and designed for a WinBoard or
an XBoard GUI, cannot be loaded and played against in ReChess because it
does not support this protocol. If your chess engine also supports UCI,
then you're in luck.

## Are there any requirements I must have for ReChess?

Yes. You should have specific requirements before launching ReChess.
Click the provided links to install any missing ones.

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

After installing ReChess's requirements, launch your favorite IDE (e.g.,
PyCharm, VSCode, Wing, Spyder, etc.) or your favorite source-code editor
(e.g., Sublime Text, Notepad++, UltraEdit, Atom, etc.), then run the
`main.py` file found in ReChess's top-level directory.

Alternatively, you can also execute the `python main.py` command in your
command-line interface within ReChess's top-level directory.

## Who should get thanks for ReChess?

1. Thanks to all the developers for their dedicated work on the Python
programming language!

    - [Source code](https://github.com/python/cpython)
    - [Downloads page](https://www.python.org/downloads)

2. Thanks to all the developers for their dedicated work on the PySide6
GUI framework!

    - [PyPI (Python Package Index) page](https://pypi.org/project/PySide6)

3. Thanks to the developer Niklas Fiekas for his dedicated work on the
python-chess library!

    - [Source code](https://github.com/niklasf/python-chess)
    - [PyPI (Python Package Index) page](https://pypi.org/project/chess)

4. Last but not least, thanks to all the developers for their dedicated
work on the Stockfish chess engine!

    - [Source code](https://github.com/official-stockfish/Stockfish)
    - [Downloads page](https://stockfishchess.org/download)

## What license does ReChess use?

ReChess uses the **MIT License**.

### Where can I see the license?

See the `LICENSE.txt` file in ReChess's top-level directory about the
permissions, limitations, and conditions of the license.

### What if I develop an app based on ReChess?

You can use whatever license you want for your app, provided you include
my copyright notice above yours.

Your copyright notice should look like this:

```
Copyright 2024 Boštjan Mejak
Copyright 2024 John Doe
```

On the second line, update your app's release year and your legal first
and last name.
