<div align="center">
 <img src="https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/86aed2d0-5393-42c1-b9a4-d0d29974a099" /><br> <h1>2-condition-triggerbot</h1>
 <img src="https://img.shields.io/badge/Live%20Status-UNDETECTED-green" />

A Color triggerbot that support native windows sending key method or with Kmbox NET (optinal)

</div>

# Check out Kmbox net AI aimbot  [Here](https://github.com/ozymotv/2CA)

## About
2CT is a highly optimized, color-detection based automatic trigger system for gaming with customizable settings and a user-friendly interface. Work for any game that support **secondary or alternate fire bind**

<div align="center">
 <img src="https://github.com/ozymotv/2CT/blob/main/docs/vi/pics/key.png?raw=true" />
 <img src="https://github.com/ozymotv/2CT/blob/main/docs/vi/pics/kmnet.png?raw=true" />
 
 </div>
 
### Key Features:

+ Color Detection: Automatically detects target colors in the center of your screen
  
+ Customizable Settings: Adjust sensitivity, delay, trigger keys, and more
  
+ Visual Debug Mode: Visualize detected targets with the debug viewer

+ Performance Optimized: High FPS with minimal system impact

+ Multiple Trigger Methods: Support for keyboard and mouse inputs

### How It Works:

+ Screen Capture and Processing: The application captures a small region in the center of your screen. From the center of the screen, rays are projected in multiple directions. Three primary directions are analyzed: up, left, and right. When rays intersect with target pixels, that direction is considered "hit"

+ Trigger Mechanism: When both conditions (target detected and scoped-in) are met, the bot simulates a mouse click to shoot, with a customizable delay to mimic human reaction times.

+ Keyboard Listener: Runs in a separate thread to allow the user to pause, reload the configuration, or exit the program using predefined hotkeys.


### Important Note:

This tool is intended for educational purposes only to showcase how screen capture and color detection can be implemented in a programming project. Using such tools in online games like Valorant is against the terms of service and can result in penalties, including permanent bans. Use this bot at your own risk, and always consider the ethical implications and potential consequences of using cheats in online games.

## Getting Started
    
### Installation

Clone the repository from GitHub:
 Download and extract the source into your dicrectory

Or if you have git installed, use this command

```
git clone https://github.com/ozymotv/2CT.git
```

### Quick Install
Step 1: Open CMD in the project location and run this code to install dependencies

```
pip install -r requirements.txt
```

Step 2: Download Visual Studio 2022 Community Edition then install -> Desktop development with c++ [Download Visual studio](https://visualstudio.microsoft.com/vs/community/)

Step 3: Running the Application
```
python triggerbot.py
```
For debugging or visualizing the detection:
```
python debug_viewer.py
```

### Configuration

The application can be configured through the UI or by editing the config.json file directly.

UI Configuration
  + Trigger Method: Select keyboard or network-based triggering
  + Trigger Key: The key that will be activated when a target is detected
  + Require Crosshair: Enable to only trigger when the crosshair color is also detected
  + Timing Settings: Configure press duration and delay between triggers
  + Mode: Choose between Always On, Toggle (with hotkey), or Hold (active while hotkey is pressed)
  + Hotkey: Set the toggle/hold activation key
Click "Save Config" to save your settings

Manual Configuration (config.json)

```
{
   "method": "kmnet",                   // Master switch method: key or kmnet

   "trigger_key": "k",                  // key bind to secondary fire in game
   "ip": "192.168.2.188",               //ip of kmbox net if you use it
   "port": 16896,                       //port
   "uuid": "46405c53",                  // uuid
  
  "target_color": [252, 60, 250],       // Target RGB color to detect [B,G,R]
  "target_color_tolerance": 60,         // Color detection tolerance
  "crosshair_color": [65, 255, 0],      // Crosshair color [B,G,R]  
  "crosshair_color_tolerance": 25,      // Crosshair detection tolerance
  "trigger_zone_size": 50,              // Detection zone size in pixels
  "center_zone_size": 3,                // Center detection zone size
  "max_ray_distance": 50,               // Maximum ray tracing distance
  "rays_per_direction": 5,              // Number of rays per direction
  "ray_angle_spread": 30,               // Angle spread of rays in degrees
  "method": "key",                      // Trigger method: "key" or "kmnet"
  "trigger_key": "Space",               // Key to activate when target detected
  "require_crosshair": 0,               // 1 to require crosshair detection, 0 to ignore
  "press_release_min_ms": 80,           // Minimum key press duration in ms
  "press_release_max_ms": 100,          // Maximum key press duration in ms
  "delay_after_shoot_min_ms": 200,      // Minimum delay after trigger in ms
  "delay_after_shoot_max_ms": 200,      // Maximum delay after trigger in ms
  "mode": "always",                     // Mode: "always", "toggle", or "hold"
  "hotkey": "T",                        // Hotkey for toggle/hold modes
  "num_threads": 4                      // number of threads is used for image processing
}
```


### Detection Algorithm

+ Color Detection: Identifies pixels matching the target color
+ Ray Tracing: Shoots rays in multiple directions to find connected areas
+ Decision Logic: Triggers when the right pattern of detection is found
+ Crosshair Verification (optional): Confirms crosshair color is present

### Troubleshooting

- **"No module named 'kmNet'"**: Ensure kmNet_xxx.pyd is in the same directory as your script
- **"DLL Failed to load"**: Install Desktop development with c++
- **Screen capture issues**: Run as administrator on Windows
- **Low FPS**: Try reducing the trigger zone size or rays per direction
- **False Positives**: Adjust color tolerance or require crosshair detection
- **No Detection**: Check your target color settings and increase tolerance
- **Application Not Responding**: Ensure you have all required dependencies installed
- **KmBox connection errors**: Verify IP address and port in config.json


## Contribution

Feel free to submit any improvement, I will credit you.


## Authors

   Ozymo

<h3 align="left">Contact:</h3>
<p align="left">
<a href="https://twitter.com/ozymotv" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/twitter.svg" alt="ozymotv" height="30" width="40" /></a>
<a href="https://linkedin.com/in/ozymo" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/linked-in-alt.svg" alt="ozymo" height="30" width="40" /></a>
<a href="https://fb.com/ozymotv" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/facebook.svg" alt="ozymotv" height="30" width="40" /></a>
<a href="https://www.youtube.com/c/ozymotv" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/youtube.svg" alt="ozymotv" height="30" width="40" /></a>

</p>


<h3 align="left">Support this project:</h3>

USDT - TRX (TRON TRC-20): TChDBfpKwHPX7CLnqvtQGG7jr9jvaB5KWq

BTC - BTC network: 1MnnTJBfdYEpeLgCFYf4NiMLg1UGRvijsz

<p><a href="https://www.buymeacoffee.com/ozymotvz"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" width="210" alt="ozymotvz" /></a><a href="https://ko-fi.com/ozymotv"> <img align="left" src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" height="50" width="210" alt="ozymotv" /></a></p><br><br>




## License

This project is licensed under the MIT License - see the LICENSE file for details.
