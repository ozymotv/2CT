#!/usr/bin/env python3
# debug_viewer_dual.py

import cv2
import numpy as np
import time
import keyboard
import mss
from shared_module import TriggerBotCore

def main():
    print("Starting Dual Window Debug Viewer")
    print("Press 'ESC' to exit")
    
    # Initialize the TriggerBotCore
    core = TriggerBotCore()
    size = core.trigger_zone_size * 2  # Full capture area size
    
    # Create stats window with fixed size
    stats_height = 350
    stats_width = 400
    stats_window = np.zeros((stats_height, stats_width, 3), dtype=np.uint8)
    
    # FPS calculation variables
    fps_values = []
    max_fps_history = 30
    
    # Initialize mss for screen capture
    with mss.mss() as sct:
        # Get the primary monitor
        mon = sct.monitors[1]  # Primary monitor
        
        # Calculate center point of the screen
        cx, cy = mon['width'] // 2, mon['height'] // 2
        
        # Define capture region (same as in TriggerBotCore)
        monitor = {
            'left': cx - size // 2,
            'top': cy - size // 2,
            'width': size,
            'height': size
        }
        
        # Main loop
        while not keyboard.is_pressed('esc'):
            # Capture screen
            start_time = time.time()
            screenshot = sct.grab(monitor)
            
            # Convert to numpy array
            img = np.array(screenshot)
            
            # Process the image with visualization enabled
            vis_img, should_fire, results = core.analyze_image(img, visualize=True)
            
            # Add capture area boundary to visualization
            cv2.rectangle(vis_img, (0, 0), (size-1, size-1), (255, 255, 255), 1)
            
            # Draw highlighted border if should fire
            if should_fire:
                cv2.rectangle(vis_img, (0, 0), (size-1, size-1), (0, 255, 0), 3)
            
            # Calculate FPS
            frame_time = time.time() - start_time
            current_fps = 1.0 / frame_time if frame_time > 0 else 0
            fps_values.append(current_fps)
            if len(fps_values) > max_fps_history:
                fps_values.pop(0)
            avg_fps = sum(fps_values) / len(fps_values) if fps_values else 0
            
            # Create stats display
            stats_window.fill(0)  # Clear previous frame
            
            # Status information
            info_text = [
                f"FPS: {avg_fps:.1f}",
                f"Frame Time: {frame_time * 1000:.1f} ms",
                "",
                "--- Detection Results ---",
                f"Up Detection: {'YES' if results['up'] else 'NO'}",
                f"Right Detection: {'YES' if results['right'] else 'NO'}",
                f"Left Detection: {'YES' if results['left'] else 'NO'}",
                f"Center Detection: {'YES' if results['center'] else 'NO'}",
                f"Crosshair Match: {'YES' if results['crosshair'] else 'NO'}",
                f"Should Fire: {'YES' if should_fire else 'NO'}",
                "",
                "--- Configuration ---",
                f"Trigger Zone Size: {core.trigger_zone_size}px",
                f"Center Zone Size: {core.center_zone_size}px",
                f"Ray Distance: {core.max_ray_distance}px",
                f"Rays Per Direction: {core.rays_per_direction}",
                f"Ray Angle Spread: {core.ray_angle_spread}°",
                "",
                "--- Color Settings ---",
                f"Target RGB: ({core.R},{core.G},{core.B})",
                f"Color Tolerance: {core.color_tol}",
                f"Crosshair RGB: {core.crosshair_color}",
                f"Crosshair Tolerance: {core.crosshair_tol}"
            ]
            
            # Draw status text on stats window
            y = 30
            for text in info_text:
                cv2.putText(stats_window, text, (20, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                           (255, 255, 255) if not text.startswith("---") else (0, 255, 255), 
                           1 if not text.startswith("---") else 2)
                y += 25 if not text == "" else 15
            
            # Add screen location info
            monitor_info = f"Monitoring: {monitor['left']},{monitor['top']} to {monitor['left']+monitor['width']},{monitor['top']+monitor['height']}"
            cv2.putText(stats_window, monitor_info, (20, stats_height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
                
            # Show both windows
            cv2.imshow('TriggerBot Visualization', vis_img)
            cv2.imshow('TriggerBot Stats', stats_window)
            
            # Break if ESC key is pressed or window is closed
            if cv2.waitKey(1) == 27:  # ESC key
                break
    
    # Clean up
    cv2.destroyAllWindows()
    print("Debug Viewer closed")

if __name__ == "__main__":
    main()