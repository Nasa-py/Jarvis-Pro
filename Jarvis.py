"""
JARVIS Pro V4.1 — Advanced AI Voice Assistant
==============================================
• Bulletproof app launcher (searches paths + Windows Registry)
• Opens File Explorer, Firefox, Chrome, Notepad etc. RELIABLY
• Full system control: close tab, lock, shutdown, volume, media
• File ops: create / delete / rename / list / open
• Weather, News, Wikipedia, Web search, YouTube
• Timer, Notes, Reminders, Calculator, Screenshot
• Claude AI brain for natural conversation
==============================================
"""

import customtkinter as ctk
import datetime
from dotenv import load_dotenv
import webbrowser
import os, sys, random, time, threading, requests, json, psutil
import wikipedia
from pathlib import Path
import queue, re, subprocess, platform, shutil

load_dotenv()

# ── Auto-install ──────────────────────────────────────────────────────────────
_PKGS = ["pyttsx3","SpeechRecognition","pyaudio","pillow","psutil",
         "wikipedia","requests","python-dotenv","customtkinter","anthropic","pyautogui"]
for _p in _PKGS:
    try: __import__(_p.replace("-","_").split(">=")[0])
    except ImportError: os.system(f'"{sys.executable}" -m pip install {_p} -q')

import pyttsx3
import speech_recognition as sr

try:
    import anthropic as _asdk
    CLAUDE_OK = True
except ImportError:
    CLAUDE_OK = False

# ── Palette ───────────────────────────────────────────────────────────────────
C = {
    'bg':'#080c1e','bg2':'#111530','card':'#181d3a','card2':'#1e2445',
    'accent':'#00d4ff','acc2':'#0099bb',
    'green':'#00ff88','green2':'#00bb66',
    'yellow':'#ffcc00','red':'#ff3366','red2':'#cc2244',
    'purple':'#a855f7','text':'#d0d0d0','textdim':'#666680',
    'white':'#ffffff','gold':'#ffd700',
}
GREETINGS = [
    "Hello Sir! JARVIS V4 online. What can I do for you?",
    "Good day. All systems operational. Ready to assist.",
    "JARVIS online. Full system control activated.",
]
WAKE_WORDS = ["jarvis","hey jarvis","ok jarvis"]
OS_TYPE = platform.system()   # 'Windows' / 'Darwin' / 'Linux'


def _m(text: str, keywords: list) -> bool:
    return any(k in text for k in keywords)


