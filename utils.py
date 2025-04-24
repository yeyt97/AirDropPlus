import base64
import os
import re
import socket
import imghdr


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
    image_type = imghdr.what(file_path)
    if image_type is not None:
        return True
    else:
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

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None