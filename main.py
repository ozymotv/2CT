#!/usr/bin/env python

import os, sys, random, string
import tkinter as tk
from ui_components import TriggerBotUI
from utils import generate_random_string, randomize_memory_footprint

# Hide console on Windows
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.FreeConsole()

def main():
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

if __name__ == '__main__':
    main()
