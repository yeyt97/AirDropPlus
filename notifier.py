import os
import urllib
from pathlib import Path
from typing import Union, Optional
from win10toast import ToastNotifier
from windows_toasts import ToastButton, ToastActivatedEventArgs, Toast, InteractableWindowsToaster, ToastDisplayImage, \
    ToastImage, ToastImagePosition
import subprocess
from abc import ABC, abstractmethod

import utils

class INotifier(ABC):
    @abstractmethod
    def notify(self, title, msg):
        pass

    @abstractmethod
    def show_file(self, folder: str, filename: str, ori_filename: str) -> None:
        """
        显示收到的文件
        图片文件会显示图片内容，非图片文件只显示文件名
        :param folder: 文件的保存目录
        :param filename: 保存的文件
        :param ori_filename: 原始文件名
        :return: None
        """
        pass

    @abstractmethod
    def show_files(self, folder: str, ori_filename_list: list):
        """
        显示收到的批量文件
        :param folder: 文件的保存目录
        :param ori_filename_list: 原始文件列表
        :return: None
        """
        pass


class Win10Notifier(INotifier):
    def __init__(self):
        self.notifier = ToastNotifier()

    def notify(self, title, msg):
        self.notifier.show_toast(title, msg, threaded=True)

    def show_file(self, folder: str, filename: str, ori_filename: str) -> None:
        self.notify('收到文件:', ori_filename)

    def show_files(self, folder: str, ori_filename_list: list):
        num_files = len(ori_filename_list)
        msg = "\n".join(ori_filename_list)
        self.notify(f"收到{num_files}个文件:", msg)


"""
用来修复windows_toasts不能显示中文路径的图片的问题
"""
class MyToastDisplayImage(ToastDisplayImage):
    class MyToastImage(ToastImage):
        def __init__(self, imagePath):
            super().__init__(imagePath)
            self.path = urllib.parse.unquote(Path(imagePath).as_uri())
    @classmethod
    def fromPath(
            cls,
            imagePath: Union[str, os.PathLike],
            altText: Optional[str] = None,
            position: ToastImagePosition = ToastImagePosition.Inline,
            circleCrop: bool = False,
    ) -> ToastDisplayImage:
        image = cls.MyToastImage(imagePath)
        return ToastDisplayImage(image, altText, position, circleCrop)


class Win11Notifier(INotifier):
    def __init__(self):
        self.toaster = InteractableWindowsToaster("")

    @staticmethod
    def _button_callback(args: ToastActivatedEventArgs):
        if args.arguments == '':
            return
        action, arg = args.arguments.split('=')
        if action == 'select':
            subprocess.Popen(f'explorer /select,{arg}')
        elif action == 'open':
            subprocess.Popen(f'explorer {arg}')

    def notify(self, title, msg):
        toast = Toast([title, msg])
        self.toaster.show_toast(toast)

    def show_file(self, folder, filename, ori_filename):
        toast = Toast([f"收到文件: {ori_filename}"])
        file_path = os.path.join(folder, filename)
        if utils.is_image_file(file_path):
            toast.AddImage(MyToastDisplayImage.fromPath(file_path))
        toast.AddAction(ToastButton("打开文件夹", arguments=f'select={file_path}'))
        toast.AddAction(ToastButton("关闭", arguments='ignore='))
        toast.on_activated = self._button_callback
        self.toaster.show_toast(toast)

    def show_files(self, folder, ori_filename_list):
        num_files = len(ori_filename_list)
        if num_files == 0:
            raise ValueError('文件数量不能为0')
        content = [f"收到{num_files}个文件:"] + ori_filename_list
        toast = Toast(content)
        toast.AddAction(ToastButton("打开文件夹", arguments=f'open={folder}'))
        toast.AddAction(ToastButton("关闭", arguments='ignore='))
        toast.on_activated = self._button_callback
        self.toaster.show_toast(toast)


def create_notifier(is_win11: bool = False):
    return Win11Notifier() if is_win11 else Win10Notifier()