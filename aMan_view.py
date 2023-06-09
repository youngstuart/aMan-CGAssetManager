from PySide2 import QtWidgets, QtCore

class Assets_View(QtWidgets.QTableView):
    def __init__(self):
        super().__init__()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.context_menu_assets = QtWidgets.QMenu()

        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.setSortingEnabled(True)

class Versions_View(QtWidgets.QTableView):
    def __init__(self):
        super().__init__()

        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

class Change_View(QtWidgets.QTableView):
    def __init__(self):
        super().__init__()
        self.setSortingEnabled(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)