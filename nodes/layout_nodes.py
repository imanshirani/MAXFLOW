# nodes/layout_nodes.py
from NodeGraphQt import BackdropNode
from PySide6 import QtWidgets, QtGui

class MaxFlowBackdropNode(BackdropNode):
    __identifier__ = 'com.maxflow.layout'
    NODE_NAME = 'Backdrop'

    def __init__(self):
        super(MaxFlowBackdropNode, self).__init__()

    def edit_value(self):
        """ Edit value """
        import qtmax
        parent_window = qtmax.GetQMaxMainWindow()

        # 1. Change color
        current_color = QtGui.QColor(*self.color())
        color = QtWidgets.QColorDialog.getColor(current_color, parent_window, "Select Backdrop Color")
        if color.isValid():
            self.set_color(color.red(), color.green(), color.blue())
        
        # 2. Change text and name
        
        current_name = self.name() 
        if current_name == 'Backdrop': 
            current_name = self.text()

        text, ok = QtWidgets.QInputDialog.getText(parent_window, "Backdrop Title", "Enter new title:", text=current_name)
        if ok and text:
            self.set_name(text) 
            self.set_text(text) 