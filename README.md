# TUI-for-Telegram

A full-featured Telegram client for the terminal, built with [Textual](https://textual.textualize.io/) and [Telethon](https://docs.telethon.dev/).

## Features

- **Real Telegram account** — Login with your phone number and 2FA
- **Full chat support** — Private chats, groups, supergroups, and channels
- **Real-time messaging** — Send and receive messages instantly
- **Inline images** — View photos directly in the terminal (Kitty/Sixel/Unicode)
- **Media support** — Thumbnails for photos, PDFs, and videos; open any file with system viewer
- **Copy to clipboard** — Copy message text or media paths with keyboard shortcuts
- **Keyboard-driven** — Vim-style navigation (j/k), plus full mouse support
- **6 dark themes** — Tokyo Night, Catppuccin, Dracula, Nord, Gruvbox, One Dark
- **Typing indicators** — See when someone is typing
- **Search** — Find chats and messages

## Requirements

- Python 3.11+
- A Telegram account
- API credentials from [my.telegram.org](https://my.telegram.org)

### Optional system dependencies

- `poppler` — PDF thumbnail generation
- `ffmpeg` — Video thumbnail generation
- `xclip`/`xsel`/`wl-copy` — Clipboard support

```bash
# Arch Linux
sudo pacman -S poppler ffmpeg xclip

# Debian/Ubuntu
sudo apt install poppler-utils ffmpeg xclip
```

## Installation

```bash
git clone https://github.com/babafish12/TUI-for-Telegram.git
cd TUI-for-Telegram
```

### Global install (recommended on Arch Linux)

```bash
pipx install -e .
```

### Virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
telegterm
```

On first run, you'll be prompted to:
1. Enter your Telegram API credentials (get them from [my.telegram.org](https://my.telegram.org))
2. Login with your phone number
3. Enter the verification code sent by Telegram
4. Enter your 2FA password (if enabled)

Your session is saved at `~/.config/telegterm/` — you only need to login once.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `j` / `↓` | Next chat |
| `k` / `↑` | Previous chat |
| `Enter` | Open chat / Send message |
| `Tab` | Switch focus (sidebar ↔ input) |
| `/` | Search |
| `y` | Copy message text |
| `Y` | Copy media path |
| `i` | Chat info |
| `g` | Scroll to newest message |
| `T` | Cycle theme |
| `S` | Settings |
| `Escape` | Back to sidebar |
| `q` | Quit |

## Image Display

telegterm uses [textual-image](https://github.com/lnqs/textual-image) for inline image rendering with automatic protocol detection:

| Protocol | Quality | Terminals |
|----------|---------|-----------|
| Kitty Graphics | Pixel-perfect | Kitty, WezTerm |
| Sixel | High | xterm, foot, mlterm, WezTerm |
| Unicode halfblock | Low-res | All terminals |

## Media Handling

| Type | Display | Action |
|------|---------|--------|
| Photos | Inline thumbnail | Full-screen viewer |
| Stickers | Rendered as image | Full-screen viewer |
| PDFs | First page thumbnail | Open with system viewer |
| Videos | First frame thumbnail | Open with system viewer |
| Audio/Voice | Duration label | Open with system player |
| Documents | Name + size | Download + open |
| GIFs | First frame | Open with system viewer |

## Configuration

Config is stored at `~/.config/telegterm/config.json`:

```json
{
  "api_id": 12345,
  "api_hash": "your_api_hash",
  "theme": "tokyo-night",
  "notifications_enabled": true,
  "media_auto_download": true,
  "message_load_limit": 50
}
```

Media cache is at `~/.cache/telegterm/`.

## Themes

Switch themes with `T` or in settings (`S`):

- Tokyo Night (default)
- Catppuccin Mocha
- Dracula
- Nord
- Gruvbox Dark
- One Dark

## Changelog

### 0.1.0 (2026-03-17)
- Initial release
- Telegram login with phone + 2FA
- Chat list with unread counts
- Real-time messaging
- Inline image display (Kitty/Sixel/Unicode)
- PDF and video thumbnail generation
- Clipboard support (copy message text / media paths)
- 6 dark themes
- Keyboard shortcuts + mouse support
- Search (chats + messages)
- Typing indicators
- Settings screen
