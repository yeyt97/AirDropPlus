import configparser
import os
from result import Result
from utils import is_port_in_use

class Config:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')

        self.config_path = config_path
        self.key = self.config.get('config', 'key')
        self.save_path = self.config.get('config', 'save_path')
        if self.save_path == '' or self.save_path is None:
            self.save_path = os.path.join(os.path.expanduser('~'), 'Downloads')

        self.port = int(self.config.get('config', 'port'))
        self.basic_notifier = self.config.get('config', 'basic_notifier')=='1'

        self.show_icon = self.config.get('config', 'show_icon') == '1'

        self.version = self.config.get('info', 'version')

    def update(self, data):

        if not os.path.exists(data['save_path']):
            return Result.success(msg=f'目录 "{data["save_path"]}" 不存在，请检查')

        port_int = int(data['port'])
        if port_int < 1024 or port_int > 65535:
            return Result.success(msg='端口号必须在 1024 到 65535 之间')

        if port_int != self.port and is_port_in_use(port_int):
            return Result.success(msg=f'端口 {data["port"]} 已被占用，请更换')

        self.config.set('config', 'key', data['key'])
        self.config.set('config', 'save_path', data['save_path'])
        self.config.set('config', 'port', str(data['port']))
        self.config.set('config', 'basic_notifier', str(int(data['basic_notifier'])))
        self.config.set('config','show_icon', str(int(data['show_icon'])))

        self.key = data['key']
        self.save_path = data['save_path']
        self.port = data['port']
        self.basic_notifier = data['basic_notifier']
        self.show_icon = data['show_icon']

        self.config.write(open(self.config_path, 'w', encoding='utf-8'))