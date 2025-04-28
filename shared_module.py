# shared_module.py

import json
import numpy as np
import cv2
import concurrent.futures
from numba import njit, prange
import threading
import time
import mss

# Optimized ray tracing with Numba
@njit(parallel=True)
def trace_rays_optimized(mask, cx, cy, directions, max_distance):
    """
    Trace rays in multiple directions simultaneously using Numba acceleration
    
    Parameters:
    - mask: binary mask image
    - cx, cy: center coordinates
    - directions: array of (dx, dy) direction vectors
    - max_distance: maximum ray distance
    
    Returns: Array of hit results (True/False for each direction)
    """
    h, w = mask.shape
    results = np.zeros(len(directions), dtype=np.bool_)
    
    for i in prange(len(directions)):
        dx, dy = directions[i]
        for step in range(1, max_distance + 1):
            x = int(cx + dx * step)
            y = int(cy + dy * step)
            
            if 0 <= x < w and 0 <= y < h and mask[y, x]:
                results[i] = True
                break
                
    return results

@njit
def create_color_mask_fast(img, B0, G0, R0, tol):
    """Numba-optimized color mask creation"""
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.bool_)
    
    for y in prange(h):
        for x in prange(w):
            B, G, R = img[y, x]
            if (B >= B0 - tol) and (B <= B0 + tol) and \
               (G >= G0 - tol) and (G <= G0 + tol) and \
               (R >= R0 - tol) and (R <= R0 + tol):
                mask[y, x] = True
    
    return mask

