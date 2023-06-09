from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance, getCppPointer
import sys

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin, MayaQDockWidget

import os, sys
sys.path.append(os.path.join(os.environ["USER_SCRIPTS"], "maya", "assetManager"))
import aMan_ui
from importlib import reload
reload(aMan_ui)

def maya_main_window():
    # Create a pointer to Maya's MainWindow
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class Window(MayaQWidgetDockableMixin, aMan_ui.AssetManager):
    
    dlg_instance = None
    
    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = Window()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show(dockable=True)
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()
            
    def __init__(self):

        super().__init__(maya_main_window())
        self.setWindowFlags(self.windowFlags() \
                    | QtCore.Qt.WindowMaximizeButtonHint \
                    | QtCore.Qt.WindowMinimizeButtonHint \
                    | QtCore.Qt.WindowCloseButtonHint)

        self.versions_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.versions_table.customContextMenuRequested.connect(self.show_versions_menu)

        self.open_action = QtWidgets.QAction("Open", self.versions_table)
        self.open_action.triggered.connect(lambda: self.on_open_action(self.versions_table.get_selected_version()))

        self.import_action = QtWidgets.QAction("Import", self.assets_table)
        self.import_action.triggered.connect(lambda: self.on_import_action(self.assets_table.get_selected_asset()))
        
        self.reference_action = QtWidgets.QAction("Reference", self.assets_table)
        self.reference_action.triggered.connect(lambda: self.on_reference_action(self.assets_table.get_selected_asset()))
        self.assets_table.context_menu_assets.addAction(self.import_action)
        self.assets_table.context_menu_assets.addAction(self.reference_action)
    
    def show_versions_menu(self, position):
        self.context_menu_versions = QtWidgets.QMenu()
        self.context_menu_versions.addAction(self.open_action)
        self.context_menu_versions.exec_(self.versions_table.viewport().mapToGlobal(position))
    
    def on_import_action(self, asset):
        asset_path = asset[2]
        cmds.file(asset_path, i=True)
    
    def on_reference_action(self, asset):
        asset_path = asset[2]
        cmds.file(asset_path, reference=True)

    def on_open_action(self, version):
        version_path = version[1]
        cmds.file(version_path, open=True)

Window.show_dialog()
