# ui/main_window.py
from PySide6 import QtWidgets, QtCore, QtGui
import pymxs
from NodeGraphQt import NodeGraph
from nodes.scene_nodes import UniversalObjectNode, GetPropertyNode
from nodes.math_nodes import FloatNode, IntNode, BoolNode, StringNode, MathOperatorNode, AxisNode
from nodes.modifier_nodes import ModifierNode
from nodes.layout_nodes import MaxFlowBackdropNode
from core.evaluator import GraphEvaluator

class MaxFlowWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MaxFlowWindow, self).__init__(parent)
        self.setWindowTitle('MAXFLOW - Node Based Workflow (LIVE)')
        self.resize(1200, 800)

        self.graph = NodeGraph()
        self.setCentralWidget(self.graph.widget)
        self.graph.set_pipe_collision(True)

        self.shortcut_del = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete), self.graph.widget)
        self.shortcut_del.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.shortcut_del.activated.connect(self.action_delete_selected)

        self.graph.node_double_clicked.connect(self.on_node_double_clicked)
        self.graph.nodes_deleted.connect(lambda: self.live_update(from_viewport=False))        
        self.graph.port_connected.connect(lambda: self.live_update(from_viewport=False))
        self.graph.port_disconnected.connect(lambda: self.live_update(from_viewport=False))
        self.graph.property_changed.connect(self.on_property_changed)

        self.register_nodes()
        self.build_right_click_menu()

        self._is_updating = False
        
        try: pymxs.runtime.unregisterRedrawViewsCallback(self.on_max_scene_changed)
        except: pass
        pymxs.runtime.registerRedrawViewsCallback(self.on_max_scene_changed)

    def on_max_scene_changed(self, *args, **kwargs):
        if not self._is_updating:
            self.live_update(from_viewport=True)

    def on_node_double_clicked(self, node):
        if hasattr(node, 'edit_value'):
            node.edit_value()

    def on_property_changed(self, node, prop_name, prop_value):
        if prop_name in ['pos', 'size']:
            self.graph.viewer().scene().update()
            return
        if prop_name not in ['selected']:
            self.live_update(from_viewport=False)

    def live_update(self, from_viewport=False, *args, **kwargs):
        if self._is_updating: return
        self._is_updating = True
        try:
            for node in self.graph.all_nodes():
                if isinstance(node, UniversalObjectNode) or isinstance(node, ModifierNode):
                    try: 
                        node.evaluate(from_viewport=from_viewport)
                    except: pass
        finally:
            self._is_updating = False

    def closeEvent(self, event):
        try: pymxs.runtime.unregisterRedrawViewsCallback(self.on_max_scene_changed)
        except: pass
        super(MaxFlowWindow, self).closeEvent(event)

    def register_nodes(self):
        nodes_to_register = [
            MaxFlowBackdropNode, UniversalObjectNode, GetPropertyNode, ModifierNode, 
            FloatNode, IntNode, BoolNode, StringNode, MathOperatorNode, AxisNode
        ]
        for node_class in nodes_to_register:
            try: self.graph.register_node(node_class)
            except: pass

    def build_right_click_menu(self):
        context_menu = self.graph.get_context_menu('graph')
        context_menu.add_command('▶ Force Execute', lambda: self.live_update(from_viewport=False))
        context_menu.add_separator()
        context_menu.add_command('🗑️ Delete Selected', self.action_delete_selected)

        nodes_menu = context_menu.add_menu('Nodes')
        
        layout_menu = nodes_menu.add_menu('Layout')
        layout_menu.add_command('Backdrop (Frame)', lambda: self.graph.create_node('com.maxflow.layout.MaxFlowBackdropNode', pos=[self.graph.viewer().scene_cursor_pos().x(), self.graph.viewer().scene_cursor_pos().y()]))

        scene = nodes_menu.add_menu('Scene')
        scene.add_command('Get Scene Object', self.action_get_scene_object)
        scene.add_command('Get Property (Extractor)', lambda: self.graph.create_node('com.maxflow.scene.GetPropertyNode', pos=[self.graph.viewer().scene_cursor_pos().x(), self.graph.viewer().scene_cursor_pos().y()]))
        
        modifiers = nodes_menu.add_menu('Modifiers')
        modifiers.add_command('Add Modifier', self.action_create_modifier) 

        inputs_menu = nodes_menu.add_menu('Inputs')
        inputs_menu.add_command('Float', lambda: self.graph.create_node('com.maxflow.input.FloatNode', pos=[self.graph.viewer().scene_cursor_pos().x(), self.graph.viewer().scene_cursor_pos().y()]))
        inputs_menu.add_command('Integer', lambda: self.graph.create_node('com.maxflow.input.IntNode', pos=[self.graph.viewer().scene_cursor_pos().x(), self.graph.viewer().scene_cursor_pos().y()]))
        inputs_menu.add_command('Boolean', lambda: self.graph.create_node('com.maxflow.input.BoolNode', pos=[self.graph.viewer().scene_cursor_pos().x(), self.graph.viewer().scene_cursor_pos().y()]))
        inputs_menu.add_command('String', lambda: self.graph.create_node('com.maxflow.input.StringNode', pos=[self.graph.viewer().scene_cursor_pos().x(), self.graph.viewer().scene_cursor_pos().y()]))
        inputs_menu.add_command('Axis (X,Y,Z)', lambda: self.graph.create_node('com.maxflow.input.AxisNode', pos=[self.graph.viewer().scene_cursor_pos().x(), self.graph.viewer().scene_cursor_pos().y()]))

        math_menu = nodes_menu.add_menu('Math')
        math_menu.add_command('Math Operator', lambda: self.graph.create_node('com.maxflow.math.MathOperatorNode', pos=[self.graph.viewer().scene_cursor_pos().x(), self.graph.viewer().scene_cursor_pos().y()]))

        node_menu = self.graph.get_context_menu('nodes')
        node_menu.add_command('Link Selected Object', self.action_pick_object, node_type='com.maxflow.scene.UniversalObjectNode')
        node_menu.add_command('⚙️ Edit Modifier in Max', self.action_jump_to_panel, node_type='com.maxflow.modifier.ModifierNode')
        node_menu.add_command('✂️ Extract / Bypass Node', self.action_extract_node, node_type='com.maxflow.modifier.ModifierNode')

    def action_get_scene_object(self):
        pos = self.graph.viewer().scene_cursor_pos()
        self.graph.create_node('com.maxflow.scene.UniversalObjectNode', pos=[pos.x(), pos.y()])

    def action_create_modifier(self):
        pos = self.graph.viewer().scene_cursor_pos()
        self.graph.create_node('com.maxflow.modifier.ModifierNode', pos=[pos.x(), pos.y()])

    def action_pick_object(self):
        selected_nodes = self.graph.selected_nodes()
        if selected_nodes and hasattr(selected_nodes[0], 'run_picker'):
            selected_nodes[0].run_picker()

    def action_jump_to_panel(self):
        selected_nodes = self.graph.selected_nodes()
        if selected_nodes and hasattr(selected_nodes[0], 'jump_to_max_panel'):
            selected_nodes[0].jump_to_max_panel()

    def action_delete_selected(self):
        nodes = self.graph.selected_nodes()
        if nodes:
            self.graph.delete_nodes(nodes)
            self.live_update(from_viewport=False)

    def action_extract_node(self):
        selected = self.graph.selected_nodes()
        if not selected: return
        for node in selected:
            in_port = node.get_input('obj_in')
            out_port = node.get_output('obj_out')
            if not in_port or not out_port: continue
            prev_port = in_port.connected_ports()[0] if in_port.connected_ports() else None
            next_ports = out_port.connected_ports() if out_port.connected_ports() else []
            in_port.clear_connections()
            out_port.clear_connections()
            if prev_port and next_ports:
                for np in next_ports: prev_port.connect_to(np)
        self.live_update(from_viewport=False)

    def enterEvent(self, event):
        pymxs.runtime.enableAccelerators = False
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        pymxs.runtime.enableAccelerators = True
        super().leaveEvent(event)

    def on_max_scene_changed(self, *args, **kwargs):
        GraphEvaluator.evaluate_graph(self.graph, from_viewport=True)

    def live_update(self, from_viewport=False, *args, **kwargs):
        """ Evaluator """
        GraphEvaluator.evaluate_graph(self.graph, from_viewport=from_viewport)