class TriggerBotCore:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self._load_config()
        
        # Thread safety
        self._lock = threading.Lock()
        self.latest_crosshair_state = False
        self.latest_should_fire_state = False
        self.current_fps = 0.0
        
        # FPS tracking
        self.frame_times = []
        self.max_frame_history = 30  # Number of frames to track for FPS calculation
        self.last_frame_time = time.time()
        
        # Pre-compute ray directions for faster processing
        self._precompute_ray_directions()
        
        # Performance optimization flags
        self.use_fast_mask = True  # Use vectorized mask creation
        self.use_direct_access = True  # Use direct pixel access where possible
        
        # Screen capture
        self.sct = None
        self.capture_thread = None
        self.running = False
        self.monitor = None  # Will be set during start_capture based on trigger_zone_size

    def _load_config(self):
        try:
            with open(self.config_path) as f:
                data = json.load(f)
            # Vision parameters
            self.color_tol = data.get("target_color_tolerance", 60)
            self.R, self.G, self.B = data.get("target_color", [252, 60, 250])
            self.crosshair_color = tuple(data.get("crosshair_color", [65, 255, 0]))
            self.crosshair_tol = data.get("crosshair_color_tolerance", 25)
            # Ray-trace parameters
            self.trigger_zone_size = data.get("trigger_zone_size", 50)
            self.center_zone_size = data.get("center_zone_size", 3)
            self.max_ray_distance = data.get("max_ray_distance", 50)
            self.rays_per_direction = data.get("rays_per_direction", 5)
            self.ray_angle_spread = data.get("ray_angle_spread", 30)
            # Thread settings
            self.num_threads = data.get("num_threads", 4)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Default values matching config.json values
            self.color_tol = 60
            self.R, self.G, self.B = 252, 60, 250
            self.crosshair_color = (65, 255, 0)
            self.crosshair_tol = 25
            self.trigger_zone_size = 50
            self.center_zone_size = 3
            self.max_ray_distance = 50
            self.rays_per_direction = 5
            self.ray_angle_spread = 30
            self.num_threads = 4

    def _precompute_ray_directions(self):
        """Pre-compute ray direction vectors for faster processing"""
        angles = np.linspace(-self.ray_angle_spread, self.ray_angle_spread, self.rays_per_direction)
        
        # Up directions
        self.up_dirs = []
        for ang_deg in angles:
            rad = np.radians(-90 + ang_deg)
            self.up_dirs.append((np.cos(rad), np.sin(rad)))
            
        # Right directions
        self.right_dirs = []
        for ang_deg in angles:
            rad = np.radians(ang_deg)
            self.right_dirs.append((np.cos(rad), np.sin(rad)))
            
        # Left directions
        self.left_dirs = []
        for ang_deg in angles:
            rad = np.radians(180 + ang_deg)
            self.left_dirs.append((np.cos(rad), np.sin(rad)))
        
        # Combined directions array for numba
        self.all_dirs = np.array(self.up_dirs + self.right_dirs + self.left_dirs, dtype=np.float32)

    def reload_config(self):
        """Reload configuration from file"""
        old_zone_size = self.trigger_zone_size
        self._load_config()
            
        # Recompute ray directions
        self._precompute_ray_directions()
        
        # Update capture zone if running
        if self.running and old_zone_size != self.trigger_zone_size:
            self.stop_capture()
            self.start_capture()
            
        return True

    def create_color_mask(self, img, color, tol):
        """Create a binary mask for pixels matching the target color within tolerance"""
        B0, G0, R0 = color
        
        if self.use_fast_mask:
            # Use vectorized operations for better performance on most systems
            mask = (
                (img[:, :, 0] >= B0 - tol) & 
                (img[:, :, 0] <= B0 + tol) & 
                (img[:, :, 1] >= G0 - tol) & 
                (img[:, :, 1] <= G0 + tol) & 
                (img[:, :, 2] >= R0 - tol) & 
                (img[:, :, 2] <= R0 + tol)
            )
            return mask
        else:
            # Fallback to Numba version for systems where it's faster
            return create_color_mask_fast(img, B0, G0, R0, tol)

    def analyze_image(self, img, visualize=False):
        """
        Match the debug_viewer.py approach: analyze the image directly
        Returns: (visualized_image or None, should_fire: bool, details: dict)
        """
        if img is None or img.size == 0:
            return None, False, {'up': False, 'right': False, 'left': False, 'center': False, 'crosshair': False, 'fire': False}

        # Convert image if needed - same as debug_viewer expects
        if img.shape[2] == 4:  # BGRA
            img = img[:, :, :3]  # Keep only BGR

        # Update FPS tracking
        current_time = time.time()
        self.frame_times.append(current_time - self.last_frame_time)
        self.last_frame_time = current_time
        
        # Keep only the last N frames for FPS calculation
        if len(self.frame_times) > self.max_frame_history:
            self.frame_times.pop(0)
        
        # Calculate current FPS
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            with self._lock:
                self.current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

        # Get image dimensions and center point
        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2
        
        # Create target mask using the faster method
        tgt = self.create_color_mask(img, (self.B, self.G, self.R), self.color_tol)
        
        # Check center hit with direct slicing for speed
        y_start = max(0, cy - self.center_zone_size)
        y_end = min(h, cy + self.center_zone_size + 1)
        x_start = max(0, cx - self.center_zone_size)
        x_end = min(w, cx + self.center_zone_size + 1)
        
        center_hit = np.any(tgt[y_start:y_end, x_start:x_end])

        # Check crosshair hit efficiently with direct access
        ch_hit = False
        if 0 <= cy < h and 0 <= cx < w:
            pixel = img[cy, cx]
            B0, G0, R0 = self.crosshair_color
            tol = self.crosshair_tol
            
            ch_hit = (
                (pixel[0] >= B0 - tol) and (pixel[0] <= B0 + tol) and
                (pixel[1] >= G0 - tol) and (pixel[1] <= G0 + tol) and
                (pixel[2] >= R0 - tol) and (pixel[2] <= R0 + tol)
            )
            
        # Update thread-safe state variables
        with self._lock:
            self.latest_crosshair_state = ch_hit

        # Perform optimized ray tracing - parallel computation
        ray_results = trace_rays_optimized(tgt, cx, cy, self.all_dirs, self.max_ray_distance)
        
        # Separate results for different directions
        up_rays = ray_results[:len(self.up_dirs)]
        right_rays = ray_results[len(self.up_dirs):len(self.up_dirs) + len(self.right_dirs)]
        left_rays = ray_results[len(self.up_dirs) + len(self.right_dirs):]

        # Compile results
        up_hit = np.any(up_rays)
        right_hit = np.any(right_rays)
        left_hit = np.any(left_rays)
        
        # Determine whether to fire - same logic as debug_viewer expects
        fire = center_hit or (up_hit and right_hit and left_hit)
        
        # Update thread-safe fire state
        with self._lock:
            self.latest_should_fire_state = fire
        
        # Prepare results dict expected by debug_viewer
        results = {
            'up': up_hit,
            'right': right_hit,
            'left': left_hit,
            'center': center_hit,
            'crosshair': ch_hit,
            'fire': fire
        }

        # Create visualization if requested (needed by debug_viewer)
        if visualize:
            vis_img = img.copy()
            
            # Draw crosshair
            cv2.line(vis_img, (cx-10, cy), (cx+10, cy), (255,255,255), 1)
            cv2.line(vis_img, (cx, cy-10), (cx, cy+10), (255,255,255), 1)
            
            # Draw center zone
            cv2.rectangle(
                vis_img,
                (cx - self.center_zone_size, cy - self.center_zone_size),
                (cx + self.center_zone_size, cy + self.center_zone_size),
                (0,255,0) if center_hit else (0,0,255), 1
            )
            
            # Draw rays
            all_directions = self.up_dirs + self.right_dirs + self.left_dirs
            for i, (dx, dy) in enumerate(all_directions):
                hit = ray_results[i]
                x2 = int(cx + dx * self.max_ray_distance)
                y2 = int(cy + dy * self.max_ray_distance)
                col = (0,255,0) if hit else (128,128,128)
                cv2.line(vis_img, (cx, cy), (x2, y2), col, 1)
                
            # Draw target mask for debugging
            mask_vis = vis_img.copy()
            mask_vis[tgt] = (255, 0, 255)  # Highlight detected pixels
            cv2.addWeighted(vis_img, 0.7, mask_vis, 0.3, 0, vis_img)
                
            return vis_img, fire, results

        return None, fire, results

    def _capture_thread_func(self):
        """Thread function to continuously capture screen"""
        self.sct = mss.mss()
        
        while self.running:
            try:
                # Capture screen
                screenshot = self.sct.grab(self.monitor)
                
                # Convert to numpy array
                img = np.array(screenshot)
                
                # Process the image
                self.analyze_image(img)
                
                # Short sleep to avoid hogging CPU
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Error capturing screen: {e}")
                time.sleep(0.1)  # Sleep longer on error

    def start_capture(self):
        """Start screen capture thread"""
        if self.running:
            return  # Already running
            
        # Define capture region based on trigger_zone_size (identical to debug_viewer.py)
        with mss.mss() as sct:
            mon = sct.monitors[1]  # Primary monitor
            size = self.trigger_zone_size * 2
            cx, cy = mon['width'] // 2, mon['height'] // 2
            self.monitor = {
                'left': cx - size // 2,
                'top': cy - size // 2,
                'width': size,
                'height': size
            }
    
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_thread_func, daemon=True)
        self.capture_thread.start()
        
    def stop_capture(self):
        """Stop screen capture thread"""
        self.running = False
        if self.capture_thread:
            if self.capture_thread.is_alive():
                self.capture_thread.join(timeout=1.0)  # Wait for thread to finish
            self.capture_thread = None
        
    def get_crosshair_state(self):
        """Thread-safe getter for crosshair state"""
        with self._lock:
            return self.latest_crosshair_state

    def get_should_fire_state(self):
        """Thread-safe getter for fire state"""
        with self._lock:
            return self.latest_should_fire_state
            
    def get_fps(self):
        """Thread-safe getter for current FPS"""
        with self._lock:
            return self.current_fps
            
    def cleanup(self):
        """Clean up resources"""
        self.stop_capture()
        if self.sct:
            self.sct.close()
            self.sct = None