from PySide6.QtWidgets import QStackedWidget

class PageManager(QStackedWidget):
    def register_page(self, name, widget):
        self.addWidget(widget)

    def show_index(self, index:int):
        self.setCurrentIndex(index)
