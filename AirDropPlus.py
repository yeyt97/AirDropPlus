import os
import signal
import subprocess
import sys

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


def start_server() -> tuple[bool, str]:
    if not os.path.exists(config.save_path):
        return False, f'目录 "{config.save_path}" 不存在，请检查配置文件'
    if utils.is_port_in_use(config.port):
        return False, f'端口{config.port}被占用'
    try:
        server = Server(config, notifier)
        server.run_in_thread('0.0.0.0', config.port)
    except Exception as e:
        return False, f'错误信息：{e}'
    return True, f'端口号：{config.port}\n文件保存路径：{config.save_path}"'


if __name__ == '__main__':
    flag, msg = start_server()
    if flag:
        notifier.notify("已启动", msg)
    else:
        notifier.notify("启动失败", msg)
        sys.exit()

    create_icon()
