<h6 align="center">
  <img src="https://raw.githubusercontent.com/edubr029/piics/master/i/014.png" alt="LyricsPy" height="250px">
  <h5 align="center">This bot displays song lyrics according to your search.</h5>
</h6>

## Requirements

- Python 3.10+
- [Playwright](https://playwright.dev/python/)
- [Hydrogram](https://github.com/pyrogram/hydrogrampy)
- [Spotipy](https://spotipy.readthedocs.io/)
- [Pillow](https://python-pillow.org/)
- Other dependencies listed in requirements.txt

## Installation

```bash
git clone https://github.com/AmanoTeam/LyricsPyRobot.git
cd LyricsPyRobot
playwright install
```

## Features

- Search for song lyrics from Spotify and Last.fm
- Multi-language support
- Generate custom artwork with album cover
- Interactive commands and WebApp integration for login
- Sticker support and Telegraph view

## Configuration

1. Copy `config.example.py` to `config.py` and fill in your credentials:
   - Telegram `API_ID`, `API_HASH`, `TOKEN`
   - Spotify and Last.fm credentials
   - Other required keys

2. Install dependencies and Playwright:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

## Usage

1. Configure your `config.py` with your credentials.
2. Run the bot:
   ```bash
   python -m lyricspybot
   ```

## Commands

- `/spoti` - shows the current Spotify song lyrics
- `/lfm` - shows the current Last.fm song lyrics
- `/lyrics` - search for lyrics
- `/np` - shows what is currently playing
- `/privacy` - manage your data and privacy

## Support

For questions or suggestions, open an issue or contact us on Telegram.
Para dúvidas ou sugestões, abra uma issue ou entre em contato pelo Telegram.