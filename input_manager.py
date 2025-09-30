# input_manager.py
import time
import random
import winsound
from pynput.keyboard import Controller, Listener as KeyListener, Key, KeyCode
from pynput.mouse import Listener as MouseListener, Button as MouseButton

# KMNet import
try:
    import kmNet
    HAS_KMNET = True
    print("✅ KMNet available")
except ImportError:
    HAS_KMNET = False
    print("⚠️  KMNet not available - falling back to pynput")

BEEP_ON_FREQ = 800
BEEP_OFF_FREQ = 600
BEEP_DURATION = 50

class InputManager:
    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback
        self.kb_hotkey = None
        self.mouse_hotkey = None
        self.mode_active = False
        self.running = False
        self.kmnet_initialized = False
        
        # Input simulation
        self.kb_controller = Controller()
        
        # Setup listeners
        self.setup_listeners()
        
        # DON'T initialize KMNet immediately - wait for explicit call
        print("🎯 InputManager initialized")

    def init_kmnet_if_needed(self):
        """Initialize KMNet if method is kmnet and not already initialized"""
        if not self.ui_callback:
            return
            
        try:
            method = self.ui_callback('get_method')
            if method == 'kmnet' and HAS_KMNET and not self.kmnet_initialized:
                ip = self.ui_callback('get_ip')
                port_str = self.ui_callback('get_port')
                port = int(port_str) if port_str else 0
                uuid = self.ui_callback('get_uuid')
                
                if ip and port and uuid:
                    kmNet.init(ip, port, uuid)
                    kmNet.monitor(10000)  # Monitor with timeout
                    self.kmnet_initialized = True
                    print(f"✅ KMNet initialized: {ip}:{port}")
                else:
                    print("❌ KMNet: Missing IP/Port/UUID")
        except Exception as e:
            print(f"❌ KMNet initialization failed: {e}")
            self.kmnet_initialized = False

    def parse_hotkey(self, hotkey_name):
        """Parse hotkey name to key objects"""
        if hotkey_name.upper() == 'XBUTTON1':
            self.mouse_hotkey = MouseButton.x1
            self.kb_hotkey = None
        elif hotkey_name.upper() == 'XBUTTON2':
            self.mouse_hotkey = MouseButton.x2
            self.kb_hotkey = None
        else:
            self.mouse_hotkey = None
            lower = hotkey_name.lower()
            try:
                key = getattr(Key, lower)
            except AttributeError:
                key = KeyCode.from_char(lower)
            self.kb_hotkey = key

    def setup_listeners(self):
        """Setup keyboard and mouse listeners"""
        def on_press(key):
            if key == self.kb_hotkey and self.ui_callback:
                mode = self.ui_callback('get_mode')
                if mode == 'toggle':
                    self.mode_active = not self.mode_active
                    winsound.Beep(BEEP_ON_FREQ if self.mode_active else BEEP_OFF_FREQ, BEEP_DURATION)
                    self.ui_callback('update_status')
                elif mode == 'hold':
                    self.mode_active = True
                    self.ui_callback('update_status')

        def on_release(key):
            if key == self.kb_hotkey and self.ui_callback:
                mode = self.ui_callback('get_mode')
                if mode == 'hold':
                    self.mode_active = False
                    self.ui_callback('update_status')

        def on_click(x, y, button, pressed):
            if button == self.mouse_hotkey and self.ui_callback:
                mode = self.ui_callback('get_mode')
                if pressed:
                    if mode == 'toggle':
                        self.mode_active = not self.mode_active
                        winsound.Beep(BEEP_ON_FREQ if self.mode_active else BEEP_OFF_FREQ, BEEP_DURATION)
                        self.ui_callback('update_status')
                    elif mode == 'hold':
                        self.mode_active = True
                        self.ui_callback('update_status')
                else:
                    if mode == 'hold':
                        self.mode_active = False
                        self.ui_callback('update_status')

        KeyListener(on_press=on_press, on_release=on_release, daemon=True).start()
        MouseListener(on_click=on_click, daemon=True).start()

    def simulate_key_press(self, key, duration_ms):
        """Simulate key press - KMNet or pynput based on method"""
        if not self.ui_callback:
            return
            
        method = self.ui_callback('get_method')
        
        if method == 'kmnet' and HAS_KMNET and self.kmnet_initialized:
            # KMNet hardware input (mouse click)
            try:
                duration = duration_ms / 1000.0
                kmNet.left(1)  # Mouse down
                time.sleep(duration)
                kmNet.left(0)  # Mouse up
                return
            except Exception as e:
                print(f"❌ KMNet click failed: {e}")
                # Fall back to pynput
        
        # Software input (pynput) - fallback or default
        duration = duration_ms / 1000.0
        mapped_key = self._map_key(key)
        self.kb_controller.press(mapped_key)
        time.sleep(duration)
        self.kb_controller.release(mapped_key)

    def _map_key(self, key_name):
        """Map key name to pynput key"""
        if isinstance(key_name, str):
            lower = key_name.lower()
            if lower == 'space':
                return Key.space
            elif lower == 'return' or lower == 'enter':
                return Key.enter
            elif lower == 'escape':
                return Key.esc
            elif lower in ['left', 'right', 'up', 'down']:
                return getattr(Key, lower)
            elif lower.startswith('f') and lower[1:].isdigit():
                return getattr(Key, lower)
            else:
                return KeyCode.from_char(lower)
        return key_name

    def get_mode_active(self):
        """Get current mode active state"""
        return self.mode_active

    def set_mode_active(self, active):
        """Set mode active state"""
        self.mode_active = active
