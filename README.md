<div align="center">
 <img src="https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/86aed2d0-5393-42c1-b9a4-d0d29974a099" /><br> <h1>2-condition-triggerbot</h1>
 <img src="https://img.shields.io/badge/Live%20Status-UNDETECTED-green" />

A hardware aimbot for Valorant using Kmbox

[**English**](.README.md)  |  [**Tiếng Việt**](./docs/vi/README.vi.md)   |   [**中国人**](.README.md)    |    [**한국인**](.README.md)   |    [**日本語**](.README.md)  

</div>

# Check out Kmbox net AI aimbot  [Here](https://github.com/ozymotv/2CA)

## About
The "2-condition-triggerbot" project is an educational tool designed to demonstrate the principles of screen capture and image processing in a gaming context. This bot is specifically tailored for the popular FPS game, Valorant. It automates the process of detecting targets and shooting by using color recognition techniques.

<div align="center">
 <img src="https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/c9e8ced2-3ab3-4c19-bfed-6f864f5aa7a7" />
 
 </div>
 
### Key Features:

+ Configurable Settings: Easily customize the bot's behavior through the config.json file, including network settings, color tolerance, and delay parameters.
  
+ Real-time Screen Capture: Utilizes mss for efficient screen capture of a small zone around the crosshair to minimize performance impact.

+ Color Detection: Detects the presence of specific target and scope colors within the capture zone to determine when to shoot.

+ Adjustable Trigger Delay: Fine-tune the bot's shooting speed with adjustable delay settings to match different game requirements.

+ Keyboard Controls: Control the bot with simple hotkeys:

### How It Works:

+ Initialization: The bot initializes by loading the configuration, setting up network communication with kmBox, and defining the screen capture zone.

+ Screen Capture and Processing: Continuously captures a small portion of the screen around the crosshair, checking for specific colors that indicate a target or scoped-in state.

+ Trigger Mechanism: When both conditions (target detected and scoped-in) are met, the bot simulates a mouse click to shoot, with a customizable delay to mimic human reaction times.

+ Keyboard Listener: Runs in a separate thread to allow the user to pause, reload the configuration, or exit the program using predefined hotkeys.


### Important Note:

This tool is intended for educational purposes only to showcase how screen capture and color detection can be implemented in a programming project. Using such tools in online games like Valorant is against the terms of service and can result in penalties, including permanent bans. Use this bot at your own risk, and always consider the ethical implications and potential consequences of using cheats in online games.

## Getting Started

### Prerequisites
* KmBox library (available as KmNet.pyd in the source)
* Python 3.11
* Kmbox Net hardware

```
http://www.kmbox.top/wiki_doc/kmboxNet/site/#_1
```
The firmware for kmbox must be at least from May 18th 2024 or above!!!
* 2 PCs setup (optional) 
  - You can use Capture card or Moonlight streaming
    
### Installation

Clone the repository from GitHub:
 Download and extract the source into your dicrectory

Or if you have git installed, use this command

```
git clone https://github.com/ozymotv/2CT.git
```

### Quick Install
Step 1: Open CMD and paste this in

```
pip install numpy mss keyboard
```

Step 2: Download Visual Studio 2022 Community Edition then install -> Desktop development with c++ [Download Visual studio](https://visualstudio.microsoft.com/vs/community/)

Step 3: Edit the config.json file:

```
{
  "ip": "192.168.2.188", 
  "port": "16896",  
  "uid": "46405C53",  
  "trigger_delay": 0,  
  "base_delay": 0,  
  "color_tolerance": 40, 
  "target_color": [250, 100, 250], 
  "scope_color": [0, 255, 0],
  "scope_color_tolerance": 40, 
  "scope_color_alt": [0, 255, 255], 
  "scope_color_tolerance_alt": 40 
}
```
Step 4: run the run.py (or open cmd and type py run.py)


3. Adjust crosshair colors:

+ Primary crosshair: Cyan
+ Aimdownsight and Sniper: Green


![Screenshot (1)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/fe5a5bcb-74fd-41d7-9336-4de2a3bb6f64)
![Screenshot (2)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/da8a76a0-7409-4225-9271-9c3af41d7581)
![Screenshot (3)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/7d8393ca-1b16-4159-bc15-71d1c4f362f7)


Turn on "Movement error", "Firing error", multiplier to 3 times

4. Keyboard Shortcuts:
   
+ F2: Exit
+ F3: Pause/unpause
+ F4: Reload config

Xmousebutton2 for alternate trigger mode

![Screenshot 2024-06-24 222638](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/c1873efc-af2f-4204-8d46-3a43210763ce)

### Troubleshooting

- **"No module named 'kmNet'"**: Ensure kmNet_xxx.pyd is in the same directory as your script
- **"DLL Failed to load"**: Install Desktop development with c++
- **Screen capture issues**: Run as administrator on Windows
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


<h3 align="left">Support:</h3>

USDT - TRX (TRON TRC-20): TChDBfpKwHPX7CLnqvtQGG7jr9jvaB5KWq

BTC - BTC network: 1MnnTJBfdYEpeLgCFYf4NiMLg1UGRvijsz

<p><a href="https://www.buymeacoffee.com/ozymotvz"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" width="210" alt="ozymotvz" /></a><a href="https://ko-fi.com/ozymotv"> <img align="left" src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" height="50" width="210" alt="ozymotv" /></a></p><br><br>




## License

This project is licensed under the GPL 3.0 License - see the LICENSE file for details
