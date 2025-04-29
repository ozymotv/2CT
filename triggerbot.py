import os, sys, random, string
import sys
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.FreeConsole()

import json
import threading
import time
import random
import webbrowser
import tkinter as tk
from tkinter import ttk
from shared_module import TriggerBotCore
import winsound
from pynput.keyboard import Controller, Listener as KeyListener, Key, KeyCode
from pynput.mouse import Listener as MouseListener, Button as MouseButton

CONFIG_PATH = 'config.json'
KEY_DOC_URL = 'https://docs.microsoft.com/windows/win32/inputdev/virtual-key-codes'
SUPPORT_URL = 'https://github.com/ozymotv/supportme'
KEY_OPTIONS = [
    *[chr(c) for c in range(ord('A'), ord('Z')+1)],
    *[str(d) for d in range(0, 10)],
    *[f'F{i}' for i in range(1, 13)],
    'Left', 'Right', 'Up', 'Down', 'Return', 'Escape', 'Space',
    'XBUTTON1', 'XBUTTON2'
]
BEEP_ON_FREQ = 800
BEEP_OFF_FREQ = 600
BEEP_DURATION = 50

# List of innocent-looking window titles to randomize
WINDOW_TITLES = [
    "System Configuration",
    "Resource Monitor",
    "Performance Monitor", 
    "Network Connections",
    "Windows Settings",
    "Calculator",
    "Notepad",
    "Calendar",
    "Weather",
    "Device Manager",
    "System Properties",
    "Control Panel",
    "Task Scheduler",
    "File Explorer",
    "Document Viewer",
    "Disk Management",
    "Sound Settings",
    "Display Settings",
    "User Accounts",
    "System Information"
]

