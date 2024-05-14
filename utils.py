import base64
import os
import re

import psutil
import imghdr


def avoid_duplicate_filename(save_path, filename):
    base_filename, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(save_path, filename)):
        filename = f"{base_filename} ({counter}){extension}"
        counter += 1
    return filename

def is_program_running():
    program_name = "AirDropPlus.exe"
    count: int = 0
    for process in psutil.process_iter((['name'])):
        if process.info['name'] == program_name:
            count += 1
            if count >= 2:  # 自身也占用一个
                return True
    return False

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

if __name__ == '__main__':
    path = r"C:\Users\11578\Downloads\PixPin_2024-05-14_08-24-08 (4).png"
    encode = file_path_encode(path)
    decode = file_path_decode(encode)
    print(encode)
    print(decode)