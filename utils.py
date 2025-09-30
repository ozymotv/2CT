# utils.py
import os
import sys
import random
import string

# List of innocent-looking window titles to randomize
WINDOW_TITLES = [
    "System Configuration", "Resource Monitor", "Performance Monitor",
    "Network Connections", "Windows Settings", "Calculator", "Notepad",
    "Calendar", "Weather", "Device Manager", "System Properties",
    "Control Panel", "Task Scheduler", "File Explorer", "Document Viewer",
    "Disk Management", "Sound Settings", "Display Settings", "User Accounts",
    "System Information"
]

def generate_random_string(length=8):
    """Generate a random alphanumeric string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_window_title():
    """Generate a random innocent window title"""
    base_title = random.choice(WINDOW_TITLES)
    
    if random.random() < 0.7:
        modifiers = ["", "Advanced ", "Windows ", "System ", "Microsoft ", ""]
        prefix = random.choice(modifiers)
        
        suffixes = ["", " Settings", " Manager", " Utility", " Tool", " Options", " Panel", " (Admin)", ""]
        suffix = random.choice(suffixes)
        return f"{prefix}{base_title}{suffix}"
    
    return base_title

def randomize_memory_footprint():
    """Create random memory data to avoid signature detection"""
    junk_size = random.randint(10, 100) * 1024  # 10-100KB of random data
    junk_data = [generate_random_string(random.randint(10, 100)) for _ in range(junk_size // 20)]
    return junk_data  # Return to prevent garbage collection