# ╔══════════════════════════════════════════════════════════════╗
# ║             BULLETPROOF APP LAUNCHER                        ║
# ╚══════════════════════════════════════════════════════════════╝
class AppLauncher:
    """
    Multi-strategy launcher.
    Windows order: PATH -> common dirs -> Registry -> shell=True
    """

    # key: user phrase -> ([win exes], mac app name, linux cmd)
    APPS = {
        'file explorer':   (['explorer.exe'],                                       'Finder',                'nautilus'),
        'file manager':    (['explorer.exe'],                                       'Finder',                'nautilus'),
        'explorer':        (['explorer.exe'],                                       'Finder',                'nautilus'),
        'files':           (['explorer.exe'],                                       'Finder',                'nautilus'),
        'notepad':         (['notepad.exe'],                                        'TextEdit',              'gedit'),
        'wordpad':         (['wordpad.exe','write.exe'],                            'TextEdit',              'gedit'),
        'calculator':      (['calc.exe'],                                           'Calculator',            'gnome-calculator'),
        'paint':           (['mspaint.exe'],                                        'Preview',               'pinta'),
        'snipping tool':   (['SnippingTool.exe','SnipSketch.exe'],                  'Screenshot',            'gnome-screenshot'),
        'task manager':    (['Taskmgr.exe'],                                        'Activity Monitor',      'gnome-system-monitor'),
        'control panel':   (['control.exe'],                                        'System Preferences',    'gnome-control-center'),
        'settings':        (['ms-settings:'],                                       'System Preferences',    'gnome-control-center'),
        'device manager':  (['devmgmt.msc'],                                        'System Information',    ''),
        'registry':        (['regedit.exe'],                                        '',                      ''),
        'cmd':             (['cmd.exe'],                                            'Terminal',              'gnome-terminal'),
        'command prompt':  (['cmd.exe'],                                            'Terminal',              'gnome-terminal'),
        'powershell':      (['powershell.exe','pwsh.exe'],                          'Terminal',              'bash'),
        'terminal':        (['wt.exe','cmd.exe'],                                   'Terminal',              'gnome-terminal'),
        'chrome':          (['chrome.exe'],                                         'Google Chrome',         'google-chrome'),
        'google chrome':   (['chrome.exe'],                                         'Google Chrome',         'google-chrome'),
        'firefox':         (['firefox.exe'],                                        'Firefox',               'firefox'),
        'mozilla':         (['firefox.exe'],                                        'Firefox',               'firefox'),
        'edge':            (['msedge.exe'],                                         'Microsoft Edge',        'microsoft-edge'),
        'microsoft edge':  (['msedge.exe'],                                         'Microsoft Edge',        'microsoft-edge'),
        'opera':           (['opera.exe','launcher.exe'],                           'Opera',                 'opera'),
        'brave':           (['brave.exe'],                                          'Brave Browser',         'brave-browser'),
        'internet explorer':(['iexplore.exe'],                                      'Safari',                ''),
        'browser':         (['chrome.exe','msedge.exe','firefox.exe'],              'Safari',                'firefox'),
        'vlc':             (['vlc.exe'],                                            'VLC',                   'vlc'),
        'media player':    (['wmplayer.exe'],                                       'QuickTime Player',      'vlc'),
        'windows media':   (['wmplayer.exe'],                                       'QuickTime Player',      'vlc'),
        'spotify':         (['Spotify.exe'],                                        'Spotify',               'spotify'),
        'itunes':          (['iTunes.exe'],                                         'Music',                 ''),
        'steam':           (['steam.exe'],                                          'Steam',                 'steam'),
        'discord':         (['Discord.exe','Update.exe'],                           'Discord',               'discord'),
        'telegram':        (['Telegram.exe'],                                       'Telegram',              'telegram-desktop'),
        'whatsapp':        (['WhatsApp.exe'],                                       'WhatsApp',              'whatsapp-desktop'),
        'zoom':            (['Zoom.exe'],                                           'zoom.us',               'zoom'),
        'teams':           (['Teams.exe'],                                          'Microsoft Teams',       'teams'),
        'microsoft teams': (['Teams.exe'],                                          'Microsoft Teams',       'teams'),
        'skype':           (['Skype.exe'],                                          'Skype',                 'skype'),
        'slack':           (['slack.exe'],                                          'Slack',                 'slack'),
        'vscode':          (['Code.exe'],                                           'Visual Studio Code',    'code'),
        'vs code':         (['Code.exe'],                                           'Visual Studio Code',    'code'),
        'visual studio code':(['Code.exe'],                                         'Visual Studio Code',    'code'),
        'visual studio':   (['devenv.exe'],                                         'Xcode',                 'code'),
        'pycharm':         (['pycharm64.exe','pycharm.exe'],                        'PyCharm',               'pycharm'),
        'android studio':  (['studio64.exe'],                                       'Android Studio',        'android-studio'),
        'word':            (['WINWORD.EXE'],                                        'Microsoft Word',        'libreoffice --writer'),
        'microsoft word':  (['WINWORD.EXE'],                                        'Microsoft Word',        'libreoffice --writer'),
        'excel':           (['EXCEL.EXE'],                                          'Microsoft Excel',       'libreoffice --calc'),
        'microsoft excel': (['EXCEL.EXE'],                                          'Microsoft Excel',       'libreoffice --calc'),
        'powerpoint':      (['POWERPNT.EXE'],                                       'Microsoft PowerPoint',  'libreoffice --impress'),
        'outlook':         (['OUTLOOK.EXE'],                                        'Mail',                  'thunderbird'),
        'onenote':         (['ONENOTE.EXE'],                                        'Notes',                 ''),
        'one note':        (['ONENOTE.EXE'],                                        'Notes',                 ''),
        'photoshop':       (['Photoshop.exe'],                                      'Photoshop',             'gimp'),
        'gimp':            (['gimp-2.10.exe','gimp.exe'],                           'GIMP',                  'gimp'),
        'obs':             (['obs64.exe','obs.exe'],                                'OBS',                   'obs'),
        '7zip':            (['7zFM.exe'],                                           'Archive Utility',       'file-roller'),
        'winrar':          (['WinRAR.exe'],                                         'Archive Utility',       'file-roller'),
        'notepad++':       (['notepad++.exe'],                                      'TextEdit',              'notepadqq'),
        'tor':             (['firefox.exe'],                                        'Tor Browser',           'tor-browser'),
        'torrent':         (['uTorrent.exe','BitTorrent.exe','qbittorrent.exe'],    'qBittorrent',           'qbittorrent'),
    }

    WIN_PATHS = [
        r"C:\Windows\System32",
        r"C:\Windows",
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expandvars(r"%LOCALAPPDATA%"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
        os.path.expandvars(r"%APPDATA%"),
        # Common specific locations
        r"C:\Program Files\Google\Chrome\Application",
        r"C:\Program Files (x86)\Google\Chrome\Application",
        r"C:\Program Files\Mozilla Firefox",
        r"C:\Program Files (x86)\Mozilla Firefox",
        r"C:\Program Files\Microsoft VS Code",
        r"C:\Program Files (x86)\Microsoft VS Code",
        r"C:\Program Files\Discord",
        os.path.expandvars(r"%LOCALAPPDATA%\Discord"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code"),
        os.path.expandvars(r"%APPDATA%\Spotify"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera"),
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        r"C:\Program Files\VideoLAN\VLC",
        r"C:\Program Files (x86)\VideoLAN\VLC",
        r"C:\Program Files\WinRAR",
        r"C:\Program Files (x86)\WinRAR",
        r"C:\Program Files\7-Zip",
        r"C:\Program Files (x86)\7-Zip",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Teams"),
    ]

    def _win_find(self, exe_names):
        # 1. shutil.which (checks PATH)
        for name in exe_names:
            found = shutil.which(name)
            if found:
                return found

        # 2. Search common directories
        for base_str in self.WIN_PATHS:
            try:
                base = Path(base_str)
                if not base.exists():
                    continue
                for name in exe_names:
                    # Direct
                    p = base / name
                    if p.exists():
                        return str(p)
                    # One level deep
                    try:
                        for sub in base.iterdir():
                            if sub.is_dir():
                                p2 = sub / name
                                if p2.exists():
                                    return str(p2)
                    except:
                        pass
            except:
                pass

        # 3. Windows Registry
        if OS_TYPE == 'Windows':
            try:
                import winreg
                for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                    for rpath in [
                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
                    ]:
                        for name in exe_names:
                            try:
                                key = winreg.OpenKey(root, f"{rpath}\\{name}")
                                val, _ = winreg.QueryValueEx(key, "")
                                winreg.CloseKey(key)
                                if val and Path(val).exists():
                                    return val
                            except:
                                pass
            except:
                pass

        return None

    def launch(self, user_input: str):
        inp = user_input.lower().strip()
        # Remove filler
        inp = re.sub(r'^(the|a|an)\s+', '', inp)

        matched_key = None
        matched_val = None
        # Longest key match first (more specific wins)
        for key in sorted(self.APPS.keys(), key=len, reverse=True):
            if key in inp:
                matched_key = key
                matched_val = self.APPS[key]
                break

        # ── Windows ──────────────────────────────────────────────
        if OS_TYPE == 'Windows':
            exe_names = matched_val[0] if matched_val else [inp + '.exe', inp]

            # ms-settings: special protocol
            if exe_names and exe_names[0].startswith('ms-'):
                try:
                    os.startfile(exe_names[0])
                    return True, f"Opened {matched_key or inp}"
                except:
                    pass

            # .msc files
            if exe_names and exe_names[0].endswith('.msc'):
                try:
                    subprocess.Popen(['mmc', exe_names[0]])
                    return True, f"Opened {matched_key or inp}"
                except:
                    pass

            # Try to find and launch
            path = self._win_find(exe_names)
            if path:
                try:
                    os.startfile(path)
                    return True, f"Opened {matched_key or inp}"
                except:
                    try:
                        subprocess.Popen([path])
                        return True, f"Opened {matched_key or inp}"
                    except:
                        pass

            # Last resort: shell=True with original name
            try:
                subprocess.Popen(exe_names[0], shell=True)
                return True, f"Tried to open {matched_key or inp}"
            except:
                # One more try: the raw user input
                try:
                    subprocess.Popen(inp, shell=True)
                    return True, f"Tried to open {inp}"
                except:
                    pass

            return False, f"Couldn't find {inp}. Make sure it's installed."

        # ── macOS ─────────────────────────────────────────────────
        elif OS_TYPE == 'Darwin':
            mac_name = matched_val[1] if matched_val else inp
            try:
                subprocess.Popen(['open', '-a', mac_name])
                return True, f"Opened {mac_name}"
            except:
                try:
                    subprocess.Popen(['open', inp])
                    return True, f"Tried to open {inp}"
                except:
                    return False, f"Couldn't open {inp}"

        # ── Linux ──────────────────────────────────────────────────
        else:
            linux_cmd = (matched_val[2] if matched_val else inp) or inp
            try:
                subprocess.Popen(linux_cmd.split())
                return True, f"Opened {matched_key or inp}"
            except:
                found = shutil.which(linux_cmd.split()[0])
                if found:
                    try:
                        subprocess.Popen([found])
                        return True, f"Opened {inp}"
                    except:
                        pass
                return False, f"Couldn't open {inp}"


# ╔══════════════════════════════════════════════════════════════╗
# ║                  SYSTEM CONTROLLER                          ║
# ╚══════════════════════════════════════════════════════════════╝
class SystemController:
    def __init__(self):
        self.launcher = AppLauncher()

    def _hk(self, *keys):
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            return True
        except:
            return False

    # Window / browser
    def close_tab(self):      return self._hk('command','w') if OS_TYPE=='Darwin' else self._hk('ctrl','w'), "ok"
    def new_tab(self):        return self._hk('command','t') if OS_TYPE=='Darwin' else self._hk('ctrl','t'), "ok"
    def close_window(self):   return self._hk('command','q') if OS_TYPE=='Darwin' else self._hk('alt','f4'), "ok"
    def reload(self):         return self._hk('command','r') if OS_TYPE=='Darwin' else self._hk('ctrl','r'), "ok"
    def go_back(self):        return self._hk('command','[') if OS_TYPE=='Darwin' else self._hk('alt','left'), "ok"
    def go_forward(self):     return self._hk('command',']') if OS_TYPE=='Darwin' else self._hk('alt','right'), "ok"
    def zoom_in(self):        return self._hk('command','+') if OS_TYPE=='Darwin' else self._hk('ctrl','+'), "ok"
    def zoom_out(self):       return self._hk('command','-') if OS_TYPE=='Darwin' else self._hk('ctrl','-'), "ok"
    def minimize_all(self):
        if OS_TYPE=='Windows':   return self._hk('win','d'), "ok"
        elif OS_TYPE=='Darwin':  return self._hk('command','option','h','m'), "ok"
        else:                    return self._hk('ctrl','alt','d'), "ok"
    def maximize(self):       return self._hk('win','up') if OS_TYPE=='Windows' else False, "ok"
    def switch_win(self):     return self._hk('command','tab') if OS_TYPE=='Darwin' else self._hk('alt','tab'), "ok"
    def snap_left(self):      return self._hk('win','left') if OS_TYPE=='Windows' else False, "ok"
    def snap_right(self):     return self._hk('win','right') if OS_TYPE=='Windows' else False, "ok"
    def task_view(self):      return self._hk('win','tab') if OS_TYPE=='Windows' else False, "ok"
    def select_all(self):     return self._hk('command','a') if OS_TYPE=='Darwin' else self._hk('ctrl','a'), "ok"
    def copy(self):           return self._hk('command','c') if OS_TYPE=='Darwin' else self._hk('ctrl','c'), "ok"
    def paste(self):          return self._hk('command','v') if OS_TYPE=='Darwin' else self._hk('ctrl','v'), "ok"
    def undo(self):           return self._hk('command','z') if OS_TYPE=='Darwin' else self._hk('ctrl','z'), "ok"
    def save(self):           return self._hk('command','s') if OS_TYPE=='Darwin' else self._hk('ctrl','s'), "ok"
    def find(self):           return self._hk('command','f') if OS_TYPE=='Darwin' else self._hk('ctrl','f'), "ok"

    # App open
    def open_app(self, name): return self.launcher.launch(name)

    # App close
    CLOSE_MAP = {
        'chrome':        ['chrome.exe','Google Chrome'],
        'google chrome': ['chrome.exe','Google Chrome'],
        'firefox':       ['firefox.exe','firefox'],
        'edge':          ['msedge.exe'],
        'opera':         ['opera.exe'],
        'brave':         ['brave.exe'],
        'file explorer': ['explorer.exe'],
        'explorer':      ['explorer.exe'],
        'notepad':       ['notepad.exe'],
        'notepad++':     ['notepad++.exe'],
        'calculator':    ['calc.exe','Calculator.exe'],
        'paint':         ['mspaint.exe'],
        'task manager':  ['Taskmgr.exe'],
        'cmd':           ['cmd.exe'],
        'powershell':    ['powershell.exe','pwsh.exe'],
        'terminal':      ['wt.exe','cmd.exe'],
        'spotify':       ['Spotify.exe','spotify'],
        'discord':       ['Discord.exe','discord'],
        'telegram':      ['Telegram.exe'],
        'whatsapp':      ['WhatsApp.exe'],
        'zoom':          ['Zoom.exe'],
        'teams':         ['Teams.exe'],
        'skype':         ['Skype.exe'],
        'slack':         ['slack.exe'],
        'vscode':        ['Code.exe'],
        'vs code':       ['Code.exe'],
        'visual studio': ['devenv.exe'],
        'word':          ['WINWORD.EXE'],
        'excel':         ['EXCEL.EXE'],
        'powerpoint':    ['POWERPNT.EXE'],
        'outlook':       ['OUTLOOK.EXE'],
        'onenote':       ['ONENOTE.EXE'],
        'vlc':           ['vlc.exe','vlc'],
        'steam':         ['steam.exe'],
        'obs':           ['obs64.exe','obs.exe'],
        'photoshop':     ['Photoshop.exe'],
        'gimp':          ['gimp-2.10.exe','gimp.exe'],
        'pycharm':       ['pycharm64.exe','pycharm.exe'],
        'winrar':        ['WinRAR.exe'],
        '7zip':          ['7zFM.exe'],
        'snipping tool': ['SnippingTool.exe','SnipSketch.exe'],
    }

    def close_app(self, user_input: str):
        """Kill all processes matching the app name."""
        inp = user_input.lower().strip()
        inp = re.sub(r'^(the|a|an)\s+', '', inp)

        exe_names = None
        matched_key = inp
        for key in sorted(self.CLOSE_MAP.keys(), key=len, reverse=True):
            if key in inp:
                exe_names = self.CLOSE_MAP[key]
                matched_key = key
                break

        if not exe_names:
            exe_names = [inp, inp + '.exe']

        killed = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                pname = proc.info['name']
                if pname and any(pname.lower() == e.lower() for e in exe_names):
                    proc.kill()
                    killed.append(pname)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if killed:
            return True, f"Closed {matched_key}."
        else:
            return False, f"I couldn't find {matched_key} running. It may already be closed."

    # Files
    def _desk(self):          return Path.home()/"Desktop"
    def _path(self, name, loc): return (Path(loc) if loc else self._desk()) / name

    def create_file(self, name, loc=None):
        try:
            p = self._path(name, loc); p.parent.mkdir(parents=True, exist_ok=True); p.touch()
            return True, f"Created file '{name}' on your Desktop."
        except Exception as e: return False, f"Could not create: {e}"

    def create_folder(self, name, loc=None):
        try:
            p = self._path(name, loc); p.mkdir(parents=True, exist_ok=True)
            return True, f"Created folder '{name}' on your Desktop."
        except Exception as e: return False, f"Could not create: {e}"

    def delete_item(self, name, loc=None):
        try:
            p = self._path(name, loc)
            if not p.exists(): return False, f"'{name}' not found on Desktop."
            if p.is_file(): p.unlink()
            else: shutil.rmtree(p)
            return True, f"Deleted '{name}'."
        except Exception as e: return False, f"Could not delete: {e}"

    def rename_item(self, old, new, loc=None):
        try:
            base = Path(loc) if loc else self._desk()
            (base/old).rename(base/new)
            return True, f"Renamed '{old}' to '{new}'."
        except Exception as e: return False, f"Could not rename: {e}"

    def list_files(self, loc=None):
        try:
            p = Path(loc) if loc else self._desk()
            items = sorted(p.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            return True, [i.name for i in items[:12]]
        except: return False, []

    def open_file(self, name, loc=None):
        try:
            p = self._path(name, loc)
            if OS_TYPE=='Windows':  os.startfile(str(p))
            elif OS_TYPE=='Darwin': subprocess.Popen(['open', str(p)])
            else:                   subprocess.Popen(['xdg-open', str(p)])
            return True, f"Opened '{name}'."
        except Exception as e: return False, f"Could not open: {e}"

    def open_folder(self, loc=None):
        try:
            p = str(Path(loc) if loc else self._desk())
            if OS_TYPE=='Windows':  os.startfile(p)
            elif OS_TYPE=='Darwin': subprocess.Popen(['open', p])
            else:                   subprocess.Popen(['xdg-open', p])
            return True, "Opened folder."
        except Exception as e: return False, str(e)

    # System
    def lock_screen(self):
        try:
            if OS_TYPE=='Windows':   subprocess.run(["rundll32.exe","user32.dll,LockWorkStation"])
            elif OS_TYPE=='Darwin':  subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession","-suspend"])
            else:                    subprocess.run(["gnome-screensaver-command","-l"])
            return True, "ok"
        except: return False, "Could not lock."

    def sleep_pc(self):
        try:
            if OS_TYPE=='Windows':   subprocess.run(["rundll32.exe","powrprof.dll,SetSuspendState","0","1","0"])
            elif OS_TYPE=='Darwin':  subprocess.run(["pmset","sleepnow"])
            return True, "ok"
        except: return False, "Could not sleep."

    def shutdown(self):
        if OS_TYPE=='Windows':   os.system("shutdown /s /t 5")
        elif OS_TYPE=='Darwin':  os.system("sudo shutdown -h now")
        else:                    os.system("shutdown -h now")

    def restart(self):
        if OS_TYPE=='Windows':   os.system("shutdown /r /t 5")
        elif OS_TYPE=='Darwin':  os.system("sudo shutdown -r now")
        else:                    os.system("sudo reboot")

    def get_stats(self):
        cpu  = psutil.cpu_percent(interval=0.5)
        ram  = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        bat  = psutil.sensors_battery()
        return {
            'cpu': cpu, 'ram_pct': ram.percent,
            'ram_used': ram.used//(1024**3), 'ram_total': ram.total//(1024**3),
            'disk_pct': disk.percent,
            'disk_used': disk.used//(1024**3), 'disk_total': disk.total//(1024**3),
            'battery': f"{bat.percent:.0f}%" if bat else "No battery",
            'bat_charging': bat.power_plugged if bat else False,
        }

    # Volume / media
    def get_volume(self):
        """Get current system volume (0-100). Windows only via pycaw/ctypes."""
        if OS_TYPE == 'Windows':
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                # scalar 0.0 - 1.0
                return int(volume.GetMasterVolumeLevelScalar() * 100)
            except:
                pass
        return None

    def set_volume(self, percent: int):
        """Set system volume to exact percent (0-100)."""
        percent = max(0, min(100, percent))
        if OS_TYPE == 'Windows':
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(percent / 100.0, None)
                return True, percent
            except ImportError:
                # pycaw not installed — install it then retry
                import subprocess, sys
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pycaw', 'comtypes', '-q'])
                try:
                    from ctypes import cast, POINTER
                    from comtypes import CLSCTX_ALL
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume.SetMasterVolumeLevelScalar(percent / 100.0, None)
                    return True, percent
                except:
                    pass
            except:
                pass
            # Fallback: use nircmd if available, else PowerShell
            try:
                nircmd_val = int(percent / 100 * 65535)
                subprocess.run(['nircmd.exe', 'setsysvolume', str(nircmd_val)], 
                               capture_output=True)
                return True, percent
            except:
                pass
            try:
                ps_cmd = f"$obj = New-Object -ComObject WScript.Shell; "                          f"for($i=0;$i -lt 50;$i++){{$obj.SendKeys([char]174)}}; "                          f"$steps=[Math]::Round({percent}/2); "                          f"for($i=0;$i -lt $steps;$i++){{$obj.SendKeys([char]175)}}"
                subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
                return True, percent
            except:
                return False, percent

        elif OS_TYPE == 'Darwin':
            try:
                subprocess.run(['osascript', '-e', f'set volume output volume {percent}'])
                return True, percent
            except:
                return False, percent
        else:
            try:
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f'{percent}%'])
                return True, percent
            except:
                return False, percent

    def vol_up(self):      return self._hk('volumeup') if OS_TYPE=='Windows' else self._hk('f12'), "ok"
    def vol_down(self):    return self._hk('volumedown') if OS_TYPE=='Windows' else self._hk('f11'), "ok"
    def mute(self):        return self._hk('volumemute') if OS_TYPE=='Windows' else self._hk('f10'), "ok"
    def play_pause(self):  return self._hk('playpause'), "ok"
    def next_track(self):  return self._hk('nexttrack'), "ok"
    def prev_track(self):  return self._hk('prevtrack'), "ok"

    def screenshot(self):
        try:
            import pyautogui
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            path = self._desk() / f"screenshot_{ts}.png"
            pyautogui.screenshot(str(path))
            return True, f"Screenshot saved as 'screenshot_{ts}.png' on your Desktop."
        except Exception as e: return False, f"Screenshot failed: {e}"


# ╔══════════════════════════════════════════════════════════════╗
# ║                     JARVIS BRAIN                            ║
# ╚══════════════════════════════════════════════════════════════╝
class JarvisEngine:
    def __init__(self):
        self.active  = True
        self.sc      = SystemController()
        self.rq      = queue.Queue()
        self.history = []

        # TTS
        self.tts = pyttsx3.init()
        voices = self.tts.getProperty('voices')
        chosen = None
        for v in voices:
            if any(n in v.name.lower() for n in ['david','zira','mark','alex','james','george']):
                chosen = v.id; break
        if chosen:    self.tts.setProperty('voice', chosen)
        elif voices:  self.tts.setProperty('voice', voices[0].id)
        self.tts.setProperty('rate', 168)
        self.tts.setProperty('volume', 1.0)

        # STT
        self.rec = sr.Recognizer()
        self.rec.energy_threshold = 3500
        self.rec.dynamic_energy_threshold = True
        self.rec.pause_threshold = 0.8

        # Data
        self.data_dir = Path("jarvis_data")
        self.data_dir.mkdir(exist_ok=True)
        self._load()

        # Claude
        self.claude = None
        if CLAUDE_OK:
            key = os.getenv("ANTHROPIC_API_KEY","")
            if key:
                try: self.claude = _asdk.Anthropic(api_key=key)
                except: pass

        # ── Thread-safe TTS queue ─────────────────────────────
        # pyttsx3 MUST run on a single dedicated thread — calling
        # runAndWait() from random daemon threads crashes it silently.
        self._tts_q = queue.Queue()
        self._tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self._tts_thread.start()

    def _load(self):
        nf = self.data_dir/"notes.json"
        rf = self.data_dir/"reminders.json"
        self.notes     = json.loads(nf.read_text()) if nf.exists() else []
        self.reminders = json.loads(rf.read_text()) if rf.exists() else []

    def _save(self):
        try:
            (self.data_dir/"notes.json").write_text(json.dumps(self.notes, indent=2))
            (self.data_dir/"reminders.json").write_text(json.dumps(self.reminders, indent=2))
        except: pass

    def _tts_worker(self):
        """Dedicated thread that owns pyttsx3 — never call runAndWait elsewhere."""
        while True:
            text = self._tts_q.get()
            if text is None:
                break
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
                try:
                    self.tts = pyttsx3.init()
                    self.tts.setProperty('rate', 168)
                    self.tts.setProperty('volume', 1.0)
                except: pass
            finally:
                self._tts_q.task_done()

    def speak(self, text: str):
        """Thread-safe speak — any thread can call this."""
        print(f"[JARVIS] {text}")
        self.rq.put(('speak', text))
        self._tts_q.put(text)

    def stop_speaking(self):
        """Drain the TTS queue and stop current speech immediately."""
        # Drain pending items
        while not self._tts_q.empty():
            try: self._tts_q.get_nowait(); self._tts_q.task_done()
            except: break
        # Stop whatever is currently being spoken
        try: self.tts.stop()
        except: pass
        self.rq.put(('status', 'Stopped', C['red']))
        print("[JARVIS] Speech stopped.")

    def listen(self, timeout=6):
        try:
            with sr.Microphone() as src:
                self.rq.put(('status','Listening…',C['green']))
                self.rec.adjust_for_ambient_noise(src, duration=0.4)
                self.rq.put(('listening', True))
                audio = self.rec.listen(src, timeout=timeout, phrase_time_limit=12)
                self.rq.put(('listening', False))
            self.rq.put(('status','Processing…',C['yellow']))
            text = self.rec.recognize_google(audio).lower()
            self.rq.put(('user_said', text))
            return text
        except sr.WaitTimeoutError: return None
        except sr.UnknownValueError:
            self.rq.put(('status',"Couldn't hear you",C['red'])); return None
        except Exception: return None

    def ai_reply(self, text: str):
        if not self.claude: return None
        try:
            self.history.append({"role":"user","content":text})
            if len(self.history)>20: self.history = self.history[-20:]
            r = self.claude.messages.create(
                model="claude-sonnet-4-20250514", max_tokens=300,
                system=("You are JARVIS from Iron Man — sharp, efficient, friendly. "
                        "Reply in under 3 sentences. No markdown. Speak-ready."),
                messages=self.history
            )
            reply = r.content[0].text
            self.history.append({"role":"assistant","content":reply})
            return reply
        except: return None

    # ── MAIN COMMAND HANDLER ──────────────────────────────────
    def handle(self, raw: str):
        if not raw: return
        c = raw.lower().strip()
        for w in WAKE_WORDS:
            if c.startswith(w): c = c[len(w):].strip(); break
        if not c: return

        # ── WINDOW / BROWSER ─────────────────────────────────
        if   _m(c,['close tab','close this tab','close the tab']):
            self.speak("Closing the current tab."); self.sc.close_tab()

        elif _m(c,['new tab','open a new tab','open new tab']):
            self.speak("Opening a new tab."); self.sc.new_tab()

        elif _m(c,['close window','close this window','close the window']):
            self.speak("Closing this window."); self.sc.close_window()

        elif _m(c,['minimize all','show desktop','minimize everything','minimize windows']):
            self.speak("Minimizing everything and showing your desktop."); self.sc.minimize_all()

        elif _m(c,['maximize','maximize window','maximize the window','full screen','fullscreen']):
            self.speak("Maximizing the window."); self.sc.maximize()

        elif _m(c,['snap left','move window left']):
            self.speak("Snapping window to the left."); self.sc.snap_left()

        elif _m(c,['snap right','move window right']):
            self.speak("Snapping window to the right."); self.sc.snap_right()

        elif _m(c,['go back','browser back','previous page','back']):
            self.speak("Going back."); self.sc.go_back()

        elif _m(c,['go forward','next page','browser forward','forward']):
            self.speak("Going forward."); self.sc.go_forward()

        elif _m(c,['reload','refresh','refresh page','reload page']):
            self.speak("Refreshing the page."); self.sc.reload()

        elif _m(c,['switch window','switch app','alt tab','next window']):
            self.speak("Switching windows."); self.sc.switch_win()

        elif _m(c,['task view','show all windows','all windows']):
            self.speak("Opening task view."); self.sc.task_view()

        elif _m(c,['zoom in']):
            self.speak("Zooming in."); self.sc.zoom_in()

        elif _m(c,['zoom out']):
            self.speak("Zooming out."); self.sc.zoom_out()

        elif _m(c,['select all']):
            self.speak("Selecting all."); self.sc.select_all()

        elif _m(c,['copy that','copy it','copy this']):
            self.speak("Copying."); self.sc.copy()

        elif _m(c,['paste that','paste it','paste']):
            self.speak("Pasting."); self.sc.paste()

        elif _m(c,['undo that','undo','undo last']):
            self.speak("Undoing."); self.sc.undo()

        elif _m(c,['save this','save file','save document','save the file']):
            self.speak("Saving."); self.sc.save()

        elif _m(c,['find on page','search on page','find text']):
            self.speak("Opening find."); self.sc.find()

        # ── LOCK / POWER ──────────────────────────────────────
        elif _m(c,['lock screen','lock the screen','lock my computer','lock pc','lock computer']):
            self.speak("Locking your screen. See you soon!"); self.sc.lock_screen()

        elif _m(c,['sleep','put computer to sleep','sleep mode','hibernate','suspend']):
            self.speak("Putting your computer to sleep."); self.sc.sleep_pc()

        elif _m(c,['shutdown','shut down','turn off computer','power off']):
            self.speak("Shutting down in 5 seconds. Goodbye Sir!")
            threading.Thread(target=self.sc.shutdown, daemon=True).start()

        elif _m(c,['restart','reboot','restart computer']):
            self.speak("Restarting in 5 seconds.")
            threading.Thread(target=self.sc.restart, daemon=True).start()

        # ── VOLUME / MEDIA ────────────────────────────────────
        elif _m(c,['volume','increase volume','decrease volume','louder','quieter',
                    'turn it up','turn it down','turn volume','set volume',
                    'vol up','vol down','volume up','volume down','lower volume']):
            self._handle_volume(c)

        elif _m(c,['mute','mute the sound','mute audio','silence']):
            self.speak("Muting."); self.sc.mute()

        elif _m(c,['play pause','pause music','resume music','pause song','play music']):
            self.speak("Play pause."); self.sc.play_pause()

        elif _m(c,['next song','next track','skip song','skip','skip track']):
            self.speak("Skipping to the next track."); self.sc.next_track()

        elif _m(c,['previous song','previous track','last song','go back song','prev song']):
            self.speak("Going to the previous track."); self.sc.prev_track()

        # ── SCREENSHOT ───────────────────────────────────────
        elif _m(c,['screenshot','take screenshot','capture screen','capture the screen','screen capture']):
            self.speak("Taking a screenshot now.")
            ok, msg = self.sc.screenshot()
            self.speak(msg)

        # ── WEBSITES (check BEFORE generic "open") ────────────
        elif _m(c,['open youtube','go to youtube','go youtube']):
            self.speak("Opening YouTube."); webbrowser.open("https://youtube.com")

        elif _m(c,['open gmail','go to gmail','open my email','check my email']):
            self.speak("Opening Gmail."); webbrowser.open("https://gmail.com")

        elif _m(c,['open google','go to google']):
            self.speak("Opening Google."); webbrowser.open("https://google.com")

        elif _m(c,['open instagram','go to instagram']):
            self.speak("Opening Instagram."); webbrowser.open("https://instagram.com")

        elif _m(c,['open twitter','go to twitter','open x','go to x']):
            self.speak("Opening X."); webbrowser.open("https://x.com")

        elif _m(c,['open facebook','go to facebook']):
            self.speak("Opening Facebook."); webbrowser.open("https://facebook.com")

        elif _m(c,['open github','go to github']):
            self.speak("Opening GitHub."); webbrowser.open("https://github.com")

        elif _m(c,['open linkedin','go to linkedin']):
            self.speak("Opening LinkedIn."); webbrowser.open("https://linkedin.com")

        elif _m(c,['open netflix','go to netflix']):
            self.speak("Opening Netflix."); webbrowser.open("https://netflix.com")

        elif _m(c,['open amazon','go to amazon']):
            self.speak("Opening Amazon."); webbrowser.open("https://amazon.in")

        elif _m(c,['open reddit','go to reddit']):
            self.speak("Opening Reddit."); webbrowser.open("https://reddit.com")

        elif _m(c,['open whatsapp web','go to whatsapp']):
            self.speak("Opening WhatsApp Web."); webbrowser.open("https://web.whatsapp.com")

        elif _m(c,['open chatgpt','go to chatgpt']):
            self.speak("Opening ChatGPT."); webbrowser.open("https://chat.openai.com")

        elif _m(c,['open maps','go to google maps','google maps']):
            self.speak("Opening Google Maps."); webbrowser.open("https://maps.google.com")

        # ── CLOSE APP ─────────────────────────────────────────
        elif _m(c,['close chrome','close firefox','close edge','close opera','close brave',
                    'close notepad','close calculator','close paint','close task manager',
                    'close spotify','close discord','close telegram','close whatsapp',
                    'close zoom','close teams','close skype','close slack',
                    'close vscode','close vs code','close visual studio',
                    'close word','close excel','close powerpoint','close outlook',
                    'close vlc','close steam','close obs','close photoshop','close gimp',
                    'close explorer','close file explorer',
                    'kill ','force close ','terminate ']):
            # Extract app name
            app_name = c
            for trigger in ['force close ','terminate ','kill ']:
                if trigger in c:
                    app_name = c.split(trigger, 1)[1].strip()
                    break
            else:
                if c.startswith('close '):
                    app_name = c[6:].strip()
                elif 'close ' in c:
                    app_name = c.split('close ', 1)[1].strip()
            app_name = re.sub(r'^(the|a|an)\s+', '', app_name).strip()
            if not app_name:
                self.speak("Which app should I close?")
                return
            self.speak(f"Closing {app_name}.")
            ok, msg = self.sc.close_app(app_name)
            self.speak(msg)

        # ── OPEN APP ──────────────────────────────────────────
        elif _m(c,['open ','launch ','start ','run ']):
            app_name = c
            for trigger in ['launch ','start ','run ','open ']:
                if trigger in c:
                    app_name = c.split(trigger, 1)[1].strip()
                    break
            app_name = re.sub(r'^(the|a|an)\s+', '', app_name).strip()
            if not app_name:
                self.speak("Which app should I open?")
                return
            self.speak(f"Opening {app_name} right now.")
            ok, msg = self.sc.open_app(app_name)
            if not ok:
                self.speak(f"Sorry, I couldn't find {app_name}. Please make sure it's installed.")

        # ── FOLDERS ───────────────────────────────────────────
        elif _m(c,['open desktop','show desktop folder']):
            self.speak("Opening your Desktop folder."); self.sc.open_folder()

        elif _m(c,['open downloads','open the downloads folder','downloads folder']):
            self.speak("Opening Downloads."); self.sc.open_folder(str(Path.home()/"Downloads"))

        elif _m(c,['open documents','documents folder']):
            self.speak("Opening Documents."); self.sc.open_folder(str(Path.home()/"Documents"))

        elif _m(c,['open pictures','pictures folder']):
            self.speak("Opening Pictures."); self.sc.open_folder(str(Path.home()/"Pictures"))

        elif _m(c,['open music','music folder']):
            self.speak("Opening Music folder."); self.sc.open_folder(str(Path.home()/"Music"))

        elif _m(c,['open videos','videos folder']):
            self.speak("Opening Videos folder."); self.sc.open_folder(str(Path.home()/"Videos"))

        # ── FILES ─────────────────────────────────────────────
        elif _m(c,['create file','make file','new file','create a file','make a file']):
            name = re.sub(r'(create|make|new)\s+(a\s+)?file\s*(called|named)?\s*','',c).strip()
            if not name: self.speak("What should I name the file?"); return
            if '.' not in name: name += '.txt'
            self.speak(f"Creating file '{name}' on your Desktop.")
            ok, msg = self.sc.create_file(name); self.speak(msg)

        elif _m(c,['create folder','make folder','new folder','create a folder','make a folder','new directory']):
            name = re.sub(r'(create|make|new)\s+(a\s+)?folder\s*(called|named)?\s*|new directory\s*','',c).strip()
            if not name: self.speak("What should I name the folder?"); return
            self.speak(f"Creating folder '{name}' on your Desktop.")
            ok, msg = self.sc.create_folder(name); self.speak(msg)

        elif _m(c,['delete file','remove file','delete the file']):
            name = re.sub(r'(delete|remove)\s+(the\s+)?file\s*(called|named)?\s*','',c).strip()
            if not name: self.speak("Which file should I delete?"); return
            self.speak(f"Deleting '{name}' from your Desktop.")
            ok, msg = self.sc.delete_item(name); self.speak(msg)

        elif _m(c,['delete folder','remove folder','delete the folder']):
            name = re.sub(r'(delete|remove)\s+(the\s+)?folder\s*(called|named)?\s*','',c).strip()
            if not name: self.speak("Which folder?"); return
            self.speak(f"Deleting folder '{name}'.")
            ok, msg = self.sc.delete_item(name); self.speak(msg)

        elif _m(c,['list files','show files','files on desktop','what files','what\'s on desktop','list desktop']):
            self.speak("Checking your Desktop.")
            ok, files = self.sc.list_files()
            if ok and files:
                self.speak(f"Found {len(files)} items on your Desktop.")
                for i, f in enumerate(files[:5], 1): self.speak(f"{i}. {f}")
            else:
                self.speak("Desktop appears empty or I couldn't access it.")

        elif _m(c,['open file','open the file']):
            name = re.sub(r'open\s+(the\s+)?file\s*(called|named)?\s*','',c).strip()
            if name:
                self.speak(f"Opening '{name}'.")
                ok, msg = self.sc.open_file(name)
                if not ok: self.speak(msg)
            else:
                self.speak("Which file should I open?")

        elif _m(c,['rename file','rename the file','rename']):
            parts = re.split(r'\bto\b', re.sub(r'rename\s+(the\s+)?file\s*','',c), maxsplit=1)
            if len(parts)==2:
                old, new = parts[0].strip(), parts[1].strip()
                self.speak(f"Renaming '{old}' to '{new}'.")
                ok, msg = self.sc.rename_item(old, new); self.speak(msg)
            else:
                self.speak("Please say: rename file old name to new name.")

        # ── WEB / SEARCH ──────────────────────────────────────
        elif _m(c,['search for','google search','search google','search ']):
            q = re.sub(r'(search\s*for|google\s*search|search\s*google|search)\s*','',c).strip()
            if q:
                self.speak(f"Searching Google for {q}.")
                webbrowser.open(f"https://www.google.com/search?q={q.replace(' ','+')}")
            else: self.speak("What should I search for?")

        elif _m(c,['play ','play on youtube','youtube search']):
            q = re.sub(r'(play\s+on\s+youtube|youtube\s*search|play)\s*','',c).strip()
            if q:
                self.speak(f"Playing {q} on YouTube.")
                webbrowser.open(f"https://www.youtube.com/results?search_query={q.replace(' ','+')}")
            else: self.speak("What should I play?")

        # ── TIME / DATE (must be BEFORE wikipedia to avoid 'what is' clash) ──
        elif _m(c,['what time','current time','what is the time','tell me the time','time please','what\'s the time']):
            self.speak(f"It is {datetime.datetime.now().strftime('%I:%M %p')}.")

        elif _m(c,['what day is it','what is today','what is the date','today\'s date','current date',
                    'what\'s today','what day','what date','todays date']):
            self.speak(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}.")

        elif _m(c,['news','headlines','latest news','top stories','what\'s happening','top news']):
            self._news()

        elif _m(c,['weather','temperature','forecast','how hot','how cold','will it rain','is it raining']):
            city = re.sub(r'(weather|temperature|forecast|how hot|how cold|will it rain|is it raining)\s*(in|for|at|today)?\s*','',c).strip()
            self._weather(city or "Mumbai")

        # ── WIKIPEDIA (note: no bare 'what is' — too ambiguous) ──────────────
        elif _m(c,['wikipedia','tell me about','who is ','who was ','what was ','explain ',
                    'search wikipedia','wiki ']):
            q = re.sub(r'(wikipedia|tell me about|who is|who was|what was|explain|search wikipedia|wiki)\s*','',c).strip()
            if q: self._wiki(q)
            else: self.speak("What would you like to know about?")

        elif _m(c,['what is ']):
            # Only treat as Wikipedia if it's clearly a knowledge question, not time/date
            q = c.replace('what is','').strip()
            if q and not _m(q, ['time','date','today','day','year']):
                self._wiki(q)
            else:
                self.speak(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}.")

        # ── NOTES ─────────────────────────────────────────────
        elif _m(c,['take a note','make a note','note down','write down','remember this','save note','note that']):
            content = re.sub(r'(take a note|make a note|note down|write down|remember this|save note|note that)\s*:?\s*','',c).strip()
            if content:
                self.notes.append({'content':content,'time':datetime.datetime.now().isoformat()})
                self._save()
                self.speak(f"Saved! I noted: {content}")
            else: self.speak("What should I note?")

        elif _m(c,['read my notes','show notes','read notes','what are my notes','my notes','show my notes']):
            if not self.notes: self.speak("You have no notes yet.")
            else:
                self.speak(f"You have {len(self.notes)} note{'s' if len(self.notes)!=1 else ''}. Latest:")
                for n in self.notes[-3:]: self.speak(n['content']); time.sleep(0.3)

        elif _m(c,['clear notes','delete notes','delete all notes','remove all notes']):
            self.notes=[]; self._save(); self.speak("All notes cleared.")

        # ── REMINDERS ────────────────────────────────────────
        elif _m(c,['remind me','set a reminder','add a reminder','add reminder']):
            content = re.sub(r'(remind me to|remind me|set a reminder|add a reminder|add reminder)\s*','',c).strip()
            if content:
                self.reminders.append({'content':content,'time':datetime.datetime.now().isoformat()})
                self._save()
                self.speak(f"Reminder set: {content}")
            else: self.speak("What should I remind you about?")

        elif _m(c,['show reminders','my reminders','read reminders','what are my reminders']):
            if not self.reminders: self.speak("No reminders set.")
            else:
                self.speak(f"You have {len(self.reminders)} reminder{'s' if len(self.reminders)!=1 else ''}:")
                for r in self.reminders[-3:]: self.speak(r['content']); time.sleep(0.3)

        # ── TIMER ─────────────────────────────────────────────
        elif _m(c,['set a timer','set timer','timer for','start timer','start a timer']):
            nums = re.findall(r'\d+', c)
            if nums:
                mins = int(nums[0])
                extra = int(nums[1]) if len(nums)>1 and 'second' in c else 0
                total = mins*60 + extra
                label = f"{mins} minute{'s' if mins!=1 else ''}"
                self.speak(f"Timer set for {label}. I'll alert you when it's done.")
                threading.Thread(target=self._timer_thread, args=(total,), daemon=True).start()
            else: self.speak("How many minutes for the timer?")

        # ── CALCULATOR ────────────────────────────────────────
        elif _m(c,['calculate','compute','how much is','math','solve ']):
            expr = re.sub(r'(calculate|compute|how much is|math|solve)\s*','',c).strip()
            self._calc(expr)

        # ── SYSTEM INFO ───────────────────────────────────────
        elif _m(c,['system info','system status','cpu usage','ram usage','memory usage','disk usage','battery level','how is my computer','pc health']):
            s = self.sc.get_stats()
            self.speak(
                f"System status: CPU at {s['cpu']:.0f}%, "
                f"RAM {s['ram_pct']:.0f}% used ({s['ram_used']} of {s['ram_total']} GB), "
                f"Disk {s['disk_pct']:.0f}% full, "
                f"Battery {s['battery']}" + (" and charging." if s['bat_charging'] else ".")
            )

        elif _m(c,['my ip','ip address','what is my ip','local ip','network ip']):
            try:
                import socket
                ip = socket.gethostbyname(socket.gethostname())
                self.speak(f"Your local IP address is {ip}.")
            except: self.speak("Could not retrieve your IP address.")

        elif _m(c,['running apps','what apps are open','running processes','what is running']):
            try:
                procs = list(set([p.name() for p in psutil.process_iter(['name']) if p.name() and p.name()!='System']))[:8]
                self.speak("Some currently running processes: " + ', '.join(procs[:6]) + ".")
            except: self.speak("Could not get process list.")

        # ── FUN ───────────────────────────────────────────────
        elif _m(c,['joke','tell me a joke','say a joke','make me laugh']):
            self._joke()

        elif _m(c,['motivate me','motivation','inspirational quote','give me a quote','quote of the day','quote']):
            self._quote()

        elif _m(c,['flip a coin','toss a coin','heads or tails','flip coin']):
            self.speak(f"I flipped a coin — {random.choice(['Heads!', 'Tails!'])}")

        elif _m(c,['roll a dice','roll dice','roll the dice','roll a die','roll die']):
            self.speak(f"I rolled the dice and got {random.randint(1,6)}.")

        elif _m(c,['random number','pick a number','generate a random number','give me a number']):
            self.speak(f"Your random number is {random.randint(1,100)}.")

        elif _m(c,['what is your name','who are you','introduce yourself','your name']):
            self.speak("I am JARVIS — Just A Rather Very Intelligent System. Your personal AI assistant, at your service.")

        elif _m(c,['how are you','how are you doing','are you okay','you alright']):
            self.speak("I'm running at peak efficiency, Sir. All systems fully operational. Thank you for asking.")

        # ── HELP ──────────────────────────────────────────────
        elif _m(c,['help','what can you do','commands','capabilities','what do you do','show commands']):
            self.speak(
                "Here's what I can do. "
                "Open any app: say open followed by the name, like open chrome, open notepad, or open file explorer. "
                "Control your browser: close tab, new tab, go back, refresh, zoom in. "
                "Manage files: create file, delete file, list files, create folder. "
                "Control system: lock screen, shutdown, volume up, take screenshot, mute. "
                "Open folders: open downloads, open documents, open pictures. "
                "Get info: weather, news, Wikipedia, search Google, play on YouTube. "
                "Personal tools: set timer, take a note, remind me, calculate, system info. "
                "Just say what you need and I'll handle it!"
            )

        # ── EXIT ─────────────────────────────────────────────
        elif _m(c,['stop talking','stop speaking','be quiet','shut up','stop']):
            self.stop_speaking()

        elif _m(c,['goodbye','bye jarvis','exit','quit','close jarvis','shut yourself down']):
            self.speak("Shutting down JARVIS. It was a pleasure, Sir. Goodbye!")
            self.active = False
            self._save()

        # ── GREETINGS ────────────────────────────────────────
        elif _m(c,['hello','hi','hey','good morning','good evening','good afternoon','sup','yo']):
            hour = datetime.datetime.now().hour
            if hour < 12:   greeting = "Good morning, Sir!"
            elif hour < 17: greeting = "Good afternoon!"
            else:           greeting = "Good evening!"
            self.speak(f"{greeting} How can I help you?")

        # ── AI FALLBACK ───────────────────────────────────────
        else:
            reply = self.ai_reply(c)
            if reply:
                self.speak(reply)
            else:
                if '?' in c:
                    self.speak("I don't have that information right now. Try saying 'search for' followed by your question and I'll Google it for you.")
                else:
                    self.speak("I'm not sure how to handle that. Say 'help' to hear what I can do, or try rephrasing.")

    # ── HELPERS ──────────────────────────────────────────────
    def _handle_volume(self, cmd: str):
        """Smart volume: set exact %, raise/lower by %, or nudge up/down."""
        # Extract any number from the command
        nums = re.findall(r'\d+', cmd)
        percent = int(nums[0]) if nums else None

        is_up   = _m(cmd, ['up','increase','louder','raise','higher','turn up'])
        is_down = _m(cmd, ['down','decrease','quieter','lower','reduce','turn down'])
        is_set  = _m(cmd, ['set','to','at'])

        if percent is not None:
            if is_set or (_m(cmd, ['to','at']) and not is_up and not is_down):
                # "set volume to 60" or "volume at 40"
                self.speak(f"Setting volume to {percent} percent.")
                ok, actual = self.sc.set_volume(percent)
                if not ok:
                    self.speak(f"I couldn't set the volume. Please make sure pycaw is installed.")
            elif is_up:
                # "volume up by 20" or "increase volume 20"
                current = self.sc.get_volume()
                if current is not None:
                    new_vol = min(100, current + percent)
                    self.speak(f"Raising volume from {current} to {new_vol} percent.")
                    self.sc.set_volume(new_vol)
                else:
                    self.speak(f"Setting volume to {percent} percent.")
                    self.sc.set_volume(percent)
            elif is_down:
                # "volume down to 30" or "lower volume by 20"
                current = self.sc.get_volume()
                if current is not None:
                    # "down to X" means set TO that value
                    if _m(cmd, ['to','down to','at']):
                        new_vol = percent
                        self.speak(f"Lowering volume to {percent} percent.")
                    else:
                        # "down by X" means subtract
                        new_vol = max(0, current - percent)
                        self.speak(f"Lowering volume from {current} to {new_vol} percent.")
                    self.sc.set_volume(new_vol)
                else:
                    self.speak(f"Setting volume to {percent} percent.")
                    self.sc.set_volume(percent)
            else:
                # Just a number with "volume" — treat as set
                self.speak(f"Setting volume to {percent} percent.")
                ok, actual = self.sc.set_volume(percent)
                if not ok:
                    self.speak("Couldn't set volume directly. Make sure pycaw is installed.")
        else:
            # No number — simple nudge
            if is_up:
                self.speak("Turning the volume up.")
                self.sc.vol_up()
            elif is_down:
                self.speak("Turning the volume down.")
                self.sc.vol_down()
            else:
                current = self.sc.get_volume()
                if current is not None:
                    self.speak(f"Current volume is {current} percent.")
                else:
                    self.speak("Say something like: volume 50, volume up to 80, or volume down to 30.")

    def _weather(self, city: str):
        self.speak(f"Checking the weather in {city}.")
        key = os.getenv("WEATHER_API_KEY","")
        if not key:
            self.speak("No weather API key set. Add WEATHER_API_KEY to your .env file. Get a free key at openweathermap.org."); return
        try:
            r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric",timeout=6).json()
            if r.get('cod')==200:
                d,t,f,h,w = r['weather'][0]['description'],round(r['main']['temp']),round(r['main']['feels_like']),r['main']['humidity'],round(r['wind']['speed'])
                self.speak(f"In {city}: {d}, {t}°C, feels like {f}°C. Humidity {h}%, wind {w} km/h.")
            else:
                self.speak(f"Couldn't find weather for {city}.")
        except: self.speak("Weather service unavailable.")

    def _news(self):
        self.speak("Fetching the latest news headlines.")
        key = os.getenv("NEWS_API_KEY","")

        # ── Try NewsAPI first ─────────────────────────────────
        if key:
            try:
                r = requests.get(
                    f"https://newsapi.org/v2/top-headlines?country=in&pageSize=5&apiKey={key}",
                    timeout=8
                ).json()
                articles = r.get('articles',[])[:5]
                if articles:
                    self.speak(f"Here are today's top {len(articles)} headlines:")
                    for i, a in enumerate(articles,1):
                        title = a.get('title','').split(' - ')[0].strip()
                        if title: self.speak(f"{i}. {title}."); time.sleep(0.3)
                    self.speak("Those are the top stories.")
                    return
            except: pass

        # ── Free RSS fallback (no API key needed) ─────────────
        try:
            import xml.etree.ElementTree as ET
            rss_urls = [
                "https://feeds.bbci.co.uk/news/world/rss.xml",
                "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
                "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            ]
            headlines = []
            for url in rss_urls:
                try:
                    resp = requests.get(url, timeout=6,
                                        headers={'User-Agent':'Mozilla/5.0'})
                    root = ET.fromstring(resp.content)
                    items = root.findall('.//item')
                    for item in items[:5]:
                        title_el = item.find('title')
                        if title_el is not None and title_el.text:
                            t = title_el.text.strip()
                            if t and t not in headlines:
                                headlines.append(t)
                    if len(headlines) >= 5:
                        break
                except: continue

            if headlines:
                self.speak(f"Here are {min(5,len(headlines))} latest headlines:")
                for i, h in enumerate(headlines[:5], 1):
                    self.speak(f"{i}. {h}."); time.sleep(0.3)
                self.speak("Those are the latest stories.")
            else:
                self.speak("I couldn't fetch the news right now. Please check your internet connection.")
        except Exception as e:
            self.speak("News service is unavailable right now.")

    def _wiki(self, q: str):
        self.speak(f"Looking up {q} on Wikipedia.")
        try:
            self.speak(wikipedia.summary(q, sentences=3, auto_suggest=True))
        except wikipedia.exceptions.DisambiguationError as e:
            self.speak(f"Multiple results. Did you mean: {', '.join(e.options[:3])}?")
        except wikipedia.exceptions.PageError:
            self.speak(f"No Wikipedia page found for {q}.")
        except: self.speak("Wikipedia search failed.")

    def _calc(self, expr: str):
        if not expr: self.speak("What should I calculate?"); return
        try:
            import math
            s = expr.replace('×','*').replace('÷','/').replace('x','*')
            s = s.replace('plus','+').replace('minus','-').replace('times','*').replace('divided by','/')
            s = s.replace('squared','**2').replace('cubed','**3').replace('to the power of','**').replace('percent','*0.01')
            result = eval(s,{"__builtins__":{},"sqrt":math.sqrt,"pi":math.pi,"sin":math.sin,"cos":math.cos,"tan":math.tan,"log":math.log})
            result = int(result) if isinstance(result,float) and result.is_integer() else round(result,4)
            self.speak(f"The answer is {result}.")
        except: self.speak("I couldn't compute that. Try saying it like: calculate 25 times 4.")

    def _timer_thread(self, seconds: int):
        time.sleep(seconds); self.speak("Time's up! Your timer has finished.")
        self.rq.put(('alert','⏰ Timer Done!'))

    def _joke(self):
        jokes = [
            "Why do Java developers wear glasses? Because they don't C sharp!",
            "Why did the programmer quit? Because he didn't get arrays.",
            "There are 10 kinds of people: those who understand binary and those who don't.",
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "A SQL query walks into a bar, walks up to two tables and asks: can I join you?",
            "I tried to think of a computer science joke but I had no cache.",
            "Why was the function depressed? Because it had too many calls but no returns.",
        ]
        self.speak(random.choice(jokes))

    def _quote(self):
        quotes = [
            "The only way to do great work is to love what you do. Steve Jobs.",
            "Innovation distinguishes between a leader and a follower. Steve Jobs.",
            "The secret of getting ahead is getting started. Mark Twain.",
            "It does not matter how slowly you go as long as you do not stop. Confucius.",
            "Believe you can and you're halfway there. Theodore Roosevelt.",
            "Success is not final, failure is not fatal. It is the courage to continue that counts. Churchill.",
        ]
        self.speak(random.choice(quotes))


# ╔══════════════════════════════════════════════════════════════╗
# ║                           GUI                               ║
# ╚══════════════════════════════════════════════════════════════╝
class JarvisGUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("JARVIS Pro  — AI Voice Assistant")
        self.root.geometry("1700x1000")
        self.root.configure(fg_color=C['bg'])
        self.root.minsize(1200,720)
        self.engine    = JarvisEngine()
        self.listening = False
        self.continuous= False
        self._build()
        self._poll()

    def _build(self):
        r = self.root
        # Topbar
        top = ctk.CTkFrame(r, fg_color=C['bg2'], height=88, corner_radius=0)
        top.pack(fill="x")
        ctk.CTkLabel(top, text="🤖", font=ctk.CTkFont(size=38)).pack(side="left",padx=(18,6),pady=18)
        tf = ctk.CTkFrame(top, fg_color="transparent"); tf.pack(side="left")
        ctk.CTkLabel(tf, text="JARVIS PRO V4.1",
                     font=ctk.CTkFont(size=30,weight="bold"),text_color=C['accent']).pack(anchor="w")
        ctk.CTkLabel(tf, text="Advanced AI Voice Assistant  •  Smart App Launcher  •  Full System Control",
                     font=ctk.CTkFont(size=11),text_color=C['textdim']).pack(anchor="w")
        sb = ctk.CTkFrame(top, fg_color=C['card'], corner_radius=12)
        sb.pack(side="right",padx=22,pady=18)
        self.dot = ctk.CTkLabel(sb, text="●", font=ctk.CTkFont(size=28), text_color=C['green'])
        self.dot.pack(side="left",padx=(12,6))
        sf = ctk.CTkFrame(sb, fg_color="transparent"); sf.pack(side="left",padx=(0,12))
        self.st_main = ctk.CTkLabel(sf, text="Ready", font=ctk.CTkFont(size=16,weight="bold"),text_color=C['text'])
        self.st_main.pack(anchor="w")
        self.st_sub = ctk.CTkLabel(sf, text="All systems operational", font=ctk.CTkFont(size=10),text_color=C['textdim'])
        self.st_sub.pack(anchor="w")

        # Body
        body = ctk.CTkFrame(r, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(10,16))

        # Sidebar
        side = ctk.CTkScrollableFrame(body, width=390, fg_color=C['bg2'], corner_radius=16)
        side.pack(side="left", fill="y", padx=(0,12))

        self._lbl(side,"🎤 Voice Control")
        self.listen_btn = ctk.CTkButton(side, text="▶  Start Listening",
            command=self._toggle_listen, height=58,
            font=ctk.CTkFont(size=17,weight="bold"),
            fg_color=C['green'],hover_color=C['green2'],corner_radius=14)
        self.listen_btn.pack(fill="x",padx=12,pady=(0,6))
        self.cont_var = ctk.BooleanVar()
        ctk.CTkCheckBox(side, text=" Continuous Listening Mode",
                        variable=self.cont_var, command=self._toggle_cont,
                        font=ctk.CTkFont(size=13)).pack(padx=12,pady=(0,6))

        self.stop_btn = ctk.CTkButton(side, text="⏹  Stop Speaking",
            command=self._stop, height=44,
            font=ctk.CTkFont(size=14,weight="bold"),
            fg_color=C['red'], hover_color=C['red2'], corner_radius=14)
        self.stop_btn.pack(fill="x",padx=12,pady=(0,12))

        self._lbl(side,"💬 Text Command")
        self.txt = ctk.CTkEntry(side, placeholder_text="Type a command and press Enter…",
                                height=44,font=ctk.CTkFont(size=13))
        self.txt.pack(fill="x",padx=12,pady=(0,6))
        self.txt.bind('<Return>', lambda _: self._send())
        ctk.CTkButton(side, text="▶  Send", command=self._send,
                      height=40,font=ctk.CTkFont(size=14,weight="bold")
                      ).pack(fill="x",padx=12,pady=(0,14))

        self._lbl(side,"⚡ Quick Actions")
        quick = [
            ("🕐 Time","what time is it"),("📅 Date","what is today's date"),
            ("🌤 Weather","weather in mumbai"),("📰 News","latest news"),
            ("❌ Close Tab","close tab"),("🗂 New Tab","new tab"),
            ("📸 Screenshot","take screenshot"),("🔒 Lock Screen","lock screen"),
            ("🔊 Vol Up","volume up"),("🔉 Vol Down","volume down"),
            ("🔇 Mute","mute"),("💻 System Info","system info"),
        ]
        qg = ctk.CTkFrame(side, fg_color="transparent"); qg.pack(fill="x",padx=12,pady=(0,10))
        for i,(lbl,cmd) in enumerate(quick):
            ctk.CTkButton(qg, text=lbl, height=42, font=ctk.CTkFont(size=12,weight="bold"),
                          command=lambda c=cmd: self._exec(c)
                          ).grid(row=i//2, column=i%2, padx=4, pady=4, sticky="ew")
        qg.grid_columnconfigure(0,weight=1); qg.grid_columnconfigure(1,weight=1)

        self._lbl(side,"🚀 Open Apps")
        apps_open = [
            ("🗂 File Explorer","open file explorer"),("🌐 Chrome","open chrome"),
            ("🦊 Firefox","open firefox"),("📝 Notepad","open notepad"),
            ("🧮 Calculator","open calculator"),("🎮 Discord","open discord"),
            ("🎵 Spotify","open spotify"),("💻 VS Code","open vs code"),
            ("📊 Excel","open excel"),("📄 Word","open word"),
            ("⚙️ Settings","open settings"),("📋 Task Mgr","open task manager"),
        ]
        ag = ctk.CTkFrame(side, fg_color="transparent"); ag.pack(fill="x",padx=12,pady=(0,10))
        for i,(lbl,cmd) in enumerate(apps_open):
            ctk.CTkButton(ag, text=lbl, height=40, font=ctk.CTkFont(size=12,weight="bold"),
                          fg_color=C['card2'],hover_color=C['acc2'],
                          command=lambda c=cmd: self._exec(c)
                          ).grid(row=i//2, column=i%2, padx=4, pady=4, sticky="ew")
        ag.grid_columnconfigure(0,weight=1); ag.grid_columnconfigure(1,weight=1)

        self._lbl(side,"🔴 Close Apps")
        apps_close = [
            ("✖ Chrome","close chrome"),("✖ Firefox","close firefox"),
            ("✖ Notepad","close notepad"),("✖ Discord","close discord"),
            ("✖ Spotify","close spotify"),("✖ VS Code","close vscode"),
            ("✖ Excel","close excel"),("✖ Word","close word"),
            ("✖ Zoom","close zoom"),("✖ Teams","close teams"),
            ("✖ VLC","close vlc"),("✖ Steam","close steam"),
        ]
        cg = ctk.CTkFrame(side, fg_color="transparent"); cg.pack(fill="x",padx=12,pady=(0,10))
        for i,(lbl,cmd) in enumerate(apps_close):
            ctk.CTkButton(cg, text=lbl, height=38, font=ctk.CTkFont(size=12,weight="bold"),
                          fg_color="#3a1a1a", hover_color=C['red2'],
                          text_color=C['red'],
                          command=lambda c=cmd: self._exec(c)
                          ).grid(row=i//2, column=i%2, padx=4, pady=3, sticky="ew")
        cg.grid_columnconfigure(0,weight=1); cg.grid_columnconfigure(1,weight=1)

        self._lbl(side,"📊 System Monitor")
        self.cpu_b  = self._stat(side,"CPU")
        self.ram_b  = self._stat(side,"RAM")
        self.dsk_b  = self._stat(side,"Disk")
        ctk.CTkButton(side, text="↺ Refresh Stats", command=self._refresh_stats,
                      height=34,font=ctk.CTkFont(size=12)
                      ).pack(fill="x",padx=12,pady=(6,16))

        # Chat area
        cf = ctk.CTkFrame(body, fg_color=C['bg2'], corner_radius=16)
        cf.pack(side="right", fill="both", expand=True)
        ch = ctk.CTkFrame(cf, fg_color="transparent", height=56)
        ch.pack(fill="x",padx=18,pady=(16,8))
        ctk.CTkLabel(ch, text="💬 Conversation",
                     font=ctk.CTkFont(size=24,weight="bold")).pack(side="left")
        ctk.CTkButton(ch, text="🗑 Clear", command=self._clear,
                      width=100,height=32).pack(side="right")
        self.chat = ctk.CTkTextbox(cf, font=ctk.CTkFont(size=15),
                                   wrap="word",fg_color=C['card'],corner_radius=12)
        self.chat.pack(fill="both",expand=True,padx=18,pady=(0,18))
        self.chat.configure(state="disabled")

        self._add("JARVIS", random.choice(GREETINGS), C['accent'])
        self._add("JARVIS", (
            "New: Say 'close chrome', 'close spotify', 'close discord' to kill apps! "
            "Hit the red ⏹ Stop button (or say 'stop') to silence me anytime. "
            "Try: 'open file explorer', 'open chrome', 'close notepad', 'latest news', 'weather'."
        ), C['gold'])
        self._refresh_stats()

    def _lbl(self,p,t):
        ctk.CTkLabel(p,text=t,font=ctk.CTkFont(size=16,weight="bold"),
                     text_color=C['accent']).pack(anchor="w",padx=12,pady=(14,4))

    def _stat(self, parent, label):
        f = ctk.CTkFrame(parent, fg_color="transparent"); f.pack(fill="x",padx=12,pady=2)
        ctk.CTkLabel(f,text=f"{label}:",width=45,font=ctk.CTkFont(size=12),
                     text_color=C['textdim']).pack(side="left")
        bar = ctk.CTkProgressBar(f,height=14,corner_radius=6)
        bar.pack(side="left",fill="x",expand=True,padx=(6,8)); bar.set(0)
        lbl = ctk.CTkLabel(f,text="0%",width=45,font=ctk.CTkFont(size=12))
        lbl.pack(side="right")
        return bar, lbl

    def _refresh_stats(self):
        try:
            s = self.engine.sc.get_stats()
            for (bar,lbl),pct in [(self.cpu_b,s['cpu']),(self.ram_b,s['ram_pct']),(self.dsk_b,s['disk_pct'])]:
                bar.set(min(pct/100,1.0)); lbl.configure(text=f"{pct:.0f}%")
        except: pass

    def _add(self, sender, msg, color=None):
        ts = datetime.datetime.now().strftime("%I:%M %p")
        self.chat.configure(state="normal")
        self.chat.insert("end",f"\n[{ts}]  {sender}\n{msg}\n")
        self.chat.see("end"); self.chat.configure(state="disabled")

    def _clear(self):
        self.chat.configure(state="normal"); self.chat.delete("1.0","end")
        self.chat.configure(state="disabled"); self._add("JARVIS","Chat cleared. Ready!",C['accent'])

    def _exec(self, cmd):
        self._add("You", cmd, C['yellow'])
        threading.Thread(target=self.engine.handle, args=(cmd,), daemon=True).start()

    def _stop(self):
        """Stop JARVIS from speaking immediately."""
        self.engine.stop_speaking()
        self._add("JARVIS", "Speaking stopped.", C['red'])

    def _send(self):
        cmd = self.txt.get().strip()
        if cmd: self.txt.delete(0,"end"); self._exec(cmd)

    def _toggle_listen(self):
        if not self.listening:
            self.listening = True
            self.listen_btn.configure(text="🔴  Listening…",fg_color=C['red'],hover_color=C['red2'])
            threading.Thread(target=self._listen_once, daemon=True).start()
        else:
            self.listening = False
            self.listen_btn.configure(text="▶  Start Listening",fg_color=C['green'],hover_color=C['green2'])

    def _listen_once(self):
        cmd = self.engine.listen()
        if cmd: self.root.after(0, lambda: self._exec(cmd))
        self.listening = False
        self.root.after(0, lambda: self.listen_btn.configure(
            text="▶  Start Listening",fg_color=C['green'],hover_color=C['green2']))

    def _toggle_cont(self):
        self.continuous = self.cont_var.get()
        if self.continuous:
            threading.Thread(target=self._cont_loop, daemon=True).start()

    def _cont_loop(self):
        while self.continuous and self.engine.active:
            cmd = self.engine.listen(timeout=4)
            if cmd: self.root.after(0, lambda c=cmd: self._exec(c))
            time.sleep(0.3)

    def _poll(self):
        try:
            while not self.engine.rq.empty():
                item = self.engine.rq.get_nowait(); kind = item[0]
                if kind=='speak':       self._add("JARVIS", item[1], C['accent'])
                elif kind=='status':    self.st_main.configure(text=item[1]); (self.dot.configure(text_color=item[2]) if len(item)>2 else None)
                elif kind=='user_said': self._add("You", item[1], C['yellow'])
                elif kind=='listening': self.dot.configure(text_color=C['green'] if item[1] else C['yellow']); self.st_main.configure(text="Listening…" if item[1] else "Processing…")
                elif kind=='alert':     self._add("⏰ Alert", item[1], C['gold'])
        except: pass
        if self.engine.active: self.root.after(80, self._poll)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.mainloop()

    def _close(self):
        self.engine.active = False; self.continuous = False
        self.engine._save(); self.root.destroy()


# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("="*65)
    print("  JARVIS Pro V4.1  —  Advanced AI Voice Assistant")
    print("="*65)
    print("\n  ✓ Bulletproof app launcher (PATH + common dirs + Registry)")
    print("  ✓ Opens File Explorer, Chrome, Firefox, Notepad, Discord...")
    print("  ✓ Browser control, file management, system ops")
    print("  ✓ Weather / News / Wikipedia / YouTube / Google")
    print("  ✓ Claude AI conversation brain")
    print("\n  Optional .env keys:")
    print("    WEATHER_API_KEY   → openweathermap.org/api (free)")
    print("    NEWS_API_KEY      → newsapi.org (free)")
    print("    ANTHROPIC_API_KEY → console.anthropic.com")
    print("\n  Launching...\n")
    try:
        JarvisGUI().run()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback; traceback.print_exc()
        input("\nPress Enter to exit...")