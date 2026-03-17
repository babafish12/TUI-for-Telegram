# telegterm

## Overview
Full-featured Telegram TUI client built with Textual + Telethon.

## Stack
- Python 3.11+, Textual, Rich, Telethon, textual-image, Pillow, pyperclip
- System deps: poppler (PDF thumbnails), ffmpeg (video thumbnails)

## Project Structure
```
src/telegterm/
├── app.py              # Main App class
├── theme.py            # Theme definitions
├── constants.py        # Enums
├── models/             # Dataclasses + ConfigManager
├── screens/            # Textual Screens (modals + regular)
├── widgets/            # Reusable UI components
├── services/           # Telegram client, event handler, media manager
└── styles/             # TCSS files (mostly inline)
```

## Commands
```bash
pip install -e .        # Dev install
telegterm               # Run the app
```

## Conventions
- Follows ssh-term patterns: Modal screens with callbacks, @work() for async, ConfigManager for JSON persistence
- Config at ~/.config/telegterm/, cache at ~/.cache/telegterm/
- Never commit .session files
- German UI strings
