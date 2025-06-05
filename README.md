# 🎮 Multiplatform Checkers Game

A modern checkers game developed in Python with Pygame, offering a complete gaming experience with multiple game modes and an intuitive user interface.

## ✨ Features

- 🎯 **Multiple game modes**
  - Single player vs AI
  - Local multiplayer
  - Online mode (network multiplayer)
  
- 🤖 **AI with different difficulty levels**
  - Beginner
  - Intermediate
  - Expert
  
- 🎨 **Modern user interface**
  - Intuitive main menu
  - Pause menu
  - Valid moves display
  - Turn indicators
  - Scoring system
  
- 🔊 **Sound effects**
  - Movement sounds
  - Error sounds
  - Audio feedback for better user experience

- 🌐 **Network features**
  - Dedicated server for online mode
  - Real-time synchronization
  - Connection/disconnection management
  - Player name system

## 🛠️ Technologies used

- Python 3
- Pygame
- Socket (for online mode)
- Threading (for network connection management)

## 📋 Prerequisites

- Python 3
- Pygame
- WebSocket
- Internet connection (for online mode)

## 🚀 Installation

### Windows
1. Download and install Python 3 from [python.org](https://www.python.org/downloads/)
2. Open command prompt (cmd) and run:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Mac/Linux
1. Open terminal and install Python 3 if not already installed:
```bash
# For Mac with Homebrew
brew install python3

# For Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3 python3-pip
```

2. Install dependencies:
```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## 🎮 How to play

1. Launch the game:
```bash
# Windows
python main.py

# Mac/Linux
python3 main.py
```

2. In the main menu, choose your game mode:
   - Single player vs AI
   - Local multiplayer
   - Online mode

3. For online mode:
   - First launch the server:
   ```bash
   # Windows
   python server.py

   # Mac/Linux
   python3 server.py
   ```
   - Then connect with the client

## 🎯 Controls

- **Left click**: Select/move a piece
- **Escape**: Pause menu
- **V**: Show/hide valid moves (visual aid to see possible movements)

## 🏗️ Project structure

```
├── main.py           # Game entry point
├── server.py         # Server for online mode
├── classes/          # Game classes
│   ├── ai.py        # Artificial intelligence
│   ├── board.py     # Game board
│   ├── constants.py # Game constants
│   ├── game.py      # Main game logic
│   ├── menu.py      # Game menus
│   ├── network.py   # Network management
│   └── piece.py     # Game pieces
└── assets/          # Resources (images, sounds)
```
