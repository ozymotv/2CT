#!/usr/bin/env python

import os, sys, random, string
import tkinter as tk
from ui_components import TriggerBotUI
from utils import generate_random_string, randomize_memory_footprint

# Hide console on Windows (uncomment to hide errors)
# if sys.platform == 'win32':
#     import ctypes
#     ctypes.windll.kernel32.FreeConsole()

def main():
    startup_junk = randomize_memory_footprint()
    
    if sys.platform == 'win32':
        try:
            import ctypes
            random_name = generate_random_string(8)
            ctypes.windll.kernel32.SetConsoleTitleW(random_name)
            
            try:
                import psutil
                process = psutil.Process(os.getpid())
                if hasattr(process, 'name') and callable(getattr(process, 'name')) and hasattr(process.name, 'setter'):
                    process.name = f"svc{generate_random_string(4)}.exe"
            except ImportError:
                pass
            except Exception:
                pass
        except:
            pass
    
    print("🚀 Starting TriggerBot...")
    
    try:
        root = tk.Tk()
        app = TriggerBotUI(root)
        print("✅ TriggerBot UI created successfully")
        root.mainloop()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
