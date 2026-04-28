from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class LeaderBoard(QWidget):

    def __init__(self):
        super().__init__()
        self.initui()

    def initui(self):
        uic.loadUi('data/ui/leaderboard.ui', self)

        self.back_button.clicked.connect(self.back)

        f = open('records.txt', 'r')
        numbers_in_file = [line.strip().split() for line in f]
        f.close()
        arr = sorted(numbers_in_file, key=lambda x: (int(x[1]), x[0]))

        self.top_1_label.setText(': '.join(arr[-1]))
        self.top_2_label.setText(': '.join(arr[-2]))
        self.top_3_label.setText(': '.join(arr[-3]))

    def back(self):
        self.close()
