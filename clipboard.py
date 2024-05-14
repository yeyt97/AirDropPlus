import base64
import io
import os
from typing import Tuple

import pyperclip
import win32clipboard
import win32con
from win32clipboard import OpenClipboard, GetClipboardData, CloseClipboard, IsClipboardFormatAvailable
from PIL import ImageGrab

from enum import Enum
from ctypes import Structure, c_uint, c_long, c_int, c_bool, sizeof


# 用于复制文件到剪贴板
# https://xxmdmst.blog.csdn.net/article/details/120631425
class DROPFILES(Structure):
    _fields_ = [
        ("pFiles", c_uint),
        ("x", c_long),
        ("y", c_long),
        ("fNC", c_int),
        ("fWide", c_bool),
    ]


pDropFiles = DROPFILES()
pDropFiles.pFiles = sizeof(DROPFILES)
pDropFiles.fWide = True
matedata = bytes(pDropFiles)


class Type(Enum):
    TEXT = 'text'
    IMG = 'img'
    FILE = 'file'


def get_content(con) -> tuple[bool, any]:
    """
    获取剪贴板内容
    :param con: win32con.xxx
    :return: 是否成功, 剪贴板内容|异常对象
    """
    if not IsClipboardFormatAvailable(con):
        return False, None
    OpenClipboard()
    try:
        res = GetClipboardData(con)
    except Exception as e:
        return False, e
    finally:
        CloseClipboard()
    return True, res


def get_files() -> tuple[bool, any]:
    """
    获取剪贴板的文件
    :return: 是否成功, 剪贴板内容|异常对象
    """
    success, res = get_content(win32con.CF_HDROP)
    if not success:
        return False, res
    file_path_list = [file for file in res if os.path.exists(file) and not os.path.isdir(file)]
    return True, file_path_list


def get_text() -> tuple[bool, any]:
    """
    获取剪贴板的文本
    :return: 是否成功, 剪贴板内容|异常对象
    """
    return get_content(win32con.CF_UNICODETEXT)


def set_text(text: str) -> tuple[bool, any]:
    """
    设置剪贴板的文本
    :return: 是否成功, 异常对象|None
    """
    try:
        pyperclip.copy(text)
    except Exception as e:
        return False, str(e)
    return True, None


def get_img_base64() -> tuple[bool, str]:
    """
    获取剪贴板的图片，并转换为base64编码
    :return: 是否成功, 图片的base64编码|错误文本
    """
    img = ImageGrab.grabclipboard()
    if not img:
        return False, '未复制图像'
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='PNG')
    img_bytes = output_buffer.getvalue()
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    return True, base64_str


def set_files(paths) -> tuple[bool, Exception] | tuple[bool, None]:
    files = ("\0".join(paths)).replace("/", "\\")
    data = files.encode("U16")[2:] + b"\0\0"
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP, matedata + data)
    except Exception as e:
        return False, e
    finally:
        win32clipboard.CloseClipboard()
    return True, None


def set_file(file) -> tuple[bool, Exception] | tuple[bool, None]:
    return set_files([file])
