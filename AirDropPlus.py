import io
import os
import flask
from flask import Flask, request

from result import Result
from utils import avoid_duplicate_filename, is_program_running, get_clipboard_files
from toaster import toaster

SAVE_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')


app = Flask(__name__)

# 统一认证
@app.before_request
def check_api_key():
    auth_header = request.headers.get("Authorization")
    if auth_header != 'jinitaimei':
        return Result.error(msg='密钥错误', code=401)


# 手机端发送文件
@app.route('/file/send', methods=['POST'])
def send_file():
    if 'file' not in request.files:
        return Result.error(msg="文件不存在")
    file = request.files['file']
    filename = request.form['filename']
    new_filename = avoid_duplicate_filename(SAVE_PATH, filename)
    file.save(os.path.join(SAVE_PATH, new_filename))
    toaster("收到文件: " + filename)
    return Result.success(msg="发送成功")


# 获取电脑端复制的文件的路径列表
@app.route('/file/receive/list')
def receive_file_list():
    file_path_list = get_clipboard_files()
    if len(file_path_list) > 0:
        return Result.success(data=file_path_list)
    return Result.error(msg='Windows未复制文件')


# 获取电脑端文件
@app.route('/file/receive', methods=['POST'])
def receive_file():
    path = request.form.get('path')
    file_name = os.path.basename(path)
    with open(path, 'rb') as f:
        file_content = f.read()
    return flask.send_file(io.BytesIO(file_content), as_attachment=True, download_name=file_name)

# 统一异常处理
@app.errorhandler(Exception)
def handle_all_exceptions(error):
    msg = '遇到一个错误：'+str(error)
    return Result.error(msg, 500)

if __name__ == '__main__':
    if is_program_running():
        toaster("请不要重复启动")
    else:
        toaster("已启动")
        app.run(host='0.0.0.0', port=53843)