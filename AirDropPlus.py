import os
import signal
import subprocess
import sys
import threading

from PIL import Image

from config import Config
import utils
from notifier import Notifier
from server import Server

from pystray import Icon, MenuItem

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(SCRIPT_DIR, 'config', 'config.ini')
config = Config(config_file_path)
notifier = Notifier(config.basic_notifier)

def create_icon():
    def on_exit(icon, item):
        notifier.notify('AirDrop Plus', '已退出')
        icon.stop()
        os.kill(os.getpid(), signal.SIGINT)

    def on_edit_config(icon, item):
        notifier.notify('AirDrop Plus', '编辑完成请保存，并重启 AirDrop Plus')
        subprocess.Popen(["notepad", config_file_path])

    menu = (
        MenuItem(text='设置', action=on_edit_config),
        MenuItem(text='退出', action=on_exit),
    )
    image = Image.open(os.path.join(SCRIPT_DIR, 'static', 'icon.ico'))
    icon = Icon("AirDrop Plus", image, "AirDrop Plus", menu)
    icon.run()
def start_server():
    if not os.path.exists(config.save_path):
        notifier.notify('启动失败', f'文件保存路径："{config.save_path}"不存在，请检查配置文件"{config_file_path}"')
        sys.exit()
    if utils.is_program_running():
        notifier.notify('启动失败', '请不要重复启动')
        sys.exit()
    try:
        server = Server(config, notifier)
        notifier.notify('启动成功', f'端口号：{config.port}\n文件保存路径：{config.save_path}"')
        threading.Thread(target=lambda:server.run(host='0.0.0.0', port=config.port)).start()
    except Exception as e:
        notifier.notify('启动失败', f'错误信息：{e}')

if __name__ == '__main__':

    start_server()
    create_icon()
