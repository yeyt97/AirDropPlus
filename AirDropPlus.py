import io
import os
import flask
from flask import Flask, request
from config import Config
from result import Result
import utils
from notifier import notifier

CONFIG_FILE_NAME = 'config.ini'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print("SCRIPT_DIR: " + SCRIPT_DIR)
config = Config(os.path.join(SCRIPT_DIR, 'config', CONFIG_FILE_NAME))

app = Flask(__name__)
# 统一认证
@app.before_request
def check_api_key():
    auth_header = request.headers.get("Authorization")
    if auth_header != config.key:
        return Result.error(msg='密钥错误', code=401)
    version = request.headers.get("ShortcutVersion")
    if version != config.version:
        msg = f'版本不匹配\n\nWindows版本为：{config.version}\n快捷指令版本为：{version}'
        return Result.error(msg=msg, code=400)


# 手机端发送文件
@app.route('/file/send', methods=['POST'])
def send_file():
    if 'file' not in request.files:
        return Result.error(msg="文件不存在")
    file = request.files['file']
    filename = request.form['filename']
    new_filename = utils.avoid_duplicate_filename(config.save_path, filename)
    file.save(os.path.join(config.save_path, new_filename))
    notifier("收到文件: " + filename + f'\n保存在: {config.save_path}')
    return Result.success(msg="发送成功")


# 获取电脑端复制的文件的路径列表
@app.route('/file/receive/list')
def receive_file_list():
    file_path_list = utils.get_clipboard_files()
    if len(file_path_list) > 0:
        return Result.success(data=file_path_list)
    return Result.error(msg='Windows未复制文件')


# 获取电脑端文件
@app.route('/file/receive', methods=['POST'])
def receive_file():
    path = request.form.get('path')
    file_name = os.path.basename(path)
    notifier(f'发送：{file_name}')
    with open(path, 'rb') as f:
        file_content = f.read()
    return flask.send_file(io.BytesIO(file_content), as_attachment=True, download_name=file_name)

# 统一异常处理
@app.errorhandler(Exception)
def handle_all_exceptions(error):
    msg = '遇到一个错误：' + str(error)
    notifier(msg)
    return Result.error(msg, 500)

# 检查启动条件
def check_startup_conditions() -> (bool, str):
    if not os.path.exists(config.save_path):
        return False, '文件保存路径："{config.save_path}"不存在，请检查配置文件"{CONFIG_FILE_NAME}"'
    if utils.is_program_running():
        return False, '请不要重复启动'
    return True, f'文件保存路径：{config.save_path}"'


if __name__ == '__main__':
    success, startup_msg = check_startup_conditions()
    if success:
        notifier("启动成功\n" + startup_msg)
        app.run(host='0.0.0.0', port=53843)
    else:
        notifier("启动失败\n" + startup_msg)