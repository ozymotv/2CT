![logo](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/86aed2d0-5393-42c1-b9a4-d0d29974a099)
# 2-condition-triggerbot

## Mô tả
Dự án "2-condition-triggerbot" là một ứng dụng với sự hỗ trợ của Kmbox, được thiết kế để nghiên cứu và hiểu cách hoạt động của các phương pháp gian lận phần cứng trong game V.
![06241-ezgif com-optimize](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/c9e8ced2-3ab3-4c19-bfed-6f864f5aa7a7)
## Bắt đầu

### Chuẩn bị

* Thư viện KmBox (có sẵn trong source dưới dạng KmNet.pyd)
* Python 3.11
* Kmbox phiên bản Net (Phần cứng)

### Cài đặt

Clone repository từ GitHub:

```
git clone https://github.com/OzymoGit/2-condition-triggerbot.git
```
Cài đặt các gói Python cần thiết:

```
pip install -r requirements.txt
```
### Chạy chương trình
1. Di chuyển đến thư mục dự án:

```
cd 2-condition-triggerbot
```
2. Chỉnh sủa file config.json
```
{
  "ip": "192.168.2.188",  #Bạn thay bằng IP của Kmbox
  "port": "16896",        #Bạn thay bằng port của Kmbox
  "uid": "46405C53",      #Bạn thay bằng UID của Kmbox
  "trigger_delay": 0,     #Delay giữa 2 lần bắn, cái này hình như quên chưa implent xD
  "base_delay": 0,        #Base delay này là delay từ lúc phát hiện pixel đến lúc gửi chuột trái nên để 0 cho nhanh
  "color_tolerance": 40,  # Color tolerance main, cái này càng cao thì khoảng màu chấp nhận càng rộng. Tăng lên nếu bot không nhận diện màu
  "target_color": [250, 100, 250],  #Đây là màu outline của địch, default là màu Tím
  "scope_color": [0, 255, 0],    #Màu tâm chính, default là màu xanh lá
  "scope_color_tolerance": 40,   #corlor tolerance của màu tâm main
  "scope_color_alt": [0, 255, 255],  #Màu tâm thứ 2, cái này sẽ check khi bạn giữ chuột bên thứ 2. thay cho màu tâm chính
  "scope_color_tolerance_alt": 40  #color tolerance của màu tâm thứ 2
}
```
3. Chỉnh sửa màu tâm
+ Primary crosshair: Cyan
+ Aimdownsight and Sniper: Green
  
![Screenshot (2)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/da8a76a0-7409-4225-9271-9c3af41d7581)
![Screenshot (3)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/7d8393ca-1b16-4159-bc15-71d1c4f362f7)
![Screenshot (1)](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/fe5a5bcb-74fd-41d7-9336-4de2a3bb6f64)

Bật cả "Movement error", "Firing error", multiplier để X3
4.Chạy chương trình:
```
python run.py
```
5. Phím tắt:
+ F2: Thoát
+ F3: Pause/unpause
+ F4: Reload config

Xmousebutton2 cho alternate trigger mode

![Screenshot 2024-06-24 222638](https://github.com/OzymoGit/2-condition-triggerbot/assets/33122491/c1873efc-af2f-4204-8d46-3a43210763ce)


## Trợ giúp

Bạn cần trợ giúp? Tham gia server discord <a href="https://discord.gg/C3MY4kuAcD" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/discord.svg" alt="C3MY4kuAcD" height="30" width="40" /></a>


## Các tác giả

Ozymo

<h3 align="left">Liên hệ:</h3>
<p align="left">
<a href="https://twitter.com/ozymotv" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/twitter.svg" alt="ozymotv" height="30" width="40" /></a>
<a href="https://linkedin.com/in/ozymo" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/linked-in-alt.svg" alt="ozymo" height="30" width="40" /></a>
<a href="https://fb.com/ozymotv" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/facebook.svg" alt="ozymotv" height="30" width="40" /></a>
<a href="https://www.youtube.com/c/ozymotv" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/youtube.svg" alt="ozymotv" height="30" width="40" /></a>

</p>


<h3 align="left">Ủng hộ:</h3>
<p><a href="https://www.buymeacoffee.com/ozymotvz"> <img align="left" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="50" width="210" alt="ozymotvz" /></a><a href="https://ko-fi.com/ozymotv"> <img align="left" src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" height="50" width="210" alt="ozymotv" /></a></p><br><br>




## License

This project is licensed under the GPL 3.0 License - see the LICENSE file for details


