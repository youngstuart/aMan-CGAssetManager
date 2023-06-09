from PySide2 import QtWidgets, QtCore, QtGui

from pathlib import Path
from functools import partial 

from aMan import aMan, User
from aMan_view import *
from aMan_model import *

class UpdateTimer(QtCore.QTimer):
    refresh_signal = QtCore.Signal()
    def __init__(self):
        super().__init__()
        self.setInterval(1000)
        self.set_refresh_interval(5)
        self.timeout.connect(self.timer_hit)
        self.time_label = QtWidgets.QLabel()
        minimal_sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.time_label.setSizePolicy(minimal_sizePolicy)
        self.set_refresh_interval(5)

    def set_refresh_interval(self, interval):
        self.refresh_interval = interval 
        self.time_remaining = self.refresh_interval

    def timer_hit(self):
        self.time_label.setText(f"Updating in {self.time_remaining} seconds")
        self.time_remaining -= 1
        if self.time_remaining < 0:
            self.refresh_signal.emit()
            self.time_remaining = self.refresh_interval
       
class LabelLineEdit(QtWidgets.QWidget):
    """A simple one liner combining a QLabel, self.label, and QLineEdit, self.value"""
    def __init__(self, label):
        super().__init__()
        self.label = QtWidgets.QLabel(label)
        self.label.setFixedWidth(100)
        self.value = QtWidgets.QLineEdit()

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.label)

        self.layout.addWidget(self.value)

class LabelRadio(QtWidgets.QWidget):
    """A simple one liner combining a QLabel, self.label, and QGroupBox, self.value"""
    def __init__(self, label):
        super().__init__()
        self.label = QtWidgets.QLabel(label)
        self.label.setFixedWidth(100)

        self.grp_box = QtWidgets.QGroupBox()
        self.button_grp = QtWidgets.QButtonGroup(self)

        self.grp_box_lyt = QtWidgets.QHBoxLayout()
        self.grp_box.setLayout(self.grp_box_lyt)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.label)

        self.layout.addWidget(self.grp_box)
    
