# nodes/math_nodes.py
from nodes.base_node import MaxFlowBaseNode
from core.style_config import NodeColors
from NodeGraphQt import NodeBaseWidget
from PySide6 import QtWidgets, QtCore
import math

# =========================================================
# CoustomUI Widgets
# =========================================================

# 1. Slider (Float)
class CustomFloatSliderUI(QtWidgets.QWidget):
    value_changed = QtCore.Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal { border-radius: 4px; height: 8px; background: #222; }
            QSlider::handle:horizontal { background: #00C896; width: 14px; margin: -3px 0; border-radius: 7px; }
        """)
        
        self.spin = QtWidgets.QDoubleSpinBox()
        self.spin.setRange(0, 1000)
        self.spin.setSingleStep(0.5)
        self.spin.setStyleSheet("background: #1e1e1e; color: #eee; border: 1px solid #333; border-radius: 4px; padding: 2px;")
        self.spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        
        layout.addWidget(self.slider, stretch=2)
        layout.addWidget(self.spin, stretch=1)
        
        self.slider.valueChanged.connect(self.on_slider)
        self.spin.valueChanged.connect(self.on_spin)
        
    def on_slider(self, val):
        self.spin.blockSignals(True)
        self.spin.setValue(val / 10.0)
        self.spin.blockSignals(False)
        self.value_changed.emit(self.spin.value())
        
    def on_spin(self, val):
        self.slider.blockSignals(True)
        self.slider.setValue(int(val * 10))
        self.slider.blockSignals(False)
        self.value_changed.emit(val)

class NodeFloatSliderWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NodeFloatSliderWidget, self).__init__(parent)
        self.set_name('custom_float')
        self.set_label('Value:')
        self.custom_ui = CustomFloatSliderUI()
        self.set_custom_widget(self.custom_ui)
        self.custom_ui.value_changed.connect(lambda val: self.value_changed.emit(self.get_name(), val))

    def get_value(self): return self.custom_ui.spin.value()
    def set_value(self, val): self.custom_ui.spin.setValue(float(val))


# 2. Slider (Integer)
class CustomIntSliderUI(QtWidgets.QWidget):
    value_changed = QtCore.Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 100) 
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal { border-radius: 4px; height: 8px; background: #222; }
            QSlider::handle:horizontal { background: #00C896; width: 14px; margin: -3px 0; border-radius: 7px; }
        """)
        
        # QSpinBox 
        self.spin = QtWidgets.QSpinBox()
        self.spin.setRange(0, 100)
        self.spin.setSingleStep(1)
        self.spin.setStyleSheet("background: #1e1e1e; color: #eee; border: 1px solid #333; border-radius: 4px; padding: 2px;")
        self.spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        
        layout.addWidget(self.slider, stretch=2)
        layout.addWidget(self.spin, stretch=1)
        
        self.slider.valueChanged.connect(self.on_slider)
        self.spin.valueChanged.connect(self.on_spin)
        
    def on_slider(self, val):
        self.spin.blockSignals(True)
        self.spin.setValue(val)
        self.spin.blockSignals(False)
        self.value_changed.emit(self.spin.value())
        
    def on_spin(self, val):
        self.slider.blockSignals(True)
        self.slider.setValue(val)
        self.slider.blockSignals(False)
        self.value_changed.emit(val)

class NodeIntSliderWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NodeIntSliderWidget, self).__init__(parent)
        self.set_name('custom_int')
        self.set_label('Value:')
        self.custom_ui = CustomIntSliderUI()
        self.set_custom_widget(self.custom_ui)
        self.custom_ui.value_changed.connect(lambda val: self.value_changed.emit(self.get_name(), val))

    def get_value(self): return self.custom_ui.spin.value()
    def set_value(self, val): self.custom_ui.spin.setValue(int(val))


# =========================================================
# MATH NODES
# =========================================================

class FloatNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.input'
    NODE_NAME = 'Float'

    def __init__(self):
        super(FloatNode, self).__init__()
        self.set_color(*NodeColors.HEADER_INPUT)

    
        self.slider_widget = NodeFloatSliderWidget(self.view)
        self.add_custom_widget(self.slider_widget)
        self.add_output('out', color=NodeColors.PORT_FLOAT)

    def evaluate(self):
        try: return float(self.get_property('custom_float'))
        except: return 0.0


class IntNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.input'
    NODE_NAME = 'Integer'

    def __init__(self):
        super(IntNode, self).__init__()
        self.set_color(*NodeColors.HEADER_INPUT)
        
        
        self.slider_widget = NodeIntSliderWidget(self.view)
        self.add_custom_widget(self.slider_widget)
        self.add_output('out', color=NodeColors.PORT_INT) 

    def evaluate(self):
        try: return int(self.get_property('custom_int')) 
        except: return 0


class BoolNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.input'
    NODE_NAME = 'Boolean'

    def __init__(self):
        super(BoolNode, self).__init__()
        self.set_color(*NodeColors.HEADER_INPUT)
        self.add_checkbox('value', 'True / False', text='', state=False)
        self.add_output('out', color=NodeColors.PORT_BOOL) 

    def evaluate(self):
        return bool(self.get_property('value'))


class StringNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.input'
    NODE_NAME = 'String'

    def __init__(self):
        super(StringNode, self).__init__()
        self.set_color(*NodeColors.HEADER_INPUT)
        self.add_text_input('value', '', text='...')
        self.add_output('out', color=NodeColors.PORT_STRING) 

    def evaluate(self):
        return str(self.get_property('value'))


class AxisNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.input'
    NODE_NAME = 'Axis'

    def __init__(self):
        super(AxisNode, self).__init__()
        self.set_color(*NodeColors.HEADER_INPUT)
        self.add_combo_menu('axis', 'Axis', items=['X', 'Y', 'Z'])
        self.add_output('out', color=NodeColors.PORT_INT)

    def evaluate(self):
        val = self.get_property('axis')
        if val == 'X': return 0
        elif val == 'Y': return 1
        elif val == 'Z': return 2
        return 0


class MathOperatorNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.math'
    NODE_NAME = 'Math Operator'

    def __init__(self):
        super(MathOperatorNode, self).__init__()
        self.set_color(*NodeColors.HEADER_MATH)
        
        self.add_input('A', color=NodeColors.PORT_FLOAT)
        self.add_input('B', color=NodeColors.PORT_FLOAT)
        
        ops = [
            'Add (+)', 'Subtract (-)', 'Multiply (*)', 'Divide (/)',
            'Power (A^B)', 'Modulo (A%B)', 
            'Minimum', 'Maximum',
            'Sine (sin A)', 'Cosine (cos A)'
        ]
        self.add_combo_menu('operator', '', items=ops)
        self.add_output('out', color=NodeColors.PORT_FLOAT)

    def evaluate(self):
        port_a = self.get_input('A')
        val_a = 0.0
        if port_a and port_a.connected_ports():
            val = port_a.connected_ports()[0].node().evaluate()
            if val is not None: val_a = val

        port_b = self.get_input('B')
        val_b = 0.0
        if port_b and port_b.connected_ports():
            val = port_b.connected_ports()[0].node().evaluate()
            if val is not None: val_b = val

        op = self.get_property('operator')
        try:
            a, b = float(val_a), float(val_b)
            if op == 'Add (+)': return a + b
            elif op == 'Subtract (-)': return a - b
            elif op == 'Multiply (*)': return a * b
            elif op == 'Divide (/)': return a / b if b != 0 else 0.0
            elif op == 'Power (A^B)': return math.pow(a, b)
            elif op == 'Modulo (A%B)': return a % b if b != 0 else 0.0
            elif op == 'Minimum': return min(a, b)
            elif op == 'Maximum': return max(a, b)
            elif op == 'Sine (sin A)': return math.sin(math.radians(a)) 
            elif op == 'Cosine (cos A)': return math.cos(math.radians(a))
        except Exception:
            return 0.0
        return 0.0