def generate_random_string(length=8):
    """Generate a random alphanumeric string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Generate variations of app names
def generate_window_title():
    base_title = random.choice(WINDOW_TITLES)
    
    # Sometimes add a modifier
    if random.random() < 0.7:
        modifiers = ["", "Advanced ", "Windows ", "System ", "Microsoft ", ""]
        prefix = random.choice(modifiers)
        
        # Sometimes add a suffix
        suffixes = ["", " Settings", " Manager", " Utility", " Tool", " Options", " Panel", " (Admin)", ""]
        suffix = random.choice(suffixes)
        
        return f"{prefix}{base_title}{suffix}"
    
    return base_title

# Create a unique session ID for this run
SESSION_ID = generate_random_string(12)

# Change the memory footprint slightly on each run to help avoid signature detection
def randomize_memory_footprint():
    # Create a random amount of junk data in memory
    junk_size = random.randint(10, 100) * 1024  # 10-100KB of random data
    junk_data = [generate_random_string(random.randint(10, 100)) for _ in range(junk_size // 20)]
    return junk_data  # Return to prevent garbage collection

class TriggerBotUI:
    def __init__(self, root):
        self.root = root
        
        # Set a random window title
        self.random_title = generate_window_title()
        root.title(self.random_title)
        root.resizable(False, False)

        # Hold reference to the random memory data
        self.junk_memory = randomize_memory_footprint()

        # Load config and init core
        try:
            self.config = json.load(open(CONFIG_PATH))
        except:
            self.config = {}
        self.core = TriggerBotCore(CONFIG_PATH)
        self.running = False
        self.mode_active = False

        # Hotkey mappings
        self.kb_hotkey = None
        self.mouse_hotkey = None

        # Random window ID and appearance variations
        self.window_id = generate_random_string(6)
        
        # Randomize window icon if possible (optional)
        try:
            random_icon = self.get_random_system_icon()
            if random_icon:
                root.iconbitmap(random_icon)
        except:
            pass  # Fail silently if icon randomization fails

        # Build UI and start listeners and threads
        self.build_ui()
        self._parse_hotkey()
        self.setup_listeners()
        threading.Thread(target=self.update_fps_display, daemon=True).start()

        # Periodically change window title
        if random.random() < 0.5:  # 50% chance to enable title rotation
            threading.Thread(target=self.rotate_window_title, daemon=True).start()

        # Resize window to fit content
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth() + 20
        h = self.root.winfo_reqheight() + 20
        
        # Add slight random variation to window size
        w += random.randint(-10, 10)
        h += random.randint(-10, 10)
        
        self.root.geometry(f"{w}x{h}")
        
        # Randomly position window to seem like a legitimate app
        self.position_window_naturally()
        
        # Set up memory pattern alteration thread
        threading.Thread(target=self.periodically_alter_memory, daemon=True).start()

    def periodically_alter_memory(self):
        """Periodically change memory patterns to avoid signature detection"""
        while True:
            sleep_time = random.randint(10, 30)
            time.sleep(sleep_time)
            
            # Replace some of the junk data
            if hasattr(self, 'junk_memory') and self.junk_memory:
                replace_count = min(len(self.junk_memory) // 10, 100)
                for _ in range(replace_count):
                    idx = random.randint(0, len(self.junk_memory) - 1)
                    self.junk_memory[idx] = generate_random_string(random.randint(10, 100))

    def get_random_system_icon(self):
        """Try to use a random system icon (Windows only)"""
        if sys.platform != 'win32':
            return None
            
        system_paths = [
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'SysWOW64')
        ]
        
        icon_files = []
        for path in system_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.lower().endswith('.exe') and not file.lower().startswith('setup'):
                        icon_files.append(os.path.join(path, file))
        
        # Return None or a random icon file
        return random.choice(icon_files) if icon_files else None

    def position_window_naturally(self):
        """Position window in a way that looks natural and not suspicious"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Most legitimate windows appear in these areas:
        # - Center of screen
        # - Left side (like Explorer)
        # - Slightly offset from corners
        
        positions = [
            {'x': screen_width // 2 - 200, 'y': screen_height // 2 - 150},  # Center
            {'x': 50, 'y': 50},  # Top left with offset
            {'x': screen_width - 400, 'y': 50},  # Top right with offset
            {'x': 50, 'y': screen_height - 400}  # Bottom left with offset
        ]
        
        # Add small random variation to position
        pos = random.choice(positions)
        variation_x = random.randint(-30, 30)
        variation_y = random.randint(-30, 30)
        
        self.root.geometry(f"+{pos['x'] + variation_x}+{pos['y'] + variation_y}")

    def rotate_window_title(self):
        """Periodically change the window title"""
        while True:
            # Sleep for a random time between 30s and 3min
            sleep_time = random.randint(30, 180)
            time.sleep(sleep_time)
            
            # Only change title if not focused to avoid user noticing
            if not self.root.focus_get():
                new_title = generate_window_title()
                self.root.title(new_title)
                self.random_title = new_title

    def _parse_hotkey(self):
        name = self.hotkey_var.get()
        if name.upper() == 'XBUTTON1':
            self.mouse_hotkey = MouseButton.x1
            self.kb_hotkey = None
        elif name.upper() == 'XBUTTON2':
            self.mouse_hotkey = MouseButton.x2
            self.kb_hotkey = None
        else:
            self.mouse_hotkey = None
            lower = name.lower()
            try:
                key = getattr(Key, lower)
            except AttributeError:
                key = KeyCode.from_char(lower)
            self.kb_hotkey = key

    def build_ui(self):
        # Randomly choose a style to apply (subtle differences)
        ui_style = random.choice(['default', 'compact', 'spaced'])
        
        # Adjust padding based on style
        if ui_style == 'compact':
            pad = {'padx': 6, 'pady': 3}
        elif ui_style == 'spaced':
            pad = {'padx': 10, 'pady': 6}
        else:
            pad = {'padx': 8, 'pady': 4}

        main = ttk.Frame(self.root, padding=12)
        main.grid(sticky='NSEW')
        self.root.columnconfigure(0, weight=1)

        # Trigger Method
        ttk.Label(main, text='Trigger Method:').grid(row=0, column=0, sticky='W', **pad)
        self.method_var = tk.StringVar(value=self.config.get('method', 'key'))
        ttk.OptionMenu(main, self.method_var, self.method_var.get(), 'key', 'kmnet', command=lambda _: self.update_visibility()).grid(row=0, column=1, sticky='EW', **pad)

        # Trigger Key Frame
        self.key_frame = ttk.Frame(main)
        ttk.Label(self.key_frame, text='Fire key:').grid(row=0, column=0, sticky='W', **pad)
        self.key_var = tk.StringVar(value=self.config.get('trigger_key', 'Space'))
        ttk.Combobox(self.key_frame, values=KEY_OPTIONS, textvariable=self.key_var, width=15).grid(row=0, column=1, sticky='EW', **pad)
        link1 = ttk.Label(self.key_frame, text='Key Codes', foreground='blue', cursor='hand2')
        link1.grid(row=1, column=1, sticky='W', **pad)
        link1.bind('<Button-1>', lambda e: webbrowser.open(KEY_DOC_URL))
        self.key_frame.grid(row=1, column=0, columnspan=2, sticky='EW')

        # KMNet Settings Frame
        self.km_frame = ttk.Frame(main)
        for i, (lbl, k) in enumerate([('IP', 'ip'), ('Port', 'port'), ('UUID', 'uuid')]):
            ttk.Label(self.km_frame, text=f'{lbl}:').grid(row=i, column=0, sticky='W', **pad)
            var = tk.StringVar(value=str(self.config.get(k, '')))
            setattr(self, f'{k}_var', var)
            ttk.Entry(self.km_frame, textvariable=var).grid(row=i, column=1, sticky='EW', **pad)
        self.km_frame.grid(row=2, column=0, columnspan=2, sticky='EW')

        # Crosshair requirement
        self.cross_check = tk.IntVar(value=self.config.get('require_crosshair', 0))
        ttk.Checkbutton(main, text='Require Crosshair', variable=self.cross_check).grid(row=3, column=0, columnspan=2, sticky='W', **pad)

        # Timing settings
        timing_labels = [
            ('Press Min (ms):', 'press_min', 'press_release_min_ms', 80),
            ('Press Max (ms):', 'press_max', 'press_release_max_ms', 100),
            ('Delay Min (ms):', 'cycle_min', 'delay_after_shoot_min_ms', 200),
            ('Delay Max (ms):', 'cycle_max', 'delay_after_shoot_max_ms', 200),
        ]
        for idx, (label, var_name, cfg_key, default) in enumerate(timing_labels, start=4):
            ttk.Label(main, text=label).grid(row=idx, column=0, sticky='W', **pad)
            var = tk.IntVar(value=self.config.get(cfg_key, default))
            setattr(self, var_name, var)
            ttk.Spinbox(main, from_=0, to=5000, textvariable=var, width=8).grid(row=idx, column=1, sticky='EW', **pad)

        # Mode selection
        ttk.Label(main, text='Mode:').grid(row=8, column=0, sticky='W', **pad)
        self.mode_var = tk.StringVar(value=self.config.get('mode', 'always'))
        ttk.OptionMenu(main, self.mode_var, self.mode_var.get(), 'always', 'toggle', 'hold', command=lambda _: self.update_visibility()).grid(row=8, column=1, sticky='EW', **pad)

        # Hotkey selection
        self.hotkey_frame = ttk.Frame(main)
        ttk.Label(self.hotkey_frame, text='Hotkey:').grid(row=0, column=0, sticky='W', **pad)
        self.hotkey_var = tk.StringVar(value=self.config.get('hotkey', 'T'))
        hotkey_cb = ttk.Combobox(self.hotkey_frame, values=KEY_OPTIONS, textvariable=self.hotkey_var, width=15)
        hotkey_cb.grid(row=0, column=1, sticky='EW', **pad)
        hotkey_cb.bind('<<ComboboxSelected>>', lambda e: self._parse_hotkey())
        
        # Always show key codes link next to hotkey
        link2 = ttk.Label(self.hotkey_frame, text='Key Codes', foreground='blue', cursor='hand2')
        link2.grid(row=0, column=2, sticky='W', padx=5)
        link2.bind('<Button-1>', lambda e: webbrowser.open(KEY_DOC_URL))
        
        self.hotkey_frame.grid(row=9, column=0, columnspan=2, sticky='EW')

        # Status and FPS
        self.status_label = tk.Label(main, text='Stopped', fg='red', font=('Arial', 10, 'bold'))
        self.status_label.grid(row=10, column=0, columnspan=2, **pad)
        fps_frame = ttk.Frame(main)
        fps_frame.grid(row=11, column=0, columnspan=2, sticky='EW', **pad)
        ttk.Label(fps_frame, text='FPS:', font=('Arial', 9)).grid(row=0, column=0, sticky='W')
        self.fps_label = ttk.Label(fps_frame, text='0 FPS', font=('Arial', 9, 'bold'))
        self.fps_label.grid(row=0, column=1, sticky='E')

        # Controls
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=12, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text='Save Config', command=self.save_config).grid(row=0, column=0, padx=4)
        self.start_btn = ttk.Button(btn_frame, text='Start', command=self.toggle)
        self.start_btn.grid(row=0, column=1, padx=4)

        # Randomize labels slightly for additional anti-detection
        # (Not all legitimate apps use identical wording)
        if random.random() < 0.3:  # 30% chance to randomize labels
            self.randomize_ui_labels(main)

        # Always show support link
        sup = ttk.Label(main, text='Support this project', foreground='blue', cursor='hand2')
        sup.grid(row=13, column=0, columnspan=2, pady=5)
        sup.bind('<Button-1>', lambda e: webbrowser.open(SUPPORT_URL))
        
        # Always show footer with MIT license
        footer = tk.Label(main, text='Made by Ozymo MIT license', font=('Arial', 8, 'italic'))
        footer.grid(row=14, column=0, columnspan=2, pady=(5,0))

        self.update_visibility()

    def randomize_ui_labels(self, main_frame):
        """Slightly modify some UI labels to make the app look different each time"""
        # Find all Label widgets
        all_widgets = main_frame.winfo_children()
        labels = []
        
        # Gather all labels and frames to check their children
        for widget in all_widgets:
            if isinstance(widget, ttk.Label) or isinstance(widget, tk.Label):
                labels.append(widget)
            elif isinstance(widget, ttk.Frame) or isinstance(widget, tk.Frame):
                # Check children of frames
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) or isinstance(child, tk.Label):
                        labels.append(child)
        
        # Randomly select some labels to modify
        labels_to_modify = random.sample(labels, min(3, len(labels)))
        
        # Alternative texts for common labels
        alternatives = {
            'Trigger Method:': ['Input Method:', 'Control Type:', 'Input Type:'],
            'Trigger Key:': ['Action Key:', 'Input Key:', 'Control Key:'],
            'Mode:': ['Operation:', 'Function:', 'Behavior:'],
            'Hotkey:': ['Shortcut:', 'Toggle Key:', 'Control Key:'],
            'FPS:': ['Rate:', 'Frequency:', 'Updates:'],
            'Require Crosshair': ['Use Target', 'Need Visual', 'Visual Required'],
            'Save Config': ['Save Settings', 'Apply', 'Update'],
            'Start': ['Begin', 'Run', 'Activate'],
            'Stop': ['End', 'Pause', 'Deactivate']
        }
        
        # Modify selected labels
        for label in labels_to_modify:
            current_text = label.cget('text')
            if current_text in alternatives:
                label.config(text=random.choice(alternatives[current_text]))

    def update_visibility(self):
        method = self.method_var.get()
        if method == 'kmnet':
            self.key_frame.grid_remove()
            self.km_frame.grid()
        else:
            self.km_frame.grid_remove()
            self.key_frame.grid()
        if self.mode_var.get() == 'always':
            self.hotkey_frame.grid_remove()
        else:
            self.hotkey_frame.grid()

    def setup_listeners(self):
        def on_press(key):
            if key == self.kb_hotkey:
                if self.mode_var.get() == 'toggle':
                    self.mode_active = not self.mode_active
                    winsound.Beep(BEEP_ON_FREQ if self.mode_active else BEEP_OFF_FREQ, BEEP_DURATION)
                    self.update_status()
                elif self.mode_var.get() == 'hold':
                    self.mode_active = True
                    self.update_status()

        def on_release(key):
            if key == self.kb_hotkey and self.mode_var.get() == 'hold':
                self.mode_active = False
                self.update_status()

        def on_click(x, y, button, pressed):
            if button == self.mouse_hotkey:
                if pressed:
                    if self.mode_var.get() == 'toggle':
                        self.mode_active = not self.mode_active
                        winsound.Beep(BEEP_ON_FREQ if self.mode_active else BEEP_OFF_FREQ, BEEP_DURATION)
                        self.update_status()
                    elif self.mode_var.get() == 'hold':
                        self.mode_active = True
                        self.update_status()
                else:
                    if self.mode_var.get() == 'hold':
                        self.mode_active = False
                        self.update_status()

        KeyListener(on_press=on_press, on_release=on_release, daemon=True).start()
        MouseListener(on_click=on_click, daemon=True).start()

    def update_fps_display(self):
        while True:
            if self.running:
                fps = self.core.get_fps()
                self.fps_label.config(text=f"{fps:.1f} FPS")
            time.sleep(0.5)

    def update_status(self):
        if not self.running:
            self.status_label.config(text='Stopped', fg='red')
        elif self.mode_var.get() == 'always':
            self.status_label.config(text='Always On', fg='green')
        elif self.mode_var.get() == 'toggle':
            status = 'Toggle On' if self.mode_active else 'Toggle Off'
            self.status_label.config(text=status, fg='green')
        else:
            text = 'Hold (Active)' if self.mode_active else 'Hold (Waiting)'
            self.status_label.config(text=text, fg='green')

    def save_config(self):
        try:
            cfg = json.load(open(CONFIG_PATH))
        except:
            cfg = {}
        cfg.update({
            'method': self.method_var.get(),
            'trigger_key': self.key_var.get(),
            'ip': self.ip_var.get(),
            'port': int(self.port_var.get() or 0),
            'uuid': self.uuid_var.get(),
            'require_crosshair': self.cross_check.get(),
            'press_release_min_ms': self.press_min.get(),
            'press_release_max_ms': self.press_max.get(),
            'delay_after_shoot_min_ms': self.cycle_min.get(),
            'delay_after_shoot_max_ms': self.cycle_max.get(),
            'mode': self.mode_var.get(),
            'hotkey': self.hotkey_var.get()
        })
        json.dump(cfg, open(CONFIG_PATH, 'w'), indent=4)
        self.core.reload_config()

    def toggle(self):
        self.running = not self.running
        self.start_btn.config(text='Stop' if self.running else 'Start')
        self.update_status()
        if self.running:
            self.core.start_capture()
            threading.Thread(target=self.loop, daemon=True).start()
        else:
            self.core.stop_capture()

    def loop(self):
        last_fire = 0
        kb = Controller()
        while self.running:
            should_fire = self.core.get_should_fire_state()
            cross_ok = not self.cross_check.get() or self.core.get_crosshair_state()
            now = time.time()
            cooldown = max(self.cycle_max.get(), 1) / 1000.0
            if should_fire and cross_ok and (self.mode_var.get() == 'always' or self.mode_active) and (now - last_fire) > cooldown:
                last_fire = now
                dur = random.uniform(self.press_min.get(), self.press_max.get()) / 1000.0
                kb.press(self.key_var.get()); time.sleep(dur); kb.release(self.key_var.get())
                time.sleep(random.uniform(self.cycle_min.get(), self.cycle_max.get()) / 1000.0)
            time.sleep(0.001)

if __name__ == '__main__':
    # Memory randomization on startup
    startup_junk = randomize_memory_footprint()
    
    # Use the Process Name randomization to help avoid detection
    if sys.platform == 'win32':
        try:
            # Set a random process name in Windows Task Manager
            import ctypes
            random_name = generate_random_string(8)
            ctypes.windll.kernel32.SetConsoleTitleW(random_name)
            
            # Attempt to mask process name in more advanced ways
            try:
                # If psutil is available, use more advanced techniques
                import psutil
                process = psutil.Process(os.getpid())
                # Some versions of psutil allow name changing
                if hasattr(process, 'name') and callable(getattr(process, 'name')) and hasattr(process.name, 'setter'):
                    process.name = f"svc{generate_random_string(4)}.exe"
            except ImportError:
                pass  # psutil not available
                
        except Exception:
            pass  # Ignore any errors during process name change
            
    root = tk.Tk()
    app = TriggerBotUI(root)
    root.mainloop()
