import win32api
import win32clipboard
import win32con
from PIL import ImageGrab, Image


def get_clipboard_data():
    win32clipboard.OpenClipboard()
    try:
        file_path_list = []
        # 检查是否有文本数据
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            text_data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            file_path_list.append(text_data)

    except Exception as e:
        print(f"Error: {e}")
        file_path_list = []
    win32clipboard.CloseClipboard()
    return file_path_list

if __name__ == '__main__':
    while True:
        res = get_clipboard_data()
        pass