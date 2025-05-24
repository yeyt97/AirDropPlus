import os
import signal
import subprocess
import sys
import time

from PIL import Image
from flask import Flask
from flask_babel import Babel, gettext as _

from config import Config
import utils
from notifier import Notifier
from server import Server

from pystray import Icon, MenuItem
import webbrowser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(SCRIPT_DIR, 'config', 'config.ini')
config = Config(config_file_path)

app = Flask(__name__)
babel = Babel(app)

def get_locale():
    return config.language if hasattr(config, 'language') else 'en'

babel.init_app(app, locale_selector=get_locale)

app_context = app.app_context()
app_context.push()

notifier = Notifier(config.basic_notifier)


def create_icon():
    def on_exit(icon, item):
        with app.app_context():
            notifier.notify(_('AirDrop Plus'), _('Exit'))
        icon.stop()
        os.kill(os.getpid(), signal.SIGINT)

    def on_edit_config(icon, item):
        with app.app_context():
            notifier.notify(_('AirDrop Plus'), _('Edit complete, please save and restart AirDrop Plus'))
        subprocess.Popen(["notepad", config_file_path])
    
    def on_web_config(icon, item):
        url = f"http://localhost:{config.port}/settings"
        try:
            webbrowser.open(url)
            with app.app_context():
                notifier.notify(_('AirDrop Plus'), _('Opened localhost in default browser'))
        except Exception as e:
            with app.app_context():
                notifier.notify(_('AirDrop Plus'), _('Failed to open browser:') + str(e))

    with app.app_context():
        menu = (
            MenuItem(text=_('Configuration file'), action=on_edit_config),
            MenuItem(text=_('Web configuration'), action=on_web_config),
            MenuItem(text=_('Exit'), action=on_exit),
        )
        image = Image.open(os.path.join(SCRIPT_DIR, 'static', 'icon.ico'))
        icon = Icon(_('AirDrop Plus'), image, _('AirDrop Plus'), menu)
        icon.run()


def start_server() -> tuple[bool, str]:
    with app.app_context():
        if not os.path.exists(config.save_path):
            return False, _('Directory "%(path)s" does not exist, please check configuration file', path=config.save_path)
        if utils.is_port_in_use(config.port):
            return False, _('Port %(port)s is already in use', port=config.port)
        try:
            server = Server(config, notifier)
            server.run_in_thread('0.0.0.0', config.port)
        except Exception as e:
            return False, _('Error message: %(error)s', error=str(e))
        return True, _('Port: %(port)s\nSave path: %(path)s', port=config.port, path=config.save_path)


if __name__ == '__main__':
    flag, msg = start_server()
    with app.app_context():
        if flag:
            notifier.notify(_('Started'), msg)
        else:
            notifier.notify(_('Start failed'), msg)
            sys.exit()
    if config.show_icon:
        create_icon()
    else:
        while True:
            time.sleep(10)
