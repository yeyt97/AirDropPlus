import io
import os
import psutil
import flask
import win32clipboard
import win32con
from flask import Flask, request, jsonify
from win10toast import ToastNotifier

toaster = ToastNotifier()

SAVE_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')

def show_toast(msg: str):
    toaster.show_toast("AirDrop Plus", msg, duration=2, threaded=True)

def is_program_running():
    program_name = "AirDropPlus.exe"
    count: int = 0
    for process in psutil.process_iter((['name'])):
        if process.info['name'] == program_name:
            count += 1
            if count >= 2:  # 自身也占用一个
                return True
    return False

def result_type(success: bool, data=None, msg: str = None):
    return jsonify({
        'success': success,
        'msg': msg,
        'data': data
    })

def get_clipboard_files():
    win32clipboard.OpenClipboard()
    try:
        file_path_list = win32clipboard.GetClipboardData(win32con.CF_HDROP)
        file_path_list = [file for file in file_path_list if os.path.exists(file) and not os.path.isdir(file)]
    except:
        file_path_list = ()
    win32clipboard.CloseClipboard()
    return file_path_list

def avoid_duplicate_filename(filename):
    base_filename, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(SAVE_PATH, filename)):
        filename = f"{base_filename} ({counter}){extension}"
        counter += 1
    return filename

app = Flask(__name__)


@app.route('/file/send', methods=['POST'])
def send_file():
    if 'file' not in request.files:
        return result_type(False, msg="文件不存在"), 400
    file = request.files['file']
    filename = request.form['filename']
    new_filename = avoid_duplicate_filename(filename)
    file.save(os.path.join(SAVE_PATH, new_filename))
    show_toast("收到文件: " + filename)
    return result_type(True, msg="发送成功"), 200


@app.route('/file/receive/list')
def receive_file_list():
    file_path_list = get_clipboard_files()
    if len(file_path_list) > 0:
        return result_type(True, data=file_path_list)
    return result_type(False, msg='Windows未复制文件')


@app.route('/file/receive', methods=['POST'])
def receive_file():
    path = request.form.get('path')
    file_name = os.path.basename(path)
    with open(path, 'rb') as f:
        file_content = f.read()
    return flask.send_file(io.BytesIO(file_content), as_attachment=True, download_name=file_name)


@app.route('/')
def test():
    return 'Hello, World!'

if __name__ == '__main__':
    if is_program_running():
        show_toast("请不要重复启动")
    else:
        show_toast("已启动")
        app.run(host='0.0.0.0', port=53843)