from win10toast import ToastNotifier


class Notifier:
    def __init__(self):
        self.notifier = ToastNotifier()

    def notify(self, msg: str):
        self.notifier.show_toast("AirDrop Plus", msg, duration=2, threaded=True)

    def __call__(self, msg: str):
        self.notify(msg)

notifier = Notifier()