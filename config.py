import configparser
import os


class Config:
    def __init__(self, config_path):
        self.config_path = None
        self.config = None
        self.key = None
        self.save_path = None
        self.version = None
        self.get_config(config_path)

    # 刷新配置
    def get_config(self, config_path):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path, encoding='utf-8')
        # 获取键值对
        self.key = self.config.get('config', 'key')
        self.save_path= self.config.get('config', 'save_path')
        if self.save_path == '' or self.save_path is None:
            self.save_path = os.path.join(os.path.expanduser('~'), 'Downloads')

        self.version = self.config.get('info', 'version')

