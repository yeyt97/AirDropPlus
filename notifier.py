import os
from datetime import datetime

from windows_toasts import ToastButton, ToastActivatedEventArgs, Toast, InteractableWindowsToaster, ToastDisplayImage, WindowsToaster
import subprocess

import utils
import clipboard
from flask_babel import gettext as _


class Notifier:
    def __init__(self, use_basic_notifier: bool = False):
        self.use_basic_notifier = use_basic_notifier
        if use_basic_notifier:
            self.toaster = WindowsToaster("AirDrop Plus")
        else:
            self.toaster = InteractableWindowsToaster("AirDrop Plus", 'Microsoft.Windows.Explorer')

    def notify(self, title, msg):
        self.clear_toasts()
        toast = Toast([title, msg])
        self.toaster.show_toast(toast)

    def clear_toasts(self):
        self.toaster.clear_scheduled_toasts()
        self.toaster.clear_toasts()

    def show_file(self, folder, new_filename, filename):
        """
        显示收到的文件，图片文件会显示图片内容，非图片文件只显示文件名
        :param folder: 文件的保存目录
        :param new_filename: 保存的文件
        :param filename: 原始文件名
        :return: None
        """
        if self.use_basic_notifier:
            self.notify(_('Received file:'), filename)
            return

        def button_cb(args: ToastActivatedEventArgs):
            action = args.arguments
            path = os.path.join(folder, new_filename)
            if action == 'select':
                subprocess.Popen(f'explorer /select,{path}')
            elif action == 'open':
                subprocess.Popen(f'explorer {path}')
            elif action == 'copy':
                success, e = clipboard.set_file(path)
                if not success:
                    self.notify("⚠️" + _("Clipboard setting error"), e)

        self.clear_toasts()
        toast = Toast([f"{_('Received file:')} {filename}"])
        file_path = os.path.join(folder, new_filename)
        if utils.is_image_file(file_path):
            toast.AddImage(ToastDisplayImage.fromPath(file_path))
        toast.AddAction(ToastButton("📁" + _("Folder"), arguments='select'))
        toast.AddAction(ToastButton("🖼︎" + _("Open"), arguments='open'))
        toast.AddAction(ToastButton("✂" + _("Copy"), arguments='copy'))
        toast.on_activated = button_cb
        self.toaster.show_toast(toast)