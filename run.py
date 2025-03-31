import json
import time
import threading
import numpy as np
from mss import mss as mss_module
import kmNet
from ctypes import WinDLL
import sys
import keyboard
import logging
import atexit

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("triggerbot.log"),
        logging.StreamHandler()
    ]
)

class TriggerBot:
    """A class that implements a trigger bot with scoping detection."""
    
    def __init__(self):
        """Initialize the TriggerBot with default settings."""
        self.exit_prog = False
        self.is_scoped = False
        self.target_detected = False
        self.paused = False
        self.threads = []
        self.sct = None
        
        try:
            self.load_config()
            self.init_kmnet()
            self.init_grab_zone()
            self.init_screen_capture()
            
            # Register cleanup function
            atexit.register(self.cleanup)
            
        except Exception as e:
            logging.error(f"Initialization error: {e}")
            self.exit()
    
    def load_config(self):
        """Load configuration from config.json file."""
        try:
            with open('config.json') as json_file:
                data = json.load(json_file)
            
            # Required configuration parameters
            required_keys = [
                "ip", "port", "uid", "trigger_delay", "base_delay", 
                "color_tolerance", "target_color", "scope_color", 
                "scope_color_tolerance", "scope_color_alt", 
                "scope_color_tolerance_alt"
            ]
            
            # Check if all required keys exist
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                raise KeyError(f"Missing required keys in config.json: {', '.join(missing_keys)}")
            
            # Assign configuration values
            self.ip = data["ip"]
            self.port = data["port"]
            self.uid = data["uid"]
            self.trigger_delay = data["trigger_delay"]
            self.base_delay = data["base_delay"]
            self.color_tol = data["color_tolerance"]
            self.R, self.G, self.B = data["target_color"]
            self.scope_R, self.scope_G, self.scope_B = data["scope_color"]
            self.scope_tol = data["scope_color_tolerance"]
            self.scope_R_alt, self.scope_G_alt, self.scope_B_alt = data["scope_color_alt"]
            self.scope_tol_alt = data["scope_color_tolerance_alt"]
            
            logging.info("Configuration loaded successfully")
            
        except FileNotFoundError:
            logging.error("config.json file not found")
            raise
        except json.JSONDecodeError:
            logging.error("Invalid JSON format in config.json")
            raise
        except KeyError as e:
            logging.error(f"Missing key in config.json: {e}")
            raise
    
    def init_kmnet(self):
        """Initialize the kmNet library for input simulation."""
        try:
            kmNet.init(self.ip, self.port, self.uid)
            kmNet.monitor(10000)
            logging.info("kmNet initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing kmNet: {e}")
            raise
    
    def init_grab_zone(self):
        """Initialize the screen region to monitor for targets."""
        try:
            user32 = WinDLL("user32", use_last_error=True)
            shcore = WinDLL("shcore", use_last_error=True)
            
            # Set DPI awareness to ensure consistent screen coordinates
            shcore.SetProcessDpiAwareness(2)
            width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            
            self.ZONE = 3  # Size of the grab zone (pixels from center)
            self.GRAB_ZONE = {
                "left": int(width / 2 - self.ZONE),
                "top": int(height / 2 - self.ZONE),
                "width": 2 * self.ZONE,
                "height": 2 * self.ZONE,
            }
            logging.info(f"Grab zone initialized: {self.GRAB_ZONE}")
        except Exception as e:
            logging.error(f"Error initializing grab zone: {e}")
            raise
    
    def init_screen_capture(self):
        """Initialize the screen capture object."""
        try:
            self.sct = mss_module()
            logging.info("Screen capture initialized")
        except Exception as e:
            logging.error(f"Error initializing screen capture: {e}")
            raise
    
    def search_and_scope(self):
        """Monitor the grab zone for targets and scope indicators."""
        grab_zone = self.GRAB_ZONE
        color_tol = self.color_tol
        R, G, B = self.R, self.G, self.B
        
        while not self.exit_prog:
            try:
                if self.paused:
                    time.sleep(0.01)
                    continue
                
                # Capture screen region
                img = np.array(self.sct.grab(grab_zone))
                
                # Determine which scope detection to use based on side button
                if kmNet.isdown_side2() == 1:
                    scope_R, scope_G, scope_B = self.scope_R_alt, self.scope_G_alt, self.scope_B_alt
                    scope_tol = self.scope_tol_alt
                else:
                    scope_R, scope_G, scope_B = self.scope_R, self.scope_G, self.scope_B
                    scope_tol = self.scope_tol
                
                # Create masks for target and scope detection
                target_mask = (
                    (img[:, :, 2] >= R - color_tol) & (img[:, :, 2] <= R + color_tol) &  # Red channel
                    (img[:, :, 1] >= G - color_tol) & (img[:, :, 1] <= G + color_tol) &  # Green channel
                    (img[:, :, 0] >= B - color_tol) & (img[:, :, 0] <= B + color_tol)    # Blue channel
                )
                
                scope_mask = (
                    (img[:, :, 2] >= scope_R - scope_tol) & (img[:, :, 2] <= scope_R + scope_tol) &  # Red channel
                    (img[:, :, 1] >= scope_G - scope_tol) & (img[:, :, 1] <= scope_G + scope_tol) &  # Green channel
                    (img[:, :, 0] >= scope_B - scope_tol) & (img[:, :, 0] <= scope_B + scope_tol)    # Blue channel
                )
                
                # Update detection flags
                self.target_detected = np.any(target_mask)
                self.is_scoped = np.any(scope_mask)
                
                # Short sleep to reduce CPU usage
                time.sleep(0.001)
                
            except Exception as e:
                logging.error(f"Error in search_and_scope: {e}")
                time.sleep(0.1)  # Sleep longer on error to avoid spam
    
    def trigger(self):
        """Trigger mouse clicks when conditions are met."""
        while not self.exit_prog:
            try:
                if self.is_scoped and self.target_detected and not self.paused:
                    # Calculate delay based on configuration
                    delay_percentage = self.trigger_delay / 100.0
                    actual_delay = self.base_delay + self.base_delay * delay_percentage
                    time.sleep(actual_delay)
                    
                    # Perform mouse click
                    kmNet.left(1)
                    # Add randomness to timing for more human-like behavior
                    time.sleep(np.random.uniform(0.080, 0.12))
                    kmNet.left(0)
                    time.sleep(np.random.uniform(0.05, 0.09))
                else:
                    time.sleep(0.001)
                    
            except Exception as e:
                logging.error(f"Error in trigger function: {e}")
                time.sleep(0.1)
    
    def start_threads(self):
        """Start all worker threads."""
        try:
            # Create and start threads
            search_thread = threading.Thread(target=self.search_and_scope, name="SearchThread")
            trigger_thread = threading.Thread(target=self.trigger, name="TriggerThread")
            keyboard_thread = threading.Thread(target=self.keyboard_listener, name="KeyboardThread")
            
            # Set threads as daemon so they exit when main thread exits
            search_thread.daemon = True
            trigger_thread.daemon = True
            keyboard_thread.daemon = True
            
            # Start threads
            search_thread.start()
            trigger_thread.start()
            keyboard_thread.start()
            
            # Store thread references
            self.threads = [search_thread, trigger_thread, keyboard_thread]
            
            logging.info("All threads started successfully")
            
        except Exception as e:
            logging.error(f"Error starting threads: {e}")
            self.exit()
    
    def keyboard_listener(self):
        """Listen for keyboard commands."""
        while not self.exit_prog:
            try:
                if keyboard.is_pressed('F2'):
                    logging.info("Exit command detected (F2)")
                    self.exit_prog = True
                    self.exit()
                    break
                    
                elif keyboard.is_pressed('F3'):
                    self.paused = not self.paused
                    state = "paused" if self.paused else "resumed"
                    logging.info(f"Program {state} (F3)")
                    time.sleep(0.3)  # Longer delay to prevent multiple toggles
                    
                elif keyboard.is_pressed('F4'):
                    logging.info("Reloading configuration (F4)")
                    self.load_config()
                    logging.info("Configuration reloaded successfully")
                    time.sleep(0.3)  # Longer delay to prevent multiple reloads
                    
                time.sleep(0.1)  # Check less frequently to reduce CPU usage
                
            except Exception as e:
                logging.error(f"Error in keyboard listener: {e}")
                time.sleep(0.5)  # Sleep longer on error
    
    def cleanup(self):
        """Clean up resources when exiting."""
        logging.info("Cleaning up resources...")
        
        # Close screen capture object if it exists
        if self.sct:
            self.sct.close()
            
        # Any other cleanup needed for kmNet
        try:
            # This is hypothetical as I don't know if kmNet has a cleanup function
            if hasattr(kmNet, 'cleanup'):
                kmNet.cleanup()
        except Exception as e:
            logging.error(f"Error during kmNet cleanup: {e}")
            
        logging.info("Cleanup completed")
    
    def exit(self):
        """Exit the program gracefully."""
        logging.info("Exiting program...")
        self.exit_prog = True
        self.cleanup()
        # Give threads a moment to terminate
        time.sleep(0.2)
        sys.exit(0)

def main():
    """Main entry point of the application."""
    try:
        logging.info("2-condition-triggerbot created by Ozymo. Version: 1.6")
        logging.info("Press F2 to exit the program")
        logging.info("Press F3 to pause/continue the program")
        logging.info("Press F4 to reload config")
        
        # Create and start the bot
        bot = TriggerBot()
        bot.start_threads()
        
        # Keep main thread alive
        while not bot.exit_prog:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logging.info("Program interrupted by user")
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}", exc_info=True)
    finally:
        # Ensure we exit properly even if an exception occurs
        logging.info("Program terminated")
        sys.exit(0)

if __name__ == "__main__":
    main()
