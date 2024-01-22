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
    def show_received_file(self, folder: str, filename: str, ori_filename: str) -> None:
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
    def show_received_files(self, folder: str, ori_filename_list: list):
        """
        显示收到的批量文件
        :param folder: 文件的保存目录
        :param ori_filename_list: 原始文件列表
        :return: None
        """
        pass

    @abstractmethod
    def show_future_files(self, folder: Optional[str], filename_list: list, to_mobile: bool):
        """
        显示接下来将要收到哪些文件
        :param folder: 文件的保存目录
        :param filename_list: 文件列表
        :param to_mobile: 是否是发送到iOS
        :return:
        """
        pass

"""
不带按钮和图片显示的通知，适用于旧版系统
"""
class BasicNotifier(INotifier):
    def __init__(self):
        self.notifier = ToastNotifier()

    def notify(self, title, msg):
        self.notifier.show_toast(title, msg, threaded=True)

    def show_received_file(self, folder: str, filename: str, ori_filename: str) -> None:
        self.notify('收到文件:', ori_filename)

    def show_received_files(self, folder: str, ori_filename_list: list):
        num_files = len(ori_filename_list)
        if num_files == 0:
            raise ValueError('文件数量不能为0')
        msg = ", ".join(ori_filename_list)
        self.notify(f"收到 {num_files} 个文件:", msg)

    def show_future_files(self, folder: str, filename_list: list, to_mobile: bool):
        num_files = len(filename_list)
        if num_files == 0:
            raise ValueError('文件数量不能为0')
        msg = ", ".join(filename_list)
        action_str = '发送' if to_mobile else '接收'
        self.notify(f"开始{action_str} {num_files} 个文件:", msg)

"""
可交互式通知
"""
class Notifier(INotifier):
    def __init__(self):
        self.toaster = InteractableWindowsToaster("", 'Microsoft.Windows.Explorer')

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

    def show_received_file(self, folder, filename, ori_filename):
        toast = Toast([f"收到文件: {ori_filename}"])
        file_path = os.path.join(folder, filename)
        if utils.is_image_file(file_path):
            toast.AddImage(self.MyToastDisplayImage.fromPath(file_path))
        toast.AddAction(ToastButton("打开文件夹", arguments=f'select={file_path}'))
        toast.AddAction(ToastButton("关闭", arguments='ignore='))
        toast.on_activated = self._button_callback
        self.toaster.show_toast(toast)

    def show_received_files(self, folder, ori_filename_list):
        num_files = len(ori_filename_list)
        if num_files == 0:
            raise ValueError('文件数量不能为0')
        content = [f"收到 {num_files} 个文件:", ', '.join(ori_filename_list)]
        toast = Toast(content)
        toast.AddAction(ToastButton("打开文件夹", arguments=f'open={folder}'))
        toast.AddAction(ToastButton("关闭", arguments='ignore='))
        toast.on_activated = self._button_callback
        self.toaster.show_toast(toast)

    def show_future_files(self, folder: str, filename_list: list, to_mobile: bool):
        num_files = len(filename_list)
        if num_files == 0:
            raise ValueError('文件数量不能为0')
        action_str = '发送' if to_mobile else '接收'
        toast = Toast([f"开始{action_str} {num_files} 个文件:", ', '.join(filename_list)])
        if not to_mobile:
            toast.AddAction(ToastButton("打开文件夹", arguments=f'open={folder}'))
            toast.AddAction(ToastButton("关闭", arguments='ignore='))
            toast.on_activated = self._button_callback
        self.toaster.show_toast(toast)

def create_notifier(basic: bool = True):
    return BasicNotifier() if basic else Notifier()
