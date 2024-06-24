import json
import time
import threading
import numpy as np
from mss import mss as mss_module
import kmNet
from ctypes import WinDLL
import sys
import keyboard

class TriggerBot:
    def __init__(self):
        self.exit_prog = False
        self.is_scoped = False
        self.target_detected = False
        self.paused = False

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

    def search_and_scope(self):
        sct = mss_module()
        while not self.exit_prog:
            if self.paused:
                time.sleep(0.01)
                continue

            img = np.array(sct.grab(self.GRAB_ZONE))
            
            if kmNet.isdown_side2() == 1:
                scope_color = (self.scope_R_alt, self.scope_G_alt, self.scope_B_alt)
                scope_tol = self.scope_tol_alt
            else:
                scope_color = (self.scope_R, self.scope_G, self.scope_B)
                scope_tol = self.scope_tol

            target_mask = (
                (img[:, :, 0] > self.R - self.color_tol) & (img[:, :, 0] < self.R + self.color_tol) &
                (img[:, :, 1] > self.G - self.color_tol) & (img[:, :, 1] < self.G + self.color_tol) &
                (img[:, :, 2] > self.B - self.color_tol) & (img[:, :, 2] < self.B + self.color_tol)
            )

            scope_mask = (
                (img[:, :, 0] > scope_color[0] - scope_tol) & (img[:, :, 0] < scope_color[0] + scope_tol) &
                (img[:, :, 1] > scope_color[1] - scope_tol) & (img[:, :, 1] < scope_color[1] + scope_tol) &
                (img[:, :, 2] > scope_color[2] - scope_tol) & (img[:, :, 2] < scope_color[2] + scope_tol)
            )

            self.target_detected = np.any(target_mask)
            self.is_scoped = np.any(scope_mask)
            time.sleep(0.001)

    def trigger(self):
        while not self.exit_prog:
            if self.is_scoped and self.target_detected and not self.paused:
                delay_percentage = self.trigger_delay / 100.0
                actual_delay = self.base_delay + self.base_delay * delay_percentage
                time.sleep(actual_delay)
                kmNet.enc_keydown(14)
                time.sleep(np.random.uniform(0.080, 0.12))
                kmNet.enc_keyup(14)
                time.sleep(np.random.uniform(0.05, 0.09))
            else:
                time.sleep(0.001)

    def start_threads(self):
        threading.Thread(target=self.search_and_scope).start()
        threading.Thread(target=self.trigger).start()
        threading.Thread(target=self.keyboard_listener).start()

    def keyboard_listener(self):
        while not self.exit_prog:
            if keyboard.is_pressed('F2'):
                print("Exiting program...")
                self.exit_prog = True
                self.exit()
            elif keyboard.is_pressed('F3'):
                self.paused = not self.paused
                state = "paused" if self.paused else "continued"
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
    bot.start_threads()

    while not bot.exit_prog:
        time.sleep(0.001)
