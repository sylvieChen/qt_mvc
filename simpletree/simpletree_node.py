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

    def add_child(self, child):
        self._children.append(child)

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
class SceneGraphModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(SceneGraphModel, self).__init__(parent)
        self._rootnode = root

    def rowCount(self, parent=QtCore.QModelIndex):
        if not parent.isValid():
            parent_node = self._rootnode
        else:
            parent_node = parent.internalPointer()
        return parent_node.child_count()

    def columnCount(self, parent=QtCore.QModelIndex):
        return 1

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return index.internalPointer().name()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        return 'Scenegraph'

    def parent(self, index):
        # Returns a void * pointer used by the model to associate the index with the internal data structure.
        node = index.internalPointer()
        parent_node = node.parent()

        if parent_node == self._rootnode:
            return QtCore.QModelIndex()

        # Creates a model index for the given row and column with the internal pointer ptr.
        #   QAbstractItemModel.createIndex (self, int row, int column, object object = 0)
        return self.createIndex(parent_node.index(), 0, parent_node)

    def index(self, row, column, parent):
        if not parent.isValid():
            parent_node = self._rootnode
        else:
            parent_node = parent.internalPointer()

        #
        children_item = parent_node.child(row)

        if children_item:
            return self.createIndex(row, column, children_item)
        else:
            return QtCore.QModelIndex()

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)

    rootnode = TreeNode('drinks')
    children_01 = TreeNode('coffee', rootnode)
    children_02 = TreeNode('tea', rootnode)
    children_03 = TreeNode('milk_tea', children_02)

    print rootnode

    scene_model = SceneGraphModel(rootnode)
    tree_view = QtGui.QTreeView()
    tree_view.show()

    tree_view.setModel(scene_model)

    sys.exit(app.exec_())