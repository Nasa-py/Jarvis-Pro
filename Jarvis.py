"""
JARVIS Pro - Advanced AI Voice Assistant
Enterprise-Grade | Multi-threaded | Natural Language Processing
"""

import customtkinter as ctk
import datetime
from dotenv import load_dotenv
import webbrowser
import os
import random
import time
import threading
import requests
import json
import psutil
import wikipedia
from pathlib import Path
from collections import deque
import queue

load_dotenv()

try:
    import pyttsx3
    import speech_recognition as sr
except ImportError:
    print("Installing required packages...")
    os.system("pip install pyttsx3 SpeechRecognition pyaudio")
    import pyttsx3
    import speech_recognition as sr

# Professional color scheme
COLORS = {
    'bg_dark': '#0a0e27',
    'bg_medium': '#1a1f3a',
    'bg_light': '#2a2f4a',
    'accent': '#00d4ff',
    'success': '#00ff88',
    'warning': '#ffaa00',
    'danger': '#ff3366',
    'text': '#e0e0e0',
    'text_dim': '#808080'
}

class JarvisEngine:
    """Advanced AI engine with enhanced NLP and accuracy"""
    
    def __init__(self):
        self.name = "JARVIS"
        self.active = True
        self.listening = False
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Command history
        self.history = deque(maxlen=50)
        
        # Data storage
        self.data_dir = Path("jarvis_data")
        self.data_dir.mkdir(exist_ok=True)
        self.notes_file = self.data_dir / "notes.json"
        self.reminders_file = self.data_dir / "reminders.json"
        self.settings_file = self.data_dir / "settings.json"
        
        self.load_data()
        
        # Enhanced command mapping with aliases
        self.commands = {
            'time': {'func': self.tell_time, 'keywords': ['time', 'clock']},
            'date': {'func': self.tell_date, 'keywords': ['date', 'today', 'day']},
            'weather': {'func': self.get_weather, 'keywords': ['weather', 'temperature', 'forecast']},
            'search': {'func': self.web_search, 'keywords': ['search', 'google', 'find', 'look up']},
            'open': {'func': self.open_website, 'keywords': ['open', 'launch', 'go to']},
            'youtube': {'func': self.play_youtube, 'keywords': ['play', 'youtube', 'music', 'video']},
            'wikipedia': {'func': self.search_wikipedia, 'keywords': ['wikipedia', 'wiki', 'define', 'what is']},
            'joke': {'func': self.tell_joke, 'keywords': ['joke', 'funny', 'laugh']},
            'news': {'func': self.get_news, 'keywords': ['news', 'headlines', 'updates']},
            'note': {'func': self.take_note, 'keywords': ['note', 'remember', 'write down']},
            'read notes': {'func': self.read_notes, 'keywords': ['read notes', 'show notes', 'my notes']},
            'reminder': {'func': self.set_reminder, 'keywords': ['remind', 'reminder', 'alert']},
            'calculate': {'func': self.calculate, 'keywords': ['calculate', 'math', 'compute']},
            'system': {'func': self.system_info, 'keywords': ['system', 'pc info', 'specs', 'performance']},
            'close app': {'func': self.close_application, 'keywords': ['close', 'kill', 'stop application']},
            'screenshot': {'func': self.take_screenshot, 'keywords': ['screenshot', 'capture screen']},
            'volume': {'func': self.control_volume, 'keywords': ['volume', 'sound']},
            'exit': {'func': self.exit_jarvis, 'keywords': ['exit', 'quit', 'shutdown', 'goodbye', 'bye']},
        }
        
        self.greetings = [
            "Hello Sir, JARVIS at your service.",
            "Good to see you. How may I assist?",
            "JARVIS online and ready.",
            "Hello. All systems operational."
        ]
    
    def load_data(self):
        """Load persistent data"""
        try:
            if self.notes_file.exists():
                with open(self.notes_file, 'r') as f:
                    self.notes = json.load(f)
            else:
                self.notes = []
            
            if self.reminders_file.exists():
                with open(self.reminders_file, 'r') as f:
                    self.reminders = json.load(f)
            else:
                self.reminders = []
        except:
            self.notes = []
            self.reminders = []
    
    def save_data(self):
        """Save persistent data"""
        with open(self.notes_file, 'w') as f:
            json.dump(self.notes, f, indent=2)
        with open(self.reminders_file, 'w') as f:
            json.dump(self.reminders, f, indent=2)
    
    def speak(self, text):
        """Text-to-speech with queue management"""
        self.response_queue.put(('speak', text))
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Enhanced speech recognition with noise filtering"""
        try:
            with sr.Microphone() as source:
                self.response_queue.put(('status', 'Listening...'))
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            self.response_queue.put(('status', 'Processing...'))
            command = self.recognizer.recognize_google(audio).lower()
            self.response_queue.put(('command', command))
            self.history.append({'time': datetime.datetime.now().strftime('%H:%M:%S'), 'command': command})
            return command
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            self.response_queue.put(('status', 'Could not understand'))
            return None
        except Exception as e:
            self.response_queue.put(('status', f'Error: {str(e)[:50]}'))
            return None
    
    def parse_command(self, command):
        """Advanced NLP command parsing"""
        if not command:
            return None, []
        
        command = command.lower().strip()
        
        # Direct command matching
        for cmd_name, cmd_data in self.commands.items():
            for keyword in cmd_data['keywords']:
                if keyword in command:
                    # Extract arguments
                    args = command.replace(keyword, '').strip()
                    return cmd_data['func'], [args] if args else []
        
        return None, []
    
    # ==================== COMMAND IMPLEMENTATIONS ====================
    
    def tell_time(self, *args):
        now = datetime.datetime.now().strftime("%I:%M %p")
        self.speak(f"The current time is {now}")
    
    def tell_date(self, *args):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        self.speak(f"Today is {today}")
    
    def get_weather(self, *args):
        city = args[0] if args and args[0] else "Mumbai"
        try:
            api_key = os.getenv("WEATHER_API_KEY")  # Get free key from openweathermap.org
            if not api_key:
                self.speak("Weather API key not configured. Add WEATHER_API_KEY to your .env file")
                return
                
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get("cod") == 200:
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                
                self.speak(f"Weather in {city}: {weather}. Temperature: {temp}°C, feels like {feels_like}°C. Humidity: {humidity}%")
            else:
                self.speak(f"Could not fetch weather for {city}")
        except:
            self.speak("Weather service unavailable. Check your API key or internet connection.")
    
    def web_search(self, *args):
        if not args or not args[0]:
            self.speak("What should I search for?")
            return
        query = args[0]
        url = f"https://www.google.com/search?q={query}"
        self.speak(f"Searching for {query}")
        webbrowser.open(url)
    
    def open_website(self, *args):
        if not args or not args[0]:
            self.speak("Which website?")
            return
        
        site = args[0].lower()
        
        # Common websites shorthand
        shortcuts = {
            'youtube': 'youtube.com',
            'gmail': 'gmail.com',
            'github': 'github.com',
            'linkedin': 'linkedin.com',
            'twitter': 'twitter.com',
            'instagram': 'instagram.com',
            'facebook': 'facebook.com',
            'reddit': 'reddit.com'
        }
        
        url = shortcuts.get(site, site)
        if not url.startswith('http'):
            url = 'https://' + url
        
        self.speak(f"Opening {site}")
        webbrowser.open(url)
    
    def play_youtube(self, *args):
        if not args or not args[0]:
            self.speak("What would you like to play?")
            return
        query = args[0]
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        self.speak(f"Playing {query} on YouTube")
        webbrowser.open(url)
    
    def search_wikipedia(self, *args):
        if not args or not args[0]:
            self.speak("What should I look up?")
            return
        
        query = args[0]
        try:
            self.speak(f"Searching Wikipedia for {query}")
            result = wikipedia.summary(query, sentences=2)
            self.speak(result)
        except wikipedia.exceptions.DisambiguationError as e:
            self.speak(f"Multiple results found. Please be more specific. Options include: {', '.join(e.options[:3])}")
        except:
            self.speak(f"Could not find information about {query}")
    
    def tell_joke(self, *args):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the computer show up at work late? It had a hard drive!",
            "What's an object-oriented way to become wealthy? Inheritance!",
            "Why do Java developers wear glasses? Because they don't C#!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "Why did the developer go broke? Because he used up all his cache!",
            "What do you call a programmer from Finland? Nerdic!",
            "Why was the JavaScript developer sad? Because he didn't Node how to Express himself!"
        ]
        self.speak(random.choice(jokes))
    
    def get_news(self, *args):
        try:
            api_key = os.getenv("NEWS_API_KEY")  # Get from newsapi.org
            if not api_key:
                self.speak("News API key not configured. Add NEWS_API_KEY to your .env file")
                return
                
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            articles = data.get("articles", [])[:5]
            if articles:
                self.speak("Here are today's top headlines:")
                for i, article in enumerate(articles, 1):
                    self.speak(f"Headline {i}: {article['title']}")
            else:
                self.speak("No news available")
        except:
            self.speak("News service unavailable. Check your API key or internet connection.")
    
    def take_note(self, *args):
        if not args or not args[0]:
            self.speak("What should I note?")
            return
        
        note = args[0]
        self.notes.append({
            'content': note,
            'timestamp': datetime.datetime.now().isoformat()
        })
        self.save_data()
        self.speak("Note saved successfully")
    
    def read_notes(self, *args):
        if not self.notes:
            self.speak("You have no notes")
            return
        
        self.speak(f"You have {len(self.notes)} notes. Reading the latest 5:")
        for note in self.notes[-5:]:
            self.speak(note['content'])
    
    def set_reminder(self, *args):
        if not args or not args[0]:
            self.speak("What should I remind you about?")
            return
        
        reminder = args[0]
        self.reminders.append({
            'content': reminder,
            'timestamp': datetime.datetime.now().isoformat()
        })
        self.save_data()
        self.speak(f"Reminder set: {reminder}")
    
    def calculate(self, *args):
        if not args or not args[0]:
            self.speak("What should I calculate?")
            return
        
        try:
            expression = args[0].replace('x', '*').replace('plus', '+').replace('minus', '-')
            result = eval(expression)
            self.speak(f"The answer is {result}")
        except:
            self.speak("Invalid calculation")
    
    def system_info(self, *args):
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        self.speak(f"System status: CPU usage {cpu}%, Memory usage {memory}%, Disk usage {disk}%")
    
    def close_application(self, *args):
        if not args or not args[0]:
            self.speak("Which application should I close?")
            return
        
        app_name = args[0].lower()
        try:
            os.system(f"taskkill /f /im {app_name}.exe")
            self.speak(f"Closed {app_name}")
        except:
            self.speak(f"Could not close {app_name}")
    
    def take_screenshot(self, *args):
        try:
            import pyautogui
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(filename)
            self.speak(f"Screenshot saved as {filename}")
        except:
            self.speak("Screenshot failed. Install pyautogui: pip install pyautogui")
    
    def control_volume(self, *args):
        if not args or not args[0]:
            self.speak("Set volume to what level?")
            return
        
        try:
            level = int(''.join(filter(str.isdigit, args[0])))
            # This works on Windows
            os.system(f"nircmd.exe setsysvolume {level * 655}")
            self.speak(f"Volume set to {level}%")
        except:
            self.speak("Could not adjust volume")
    
    def exit_jarvis(self, *args):
        self.speak("Shutting down. Goodbye Sir.")
        self.active = False


class JarvisGUI:
    """Modern GUI with animated visualizer"""
    
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("JARVIS Pro - AI Voice Assistant")
        self.root.geometry("1400x900")
        self.root.configure(fg_color=COLORS['bg_dark'])
        
        self.engine = JarvisEngine()
        self.is_listening = False
        
        self.setup_ui()
        self.start_background_thread()
    
    def setup_ui(self):
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header = ctk.CTkFrame(main_container, fg_color=COLORS['bg_medium'], height=100, corner_radius=15)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="🤖 JARVIS PRO",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=COLORS['accent']
        )
        title.pack(side="left", padx=30)
        
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", padx=30)
        
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=30),
            text_color=COLORS['success']
        )
        self.status_indicator.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        self.status_label.pack(side="left")
        
        # Content area
        content = ctk.CTkFrame(main_container, fg_color="transparent")
        content.pack(fill="both", expand=True)
        
        # Left panel - Controls
        left_panel = ctk.CTkFrame(content, width=400, fg_color=COLORS['bg_medium'], corner_radius=15)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)
        
        controls_title = ctk.CTkLabel(
            left_panel,
            text="⚙️ Controls",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        controls_title.pack(pady=20)
        
        # Voice control button
        self.voice_btn = ctk.CTkButton(
            left_panel,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=COLORS['success'],
            hover_color=COLORS['accent']
        )
        self.voice_btn.pack(pady=10, padx=20, fill="x")
        
        # Text input
        text_frame = ctk.CTkFrame(left_panel, fg_color=COLORS['bg_light'], corner_radius=10)
        text_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            text_frame,
            text="💬 Text Command",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.text_input = ctk.CTkEntry(
            text_frame,
            placeholder_text="Type a command...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.text_input.pack(pady=5, padx=10, fill="x")
        self.text_input.bind('<Return>', lambda e: self.process_text_command())
        
        ctk.CTkButton(
            text_frame,
            text="Send",
            command=self.process_text_command,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(5, 10), padx=10, fill="x")
        
        # Quick actions
        quick_frame = ctk.CTkFrame(left_panel, fg_color=COLORS['bg_light'], corner_radius=10)
        quick_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            quick_frame,
            text="⚡ Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        quick_actions = [
            ("⏰ Tell Time", "time"),
            ("📅 Tell Date", "date"),
            ("🌤️ Weather", "weather Mumbai"),
            ("📰 News", "news"),
            ("😂 Tell Joke", "joke"),
            ("📊 System Info", "system"),
        ]
        
        for label, command in quick_actions:
            ctk.CTkButton(
                quick_frame,
                text=label,
                command=lambda cmd=command: self.execute_command(cmd),
                height=40,
                font=ctk.CTkFont(size=13)
            ).pack(pady=5, padx=10, fill="x")
        
        # Right panel - Output
        right_panel = ctk.CTkFrame(content, fg_color=COLORS['bg_medium'], corner_radius=15)
        right_panel.pack(side="right", fill="both", expand=True)
        
        output_title = ctk.CTkLabel(
            right_panel,
            text="💬 Conversation",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        output_title.pack(pady=20)
        
        # Chat display
        self.chat_display = ctk.CTkTextbox(
            right_panel,
            font=ctk.CTkFont(size=14),
            wrap="word",
            fg_color=COLORS['bg_light']
        )
        self.chat_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add welcome message
        self.add_chat_message("JARVIS", random.choice(self.engine.greetings), COLORS['accent'])
    
    def add_chat_message(self, sender, message, color=COLORS['text']):
        """Add message to chat display - FIXED VERSION"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert("end", f"\n[{timestamp}] {sender}:\n", "sender")
        self.chat_display.insert("end", f"{message}\n", "message")
        # CustomTkinter doesn't support font in tag_config, only foreground
        self.chat_display.tag_config("sender", foreground=color)
        self.chat_display.tag_config("message", foreground=COLORS['text'])
        self.chat_display.see("end")
    
    def toggle_listening(self):
        """Toggle voice listening"""
        if not self.is_listening:
            self.is_listening = True
            self.voice_btn.configure(text="🔴 Listening...", fg_color=COLORS['danger'])
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.is_listening = False
            self.voice_btn.configure(text="🎤 Start Listening", fg_color=COLORS['success'])
    
    def listen_loop(self):
        """Continuous listening loop"""
        while self.is_listening and self.engine.active:
            command = self.engine.listen()
            if command:
                self.execute_command(command)
            time.sleep(0.5)
    
    def execute_command(self, command):
        """Execute a command"""
        self.add_chat_message("You", command, COLORS['warning'])
        
        func, args = self.engine.parse_command(command)
        if func:
            try:
                func(*args)
            except Exception as e:
                self.engine.speak(f"Error executing command: {str(e)}")
        else:
            self.engine.speak("I don't understand that command. Try 'help' for available commands.")
    
    def process_text_command(self):
        """Process text input"""
        command = self.text_input.get().strip()
        if command:
            self.execute_command(command)
            self.text_input.delete(0, 'end')
    
    def start_background_thread(self):
        """Monitor response queue"""
        def check_queue():
            try:
                while not self.engine.response_queue.empty():
                    msg_type, msg_data = self.engine.response_queue.get_nowait()
                    
                    if msg_type == 'speak':
                        self.add_chat_message("JARVIS", msg_data, COLORS['accent'])
                    elif msg_type == 'status':
                        self.status_label.configure(text=msg_data)
                    elif msg_type == 'command':
                        pass  # Already handled
            except:
                pass
            
            if self.engine.active:
                self.root.after(100, check_queue)
        
        check_queue()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Clean shutdown"""
        self.engine.active = False
        self.is_listening = False
        self.root.destroy()


if __name__ == "__main__":
    print("Initializing JARVIS Pro...")
    app = JarvisGUI()
    app.run()