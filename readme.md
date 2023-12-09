# AirDrop Plus

用于 iOS 设备和 Windows 电脑之间进行文件传输，需要配合快捷指令使用

打包：

```bash
pyinstaller --add-data 'config;config' -w AirDropPlus.py
```

打包后运行前需要在

依赖：

```
python==3.10.6
flask==3.0.0
win10toast==0.9
psutil==5.9.6
pyinstaller==6.2.0
```
