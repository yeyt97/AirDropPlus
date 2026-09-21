import base64
import locale
import os
import re
import socket

from PIL import Image, UnidentifiedImageError


def avoid_duplicate_filename(save_path, filename):
    base_filename, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(save_path, filename)):
        filename = f"{base_filename} ({counter}){extension}"
        counter += 1
    return filename

def clean_filename(file_name):
    cleaned_file_name = re.sub(r'[\\/*?:"<>|]', '', file_name)
    return cleaned_file_name

def is_image_file(file_path):
    try:
        with Image.open(file_path):
            return True
    except (UnidentifiedImageError, OSError):
        return False


def file_path_encode(path):
    return base64.b64encode(path.encode('utf-8')).decode('utf-8')


def file_path_decode(path):
    try:
        return base64.b64decode(path).decode('utf-8')
    except:
        return None


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port, max_tries=100):
    """从 start_port 起向上查找一个未被占用的端口，端口范围限定在 1024-65535。

    找不到时返回 None。
    """
    port = max(start_port, 1024)
    for _ in range(max_tries):
        if port > 65535:
            break
        if not is_port_in_use(port):
            return port
        port += 1
    return None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None


def get_system_language(supported_languages, default='en'):
    """匹配操作系统语言，无法匹配时返回 default。

    supported_languages: 支持的语言代码列表，如 ['en', 'ru', 'zh']
    """
    try:
        lang_code = locale.getlocale()[0] or locale.getdefaultlocale()[0]
    except Exception:
        lang_code = None
    if not lang_code:
        return default
    # 形如 'zh_CN' / 'Chinese (Simplified)_China' / 'en_US'，取主语言部分
    primary = lang_code.replace('-', '_').split('_')[0].lower().strip()
    # 已是标准语言代码
    if primary in supported_languages:
        return primary
    # Windows 上可能返回英文语言全称，按前缀匹配
    alias = {
        'chinese': 'zh',
        'russian': 'ru',
        'english': 'en',
    }
    for name, code in alias.items():
        if primary.startswith(name) and code in supported_languages:
            return code
    return default