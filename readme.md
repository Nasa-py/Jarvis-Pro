# 🤖 JARVIS Pro V4.1 — Advanced AI Voice Assistant

> A fully-featured desktop voice assistant inspired by Iron Man's JARVIS.  
> Control your entire computer with just your voice or text commands.

---

## ✨ Features

- 🎤 **Voice & Text Control** — speak or type commands
- 🚀 **Smart App Launcher** — opens any installed app reliably (searches PATH, common dirs, Windows Registry)
- 🔴 **App Closer** — close any running app by name
- 🖥️ **Full System Control** — lock, shutdown, restart, sleep, screenshot
- 🌐 **Browser Control** — close tab, new tab, go back, refresh, zoom
- 📂 **File Management** — create, delete, rename, list, open files and folders
- 🔊 **Smart Volume** — set exact % (`volume 50`, `volume down to 30`)
- 🎵 **Media Controls** — play/pause, next/previous track, mute
- ⌨️ **Keyboard Shortcuts** — copy, paste, undo, save, find by voice
- 🌤️ **Weather** — live weather for any city
- 📰 **News** — top headlines (works with or without API key via RSS)
- 📖 **Wikipedia** — instant summaries
- 🔍 **Web Search** — Google, YouTube, and 15+ quick-open websites
- ⏱️ **Timer** — set any duration, get alerted when done
- 📝 **Notes and Reminders** — save and read back
- 🧮 **Calculator** — natural language math
- 🤖 **Claude AI Brain** — natural conversation (optional, needs API key)
- 📊 **Live System Monitor** — CPU, RAM, Disk bars in the sidebar
- ⏹️ **Stop Button** — silence JARVIS instantly anytime

---

## 🚀 Quick Start

### 1. Clone or download
```
git clone https://github.com/yourusername/jarvis-pro
cd jarvis-pro
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

> **Windows users:** If you want exact % volume control, also run:
> ```
> pip install pycaw comtypes
> ```

### 3. Set up API keys (optional but recommended)
Create a `.env` file in the same folder as `jarvis_pro_v4.py`:
```
WEATHER_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

| Key | Where to get it | Cost |
|-----|----------------|------|
| `WEATHER_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) | Free |
| `NEWS_API_KEY` | [newsapi.org](https://newsapi.org) | Free |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Paid |

> **Note:** News works without an API key too. JARVIS falls back to free RSS feeds from BBC, Times of India, and NYT automatically.

### 4. Run
```
python jarvis_pro_v4.py
```

---

## 🗣️ Voice Commands

### 🕐 Time and Date
| Command | Result |
|---------|--------|
| `what time is it` | Current time |
| `what is today's date` | Today's date |

### 🚀 Open Apps
| Command | Result |
|---------|--------|
| `open file explorer` | Opens Windows Explorer |
| `open chrome` | Opens Google Chrome |
| `open firefox` | Opens Firefox |
| `open notepad` | Opens Notepad |
| `open calculator` | Opens Calculator |
| `open discord` | Opens Discord |
| `open spotify` | Opens Spotify |
| `open vs code` | Opens VS Code |
| `open word` | Opens Microsoft Word |
| `open excel` | Opens Microsoft Excel |
| `open task manager` | Opens Task Manager |
| `open settings` | Opens Windows Settings |
| `launch <any app>` | Opens any installed app |

### 🔴 Close Apps
| Command | Result |
|---------|--------|
| `close chrome` | Kills Chrome |
| `close spotify` | Kills Spotify |
| `close discord` | Kills Discord |
| `close notepad` | Kills Notepad |
| `close <any app>` | Kills that app's process |
| `kill firefox` | Force kills Firefox |
| `force close zoom` | Force kills Zoom |

### 🔊 Smart Volume
| Command | Result |
|---------|--------|
| `volume 50` | Sets volume to exactly 50% |
| `set volume to 70` | Sets volume to 70% |
| `volume down to 30` | Lowers volume to 30% |
| `volume up to 80` | Raises volume to 80% |
| `lower volume by 20` | Subtracts 20 from current volume |
| `increase volume by 10` | Adds 10 to current volume |
| `what's the volume` | Tells you current volume % |
| `volume up` | Nudges volume up one step |
| `volume down` | Nudges volume down one step |
| `mute` | Mutes system audio |

### 🌐 Browser Control
| Command | Result |
|---------|--------|
| `close tab` | Ctrl+W |
| `new tab` | Ctrl+T |
| `close window` | Alt+F4 |
| `go back` | Browser back |
| `go forward` | Browser forward |
| `reload` or `refresh` | Refreshes current page |
| `zoom in` | Zooms in |
| `zoom out` | Zooms out |

### 🌍 Websites
| Command | Result |
|---------|--------|
| `open youtube` | Opens YouTube |
| `open gmail` | Opens Gmail |
| `open instagram` | Opens Instagram |
| `open whatsapp web` | Opens WhatsApp Web |
| `open netflix` | Opens Netflix |
| `open github` | Opens GitHub |
| `open chatgpt` | Opens ChatGPT |
| `search for <query>` | Google search |
| `play <song or video>` | YouTube search |

