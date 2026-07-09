import sys
import os
import importlib
import pymxs
from PySide6 import QtWidgets, QtCore, QtGui

# Project path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Mouse selection patch
if not hasattr(QtWidgets.QGraphicsScene, '_maxflow_patched'):
    _orig_setSelectionArea = QtWidgets.QGraphicsScene.setSelectionArea
    def _patched_setSelectionArea(self, path, *args):
        
        if len(args) == 1:
            t = QtGui.QTransform()
            op = QtCore.Qt.ItemSelectionOperation.ReplaceSelection
            return _orig_setSelectionArea(self, path, op, args[0], t)
        return _orig_setSelectionArea(self, path, *args)
    QtWidgets.QGraphicsScene.setSelectionArea = _patched_setSelectionArea
    QtWidgets.QGraphicsScene._maxflow_patched = True

# Cleanup Memory
maxflow_modules = [
    'core.style_config', 'core.max_utils', 'core.evaluator', 
    'nodes.base_node', 'nodes.scene_nodes', 'nodes.math_nodes', 
    'nodes.modifier_nodes', 'nodes.layout_nodes', 'ui.main_window'
]

for mod in maxflow_modules:
    if mod in sys.modules:
        del sys.modules[mod]

# Import modules
import core.style_config
import core.max_utils
import nodes.base_node
import nodes.scene_nodes  
import nodes.math_nodes
import nodes.modifier_nodes
import nodes.layout_nodes
import core.evaluator
import ui.main_window

# Reload
importlib.reload(core.style_config)
importlib.reload(core.max_utils)
importlib.reload(nodes.base_node)
importlib.reload(nodes.scene_nodes)
importlib.reload(nodes.math_nodes)
importlib.reload(nodes.modifier_nodes)
importlib.reload(nodes.layout_nodes)
importlib.reload(core.evaluator)
importlib.reload(ui.main_window)

from ui.main_window import MaxFlowWindow

_maxflow_window_instance = None 

def show_maxflow():
    global _maxflow_window_instance
    import qtmax
    
    # Close old window
    if _maxflow_window_instance:
        _maxflow_window_instance.close()
        _maxflow_window_instance.deleteLater() 
        _maxflow_window_instance = None
    
    # Run new
    max_window = qtmax.GetQMaxMainWindow()
    _maxflow_window_instance = MaxFlowWindow(parent=max_window)
    _maxflow_window_instance.show()

if __name__ == '__main__':
    show_maxflow()