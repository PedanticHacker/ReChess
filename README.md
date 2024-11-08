# ReChess

## What's this?

ReChess is an app for playing chess against a UCI chess engine.

## In what programming language is ReChess written?

That would be **Python**.

### What version of Python are we talking about here?

It would be best if you launch ReChess using Python **3.13**.

### Why 3.13 specifically?

As tested, ReChess works on all major platforms using Python 3.13, so on
Windows, Linux, and macOS.

### What about other Python versions?

ReChess should work using a Python version older than 3.13, but surely
won't work using a 2.x version. Feel free to modify the source code to
adapt it to your specific Python version, if required.

## Are there any dependencies?

Yes. ReChess depends upon:

- **psutil**: A library for getting operating system metrics
- **PySide6**: A framework for developing cross-platform GUI apps
- **python-chess**: A library for developing chess apps

### Is there any 3rd-party software integrated?

Yes. ReChess integrates **Stockfish**, a powerful UCI chess engine for
playing and analyzing a chess game.

## What features does ReChess provide?

You get all the basic features for playing chess:

- chess clocks
- SVG chessboard
- FEN editor
- table for showing chess move notation in standard algebraic notation
(SAN) format

### Is that it?

There are also many functionalities you can utilize:

- navigate through move history by scrolling your mouse wheel upwards or
downwards, or make a corresponding touchpad gesture, and play a game
from whichever move onwards
- play against the latest official version of the Stockfish chess engine
- analyze a chessboard position
- load a UCI chess engine to play against it or to analyze with it
- flip the chessboard
- force the loaded UCI chess engine to make a move when its opponent is
on turn
- paste a FEN from the clipboard by double-clicking the FEN editor, then
analyze the chessboard position or play the game from there onwards
- select from one of the dark or light styles

## Which chess variants are supported?

Chess variants are not supported. There are no plans they will ever be.

## How do I move a piece on the board?

Making a move in ReChess is as simple as a click. Just click a piece and
then click one of its legal squares to make your move.

### How do I know which legal squares are availabe for a piece?

After you click a piece, all of its legal squares get marked with a dot.
That's how you know.

### Can I drag and then drop a piece?

No. Drag-and-drop functionality is not supported, just click-click.

## How does ReChess look?

The following screenshots show how ReChess looks.

![ReChess on Windows 11](https://github.com/user-attachments/assets/bb1c558d-44aa-48da-9cb1-13999da84bf9 "ReChess on Windows 11")
*Changing the settings.*

![ReChess on Windows 11](https://github.com/user-attachments/assets/6aff84c3-b4c1-44f9-a1e9-ac49f80e49b4 "ReChess on Windows 11")
*Selecting a move from the chess notation table.*

![ReChess on Windows 11](https://github.com/user-attachments/assets/c61260a8-747f-44ad-893b-71cc509f427b "ReChess on Windows 11")
*Analyzing a position with the default Stockfish 17 chess engine.*

![ReChess on Windows 11](https://github.com/user-attachments/assets/d92bd7e4-1ffa-4d34-912a-2bbb4d35dc03 "ReChess on Windows 11")
*Promoting a white pawn to a queen, a rook, a bishop, or a knight.*

## What's the default chess engine in ReChess?

The latest version of the **Stockfish** chess engine is the default. It
works on Windows, Linux, and macOS platforms.

### What if I want to play against some other chess engine?

You can load and then play against any chess engine in ReChess, just
make sure it is a UCI-compatible one.

### Why does it have to be a UCI-compatible chess engine?

Chess engines, compatible only with the chess engine communication
protocol (CECP) and designed for either the WinBoard GUI (for Windows)
or for the XBoard GUI (for Unix-based platforms like Linux), can't be
loaded and hence can't be played against in ReChess because it doesn't
support this type of protocol. However, if your chess engine is also
compatible with the UCI protocol, then you're in luck.

### Can I analyze a position?

Yes. You can analyze a position with the default Stockfish chess engine
or a UCI-compatible chess engine you load yourself.

## Are there any requirements I must meet to launch ReChess?

Yes. You must have some things installed. If not installed already,
install them in this order:

1. For a 64-bit Windows 10 or 11, install Python by clicking the link to
the installer located below. (We will need the *pip* package manager, so
make sure to select the Install Now option when the installer launches.)

    - [**Python 3.13.0 for Windows**](https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe)

For macOS version 10.13 or later, use [**this installer**](https://www.python.org/ftp/python/3.13.0/python-3.13.0-macos11.pkg).

2. In your command-line interface, install these Python packages:

    - **psutil**, by executing the command `pip install psutil`
    - **PySide6**, by executing the command `pip install PySide6`
    - **python-chess**, by executing the command `pip install chess`

Alternatively, you can also execute this command to achieve the same:

```bash
pip install -r requirements.txt
```

> :memo: On macOS, all *pip* commands start with `pip3`, not `pip`.
That's a minor quirk to be aware of.

## How can I launch ReChess?

After installing ReChess's requirements, launch your favorite IDE (e.g.,
PyCharm, VSCode, Wing, Spyder, etc.) or your favorite source-code editor
(e.g., Sublime Text, Notepad++, UltraEdit, Atom, etc.), then run the
`main.py` file found in ReChess's top-level folder/directory.

Alternatively, you can also execute this command in your command-line
interface within ReChess's top-level folder/directory:

```bash
python main.py
```

## Who should get thanks for ReChess?

1. Thanks to all the developers for their dedicated work on the Python
programming language!

    - [Source code](https://github.com/python/cpython)
    - [Downloads page](https://www.python.org/downloads)

2. Thanks to the developer Giampaolo Rodola for his dedicated work on
the psutil library!

    - [Source code](https://github.com/giampaolo/psutil)
    - [PyPI (Python Package Index) page](https://pypi.org/project/psutil)

3. Thanks to all the developers for their dedicated work on the PySide6
GUI framework!

    - [PyPI (Python Package Index) page](https://pypi.org/project/PySide6)

4. Thanks to the developer Niklas Fiekas for his dedicated work on the
python-chess library!

    - [Source code](https://github.com/niklasf/python-chess)
    - [PyPI (Python Package Index) page](https://pypi.org/project/chess)

5. Last but not least, thanks to all the developers for their dedicated
work on the Stockfish chess engine!

    - [Source code](https://github.com/official-stockfish/Stockfish)
    - [Downloads page](https://stockfishchess.org/download)

## What license does ReChess use?

ReChess uses the **MIT License**.

### Where can I see ReChess's license?

See the `LICENSE.txt` file in ReChess's top-level directory about the
permissions, limitations, and conditions of the license.

### Can I develop an app based on ReChess?

Yes. For your app, you can use whatever license, but make sure that you
include my copyright notice above yours.

Your copyright notice should look like this:

```
Copyright 2024 Boštjan Mejak
Copyright 2024 John Doe
```

On the second line, provide the year in which you are releasing your app
and provide your legal first and last name. That's it.
