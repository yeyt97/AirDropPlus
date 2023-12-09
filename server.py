import io
import os

import flask
from flask import Flask, request, Blueprint

import utils
from notifier import notifier
from result import Result

class Server:
    def __init__(self, config):
        self.config = config
        self.blueprint = Blueprint('server', __name__)
        self.register_routes()
        self.app = Flask(__name__)
        self.app.register_blueprint(self.blueprint)

    def run(self, host, port):
        self.app.run(host=host, port=port)

    def register_routes(self):
        # 统一认证
        @self.blueprint.before_request
        def check_api_key():
            auth_header = request.headers.get("Authorization")
            if auth_header != self.config.key:
                return Result.error(msg='密钥错误', code=401)
            version = request.headers.get("ShortcutVersion")
            if version != self.config.version:
                msg = f'版本不匹配\n\nWindows版本为：{self.config.version}\n快捷指令版本为：{version}'
                return Result.error(msg=msg, code=400)

        # 手机端发送文件
        @self.blueprint.route('/file/send', methods=['POST'])
        def send_file():
            if 'file' not in request.files:
                return Result.error(msg="文件不存在")
            file = request.files['file']
            filename = request.form['filename']
            new_filename = utils.avoid_duplicate_filename(self.config.save_path, filename)
            file.save(os.path.join(self.config.save_path, new_filename))
            notifier("收到: " + new_filename + f'\n保存在: {self.config.save_path}')
            return Result.success(msg="发送成功")

        # 获取电脑端复制的文件的路径列表
        @self.blueprint.route('/file/receive/list')
        def receive_file_list():
            file_path_list = utils.get_clipboard_files()
            if len(file_path_list) > 0:
                return Result.success(data=file_path_list)
            return Result.error(msg='Windows未复制文件')

        # 获取电脑端文件
        @self.blueprint.route('/file/receive', methods=['POST'])
        def receive_file():
            path = request.form.get('path')
            file_name = os.path.basename(path)
            notifier(f'发送：{file_name}')
            with open(path, 'rb') as f:
                file_content = f.read()
            return flask.send_file(io.BytesIO(file_content), as_attachment=True, download_name=file_name)

        # 统一异常处理
        @self.blueprint.errorhandler(Exception)
        def handle_all_exceptions(error):
            msg = '遇到一个错误：' + str(error)
            notifier(msg)
            return Result.error(msg, 500)