# nodes/scene_nodes.py
from nodes.base_node import MaxFlowBaseNode
from core.style_config import NodeColors
from NodeGraphQt import NodeBaseWidget
from PySide6 import QtWidgets, QtCore
import pymxs

# =========================================================
# CoustomUI Widgets left-aligned
# =========================================================
class FlatTextRow(NodeBaseWidget):
    
    def __init__(self, parent=None, name='', category='', label='', text=''):
        super(FlatTextRow, self).__init__(parent, name)
        self.set_label('')
        
        w = QtWidgets.QWidget()
        w.setFixedHeight(20) 
        
        layout = QtWidgets.QHBoxLayout(w)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(2)
        layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        
        # Category Label ([EXT] mean Extract)
        if category:
            cat_lbl = QtWidgets.QLabel(category)
            # Gold colore for Extract
            cat_lbl.setStyleSheet("color: #e6a822; font-weight: bold; font-size: 10px;")
            cat_lbl.setFixedWidth(35)
            layout.addWidget(cat_lbl)
        else:
            spacer = QtWidgets.QLabel("")
            spacer.setFixedWidth(35)
            layout.addWidget(spacer)
            
        lbl = QtWidgets.QLabel(label)
        lbl.setStyleSheet("color: #ccc; font-weight: bold;")
        lbl.setFixedWidth(60)
        layout.addWidget(lbl)
        
        
        self.ui_widget = QtWidgets.QLineEdit(text)
        self.ui_widget.setStyleSheet("""
            background: #181818; 
            color: #eee; 
            border: 1px solid #333; 
            border-radius: 2px; 
            padding: 1px 4px;
        """)
        self.ui_widget.setFixedWidth(80)
        self.ui_widget.textChanged.connect(lambda v: self.value_changed.emit(self.get_name(), v))
        
        layout.addWidget(self.ui_widget)
        self.set_custom_widget(w)

    def get_value(self):
        return self.ui_widget.text()

    def set_value(self, val):
        self.ui_widget.blockSignals(True)
        self.ui_widget.setText(str(val))
        self.ui_widget.blockSignals(False)

class FlatPropertyRow(NodeBaseWidget):
    def __init__(self, parent=None, name='', category='', label='', val=0.0, dtype='float'):
        super(FlatPropertyRow, self).__init__(parent, name)
        self.set_label('')
        
        w = QtWidgets.QWidget()
        #NodeGraphQt
        w.setFixedHeight(20) 
        
        layout = QtWidgets.QHBoxLayout(w)
        layout.setContentsMargins(1, 0, 1, 0)
        layout.setSpacing(5)
        
        layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        
        # 1. Category Label (POS or ROT)
        if category:
            cat_lbl = QtWidgets.QLabel(category)
            cat_lbl.setStyleSheet("color: #00C896; font-weight: bold; font-size: 10px;")
            cat_lbl.setFixedWidth(35)
            layout.addWidget(cat_lbl)
        else:
            spacer = QtWidgets.QLabel("")
            spacer.setFixedWidth(35)
            layout.addWidget(spacer)
            
        # 2.Label Parameter (X or length)
        lbl = QtWidgets.QLabel(label)
        lbl.setStyleSheet("color: #ccc; font-weight: bold;")
        
        lbl.setFixedWidth(120 if len(label) > 3 else 20)
        layout.addWidget(lbl)
        
        # 3. value
        if dtype == 'bool':
            self.ui_widget = QtWidgets.QCheckBox()
            self.ui_widget.setChecked(bool(val))
            self.ui_widget.toggled.connect(lambda v: self.value_changed.emit(self.get_name(), v))
        else:
            if dtype == 'int':
                self.ui_widget = QtWidgets.QSpinBox()
                self.ui_widget.setRange(-999999, 999999)
                self.ui_widget.setValue(int(val))
            else:
                self.ui_widget = QtWidgets.QDoubleSpinBox()
                self.ui_widget.setRange(-999999.0, 999999.0)
                self.ui_widget.setDecimals(3)
                self.ui_widget.setValue(float(val))
                
            self.ui_widget.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
            self.ui_widget.setStyleSheet("""
                background: #181818; 
                color: #eee; 
                border: 1px solid #333; 
                border-radius: 2px; 
                padding: 2px;
            """)
            self.ui_widget.setFixedWidth(70) 
            self.ui_widget.valueChanged.connect(lambda v: self.value_changed.emit(self.get_name(), v))
            
        layout.addWidget(self.ui_widget)
        self.set_custom_widget(w)

    def get_value(self):
        if isinstance(self.ui_widget, QtWidgets.QCheckBox): return self.ui_widget.isChecked()
        return self.ui_widget.value()

    def set_value(self, val):
        self.ui_widget.blockSignals(True)
        if isinstance(self.ui_widget, QtWidgets.QCheckBox): self.ui_widget.setChecked(bool(val))
        else: self.ui_widget.setValue(val)
        self.ui_widget.blockSignals(False)


