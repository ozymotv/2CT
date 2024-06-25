import json
import time
import threading
import numpy as np
import kmNet
from ctypes import WinDLL
import sys
import keyboard
import dxcam
import pyopencl as cl
import multiprocessing as mp

class TriggerBot:
    def __init__(self):
        self.exit_prog = mp.Value('b', False)
        self.is_scoped = mp.Value('b', False)
        self.target_detected = mp.Value('b', False)
        self.paused = mp.Value('b', False)

        self.load_config()
        self.init_kmnet()
        self.init_grab_zone()

    def load_config(self):
        try:
            with open('config.json') as json_file:
                data = json.load(json_file)

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
        except KeyError as e:
            print(f"Missing key in config.json: {e}")
            self.exit()

    def init_kmnet(self):
        kmNet.init(self.ip, self.port, self.uid)
        kmNet.monitor(10000)

    def init_grab_zone(self):
        user32 = WinDLL("user32", use_last_error=True)
        shcore = WinDLL("shcore", use_last_error=True)

        shcore.SetProcessDpiAwareness(2)
        width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        self.ZONE = 3
        self.GRAB_ZONE = {
            "left": int(width / 2 - self.ZONE),
            "top": int(height / 2 - self.ZONE),
            "width": 2 * self.ZONE,
            "height": 2 * self.ZONE,
        }

    def search_and_scope(self, exit_prog, is_scoped, target_detected, paused):
        import pyopencl as cl  # Import inside the function to avoid pickling issues
        
        # Initialize OpenCL context here
        ctx = cl.create_some_context()
        queue = cl.CommandQueue(ctx)
        with open('check_colors.cl', 'r') as f:
            program = cl.Program(ctx, f.read()).build()
        mf = cl.mem_flags
        img_buf = None
        results_buf = None
        
        camera = dxcam.create(region=(self.GRAB_ZONE['left'], self.GRAB_ZONE['top'], self.GRAB_ZONE['width'], self.GRAB_ZONE['height']))
        while not exit_prog.value:
            if paused.value:
                time.sleep(0.01)
                continue

            img = camera.grab()
            img = np.array(img, dtype=np.uint8)

            if kmNet.isdown_side2() == 1:
                scope_color = (self.scope_R_alt, self.scope_G_alt, self.scope_B_alt)
                scope_tol = self.scope_tol_alt
            else:
                scope_color = (self.scope_R, self.scope_G, self.scope_B)
                scope_tol = self.scope_tol

            if img_buf is None or results_buf is None:
                img_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img)
                results_buf = cl.Buffer(ctx, mf.WRITE_ONLY, img.shape[0] * img.shape[1])
            else:
                cl.enqueue_copy(queue, img_buf, img)

            program.check_colors(
                queue, img.shape[:2], None,
                img_buf, np.int32(img.shape[1]), np.int32(img.shape[0]),
                np.int32(self.R), np.int32(self.G), np.int32(self.B), np.int32(self.color_tol),
                np.int32(scope_color[0]), np.int32(scope_color[1]), np.int32(scope_color[2]), np.int32(scope_tol),
                results_buf
            )

            results = np.empty(img.shape[:2], dtype=np.uint8)
            cl.enqueue_copy(queue, results, results_buf).wait()

            target_detected.value = np.any(results & 0b10)
            is_scoped.value = np.any(results & 0b01)
            time.sleep(0.001)

    def trigger(self, exit_prog, is_scoped, target_detected, paused):
        while not exit_prog.value:
            if is_scoped.value and target_detected.value and not paused.value:
                delay_percentage = self.trigger_delay / 100.0
                actual_delay = self.base_delay + self.base_delay * delay_percentage
                time.sleep(actual_delay)
                kmNet.enc_left(1)
                time.sleep(np.random.uniform(0.080, 0.12))
                kmNet.enc_left(0)
                time.sleep(np.random.uniform(0.05, 0.09))
            else:
                time.sleep(0.001)

    def start_processes(self):
        processes = [
            mp.Process(target=self.search_and_scope, args=(self.exit_prog, self.is_scoped, self.target_detected, self.paused)),
            mp.Process(target=self.trigger, args=(self.exit_prog, self.is_scoped, self.target_detected, self.paused)),
            threading.Thread(target=self.keyboard_listener, daemon=True)
        ]
        for p in processes:
            p.start()

    def keyboard_listener(self):
        while not self.exit_prog.value:
            if keyboard.is_pressed('F2'):
                print("Exiting program...")
                self.exit_prog.value = True
                self.exit()
            elif keyboard.is_pressed('F3'):
                self.paused.value = not self.paused.value
                state = "paused" if self.paused.value else "continued"
                print(f"Program {state}...")
                time.sleep(0.1)
            elif keyboard.is_pressed('F4'):
                print("Reload config: Done")
                self.load_config()
                time.sleep(0.1)
            time.sleep(0.1)

    def exit(self):
        sys.exit()

if __name__ == "__main__":
    print("            2-condition-triggerbot created by Ozymo. Version: 1.4")
    print("-" * 50)
    print("Press F2 to exit the program")
    print("Press F3 to pause/continue the program")
    print("Press F4 to reload config")
    print("For any questions, join my discord: https://discord.gg/C3MY4kuAcD")
    print("-" * 50)

    bot = TriggerBot()
    bot.start_processes()

    while not bot.exit_prog.value:
        time.sleep(0.001)
