import io
import os

import flask
from flask import Flask, request, Blueprint

from config import Config
import utils
from notifier import INotifier
from result import Result

class Server:
    def __init__(self, config: Config, notifier: INotifier):
        self.config = config
        self.notifier = notifier
        self.blueprint = Blueprint('server', __name__)
        self.register_routes()
        self.app = Flask(__name__)
        self.app.register_blueprint(self.blueprint)

    def run(self, host: str, port: int):
        self.app.run(host=host, port=port)

    def register_routes(self):
        """ ----------- 统一处理 ----------- """
        # 统一认证
        @self.blueprint.before_request
        def check_api_key():
            if request.path == '/':
                return
            auth_header = request.headers.get("Authorization")
            if auth_header != self.config.key:
                return Result.error(msg='密钥错误', code=401)
            version = request.headers.get("ShortcutVersion")
            if version != self.config.version:
                msg = f'版本不匹配\n\nWindows版本为：{self.config.version}\n快捷指令版本为：{version}'
                return Result.error(msg=msg, code=400)

        # 统一异常处理
        @self.blueprint.errorhandler(Exception)
        def handle_all_exceptions(error):
            msg = str(error)
            self.notifier.notify('错误', '遇到一个错误' + msg)
            return Result.error(msg, 500)

        """ ----------- 测试 ----------- """
        @self.blueprint.route('/')
        def test():
            return 'Hello world!'

        """ ----------- 文件 ----------- """
        # 手机端发送接下来要发送的文件列表
        @self.blueprint.route('/file/send/list', methods=['POST'])
        def send_file_list():
            filename_list = request.form['file_list'].splitlines()
            self.notifier.show_future_files(self.config.save_path, filename_list, to_mobile=False)
            return Result.success(msg="发送成功")

        # 手机端发送文件
        @self.blueprint.route('/file/send', methods=['POST'])
        def send_file():
            if 'file' not in request.files:
                return Result.error(msg="文件不存在")
            file = request.files['file']
            ori_filename = request.form['filename']
            notify_content = request.form['notify_content']
            filename = utils.avoid_duplicate_filename(self.config.save_path, ori_filename)
            file.save(os.path.join(self.config.save_path, filename))

            if notify_content != '':
                ori_filename_list = notify_content.splitlines()
                if len(ori_filename_list) == 1:
                    self.notifier.show_received_file(self.config.save_path, filename, ori_filename)
                else:
                    self.notifier.show_received_files(self.config.save_path, ori_filename_list)
            return Result.success(msg="发送成功")

        # 获取电脑端复制的文件的路径列表
        @self.blueprint.route('/file/receive/list')
        def receive_file_list():
            success, res = utils.get_clipboard_files()
            if not success:
                msg = f'未复制文件: {res}'
                self.notifier.notify('错误', msg)
                return Result.error(msg=msg)
            if len(res) > 0:
                file_names = [os.path.basename(path) for path in res]
                self.notifier.show_future_files(None, file_names, to_mobile=True)
                return Result.success(data=res)
            return Result.error(msg='Windows未复制文件')

        # 获取电脑端文件
        @self.blueprint.route('/file/receive', methods=['POST'])
        def receive_file():
            path = request.form.get('path')
            file_name = os.path.basename(path)
            # self.notifier.notify('文件', f'发送: {file_name}')
            with open(path, 'rb') as f:
                file_content = f.read()
            return flask.send_file(io.BytesIO(file_content), as_attachment=True, download_name=file_name)

        """ ----------- 剪贴板 ----------- """
        # 获取电脑端剪贴板
        @self.blueprint.route('/clipboard/receive')
        def receive_clipboard():
            success, res = utils.get_clipboard_content()
            if not success:
                msg = f'获取剪贴板出错: {res}'
                self.notifier.notify('错误', msg)
                return Result.error(msg=msg)
            if res != '':
                self.notifier.notify('剪贴板', f'发送: {res}')
                return Result.success(data=res)
            else:
                self.notifier.notify('剪贴板', '发送失败: Windows剪贴板为空')
                return Result.error(msg='Windows剪贴板为空')

        # 接收手机端剪贴板
        @self.blueprint.route('/clipboard/send', methods=['POST'])
        def send_clipboard():
            clipboard = request.form['clipboard']
            if clipboard is None or clipboard == '':
                self.notifier.notify('剪贴板', '接收失败: iPhone剪贴板为空')
                return Result.error(msg='iPhone剪贴板为空')
            success, msg = utils.set_clipboard_content(clipboard)
            if success:
                self.notifier.notify('剪贴板', f'收到剪贴板内容: {clipboard}')
            else:
                self.notifier.notify('错误', f'设置剪贴板出错: {msg}')
            return Result.success(msg='发送成功') if success else Result.error(msg=msg)
