# shared_module.py

import json
import numpy as np
import cv2
import concurrent.futures
from numba import njit, prange
import threading
import time
import mss
import queue

# thử import dxcam
try:
    import dxcam
    HAS_DXCAM = True
except ImportError:
    HAS_DXCAM = False

# ----------------------------
# Optimized ray tracing
# ----------------------------
@njit(parallel=True)
def trace_rays_optimized(mask, cx, cy, directions, max_distance):
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

@njit(parallel=True, fastmath=True)
def create_color_mask_fast(img, B0, G0, R0, tol):
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.bool_)
    for y in prange(h):
        for x in range(w):
            B, G, R = img[y, x]
            if (B0 - tol <= B <= B0 + tol) and \
               (G0 - tol <= G <= G0 + tol) and \
               (R0 - tol <= R <= R0 + tol):
                mask[y, x] = True
    return mask


# ----------------------------
# Core class
# ----------------------------
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
        self.max_frame_history = 30
        self.last_frame_time = time.time()
        
        # Pre-compute ray directions
        self._precompute_ray_directions()
        
        # Flags
        self.use_fast_mask = True
        self.use_direct_access = True
        
        # Threads & capture
        self.running = False
        self.monitor = None
        self.frame_queue = queue.Queue(maxsize=2)
        self.num_threads = self.num_threads or 4

    # ----------------------------
    # Config
    # ----------------------------
    def _load_config(self):
        try:
            with open(self.config_path) as f:
                data = json.load(f)
            self.color_tol = data.get("target_color_tolerance", 60)
            self.R, self.G, self.B = data.get("target_color", [252, 60, 250])
            self.crosshair_color = tuple(data.get("crosshair_color", [65, 255, 0]))
            self.crosshair_tol = data.get("crosshair_color_tolerance", 25)
            self.trigger_zone_size = data.get("trigger_zone_size", 50)
            self.center_zone_size = data.get("center_zone_size", 3)
            self.max_ray_distance = data.get("max_ray_distance", 50)
            self.rays_per_direction = data.get("rays_per_direction", 5)
            self.ray_angle_spread = data.get("ray_angle_spread", 30)
            self.num_threads = data.get("num_threads", 4)
        except Exception as e:
            print(f"Error loading config: {e}")
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
        angles = np.linspace(-self.ray_angle_spread, self.ray_angle_spread, self.rays_per_direction)
        self.up_dirs, self.right_dirs, self.left_dirs = [], [], []
        for ang_deg in angles:
            rad = np.radians(-90 + ang_deg)
            self.up_dirs.append((np.cos(rad), np.sin(rad)))
        for ang_deg in angles:
            rad = np.radians(ang_deg)
            self.right_dirs.append((np.cos(rad), np.sin(rad)))
        for ang_deg in angles:
            rad = np.radians(180 + ang_deg)
            self.left_dirs.append((np.cos(rad), np.sin(rad)))
        self.all_dirs = np.array(self.up_dirs + self.right_dirs + self.left_dirs, dtype=np.float32)

    def reload_config(self):
        old_zone_size = self.trigger_zone_size
        self._load_config()
        self._precompute_ray_directions()
        if self.running and old_zone_size != self.trigger_zone_size:
            self.stop_capture()
            self.start_capture()
        return True

    # ----------------------------
    # Image analysis
    # ----------------------------
    def create_color_mask(self, img, color, tol):
        B0, G0, R0 = color
        if self.use_fast_mask:
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
            return create_color_mask_fast(img, B0, G0, R0, tol)

    def analyze_image(self, img, visualize=False):
        if img is None or img.size == 0:
            return None, False, {}

        if img.shape[2] == 4:  # BGRA
            img = img[:, :, :3]

        # FPS tracking
        current_time = time.time()
        self.frame_times.append(current_time - self.last_frame_time)
        self.last_frame_time = current_time
        if len(self.frame_times) > self.max_frame_history:
            self.frame_times.pop(0)
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            with self._lock:
                self.current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2

        tgt = self.create_color_mask(img, (self.B, self.G, self.R), self.color_tol)

        # center
        y0, y1 = max(0, cy - self.center_zone_size), min(h, cy + self.center_zone_size + 1)
        x0, x1 = max(0, cx - self.center_zone_size), min(w, cx + self.center_zone_size + 1)
        center_hit = np.any(tgt[y0:y1, x0:x1])

        # crosshair
        ch_hit = False
        if 0 <= cy < h and 0 <= cx < w:
            B, G, R = img[cy, cx]
            B0, G0, R0 = self.crosshair_color
            tol = self.crosshair_tol
            ch_hit = (B0 - tol <= B <= B0 + tol and
                      G0 - tol <= G <= G0 + tol and
                      R0 - tol <= R <= R0 + tol)
        with self._lock:
            self.latest_crosshair_state = ch_hit

        # rays
        ray_results = trace_rays_optimized(tgt, cx, cy, self.all_dirs, self.max_ray_distance)
        up_hit = np.any(ray_results[:len(self.up_dirs)])
        right_hit = np.any(ray_results[len(self.up_dirs):len(self.up_dirs)+len(self.right_dirs)])
        left_hit = np.any(ray_results[len(self.up_dirs)+len(self.right_dirs):])
        fire = center_hit or (up_hit and right_hit and left_hit)
        with self._lock:
            self.latest_should_fire_state = fire

        return None, fire, {
            'up': up_hit, 'right': right_hit, 'left': left_hit,
            'center': center_hit, 'crosshair': ch_hit, 'fire': fire
        }

    # ----------------------------
    # Threads
    # ----------------------------
    def _capture_thread_func(self):
        """Capture thread: grab screen and push to queue"""
        if HAS_DXCAM:
            cam = dxcam.create()
        else:
            cam = None
            sct = mss.mss()

        while self.running:
            try:
                if HAS_DXCAM:
                    frame = cam.grab(region=(
                        self.monitor['left'], self.monitor['top'],
                        self.monitor['left'] + self.monitor['width'],
                        self.monitor['top'] + self.monitor['height']
                    ))
                else:
                    frame = np.array(sct.grab(self.monitor))

                if frame is not None:
                    try:
                        self.frame_queue.put_nowait(frame)
                    except queue.Full:
                        pass
            except Exception as e:
                print(f"Error capture: {e}")
                time.sleep(0.1)

    def _process_thread_func(self):
        """Worker thread: process frames"""
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=0.1)
                self.analyze_image(frame)
            except queue.Empty:
                continue

    def start_capture(self):
        if self.running:
            return
        with mss.mss() as sct:
            mon = sct.monitors[1]
            size = self.trigger_zone_size * 2
            cx, cy = mon['width']//2, mon['height']//2
            self.monitor = {
                'left': cx - size//2,
                'top': cy - size//2,
                'width': size,
                'height': size
            }
        self.running = True
        threading.Thread(target=self._capture_thread_func, daemon=True).start()
        for _ in range(self.num_threads):
            threading.Thread(target=self._process_thread_func, daemon=True).start()

    def stop_capture(self):
        self.running = False
        time.sleep(0.2)

    # ----------------------------
    # Getters
    # ----------------------------
    def get_crosshair_state(self):
        with self._lock:
            return self.latest_crosshair_state

    def get_should_fire_state(self):
        with self._lock:
            return self.latest_should_fire_state

    def get_fps(self):
        with self._lock:
            return self.current_fps

    def cleanup(self):
        self.stop_capture()
