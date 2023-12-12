import os
import sys

from config import Config
import utils
from notifier import notifier
from server import Server

if __name__ == '__main__':
    CONFIG_FILE_NAME = 'config.ini'
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    print('script_dir: ' + SCRIPT_DIR)

    config_file_path = os.path.join(SCRIPT_DIR, 'config', CONFIG_FILE_NAME)
    config = Config(config_file_path)

    if not os.path.exists(config.save_path):
        notifier.notify('启动失败', f'文件保存路径："{config.save_path}"不存在，请检查配置文件"{CONFIG_FILE_NAME}"')
        sys.exit()
    if utils.is_program_running():
        notifier.notify('启动失败', '请不要重复启动')
        sys.exit()
    notifier.notify('启动成功', f'文件保存路径：{config.save_path}"')
    server = Server(config)
    server.run(host='0.0.0.0', port=53843)