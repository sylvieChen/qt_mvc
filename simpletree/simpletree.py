from PySide import QtGui, QtCore


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

    def type_info(self):
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
#
class TreeModel(QtCore.QAbstractItemModel):
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
            if index.column() == 0:
                return index.internalPointer().name()
            else:
                return index.internalPointer().type_info()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.set_name(value)
                return True

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return 'Node'
            else:
                return 'TYPE'

    def parent(self, index):
        # Returns a void * pointer used by the model to associate the index with the internal data structure.
        node = self.get_node(index)
        parent_node = node.parent()


        if parent_node == self._rootnode:
            return QtCore.QModelIndex()

        # Creates a model index for the given row and column with the internal pointer ptr.
        #   QAbstractItemModel.createIndex (self, int row, int column, object object = 0)
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
        parent_node = self.get_node(parent)
        for i in range(count):
            node_name = 'untitled{}'.format(parent_node.child_count())
            child_node = TreeNode(node_name)
            success = parent_node.insert_child(row, child_node)
        self.endInsertRows()
        return success

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row+count-1)
        node = self.get_node(parent)
        for i in range(count):
            success = node.remove_child(row)
        self.endRemoveRows()
        return success

    # ====================================== #
    #   customize
    # ====================================== #
    def get_node(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootnode

class CameraTreeNode(TreeNode):
    def __init__(self, name, parent=None):
        super(CameraTreeNode,  self).__init__(name, parent)

    def type_info(self):
        return 'camera'


class GeometryTreeNode(TreeNode):
    def __init__(self, name, parent=None):
        super(GeometryTreeNode,  self).__init__(name, parent)

    def type_info(self):
        return 'Geo'

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setStyle('playstique')

    rootnode = TreeNode('root')

    camera_node = CameraTreeNode('Cam', rootnode)
    geo_node = GeometryTreeNode('body', rootnode)
    sphere_node = GeometryTreeNode('leg', geo_node)

    print rootnode

    tree_view = QtGui.QTreeView()
    tree_view.show()

    model = TreeModel(rootnode)
    tree_view.setModel(model)

    # insert/remove node as child of root node
    model.insertRows(0, 3)
    model.removeRows(0, 1)

    # insert node as child of body node
    body_index = model.index(3, 0, QtCore.QModelIndex())
    model.insertRows(0, 3, body_index)


    sys.exit(app.exec_())