from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator


class Records(QWidget):

    def __init__(self, stats):
        super().__init__()
        self.stats = int(stats)
        self.initui()

    def initui(self):
        uic.loadUi('data/ui/records.ui', self)
        self.successfully.setHidden(True)

        self.save_button.clicked.connect(self.save)
        self.back_button.clicked.connect(self.back)

        self.name_edit.setPlaceholderText("Max nickname length 18 characters")
        self.name_edit.setValidator(QRegExpValidator(QRegExp("^[^\s()-]*$")))

    def back(self):
        self.close()

    def save(self):
        f = open('records.txt', 'r')
        data = [line.strip() for line in f]
        f.close()
        names = [line.split()[0] for line in data]
        records = [line.split()[1] for line in data]
        if not self.name_edit.text() in names:
            f = open('records.txt', 'a')
            name = self.name_edit.text()
            f.write(f'{name} {self.stats}\n')
            f.close()
        else:
            with open('records.txt', 'w') as f:
                name = self.name_edit.text()
                if int(records[names.index(name)]) < self.stats:
                    records[names.index(name)] = str(self.stats)

                f.writelines("%s\n" % line for line in data)
        self.successfully.setHidden(False)
