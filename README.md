# Breakout Universe

Breakout Universe is a demo arcade game built with Python and
[pygame](https://www.pygame.org/).

This project was developed as coursework for the **Linguagem de Programação
Aplicada** class at **Uninter**.

The player controls a paddle, launches the ball, destroys bricks, clears three
levels, and can save their score to a local ranking.

## Features

- Classic Breakout-style gameplay.
- Three levels with increasing difficulty.
- Brick colors indicate HP, making stronger blocks easy to identify.
- Pixel-art sprites, pixel font and music.
- Local top-10 score board stored with SQLite.

## Requirements

- Python 3.10 or newer
- pygame 2.6.1

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Controls

- **Left / Right:** move the paddle
- **Space:** launch the ball
- **Up / Down:** navigate the menu
- **Enter:** select an option
- **Esc:** leave the current level
- **F11:** toggle fullscreen
- **Ctrl + N:** skip the current level for debugging

## Assets

- Background images and music were generated with AI tools.
- Paddle, ball and brick sprites use the
  [Brick Breaker Asset Pack by Schwarnhild](https://schwarnhild.itch.io/brick-breaker-asset-pack).
- The game uses the
  [m5x7 pixel-art font by Daniel Linssen](https://managore.itch.io/m5x7),
  included in the `assets/` folder.

## Building an executable

Install PyInstaller and run the build script:

```bash
pip install pyinstaller
python scripts/build.py
```

The script runs PyInstaller with the correct `--add-data` separator for the
current operating system and then copies the `assets/` folder to `dist/assets/`.
The generated executable is written to the `dist/` folder.

## Creating a GitHub release

This repository includes a GitHub Actions workflow that builds Linux and
Windows executables and attaches them to a release.

Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub will create a release with:

- `BreakoutUniverse-linux.zip`
- `BreakoutUniverse-windows.zip`
- Source code archives generated automatically by GitHub

## Development

Run the linter with:

```bash
flake8 main.py code/
```
