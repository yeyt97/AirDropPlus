from win10toast import ToastNotifier


class Toaster:
    def __init__(self):
        self.toaster = ToastNotifier()

    def show(self, msg: str):
        self.toaster.show_toast("AirDrop Plus", msg, duration=2, threaded=True)

    def __call__(self, msg: str):
        self.show(msg)

toaster = Toaster()