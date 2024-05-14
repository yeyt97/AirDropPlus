import io
import os
import traceback

import flask
from flask import Flask, request, Blueprint, stream_with_context

from config import Config
import utils
from notifier import INotifier
from result import Result

from clipboard import ClipboardType, ClipboardUtil
from werkzeug.utils import secure_filename


def get_clipboard_dto(clipboard_type: ClipboardType, data: str):
    return {
        'type': clipboard_type.value,
        'data': data
    }


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
                self.notifier.notify("⚠️错误:", "密钥错误")
                return Result.error(msg='密钥错误', code=401)
            version = request.headers.get("ShortcutVersion")
            client_version = '.'.join(self.config.version.split('.')[:2])
            if '.'.join(version.split('.')[:2]) != client_version:
                msg = f'''版本不匹配\n\nWindows版本为：{self.config.version}\n快捷指令版本为：{version}'''
                self.notifier.notify("⚠️错误:", msg)
                return Result.error(msg=msg, code=400)

        # 统一异常处理
        @self.blueprint.errorhandler(Exception)
        def handle_all_exceptions(error):
            traceback.print_exc()
            msg = str(error)
            self.notifier.notify('⚠️错误:', msg)
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
            filename = secure_filename(file.filename)
            notify_content = request.form['notify_content']
            new_filename = utils.avoid_duplicate_filename(self.config.save_path, filename)
            file_path = os.path.join(self.config.save_path, new_filename)
            with open(file_path, 'wb') as f:
                for chunk in stream_with_context(file.stream):
                    if chunk:
                        f.write(chunk)

            if notify_content != '':
                ori_filename_list = notify_content.splitlines()
                if len(ori_filename_list) == 1:
                    self.notifier.show_received_file(self.config.save_path, new_filename, filename)
                else:
                    self.notifier.show_received_files(self.config.save_path, ori_filename_list)
            return Result.success(msg="发送成功")

        # 获取电脑端文件
        @self.blueprint.route('/file/receive', methods=['POST'])
        def receive_file():
            path = request.form.get('path')
            file_name = os.path.basename(path)
            with open(path, 'rb') as f:
                file_content = f.read()
            return flask.send_file(io.BytesIO(file_content), as_attachment=True, download_name=file_name)

        """ ----------- 剪贴板 ----------- """
        # 获取电脑端剪贴板
        @self.blueprint.route('/clipboard/receive')
        def receive_clipboard():
            # 文本
            success, res = ClipboardUtil.get_text()
            if success:
                dto = get_clipboard_dto(ClipboardType.TEXT, res)
                self.notifier.notify('📝发送剪贴板文本:', res)
                return Result.success(data=dto)
            success, res = ClipboardUtil.get_files()
            # 文件
            if success:
                dto = get_clipboard_dto(ClipboardType.FILE, res)
                file_names = [os.path.basename(path) for path in res]
                self.notifier.show_future_files(None, file_names, to_mobile=True)
                return Result.success(data=dto)
            # 图片
            success, res = ClipboardUtil.get_img_base64()
            if success:
                dto = get_clipboard_dto(ClipboardType.IMG, res)
                self.notifier.notify('🏞️发送剪贴板图片', "")
                return Result.success(data=dto)

            self.notifier.notify('⚠️发送剪贴板出错:', 'Windows剪贴板为空')
            return Result.error(msg='Windows剪贴板为空')

        # 接收手机端剪贴板
        @self.blueprint.route('/clipboard/send', methods=['POST'])
        def send_clipboard():
            text = request.form['clipboard']
            if text is None or text == '':
                self.notifier.notify('⚠️设置剪贴板出错:', ' iPhone剪贴板为空')
                return Result.error(msg='iPhone剪贴板为空')
            success, msg = ClipboardUtil.set_text(text)
            if success:
                self.notifier.notify('📝设置剪贴板文本:', text)
            else:
                self.notifier.notify('⚠️设置剪贴板出错:', msg)
            return Result.success(msg='发送成功') if success else Result.error(msg=msg)