# =========================================================
# Secene Node Or Unicerasl object Node
# =========================================================
class UniversalObjectNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.scene'
    NODE_NAME = 'Scene Object [Unlinked]'

    def __init__(self):
        super(UniversalObjectNode, self).__init__()
        self.set_color(*NodeColors.HEADER_SCENE)
        self.create_property('obj_name', '')
        self.add_output('obj_out', color=NodeColors.PORT_OBJECT) 

    def run_picker(self):
        rt = pymxs.runtime
        current_obj = self.get_property('obj_name')
        if current_obj:
            max_obj = rt.getNodeByName(current_obj)
            if max_obj: rt.select(max_obj)
            return

        sel = rt.selection
        if len(sel) > 0:
            picked_name = sel[0].name
            self.set_property('obj_name', picked_name)
            self.set_name(f"Object: {picked_name}")
            self.generate_dynamic_ui(picked_name)
            print(f"MAXFLOW > Linked to: {picked_name}")
        else: print("MAXFLOW > Please select an object in Max first!")

    def generate_dynamic_ui(self, obj_name):
        rt = pymxs.runtime
        max_obj = rt.getNodeByName(obj_name)
        if not max_obj: return

        # 1. Position 
        self._add_flat_row('[POS]', max_obj.pos, ['pos.x', 'pos.y', 'pos.z'])

        # 2. Rotation
        try: euler_rot = rt.toEuler(max_obj.rotation)
        except: euler_rot = max_obj.rotation
        self._add_flat_row('[ROT]', euler_rot, ['rotation.x_rotation', 'rotation.y_rotation', 'rotation.z_rotation'])

        # 3. Scale
        self._add_flat_row('[SCL]', max_obj.scale, ['scale.x', 'scale.y', 'scale.z'])

        # 4. Base Object
        props = rt.getPropNames(max_obj)
        valid_props = []
        JUNK_PROPS = ['enabled', 'gizmo', 'center', 'limit']
        for prop in props:
            p_name = str(prop)
            if p_name.lower() in JUNK_PROPS: continue
            try:
                val = rt.getProperty(max_obj, p_name)
                if type(val) in [float, int, bool]: valid_props.append((p_name, val))
            except: pass
        
        if valid_props:
            for i, (p_name, val) in enumerate(valid_props):
                dtype = 'bool' if isinstance(val, bool) else ('int' if isinstance(val, int) else 'float')
                port_color = NodeColors.PORT_BOOL if dtype == 'bool' else (NodeColors.PORT_INT if dtype == 'int' else NodeColors.PORT_FLOAT)
                
                cat_display = '[OBJ]' if i == 0 else '' 
                row = FlatPropertyRow(self.view, name=f"val_{p_name}", category=cat_display, label=f"{p_name}:", val=val, dtype=dtype)
                self.add_custom_widget(row)
                self.add_input(p_name, color=port_color)

        self.view.draw_node()

    def _add_flat_row(self, category, vector_val, prop_names):
        xyz_labels = ['X:', 'Y:', 'Z:']
        for i, p_name in enumerate(prop_names):
            try: val = getattr(vector_val, ['x', 'y', 'z'][i])
            except: 
                try: val = vector_val[i]
                except: val = 0.0
                
            cat_display = category if i == 0 else ''
            
            row = FlatPropertyRow(self.view, name=f"val_{p_name}", category=cat_display, label=xyz_labels[i], val=float(val), dtype='float')
            self.add_custom_widget(row)
            self.add_input(p_name, color=NodeColors.PORT_VECTOR)

    def evaluate(self, from_viewport=False):
        rt = pymxs.runtime
        obj_name = self.get_property('obj_name')
        if not obj_name: return None
        max_obj = rt.getNodeByName(obj_name)
        if not max_obj or not rt.isValidNode(max_obj): return None

        active_tags = self.get_active_modifier_tags()
        mods_to_delete = []
        for i in range(max_obj.modifiers.count):
            mod = max_obj.modifiers[i]
            if "[MF-" in mod.name:
                is_active = any(tag in mod.name for tag in active_tags)
                if not is_active: mods_to_delete.append(mod)
        for mod in mods_to_delete:
            try: rt.deleteModifier(max_obj, mod)
            except: pass

        input_ports = list(self.inputs().keys())
        for port_name in input_ports:
            port = self.get_input(port_name)
            if not port: continue
            
            val = None
            if port.connected_ports():
                connected_node = port.connected_ports()[0].node()
                val = connected_node.evaluate()
            else:
                if from_viewport: continue 
                val = self.get_property(f"val_{port_name}")

            if val is not None:
                if '.' not in port_name:
                    try:
                        curr_val = rt.getProperty(max_obj, port_name)
                        if curr_val != val: rt.setProperty(max_obj, port_name, val)
                    except: pass
                else:
                    try:
                        curr_val = rt.execute(f"$'{obj_name}'.{port_name}")
                        needs_update = False
                        if type(curr_val) in [float, int] and type(val) in [float, int]:
                            if abs(float(curr_val) - float(val)) > 0.001: needs_update = True
                        elif str(curr_val) != str(val):
                            needs_update = True
                            
                        if needs_update:
                            rt.execute(f"$'{obj_name}'.{port_name} = {val}")
                    except Exception: pass
        return obj_name

    def get_active_modifier_tags(self):
        active_tags = []
        current_port = self.get_output('obj_out')
        while current_port and current_port.connected_ports():
            next_node = current_port.connected_ports()[0].node()
            if next_node.__identifier__ == 'com.maxflow.modifier':
                tag = f"[MF-{next_node.id[-4:]}]"
                active_tags.append(tag)
                current_port = next_node.get_output('obj_out')
            else: break
        return active_tags

# =========================================================
# Extrcate Property Node
# =========================================================
class GetPropertyNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.scene'
    NODE_NAME = 'Get Property'

    def __init__(self):
        super(GetPropertyNode, self).__init__()
        
        self.set_color(*NodeColors.HEADER_EXTRACT)       
        
        self.add_input('obj_in', color=NodeColors.PORT_OBJECT)        
        
        row = FlatTextRow(self.view, name='prop_name', category='[EXT]', label='Property:', text='pos.x')
        self.add_custom_widget(row)
        
        
        self.add_output('val_out', color=NodeColors.PORT_FLOAT)

    def evaluate(self):
        rt = pymxs.runtime
        in_port = self.get_input('obj_in')
        if not in_port or not in_port.connected_ports(): return 0.0
        
        connected_node = in_port.connected_ports()[0].node()
        # evaluate
        obj_name = connected_node.evaluate() 
        if not obj_name: return 0.0
        
        max_obj = rt.getNodeByName(obj_name)
        if not max_obj: return 0.0
        
        try:
            val = max_obj
            prop_path = self.get_property('prop_name')
            if not prop_path: return 0.0
            
            for attr in prop_path.split('.'): 
                val = getattr(val, attr)
            return float(val)
        except Exception: 
            return 0.0