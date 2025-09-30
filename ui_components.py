# ui_components.py
import json
import threading
import time
import random
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

from config_manager import ConfigManager
from detection_engine import DetectionEngine
from input_manager import InputManager
from utils import *

KEY_DOC_URL = 'https://docs.microsoft.com/windows/win32/inputdev/virtual-key-codes'
SUPPORT_URL = 'https://github.com/ozymotv/supportme'

KEY_OPTIONS = [
    *[chr(c) for c in range(ord('A'), ord('Z')+1)],
    *[str(d) for d in range(0, 10)],
    *[f'F{i}' for i in range(1, 13)],
    'Left', 'Right', 'Up', 'Down', 'Return', 'Escape', 'Space',
    'XBUTTON1', 'XBUTTON2'
]

class TriggerBotUI:
    def __init__(self, root):
        self.root = root
        
        # Anti-detection setup
        self.random_title = generate_window_title()
        root.title(self.random_title)
        root.resizable(False, False)
        self.junk_memory = randomize_memory_footprint()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # State variables
        self.running = False
        self.window_id = generate_random_string(6)
        
        # 🔧 CRITICAL FIX: Define ALL UI variables FIRST before creating managers
        self.method_var = tk.StringVar(value=self.config.get('method', 'key'))
        self.key_var = tk.StringVar(value=self.config.get('trigger_key', 'Space'))
        self.ip_var = tk.StringVar(value=self.config.get('ip', ''))
        self.port_var = tk.StringVar(value=str(self.config.get('port', '')))
        self.uuid_var = tk.StringVar(value=self.config.get('uuid', ''))
        self.cross_check = tk.IntVar(value=self.config.get('require_crosshair', 0))
        self.press_min = tk.IntVar(value=self.config.get('press_release_min_ms', 80))
        self.press_max = tk.IntVar(value=self.config.get('press_release_max_ms', 100))
        self.cycle_min = tk.IntVar(value=self.config.get('delay_after_shoot_min_ms', 200))
        self.cycle_max = tk.IntVar(value=self.config.get('delay_after_shoot_max_ms', 200))
        self.mode_var = tk.StringVar(value=self.config.get('mode', 'always'))
        self.hotkey_var = tk.StringVar(value=self.config.get('hotkey', 'T'))
        
        # UI Variables - Advanced Settings (Previously Hidden)
        self.target_color_tol = tk.IntVar(value=self.config.get('target_color_tolerance', 60))
        self.target_color_r = tk.IntVar(value=self.config.get('target_color', [252, 60, 250])[0])
        self.target_color_g = tk.IntVar(value=self.config.get('target_color', [252, 60, 250])[1])
        self.target_color_b = tk.IntVar(value=self.config.get('target_color', [252, 60, 250])[2])
        self.crosshair_color_r = tk.IntVar(value=self.config.get('crosshair_color', [65, 255, 0])[0])
        self.crosshair_color_g = tk.IntVar(value=self.config.get('crosshair_color', [65, 255, 0])[1])
        self.crosshair_color_b = tk.IntVar(value=self.config.get('crosshair_color', [65, 255, 0])[2])
        self.crosshair_color_tol = tk.IntVar(value=self.config.get('crosshair_color_tolerance', 25))
        self.trigger_zone_size = tk.IntVar(value=self.config.get('trigger_zone_size', 50))
        self.center_zone_size = tk.IntVar(value=self.config.get('center_zone_size', 3))
        self.max_ray_distance = tk.IntVar(value=self.config.get('max_ray_distance', 50))
        self.rays_per_direction = tk.IntVar(value=self.config.get('rays_per_direction', 5))
        self.ray_angle_spread = tk.IntVar(value=self.config.get('ray_angle_spread', 30))
        self.num_threads = tk.IntVar(value=self.config.get('num_threads', 4))
        
        # NOW create managers AFTER all variables are defined
        print("🔧 Creating detection engine...")
        self.detection_engine = DetectionEngine(self.config)
        print("🔧 Creating input manager...")
        self.input_manager = InputManager(self.ui_callback)
        
        # Setup UI
        self.setup_anti_detection()
        self.build_ui()
        self.input_manager.parse_hotkey(self.hotkey_var.get())
        
        # 🔧 DELAY KMNet init until UI is fully loaded
        if self.method_var.get() == 'kmnet':
            threading.Thread(target=self.delayed_kmnet_init, daemon=True).start()
        
        # Start background threads
        threading.Thread(target=self.update_fps_display, daemon=True).start()
        if random.random() < 0.5:
            threading.Thread(target=self.rotate_window_title, daemon=True).start()
        threading.Thread(target=self.periodically_alter_memory, daemon=True).start()
        
        # Position window
        self.position_window_naturally()
        print("✅ TriggerBotUI fully initialized")
        
    def delayed_kmnet_init(self):
        """Initialize KMNet after UI is fully loaded"""
        time.sleep(1.0)  # Wait for UI to be ready
        try:
            self.input_manager.init_kmnet_if_needed()
            print("✅ KMNet initialization completed")
        except Exception as e:
            print(f"⚠️ KMNet initialization failed: {e}")

    def setup_anti_detection(self):
        """Setup anti-detection features"""
        try:
            random_icon = self.get_random_system_icon()
            if random_icon:
                self.root.iconbitmap(random_icon)
        except:
            pass

    def build_ui(self):
        """Build the complete UI with tabs for basic and advanced settings"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Basic Settings Tab
        basic_frame = ttk.Frame(notebook, padding=10)
        notebook.add(basic_frame, text='Basic Settings')
        self.build_basic_tab(basic_frame)
        
        # Advanced Settings Tab (NEW - Previously Hidden)
        advanced_frame = ttk.Frame(notebook, padding=10)
        notebook.add(advanced_frame, text='Advanced Settings')
        self.build_advanced_tab(advanced_frame)
        
        # Control Panel (at bottom)
        self.build_control_panel()

    def build_basic_tab(self, parent):
        """Build basic settings tab"""
        pad = {'padx': 8, 'pady': 4}
        
        # Trigger Method
        ttk.Label(parent, text='Trigger Method:').grid(row=0, column=0, sticky='W', **pad)
        ttk.OptionMenu(parent, self.method_var, self.method_var.get(), 'key', 'kmnet',
                       command=lambda _: self.update_visibility()).grid(row=0, column=1, sticky='EW', **pad)
        
        # Trigger Key Frame
        self.key_frame = ttk.Frame(parent)
        ttk.Label(self.key_frame, text='Fire key:').grid(row=0, column=0, sticky='W', **pad)
        ttk.Combobox(self.key_frame, values=KEY_OPTIONS, textvariable=self.key_var, width=15).grid(row=0, column=1, sticky='EW', **pad)
        link1 = ttk.Label(self.key_frame, text='Key Codes', foreground='blue', cursor='hand2')
        link1.grid(row=1, column=1, sticky='W', **pad)
        link1.bind('<Button-1>', lambda e: webbrowser.open(KEY_DOC_URL))
        self.key_frame.grid(row=1, column=0, columnspan=2, sticky='EW')
        
        # KMNet Settings Frame
        self.km_frame = ttk.Frame(parent)
        for i, (lbl, k) in enumerate([('IP', 'ip'), ('Port', 'port'), ('UUID', 'uuid')]):
            ttk.Label(self.km_frame, text=f'{lbl}:').grid(row=i, column=0, sticky='W', **pad)
            var = getattr(self, f'{k}_var')
            ttk.Entry(self.km_frame, textvariable=var).grid(row=i, column=1, sticky='EW', **pad)
        self.km_frame.grid(row=2, column=0, columnspan=2, sticky='EW')
        
        # Crosshair requirement
        ttk.Checkbutton(parent, text='Require Crosshair', variable=self.cross_check).grid(row=3, column=0, columnspan=2, sticky='W', **pad)
        
        # Timing settings
        timing_labels = [
            ('Press Min (ms):', 'press_min'),
            ('Press Max (ms):', 'press_max'),
            ('Delay Min (ms):', 'cycle_min'),
            ('Delay Max (ms):', 'cycle_max'),
        ]
        
        for idx, (label, var_name) in enumerate(timing_labels, start=4):
            ttk.Label(parent, text=label).grid(row=idx, column=0, sticky='W', **pad)
            var = getattr(self, var_name)
            ttk.Spinbox(parent, from_=0, to=5000, textvariable=var, width=8).grid(row=idx, column=1, sticky='EW', **pad)
        
        # Mode selection
        ttk.Label(parent, text='Mode:').grid(row=8, column=0, sticky='W', **pad)
        ttk.OptionMenu(parent, self.mode_var, self.mode_var.get(), 'always', 'toggle', 'hold',
                       command=lambda _: self.update_visibility()).grid(row=8, column=1, sticky='EW', **pad)
        
        # Hotkey selection
        self.hotkey_frame = ttk.Frame(parent)
        ttk.Label(self.hotkey_frame, text='Hotkey:').grid(row=0, column=0, sticky='W', **pad)
        hotkey_cb = ttk.Combobox(self.hotkey_frame, values=KEY_OPTIONS, textvariable=self.hotkey_var, width=15)
        hotkey_cb.grid(row=0, column=1, sticky='EW', **pad)
        hotkey_cb.bind('<<ComboboxSelected>>', lambda e: self.input_manager.parse_hotkey(self.hotkey_var.get()))
        link2 = ttk.Label(self.hotkey_frame, text='Key Codes', foreground='blue', cursor='hand2')
        link2.grid(row=0, column=2, sticky='W', padx=5)
        link2.bind('<Button-1>', lambda e: webbrowser.open(KEY_DOC_URL))
        self.hotkey_frame.grid(row=9, column=0, columnspan=2, sticky='EW')
        
        self.update_visibility()

    def build_advanced_tab(self, parent):
        """Build advanced settings tab (Previously hidden settings)"""
        pad = {'padx': 8, 'pady': 4}
        
        # Warning label
        warning = ttk.Label(parent, text="⚠️ Advanced Settings - Change only if you know what you're doing",
                           foreground='red', font=('Arial', 9, 'bold'))
        warning.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Target Color Settings
        color_frame = ttk.LabelFrame(parent, text="Target Color Detection", padding=10)
        color_frame.grid(row=1, column=0, columnspan=3, sticky='EW', **pad)
        
        ttk.Label(color_frame, text='Target Color Tolerance:').grid(row=0, column=0, sticky='W', **pad)
        ttk.Spinbox(color_frame, from_=1, to=255, textvariable=self.target_color_tol, width=8).grid(row=0, column=1, **pad)
        
        ttk.Label(color_frame, text='Target Color RGB:').grid(row=1, column=0, sticky='W', **pad)
        rgb_frame = ttk.Frame(color_frame)
        rgb_frame.grid(row=1, column=1, columnspan=2, **pad)
        ttk.Label(rgb_frame, text='R:').grid(row=0, column=0)
        ttk.Spinbox(rgb_frame, from_=0, to=255, textvariable=self.target_color_r, width=6).grid(row=0, column=1, padx=2)
        ttk.Label(rgb_frame, text='G:').grid(row=0, column=2)
        ttk.Spinbox(rgb_frame, from_=0, to=255, textvariable=self.target_color_g, width=6).grid(row=0, column=3, padx=2)
        ttk.Label(rgb_frame, text='B:').grid(row=0, column=4)
        ttk.Spinbox(rgb_frame, from_=0, to=255, textvariable=self.target_color_b, width=6).grid(row=0, column=5, padx=2)
        
        # Crosshair Color Settings
        crosshair_frame = ttk.LabelFrame(parent, text="Crosshair Detection", padding=10)
        crosshair_frame.grid(row=2, column=0, columnspan=3, sticky='EW', **pad)
        
        ttk.Label(crosshair_frame, text='Crosshair Color Tolerance:').grid(row=0, column=0, sticky='W', **pad)
        ttk.Spinbox(crosshair_frame, from_=1, to=255, textvariable=self.crosshair_color_tol, width=8).grid(row=0, column=1, **pad)
        
        ttk.Label(crosshair_frame, text='Crosshair Color RGB:').grid(row=1, column=0, sticky='W', **pad)
        ch_rgb_frame = ttk.Frame(crosshair_frame)
        ch_rgb_frame.grid(row=1, column=1, columnspan=2, **pad)
        ttk.Label(ch_rgb_frame, text='R:').grid(row=0, column=0)
        ttk.Spinbox(ch_rgb_frame, from_=0, to=255, textvariable=self.crosshair_color_r, width=6).grid(row=0, column=1, padx=2)
        ttk.Label(ch_rgb_frame, text='G:').grid(row=0, column=2)
        ttk.Spinbox(ch_rgb_frame, from_=0, to=255, textvariable=self.crosshair_color_g, width=6).grid(row=0, column=3, padx=2)
        ttk.Label(ch_rgb_frame, text='B:').grid(row=0, column=4)
        ttk.Spinbox(ch_rgb_frame, from_=0, to=255, textvariable=self.crosshair_color_b, width=6).grid(row=0, column=5, padx=2)
        
        # Detection Zone Settings
        zone_frame = ttk.LabelFrame(parent, text="Detection Zones", padding=10)
        zone_frame.grid(row=3, column=0, columnspan=3, sticky='EW', **pad)
        
        ttk.Label(zone_frame, text='Trigger Zone Size:').grid(row=0, column=0, sticky='W', **pad)
        ttk.Spinbox(zone_frame, from_=10, to=200, textvariable=self.trigger_zone_size, width=8).grid(row=0, column=1, **pad)
        
        ttk.Label(zone_frame, text='Center Zone Size:').grid(row=1, column=0, sticky='W', **pad)
        ttk.Spinbox(zone_frame, from_=1, to=20, textvariable=self.center_zone_size, width=8).grid(row=1, column=1, **pad)
        
        # Ray Tracing Settings
        ray_frame = ttk.LabelFrame(parent, text="Ray Tracing", padding=10)
        ray_frame.grid(row=4, column=0, columnspan=3, sticky='EW', **pad)
        
        ttk.Label(ray_frame, text='Max Ray Distance:').grid(row=0, column=0, sticky='W', **pad)
        ttk.Spinbox(ray_frame, from_=10, to=200, textvariable=self.max_ray_distance, width=8).grid(row=0, column=1, **pad)
        
        ttk.Label(ray_frame, text='Rays Per Direction:').grid(row=1, column=0, sticky='W', **pad)
        ttk.Spinbox(ray_frame, from_=1, to=20, textvariable=self.rays_per_direction, width=8).grid(row=1, column=1, **pad)
        
        ttk.Label(ray_frame, text='Ray Angle Spread:').grid(row=2, column=0, sticky='W', **pad)
        ttk.Spinbox(ray_frame, from_=5, to=90, textvariable=self.ray_angle_spread, width=8).grid(row=2, column=1, **pad)
        
        # Performance Settings
        perf_frame = ttk.LabelFrame(parent, text="Performance", padding=10)
        perf_frame.grid(row=5, column=0, columnspan=3, sticky='EW', **pad)
        
        ttk.Label(perf_frame, text='Number of Threads:').grid(row=0, column=0, sticky='W', **pad)
        ttk.Spinbox(perf_frame, from_=1, to=16, textvariable=self.num_threads, width=8).grid(row=0, column=1, **pad)
        
        # Reset to defaults button
        ttk.Button(parent, text='Reset to Defaults', command=self.reset_advanced_defaults).grid(row=6, column=0, columnspan=3, pady=10)

    def build_control_panel(self):
        """Build control panel at bottom"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Status and FPS
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill='x')
        
        self.status_label = tk.Label(status_frame, text='Stopped', fg='red', font=('Arial', 10, 'bold'))
        self.status_label.pack(side='left')
        
        fps_frame = ttk.Frame(status_frame)
        fps_frame.pack(side='right')
        ttk.Label(fps_frame, text='FPS:', font=('Arial', 9)).pack(side='left')
        self.fps_label = ttk.Label(fps_frame, text='0 FPS', font=('Arial', 9, 'bold'))
        self.fps_label.pack(side='left')
        
        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text='Save Config', command=self.save_config).pack(side='left', padx=4)
        self.start_btn = ttk.Button(btn_frame, text='Start', command=self.toggle)
        self.start_btn.pack(side='left', padx=4)
        
        # Links
        sup = ttk.Label(control_frame, text='Support this project', foreground='blue', cursor='hand2')
        sup.pack(pady=5)
        sup.bind('<Button-1>', lambda e: webbrowser.open(SUPPORT_URL))
        
        footer = tk.Label(control_frame, text='Made by Ozymo MIT license', font=('Arial', 8, 'italic'))
        footer.pack()

    def reset_advanced_defaults(self):
        """Reset advanced settings to defaults"""
        if messagebox.askyesno("Reset Advanced Settings", "Reset all advanced settings to default values?"):
            defaults = self.config_manager.default_config
            self.target_color_tol.set(defaults['target_color_tolerance'])
            self.target_color_r.set(defaults['target_color'][0])
            self.target_color_g.set(defaults['target_color'][1])
            self.target_color_b.set(defaults['target_color'][2])
            self.crosshair_color_r.set(defaults['crosshair_color'][0])
            self.crosshair_color_g.set(defaults['crosshair_color'][1])
            self.crosshair_color_b.set(defaults['crosshair_color'][2])
            self.crosshair_color_tol.set(defaults['crosshair_color_tolerance'])
            self.trigger_zone_size.set(defaults['trigger_zone_size'])
            self.center_zone_size.set(defaults['center_zone_size'])
            self.max_ray_distance.set(defaults['max_ray_distance'])
            self.rays_per_direction.set(defaults['rays_per_direction'])
            self.ray_angle_spread.set(defaults['ray_angle_spread'])
            self.num_threads.set(defaults['num_threads'])

    def save_config(self):
        """Save all settings to config file"""
        try:
            config = {
                # Basic settings
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
                'hotkey': self.hotkey_var.get(),
                
                # Advanced settings (Previously hidden)
                'target_color_tolerance': self.target_color_tol.get(),
                'target_color': [self.target_color_r.get(), self.target_color_g.get(), self.target_color_b.get()],
                'crosshair_color': [self.crosshair_color_r.get(), self.crosshair_color_g.get(), self.crosshair_color_b.get()],
                'crosshair_color_tolerance': self.crosshair_color_tol.get(),
                'trigger_zone_size': self.trigger_zone_size.get(),
                'center_zone_size': self.center_zone_size.get(),
                'max_ray_distance': self.max_ray_distance.get(),
                'rays_per_direction': self.rays_per_direction.get(),
                'ray_angle_spread': self.ray_angle_spread.get(),
                'num_threads': self.num_threads.get()
            }
            
            self.config_manager.save_config(config)
            self.config = config
            self.detection_engine.reload_config(config)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def toggle(self):
        """Toggle bot running state"""
        self.running = not self.running
        self.start_btn.config(text='Stop' if self.running else 'Start')
        self.update_status()
        
        if self.running:
            # Initialize KMNet if using kmnet method
            if self.method_var.get() == 'kmnet':
                self.input_manager.init_kmnet_if_needed()
            
            self.detection_engine.start_capture()
            threading.Thread(target=self.bot_loop, daemon=True).start()
            print("🚀 Bot started!")
        else:
            self.detection_engine.stop_capture()
            print("🛑 Bot stopped!")

    def bot_loop(self):
        """Main bot execution loop with KMNet support"""
        last_fire = 0
        while self.running:
            should_fire = self.detection_engine.get_should_fire_state()
            cross_ok = not self.cross_check.get() or self.detection_engine.get_crosshair_state()
            now = time.time()
            cooldown = max(self.cycle_max.get(), 1) / 1000.0
            mode = self.mode_var.get()
            mode_ready = (mode == 'always' or self.input_manager.get_mode_active())

            if should_fire and cross_ok and mode_ready and (now - last_fire) > cooldown:
                last_fire = now
                duration = random.uniform(self.press_min.get(), self.press_max.get())
                
                # For KMNet, we use empty key name - it will use mouse click
                if self.method_var.get() == 'kmnet':
                    self.input_manager.simulate_key_press('', duration)
                else:
                    self.input_manager.simulate_key_press(self.key_var.get(), duration)
                    
                time.sleep(random.uniform(self.cycle_min.get(), self.cycle_max.get()) / 1000.0)

            time.sleep(0.001)

    def update_visibility(self):
        """Update UI visibility based on current settings"""
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

    def update_status(self):
        """Update status display"""
        if not self.running:
            self.status_label.config(text='Stopped', fg='red')
        elif self.mode_var.get() == 'always':
            self.status_label.config(text='Always On', fg='green')
        elif self.mode_var.get() == 'toggle':
            status = 'Toggle On' if self.input_manager.get_mode_active() else 'Toggle Off'
            self.status_label.config(text=status, fg='green')
        else:
            text = 'Hold (Active)' if self.input_manager.get_mode_active() else 'Hold (Waiting)'
            self.status_label.config(text=text, fg='green')

    def update_fps_display(self):
        """Update FPS display"""
        while True:
            if self.running:
                fps = self.detection_engine.get_fps()
                self.fps_label.config(text=f"{fps:.1f} FPS")
            time.sleep(0.5)

    def ui_callback(self, action):
        """Callback for input manager - COMPLETE IMPLEMENTATION WITH KMNET SUPPORT"""
        try:
            if action == 'get_mode':
                return getattr(self, 'mode_var', tk.StringVar(value='always')).get()
            elif action == 'get_method':
                return getattr(self, 'method_var', tk.StringVar(value='key')).get()
            elif action == 'get_ip':
                return getattr(self, 'ip_var', tk.StringVar(value='')).get()
            elif action == 'get_port':
                return getattr(self, 'port_var', tk.StringVar(value='0')).get()
            elif action == 'get_uuid':
                return getattr(self, 'uuid_var', tk.StringVar(value='')).get()
            elif action == 'update_status':
                if hasattr(self, 'update_status'):
                    self.update_status()
            else:
                return None
        except Exception as e:
            print(f"ui_callback error: {e}")
            return None

    # Anti-detection methods (preserved from original)
    def get_random_system_icon(self):
        """Try to use a random system icon (Windows only)"""
        import sys, os
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
        
        return random.choice(icon_files) if icon_files else None

    def position_window_naturally(self):
        """Position window naturally"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        positions = [
            {'x': screen_width // 2 - 250, 'y': screen_height // 2 - 200},  # Center
            {'x': 50, 'y': 50},  # Top left
            {'x': screen_width - 500, 'y': 50},  # Top right
            {'x': 50, 'y': screen_height - 500}  # Bottom left
        ]
        
        pos = random.choice(positions)
        variation_x = random.randint(-30, 30)
        variation_y = random.randint(-30, 30)
        self.root.geometry(f"+{pos['x'] + variation_x}+{pos['y'] + variation_y}")

    def rotate_window_title(self):
        """Periodically change window title"""
        while True:
            sleep_time = random.randint(30, 180)
            time.sleep(sleep_time)
            if not self.root.focus_get():
                new_title = generate_window_title()
                self.root.title(new_title)
                self.random_title = new_title

    def periodically_alter_memory(self):
        """Periodically change memory patterns"""
        while True:
            sleep_time = random.randint(10, 30)
            time.sleep(sleep_time)
            if hasattr(self, 'junk_memory') and self.junk_memory:
                replace_count = min(len(self.junk_memory) // 10, 100)
                for _ in range(replace_count):
                    idx = random.randint(0, len(self.junk_memory) - 1)
                    self.junk_memory[idx] = generate_random_string(random.randint(10, 100))
