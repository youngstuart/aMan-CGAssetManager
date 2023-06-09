from PySide2 import QtWidgets, QtCore, QtGui
import sys
from functools import partial
import aMan_ui

app = QtWidgets.QApplication(sys.argv)

class MainWindow(aMan_ui.AssetManager): 
    def __init__(self):
        super().__init__(self)
        self.setWindowFlags(self.windowFlags() \
                    | QtCore.Qt.WindowMaximizeButtonHint \
                    | QtCore.Qt.WindowMinimizeButtonHint \
                    | QtCore.Qt.WindowCloseButtonHint)
        
        self.appearanceMenu = QtWidgets.QMenu("Appearance")

        styleAction_light = QtWidgets.QAction("Default", self.appearanceMenu)
        styleAction_light.triggered.connect(partial(self.set_style, "Default"))
        self.appearanceMenu.addAction(styleAction_light)
        styleAction_dark = QtWidgets.QAction("Dark", self.appearanceMenu)
        styleAction_dark.triggered.connect(partial(self.set_style, "Dark"))
        self.appearanceMenu.addAction(styleAction_dark)

        self.settings_menu.addMenu(self.appearanceMenu)

    def set_style(self, style):
        styles = {
        'Default': {'stylesheet': '',
                'submenu': '',
                'icon': ''},
        'Dark':{'stylesheet': './style_dark.qss',
                'submenu': "QMenu { background-color: #525252; color: #EEEEEE;} QMenu::item:selected { background-color: #5285A6; }",
                'icon': ''},
            }
        
        if style == 'Default':
            self.setStyleSheet('')
        else:
            with open(styles[style]['stylesheet'], 'r') as f:
                self.setStyleSheet(f.read())
            
        for menu in [self.refreshMenu, self.appearanceMenu]:
            menu.setStyleSheet(styles[style]['submenu'])
        
        self.setWindowIcon(QtGui.QIcon(styles[style]['icon']))

w = MainWindow()
w.show()

app.exec_()