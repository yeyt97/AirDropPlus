import os
import psutil
import win32clipboard
import win32con

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

def get_clipboard_files():
    win32clipboard.OpenClipboard()
    try:
        file_path_list = win32clipboard.GetClipboardData(win32con.CF_HDROP)
        file_path_list = [file for file in file_path_list if os.path.exists(file) and not os.path.isdir(file)]
    except:
        file_path_list = ()
    win32clipboard.CloseClipboard()
    return file_path_list