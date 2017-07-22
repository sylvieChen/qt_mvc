from PySide import QtGui, QtCore
import json


class TreeNode(object):
    def __init__(self, name, parent=None):
        super(TreeNode,  self).__init__()

        self._children = []
        self._parent = parent
        self._name = name
        if parent is not None:
            parent.add_child(self)

    def name(self):
        return self._name

    def set_name(self, new_name):
        self._name = new_name

    def type(self):
        return 'node'

    def add_child(self, child):
        self._children.append(child)

    def insert_child(self, position, child):
        if position <0 or position>self.child_count():
            return False
        self._children.insert(position, child)
        child._parent = self
        return True

    def remove_child(self, position):
        if position <0 or position>self.child_count():
            return False
        child = self._children.pop(position)
        child._parent = None
        return True

    def child(self, index):
        return self._children[index]

    def child_count(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def index(self):
        if self._parent:
            return self._parent._children.index(self)

    def log(self, tab_level=-1):
        output = ''
        tab_level += 1

        for i in range(tab_level):
            output += '---{}|'.format(i)
        output += self.name() + '\n'
        for child in self._children:
            output += child.log(tab_level)
        tab_level -= 1

        return output

    def __repr__(self):
        return self.log()

class TreeModel(QtCore.QAbstractItemModel):
    """
    A basic class for tree model. with drag and drop.
    """
    def __init__(self, root, parent=None):
        super(TreeModel, self).__init__(parent)
        self._rootnode = root

    def rowCount(self, parent=QtCore.QModelIndex):
        if not parent.isValid():
            parent_node = self._rootnode
        else:
            parent_node = parent.internalPointer()
        return parent_node.child_count()

    def columnCount(self, parent=QtCore.QModelIndex):
        return 2

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            node = self.get_node(index)
            if index.column() == 0:
                return index.internalPointer().name()
            elif index.column() == 1 and node._parent!=self._rootnode:
                return index.internalPointer().type()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
               | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.set_name(value)
                return True

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return 'Assets'
            else:
                return 'type'

    def parent(self, index):
        #   Returns a void * pointer used by the model to associate the index with the internal data structure.
        node = self.get_node(index)
        parent_node = node.parent()

        if parent_node == self._rootnode:
            #   when it is rootnode, it has no parent, so we return empty QModelIndex()
            return QtCore.QModelIndex()

        return self.createIndex(parent_node.index(), 0, parent_node)

    def index(self, row, column, parent):
        parent_node = self.get_node(parent)
        children_item = parent_node.child(row)

        if children_item:
            return self.createIndex(row, column, children_item)
        else:
            return QtCore.QModelIndex()

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row+count-1)
        # parent_node = self.get_node(parent)
        # for i in range(count):
        #     node_name = 'untitled{}'.format(parent_node.child_count())
        #     child_node = TreeNode(node_name)
        #     success = parent_node.insert_child(row, child_node)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row+count-1)
        node = self.get_node(parent)
        for i in range(count):
            success = node.remove_child(row)
        self.endRemoveRows()
        return success

    def supportedDropActions(self):
        '''Items can be copied.'''
        return QtCore.Qt.CopyAction

    def mimeTypes(self):
        '''The MimeType for the encoded data.'''
        types = ['text/scene_tree_node']
        return types

    def mimeData(self, indices):
        '''Encode serialized data from the item at the given index into a QMimeData object.'''
        data = dict()
        for index in indices:
            if index.isValid():
                item = index.internalPointer()
                data[item] = item.name()
        item_name = data.values()[0]
        mimedata = QtCore.QMimeData()
        mimedata.setData('text/scene_tree_node', json.dumps(item_name))
        return mimedata

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        '''Handles the dropping of an item onto the model.

        De-serializes the data into a TreeItem instance and inserts it into the model.
        '''
        drag_data = str(mimedata.data('text/scene_tree_node'))
        item_name = json.loads(drag_data)
        node = parentIndex.internalPointer()
        if node.type() == 'char':
            CharTreeNode(item_name, node)
        if node.type() == 'prop':
            PropTreeNode(item_name, node)
        if node.type() == 'env':
            EnvTreeNode(item_name, node)
        self.insertRows(node.child_count()-1, 1, parentIndex)

        return True

    # ====================================== #
    #   customize
    # ====================================== #
    def get_node(self, index):
        #   A valid index belongs to a model, and has non-negative row and column numbers.
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._rootnode


class CharTreeNode(TreeNode):
    def __init__(self, name, parent=None):
        super(CharTreeNode,  self).__init__(name, parent)

    def type(self):
        return 'char'


class PropTreeNode(TreeNode):
    def __init__(self, name, parent=None):
        super(PropTreeNode,  self).__init__(name, parent)

    def type(self):
        return 'prop'

class EnvTreeNode(TreeNode):
    def __init__(self, name, parent=None):
        super(EnvTreeNode,  self).__init__(name, parent)

    def type(self):
        return 'env'


class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        rootnode = TreeNode('root')
        CharTreeNode('Sally', rootnode)
        PropTreeNode('tea', rootnode)
        EnvTreeNode('school', rootnode)
        # print rootnode

        scene_model = TreeModel(rootnode)
        tree_view = QtGui.QTreeView()
        tree_view.setModel(scene_model)
        tree_view.setDragEnabled(True)
        tree_view.setAcceptDrops(True)
        tree_view.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        # insert node as child of body node
        # char_index = scene_model.index(2, 0, QtCore.QModelIndex())
        # scene_model.insertRows(0, 3, char_index)

        rootnode2 = TreeNode('root')
        CharTreeNode('char', rootnode2)
        PropTreeNode('prop', rootnode2)
        EnvTreeNode('env', rootnode2)
        # print rootnode2

        scene_model2 = TreeModel(rootnode2)
        tree_view2 = QtGui.QTreeView()
        tree_view2.setModel(scene_model2)
        tree_view2.setAcceptDrops(True)

        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.addWidget(tree_view)
        self.vLayout.addWidget(tree_view2)

        self.setLayout(self.vLayout)
        self.setGeometry(300, 300, 280, 150)
        self.show()


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setStyle('playstique')

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())