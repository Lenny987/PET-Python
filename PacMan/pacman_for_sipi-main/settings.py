from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class Settings(QWidget):

    def __init__(self):
        super().__init__()
        self.initui()

    def initui(self):
        uic.loadUi('data/ui/settings.ui', self)
        self.error.setHidden(True)
        self.successfully.setHidden(True)

        self.save_button.clicked.connect(self.save)
        self.back_button.clicked.connect(self.back)

        self.ghosts_num.setPlaceholderText("1 - 10")
        self.volume_num.setPlaceholderText("0 - 100")

        f = open('settings.txt', 'r')
        numbers_in_file = [line.strip() for line in f]
        f.close()
        self.file_ghosts_num.setText(numbers_in_file[0])
        self.file_volume_num.setText(numbers_in_file[1])

    def back(self):
        self.close()

    def check(self):
        if self.ghosts_num.text().isnumeric() and self.volume_num.text().isnumeric()\
                and 1 <= int(self.ghosts_num.text()) <= 10 and 0 <= int(self.volume_num.text()) <= 100:
            return True
        return False

    def save(self):
        self.error.setHidden(True)
        if self.check():
            with open('settings.txt', 'w') as f:
                f.write(f'{self.ghosts_num.text()}\n{self.volume_num.text()}')
            self.successfully.setHidden(False)
        else:
            self.error.setHidden(False)
