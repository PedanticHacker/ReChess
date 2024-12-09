# ReChess 1.0

## What's this?

This is ReChess, an app for playing chess against an engine.

## How can I get started quickly?

Here's what you need to do:

1. Install Python 3.13 from the official website:

    - For Windows:
        - [Download Python 3.13 installer](https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe)
    - For Linux:
        - Execute `sudo apt-get install python3.13` in the terminal or a
        command applicable for the package manager of your distro
    - For macOS:
        - [Download Python 3.13 installer](https://www.python.org/ftp/python/3.13.1/python-3.13.1-macos11.pkg)

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Launch ReChess:

```bash
python main.py
```

4. Start playing by:

    - Click a piece to see its legal moves.
    - Click a legal square to make your move.
    - Use the Settings button to customize your experience.

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

Yes. ReChess integrates **Stockfish**, a powerful engine for playing and
analyzing a game.

## What features does ReChess provide?

You get all the basic features for playing chess:

- board
- chess clocks
- FEN viewer and editor
- table view for showing standard algebraic notation (SAN)

### Is that it?

There are also many functionalities you can utilize:

- navigate through moves of the game by scrolling the mouse wheel
- play against the latest version of the Stockfish engine
- analyze a position
- load an engine
- flip the board
- force the engine to make a move
- paste a FEN from the clipboard by double-clicking the FEN editor
- select from one of the dark or light styles

## Which chess variants are supported?

Chess variants are not supported.

## How do I move a piece on the board?

Making a move in ReChess is as simple as a click. Just click a piece and
then click one of its legal squares to make your move.

### How do I know which legal squares are available for a piece?

After you click a piece, all of its legal squares get marked with a dot.
That's how you know.

### Can I drag and drop a piece?

No. Drag-and-drop functionality is not supported, just click-click.

## How does ReChess look?

The following screenshots show how ReChess looks in "Dark mint" style.

![ReChess on Windows 11]( "ReChess on Windows 11")

*Changing the settings.*

![ReChess on Windows 11]( "ReChess on Windows 11")

*Selecting a move from the chess notation table.*

![ReChess on Windows 11]( "ReChess on Windows 11")

*Analyzing a position with the default Stockfish 17 chess engine.*

![ReChess on Windows 11]( "ReChess on Windows 11")

*Promoting a white pawn to a queen, a rook, a bishop, or a knight.*

## What's the default engine in ReChess?

The latest public version of **Stockfish** is the default engine. It
works on Windows, Linux, and macOS platforms.

### What if I want to play against some other engine?

You can load and then play against or analyze with any engine, but it
has to be a UCI-compliant one.

### Why does it have to be a UCI-compliant engine?

Engines, compliant only with the Chess Engine Communication Protocol
(CECP) and designed for either the WinBoard GUI (Windows platform) or
the XBoard GUI (UNIX or UNIX-based platform like Linux), can't be loaded
and hence can't be played against in ReChess because it doesn't support
this type of protocol. However, if your engine is also compliant with
Universal Chess Interface (UCI), then you're in luck.

### Can I analyze a position?

Yes. You can analyze a position with the default Stockfish engine or a
UCI-compliant engine you load yourself.

## How can I launch ReChess?

After installing ReChess's requirements, launch your favorite IDE (e.g.,
PyCharm, VSCode, Wing, Spyder, etc.) or your favorite source-code editor
(e.g., Sublime Text, Notepad++, UltraEdit, Atom, etc.), then run the
`main.py` file found in ReChess's top-level directory.

You can also execute this command in your command-line interface within
ReChess's top-level directory:

```bash
python main.py
```

:point_right: On macOS, *python* commands are written as `python3`.

## Who should get thanks for ReChess?

1. Thanks to all developers for their dedicated work on the Python
programming language!

    - [Source](https://github.com/python/cpython)
    - [Downloads](https://www.python.org/downloads)

2. Thanks to developer Giampaolo Rodola for his dedicated work on the
psutil library!

    - [Source](https://github.com/giampaolo/psutil)
    - [PyPI](https://pypi.org/project/psutil)

3. Thanks to all developers for their dedicated work on the PySide6 GUI
framework!

    - [PyPI](https://pypi.org/project/PySide6)

4. Thanks to developer Niklas Fiekas for his dedicated work on the
python-chess library!

    - [Source](https://github.com/niklasf/python-chess)
    - [PyPI](https://pypi.org/project/chess)

5. Last but not least, thanks to all developers for their dedicated work
on the Stockfish engine!

    - [Source](https://github.com/official-stockfish/Stockfish)
    - [Downloads](https://stockfishchess.org/download)

## What license does ReChess use?

ReChess uses the **MIT License**.

### Where can I see the license?

See the `LICENSE.txt` file in ReChess's top-level directory about the
permissions, limitations, and conditions of the license.

### Can I develop an app based on ReChess?

Absolutely! For your app, you can use any license, but make sure to
include my copyright notice above yours.

Your copyright notice should look like this:

```
Copyright 2024 Boštjan Mejak
Copyright 2024 John Doe
```

On the second line, provide the year in which you are releasing your app
and provide your legal first and last name.

If you intend to also integrate Stockfish in your app like ReChess does,
you must do this:

1. Include Stockfish's copyright notice
2. Include the GPLv3 License to comply with Stockfish's license
3. License your app under GPLv3 or any of its compatible licenses
