from win10toast import ToastNotifier


class Notifier:
    def __init__(self):
        self.notifier = ToastNotifier()

    def notify(self, title, msg):
        self.notifier.show_toast(title, msg, duration=2, threaded=True)

notifier = Notifier()