import os
import sys

from config import Config
import utils
from notifier import create_notifier
from server import Server

if __name__ == '__main__':
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(SCRIPT_DIR, 'config', 'config.ini')
    config = Config(config_file_path)
    notifier = create_notifier(config.basic_notifier)
    if not os.path.exists(config.save_path):
        notifier.notify('启动失败', f'文件保存路径："{config.save_path}"不存在，请检查配置文件"{config_file_path}"')
        sys.exit()
    if utils.is_program_running():
        notifier.notify('启动失败', '请不要重复启动')
        sys.exit()
    try:
        server = Server(config, notifier)
        notifier.notify('启动成功', f'端口号：{config.port}\n文件保存路径：{config.save_path}"')
        server.run(host='0.0.0.0', port=config.port)
    except Exception as e:
        notifier.notify('启动失败', f'错误信息：{e}')
