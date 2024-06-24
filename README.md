<div align="center">
 <img src="https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/86aed2d0-5393-42c1-b9a4-d0d29974a099" /><br> <h1>2-condition-triggerbot</h1>
<img src="https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange" />
 
Hardware trigger-bot base on Kmbox 

[**English**](.README.md)  |  [**Tiếng Việt**](./docs/vi/README.vi.md)   |   [**中国人**](.README.md)    |    [**한국인**](.README.md)   |    [**日本語**](.README.md)  

</div>

## About
The "2-condition-triggerbot" project, powered by Kmbox, is an application designed to explore and study hardware cheating methods within the game V. It utilizes computer vision techniques to detect and respond to specific in-game visual cues, enabling research into gaming automation and enhancement techniques.
<div align="center">
 <img src="https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/c9e8ced2-3ab3-4c19-bfed-6f864f5aa7a7" />
 </div>
 
## Getting Started

### Prerequisites
* KmBox library (available as KmNet.pyd in the source)
* Python 3.11
* Kmbox Net version

### Installation

Clone the repository from GitHub:

```
git clone https://github.com/OzymoGit/2-condition-triggerbot.git
```
Install required Python packages:

```
pip install -r requirements.txt
```
### Running the Program
1. Navigate to the project directory:

```
cd 2-condition-triggerbot
```
2. Edit the config.json file:
```
{
  "ip": "192.168.2.188",  // Replace with Kmbox IP
  "port": "16896",        // Replace with Kmbox port
  "uid": "46405C53",      // Replace with Kmbox UID
  "trigger_delay": 0,     // Delay between shots (not implemented yet)
  "base_delay": 0,        // Base delay from pixel detection to left mouse click, set to 0 for faster response
  "color_tolerance": 40,  // Main color tolerance, increase if the bot does not detect color
  "target_color": [250, 100, 250],  // Enemy outline color, default is Purple
  "scope_color": [0, 255, 0],       // Primary crosshair color, default is Green
  "scope_color_tolerance": 40,      // Color tolerance for primary crosshair
  "scope_color_alt": [0, 255, 255], // Secondary crosshair color, used when holding second mouse button instead of primary
  "scope_color_tolerance_alt": 40   // Color tolerance for secondary crosshair
}
```
3. Adjust crosshair colors:
+ Primary crosshair: Cyan
+ Aimdownsight and Sniper: Green
  
![Screenshot (2)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/da8a76a0-7409-4225-9271-9c3af41d7581)
![Screenshot (3)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/7d8393ca-1b16-4159-bc15-71d1c4f362f7)
![Screenshot (1)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/fe5a5bcb-74fd-41d7-9336-4de2a3bb6f64)

Turn on "Movement error", "Firing error", multiplier to 3 times

4.Run the program:
```
python run.py
```
5. Keyboard Shortcuts:
+ F2: Exit
+ F3: Pause/unpause
+ F4: Reload config

Xmousebutton2 for alternate trigger mode

![Screenshot 2024-06-24 222638](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/c1873efc-af2f-4204-8d46-3a43210763ce)


## Help

Need assistance? Join the Discord server <a href="https://discord.gg/C3MY4kuAcD" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/discord.svg" alt="C3MY4kuAcD" height="30" width="40" /></a>


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
<p><a href="https://www.buymeacoffee.com/ozymotvz"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" width="210" alt="ozymotvz" /></a><a href="https://ko-fi.com/ozymotv"> <img align="left" src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" height="50" width="210" alt="ozymotv" /></a></p><br><br>




## License

This project is licensed under the GPL 3.0 License - see the LICENSE file for details


