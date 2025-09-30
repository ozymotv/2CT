# input_manager.py
import time
import random
import winsound
from pynput.keyboard import Controller, Listener as KeyListener, Key, KeyCode
from pynput.mouse import Listener as MouseListener, Button as MouseButton

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
        
        # Input simulation
        self.kb_controller = Controller()
        
        # Setup listeners
        self.setup_listeners()
    
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
        """Simulate key press with specified duration"""
        duration = duration_ms / 1000.0
        self.kb_controller.press(key)
        time.sleep(duration)
        self.kb_controller.release(key)
    
    def get_mode_active(self):
        """Get current mode active state"""
        return self.mode_active
    
    def set_mode_active(self, active):
        """Set mode active state"""
        self.mode_active = active