### 📂 File Management
| Command | Result |
|---------|--------|
| `create file report.txt` | Creates file on Desktop |
| `create folder Projects` | Creates folder on Desktop |
| `delete file old.txt` | Deletes file from Desktop |
| `list files` | Lists Desktop contents |
| `open file notes.txt` | Opens a file |
| `rename file old.txt to new.txt` | Renames a file |
| `open downloads` | Opens Downloads folder |
| `open documents` | Opens Documents folder |
| `open pictures` | Opens Pictures folder |

### 📰 Info and Search
| Command | Result |
|---------|--------|
| `latest news` | Top headlines |
| `weather in Mumbai` | Live weather data |
| `tell me about Python` | Wikipedia summary |
| `who is Elon Musk` | Wikipedia lookup |

### 🖥️ System Control
| Command | Result |
|---------|--------|
| `lock screen` | Locks the PC |
| `shutdown` | Shuts down in 5 seconds |
| `restart` | Restarts in 5 seconds |
| `sleep` | Puts PC to sleep |
| `take screenshot` | Saves PNG to Desktop |
| `system info` | CPU, RAM, Disk, Battery status |
| `my ip address` | Shows local IP |

### 🎵 Media
| Command | Result |
|---------|--------|
| `play pause` | Play or pause media |
| `next song` | Skip to next track |
| `previous song` | Go to previous track |

### ⌨️ Keyboard Shortcuts
| Command | Result |
|---------|--------|
| `copy that` | Ctrl+C |
| `paste` | Ctrl+V |
| `undo` | Ctrl+Z |
| `save file` | Ctrl+S |
| `find on page` | Ctrl+F |
| `select all` | Ctrl+A |
| `minimize all` | Win+D (show desktop) |
| `switch window` | Alt+Tab |
| `snap left` | Win+Left |
| `snap right` | Win+Right |

### 🎮 Fun
| Command | Result |
|---------|--------|
| `tell me a joke` | Random programming joke |
| `motivate me` | Inspirational quote |
| `flip a coin` | Heads or tails |
| `roll a dice` | Random number 1 to 6 |
| `random number` | Random number 1 to 100 |

### 📝 Notes and Reminders
| Command | Result |
|---------|--------|
| `take a note: buy groceries` | Saves a note |
| `read my notes` | Reads your saved notes |
| `clear notes` | Deletes all notes |
| `remind me to call mom` | Saves a reminder |
| `show reminders` | Reads your reminders |

### ⏱️ Timer and Math
| Command | Result |
|---------|--------|
| `set timer for 5 minutes` | Countdown timer with alert |
| `calculate 25 times 4` | Returns 100 |
| `how much is 150 divided by 3` | Returns 50 |
| `what is the square root of 144` | Returns 12 |

---

## ⏹️ Stop Button

Hit the red **Stop Speaking** button in the sidebar at any time to instantly silence JARVIS mid-sentence. You can also say **"stop"**, **"be quiet"**, or **"shut up"**.

---

## 📁 Project Structure

```
jarvis-pro/
│
├── jarvis_pro_v4.py      <- Main application
├── requirements.txt      <- All dependencies
├── .env                  <- Your API keys (create this yourself)
├── README.md             <- This file
│
└── jarvis_data/          <- Auto-created on first run
    ├── notes.json        <- Your saved notes
    └── reminders.json    <- Your saved reminders
```

---

## ⚙️ System Requirements

- Python 3.9 or higher
- Windows 10/11 (primary target), macOS, or Linux
- Microphone (for voice commands)
- Speakers (for JARVIS to speak back)
- Internet connection (for weather, news, Wikipedia, search)

---

## 🔧 Troubleshooting

**JARVIS isn't speaking?**  
Make sure `pyttsx3` installed correctly. On Windows it uses SAPI5 built-in voices. Check Control Panel → Speech Recognition → Text to Speech to confirm a voice is installed.

**Microphone not working?**  
Install `pyaudio`. On Windows you may need:
```
pip install pipwin
pipwin install pyaudio
```

**Volume % control not working?**  
Install pycaw for direct Windows volume control:
```
pip install pycaw comtypes
```

**App won't open?**  
Make sure the app is installed on your system. JARVIS searches common install paths and the Windows Registry automatically. Try using the full app name if a short name doesn't work.

**pyautogui fails on startup?**  
```
pip install pyautogui
```

**Getting a ModuleNotFoundError?**  
Run the full install again:
```
pip install -r requirements.txt
```

---

## 🤖 AI Conversation

Add your `ANTHROPIC_API_KEY` to `.env` to enable natural conversation powered by Claude. Any command JARVIS doesn't recognise as a system command gets sent to Claude for a smart, context-aware reply. JARVIS remembers the last 20 messages for context.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---