class CreateAsset(QtWidgets.QDialog):
    """A Simple dialog used for the creation of assets to the database
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() \
                    | QtCore.Qt.WindowMaximizeButtonHint \
                    | QtCore.Qt.WindowMinimizeButtonHint \
                    | QtCore.Qt.WindowCloseButtonHint)
        self.parent = parent
        self.setWindowTitle("Create Asset")
        self.setMinimumWidth(500)
        self.main_lyt = QtWidgets.QVBoxLayout(self)

        self.asset_name = LabelLineEdit("Asset Name")
        self.asset_type = LabelRadio("Asset Type")
        
        asset_type_geo = QtWidgets.QRadioButton("Geo")
        asset_type_img = QtWidgets.QRadioButton("Texture")
        asset_type_geo.setChecked(True)

        self.asset_type.grp_box_lyt.addWidget(asset_type_geo)
        self.asset_type.button_grp.addButton(asset_type_geo)
        self.asset_type.grp_box_lyt.addWidget(asset_type_img)
        self.asset_type.button_grp.addButton(asset_type_img)

        self.asset_path = LabelLineEdit("Asset Path")
        
        for i in [self.asset_name, self.asset_type, self.asset_path]:
            i.label.setFixedWidth(65)

        self.assetBrowse = QtWidgets.QPushButton("Browse")
        self.assetBrowse.clicked.connect(self.openFileBrowser)
        self.asset_path.layout.addWidget(self.assetBrowse)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.asset_path.value.textChanged.connect(self.asset_path_set)

        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.on_cancel)

        self.main_lyt.addWidget(self.asset_name)
        
        self.main_lyt.addWidget(self.asset_type)

        self.main_lyt.addWidget(self.asset_path)

        self.main_lyt.addWidget(self.button_box)

    def asset_path_set(self):
        """Enable/Disable OK button if asset path is not empty
        """
        if self.asset_path.value.text():
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

    def on_accept(self):
        """If asset_path is a valid file, create an asset in the database
        """
        asset_name = self.asset_name.value.text()
        asset_type = self.asset_type.button_grp.checkedButton().text()
        asset_path = self.asset_path.value.text()

        if Path(asset_path).exists():
            aman = aMan()
            user = self.parent.user
            aman.set_user(user)
            asset_id = aman.create_asset(asset_name, asset_type, asset_path)
            if asset_id:
                # Force an update to show the new asset
                self.parent.assets_table._model.update_data()
        else:
            print(f"Asset path invalid!")

    def on_cancel(self):
        self.close()

    def openFileBrowser(self):
        browser = QtWidgets.QFileDialog(self)
        browser.setFileMode(QtWidgets.QFileDialog.AnyFile)
        if browser.exec_():
            selected_files = browser.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.asset_path.value.setText(file_path)

class CreateUser(QtWidgets.QDialog):
    """A Simple dialog used for the creation of a user to the database
    """
    def __init__(self, parent, user):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() \
                    | QtCore.Qt.WindowMaximizeButtonHint \
                    | QtCore.Qt.WindowMinimizeButtonHint \
                    | QtCore.Qt.WindowCloseButtonHint)
        self.parent = parent
        self.user = user
        self.setWindowTitle("Create User")
        self.setMinimumWidth(500)
        self.main_lyt = QtWidgets.QVBoxLayout(self)

        self.nameFirst = LabelLineEdit("First Name")
        self.nameLast = LabelLineEdit("Last Name")
        self.email = LabelLineEdit("email")
        self.username = LabelLineEdit("Username")
        self.username.value.setText(self.user.username)
        self.username.value.setReadOnly(True)

        self.main_lyt.addWidget(self.nameFirst)
        self.main_lyt.addWidget(self.nameLast)
        self.main_lyt.addWidget(self.email)
        self.main_lyt.addWidget(self.username)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.on_cancel)

        self.main_lyt.addWidget(self.button_box)

    def on_accept(self):
        self.user.create_user(
            self.nameFirst.value.text(),
            self.nameLast.value.text(),
            self.email.value.text(),
        )

        self.close()

    def on_cancel(self):
        self.close()


class AssetsTable(Assets_View):
    def __init__(self):
        super().__init__()
        self._model = Assets_Model()

        self.proxy_model = Asset_SortFilterProxyModel()
        self.proxy_model.setSourceModel(self._model)
        self.setModel(self.proxy_model)

        self.customContextMenuRequested.connect(self.show_assets_menu)
        self.delete_asset_action = QtWidgets.QAction("Delete", self)
        self.context_menu_assets.addAction(self.delete_asset_action)
        self.delete_asset_action.triggered.connect(lambda: self.on_delete_asset(self.get_selected_asset()))

        for col in range(self._model.columnCount(0)):

            self._model.headerData(col, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        asset_header = self.horizontalHeader()
        asset_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

    def show_assets_menu(self, position):
        self.context_menu_assets.exec_(self.viewport().mapToGlobal(position))

    def get_selected_asset(self):
        """Translates the selected proxy row to the underlying data row in self.assets_model

        Returns:
            tuple: row in self.assets_model.data()
        """
        selected_proxy_index = self.selectedIndexes()[0]
        selected_index_model = self.proxy_model.mapToSource(selected_proxy_index)
        selected_asset = self._model.db[selected_index_model.row()]
        if selected_asset:
            return selected_asset
        
        return None
    
    def on_delete_asset(self, asset: tuple):
        """Deletes the asset in the given row from the database

        Args:
            row (int): row in self.assets_model.data()
        """
        asset_id = asset[0]
        delete_asset = self._model.aman.delete_asset(asset_id)
        if delete_asset:
            self._model.update_data()
  
class VersionsTable(Versions_View):
    def __init__(self):
        super().__init__()
        self._model = Versions_Model()
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self._model)
        self.setModel(self.proxy_model)
        # Populate version table header columns
        for col in range(self._model.columnCount(0)):

            self._model.headerData(col, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        header = self.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    def get_selected_version(self):
        """Translates the selected proxy row to the underlying data row in self.versions_model

        Returns:
            int: row in self.versions_model.data()
        """
        selected_proxy_index = self.selectedIndexes()[0]
        selected_index_model = self.proxy_model.mapToSource(selected_proxy_index)
        selected_version = self._model.db[selected_index_model.row()]
        if selected_version:
            return selected_version
        
        return None

class ChangeTable(Change_View):
    def __init__(self):
        super().__init__()
        self._model = Change_Model()
        proxy_model = QtCore.QSortFilterProxyModel()
        proxy_model.setSourceModel(self._model)
        self.setModel(proxy_model)
        # Populate changelog header columns
        for col in range(self._model.columnCount(0)):

            self._model.headerData(col, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        header = self.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

class AssetManager(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.menu = self.menuBar()

        self.settings_menu = self.menu.addMenu("&Settings")
        self.refresh_menu = QtWidgets.QMenu("Refresh Interval")
        
        for i in [1,5,30,60]:
            refresh_action = QtWidgets.QAction(f"{i} Second", self.settings_menu)
            refresh_action.triggered.connect(partial(self.on_refresh_action, i))

            self.refresh_menu.addAction(refresh_action)

        self.settings_menu.addMenu(self.refresh_menu)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.create_menu = self.menu.addMenu("&Create")
        self.asset_action = QtWidgets.QAction("&Asset", self.create_menu)
        self.asset_action.triggered.connect(self.on_asset_action)
        self.create_menu.addAction(self.asset_action)

        self.setWindowTitle(f"Asset Manager - {len(self.assets_table._model.db)} Assets")
        self.update_timer.start()

        self.user = User()
        
        if not self.user.user_id:
            self.create_user = CreateUser(self, self.user)
            self.create_user.show()
            # CreateUser window will be inactive/focus returned to main window on launch
            # CreateUser.activateWindow() can be called after main window init

    def on_asset_action(self):
        create_asset = CreateAsset(self)
        create_asset.show()
        
    def on_refresh_action(self, seconds):
        self.update_timer.set_refresh_interval(seconds)

    def create_widgets(self):
        self.central_widget = QtWidgets.QWidget()

        self.asset_widget = QtWidgets.QWidget()

        self.assets_table = AssetsTable()

        self.versions_table = VersionsTable()

        self.change_table = ChangeTable()

        self.search_id = LabelLineEdit("ID: ")
        self.search_name = LabelLineEdit("Asset Name: ")
        self.search_path = LabelLineEdit("Path: ")
        self.search_type = LabelLineEdit("Asset Type: ")

        self.horizontal_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.vertical_splitter.addWidget(self.versions_table)
        self.vertical_splitter.addWidget(self.change_table)
        self.horizontal_splitter.addWidget(self.asset_widget)
        self.horizontal_splitter.addWidget(self.vertical_splitter)

        # Timer for automatic db query and table update
        self.update_timer = UpdateTimer()
        self.update_timer.refresh_signal.connect(self.assets_table._model.update_data)

        self.setCentralWidget(self.central_widget)
  
    def create_layouts(self):
        main_lyt = QtWidgets.QVBoxLayout(self.central_widget)

        assetLyt = QtWidgets.QVBoxLayout(self.asset_widget)
        assetLyt.setMargin(0)

        search_bar = QtWidgets.QVBoxLayout()
        search_bar.addWidget(self.search_id)
        search_bar.addWidget(self.search_name)
        search_bar.addWidget(self.search_path)
        search_bar.addWidget(self.search_type)

        assetLyt.addLayout(search_bar)
        assetLyt.addWidget(self.assets_table)

        main_lyt.addWidget(self.horizontal_splitter)
        main_lyt.addWidget(self.update_timer.time_label)

    def create_connections(self):
        self.search_id.value.textChanged.connect(self.assets_table.proxy_model.setIDFilter)
        self.search_name.value.textChanged.connect(self.assets_table.proxy_model.setNameFilter)
        self.search_path.value.textChanged.connect(self.assets_table.proxy_model.setPathFilter)
        self.search_type.value.textChanged.connect(self.assets_table.proxy_model.setTypeFilter)
        # Bind selectionModel to a variable before accessing
        selection_model = self.assets_table.selectionModel()
        selection_model.selectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self, selected, deselected):
        if selected.indexes():
            row = selected.indexes()[0].row()
            value = self.assets_table.model().index(row, 0).data()
            self.change_table._model.update_data(value)
            self.versions_table._model.update_data(value)


