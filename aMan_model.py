from PySide2 import QtCore
from aMan import aMan

class Assets_Model(QtCore.QAbstractTableModel):
    
    def __init__(self, parent = None):
        
        super().__init__(parent)
        self.aman = aMan()
        

        self.db = []
        self.update_data()
    
    def rowCount(self, *args):
        return len(self.db)
    
    def columnCount(self, *args, **kwargs):
        return 4
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            asset = self.db[index.row()]
            return asset[index.column()]
            
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return ['Asset ID', 'Asset Name', 'Path', "Asset Type"][section]
    
    def delete_row(self, index):
        if index.isValid():
            self.beginRemoveRows(QtCore.QModelIndex(), index.row(), index.row())
            del self.db[index.row()]
            self.endRemoveRows()
        
    def update_data(self):
        self.db = self.aman.get_assets()
        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()

class Change_Model(QtCore.QAbstractTableModel):
    
    def __init__(self, parent = None):
        
        super().__init__(parent)
        self.aman = aMan()
        self.db = []
    
    def rowCount(self, role = QtCore.Qt.DisplayRole):
        return len(self.db)
    
    def columnCount(self, index, role = QtCore.Qt.DisplayRole):
        return 3
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        row = index.row()
        col = index.column()

        if role == QtCore.Qt.DisplayRole:
            chlog_timestamp, chlog_message, username = self.db[row]
            
            if col == 0:
                return str(chlog_timestamp)
            if col == 1:
                return chlog_message
            if col == 2:
                return username

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return ['Timestamp', 'Message', 'Username'][section]
        
    def update_data(self, asset_id: int):
        self.db = self.aman.get_changelog(asset_id)
        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()

class Versions_Model(QtCore.QAbstractTableModel):
    
    def __init__(self, parent = None):
        
        super().__init__(parent)
        self.aman = aMan()
        self.db = []
    
    def rowCount(self, role = QtCore.Qt.DisplayRole):
        return len(self.db)
    
    def columnCount(self, index, role = QtCore.Qt.DisplayRole):
        return 2
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        row = index.row()
        col = index.column()

        if role == QtCore.Qt.DisplayRole:
            asset_version, asset_path = self.db[row]
            
            if col == 0:
                return str(asset_version)
            if col == 1:
                return asset_path

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return ['Version', 'Path',][section]
        
    def update_data(self, asset_id: int):
        self.db = self.aman.get_versions(asset_id)
        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()

class Asset_SortFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Custom FilterProxyModel for combining filter expressions"""
    def __init__(self, parent = None):
        
        super().__init__(parent)

        self.IDRegExp = QtCore.QRegExp()
        self.IDRegExp.setPatternSyntax(QtCore.QRegExp.RegExp)

        self.nameRegExp = QtCore.QRegExp()
        self.nameRegExp.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.nameRegExp.setPatternSyntax(QtCore.QRegExp.RegExp)

        self.pathRegExp = QtCore.QRegExp()
        self.pathRegExp.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.pathRegExp.setPatternSyntax(QtCore.QRegExp.RegExp)

        self.typeRegExp = QtCore.QRegExp()
        self.typeRegExp.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.typeRegExp.setPatternSyntax(QtCore.QRegExp.RegExp)
    
    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        """Determines if the given row, source_row, contains a regex match for all search indexes

        Args:
            source_row (int): _description_
            source_parent (QtCore.QModelIndex): _description_

        Returns:
            bool: _description_
        """
        idIndex = self.sourceModel().index(source_row, 0, source_parent)
        nameIndex = self.sourceModel().index(source_row, 1, source_parent)
        pathIndex = self.sourceModel().index(source_row, 2, source_parent)
        typeIndex = self.sourceModel().index(source_row, 3, source_parent)

        id = self.sourceModel().data(idIndex)
        name = self.sourceModel().data(nameIndex)
        path = self.sourceModel().data(pathIndex)
        assetType = self.sourceModel().data(typeIndex)
        return (self.IDRegExp.pattern() in str(id) \
                and self.nameRegExp.pattern() in name \
                and self.pathRegExp.pattern() in path \
                and self.typeRegExp.pattern() in assetType)
    
    def setIDFilter(self, regExp):
        self.IDRegExp.setPattern(regExp)
        self.invalidateFilter()
    
    def setNameFilter(self, regExp):
        self.nameRegExp.setPattern(regExp)
        self.invalidateFilter()

    def setPathFilter(self, regExp):
        self.pathRegExp.setPattern(regExp)
        self.invalidateFilter()
    
    def setTypeFilter(self, regExp):
        self.typeRegExp.setPattern(regExp)
        self.invalidateFilter()
 