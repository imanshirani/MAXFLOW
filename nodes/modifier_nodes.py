# nodes/modifier_nodes.py
from nodes.base_node import MaxFlowBaseNode
from core.style_config import NodeColors
from NodeGraphQt import NodeBaseWidget
from PySide6 import QtWidgets, QtCore
import pymxs

def get_max_modifiers():
    import pymxs
    try:
        mod_classes = pymxs.runtime.modifier.classes
        return sorted([str(m) for m in mod_classes])
    except:
        return ['Bend', 'Taper', 'Twist', 'TurboSmooth']

DYNAMIC_MODIFIERS = get_max_modifiers()

# =========================================================
# Coustom UI WIDGET for FlatPropertyRow
# =========================================================
class FlatPropertyRow(NodeBaseWidget):
    def __init__(self, parent=None, name='', category='', label='', val=0.0, dtype='float'):
        super(FlatPropertyRow, self).__init__(parent, name)
        self.set_label('')
        
        w = QtWidgets.QWidget()
        w.setFixedHeight(20) 
        
        layout = QtWidgets.QHBoxLayout(w)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(2) 
        layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        
        # Category Label ([MOD])
        if category:
            cat_lbl = QtWidgets.QLabel(category)
            # Color: #b388ff for modifier
            cat_lbl.setStyleSheet("color: #b388ff; font-weight: bold; font-size: 10px;")
            cat_lbl.setFixedWidth(35)
            layout.addWidget(cat_lbl)
        else:
            spacer = QtWidgets.QLabel("")
            spacer.setFixedWidth(35)
            layout.addWidget(spacer)
            
        # Lablel Parameter
        lbl = QtWidgets.QLabel(label)
        lbl.setStyleSheet("color: #ccc; font-weight: bold;")
        lbl.setFixedWidth(80 if len(label) > 3 else 20)
        layout.addWidget(lbl)
        
        # Number Box
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
                padding: 1px;
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


class ModifierSearchDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, current_mod=""):
        super().__init__(parent)
        self.setWindowTitle("Search Modifier")
        self.resize(300, 420)
        self.selected_modifier = None
        self.wants_advanced = False

        layout = QtWidgets.QVBoxLayout(self)

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Type to search...")
        layout.addWidget(self.search_bar)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.addItems(DYNAMIC_MODIFIERS)
        layout.addWidget(self.list_widget)
        
        self.chk_advanced = QtWidgets.QCheckBox("➕ Show Advanced Parameters")
        layout.addWidget(self.chk_advanced)
        
        self.btn_ok = QtWidgets.QPushButton("Apply")
        layout.addWidget(self.btn_ok)

        self.search_bar.textChanged.connect(self.filter_list)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        self.btn_ok.clicked.connect(self.accept_selection)

    def filter_list(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def accept_selection(self):
        item = self.list_widget.currentItem()
        if item:
            self.selected_modifier = item.text()
            self.wants_advanced = self.chk_advanced.isChecked()
            self.accept()


# =========================================================
# Modifier Node
# =========================================================
class ModifierNode(MaxFlowBaseNode):
    __identifier__ = 'com.maxflow.modifier'
    NODE_NAME = 'Double-Click to Assign'

    def __init__(self):
        super(ModifierNode, self).__init__()
        self.set_color(*NodeColors.HEADER_MODIFIER) 
        self.add_input('obj_in', color=NodeColors.PORT_OBJECT) 
        self.create_property('mod_type', 'None')
        self.add_output('obj_out', color=NodeColors.PORT_OBJECT) 

    def generate_dynamic_ports(self, mod_type, show_advanced=False):
        rt = pymxs.runtime
        if mod_type == 'None' or not mod_type: return
        JUNK_PROPS = [
            'gizmo', 'center', 'limit', 'upperlimit', 'lowerlimit', 'enabled',
            'fromto', 'bendfrom', 'bendto', 'bendaxis', 'axis', 'limits',
            'smooth', 'mapchannel', 'usechannel', 'keep_faces_together', 'materials'
        ]
        try:
            temp_mod = getattr(rt, mod_type)()
            props = rt.getPropNames(temp_mod)
            valid_props = []
            for prop in props:
                p_name = str(prop)
                if not show_advanced and p_name.lower() in JUNK_PROPS: continue
                try:
                    val = rt.getProperty(temp_mod, p_name)
                    if type(val) in [float, int, bool, str]: valid_props.append((p_name, val))
                except: pass

            for i, (p_name, val) in enumerate(valid_props): 
                dtype = 'bool' if isinstance(val, bool) else ('int' if isinstance(val, int) else 'float')
                port_color = NodeColors.PORT_BOOL if dtype == 'bool' else (NodeColors.PORT_INT if dtype == 'int' else NodeColors.PORT_FLOAT)
                
                cat_display = '[MOD]' if i == 0 else '' 
                row = FlatPropertyRow(self.view, name=f"val_{p_name}", category=cat_display, label=f"{p_name}:", val=val, dtype=dtype)
                self.add_custom_widget(row)
                self.add_input(p_name, color=port_color)

            self.view.draw_node()
        except Exception as e: print(f"MAXFLOW > Error: {e}")

    def evaluate(self, from_viewport=False):
        rt = pymxs.runtime
        in_port = self.get_input('obj_in')
        
        if in_port and in_port.connected_ports():
            connected_node = in_port.connected_ports()[0].node()
            
            if connected_node.__identifier__ in ['com.maxflow.scene', 'com.maxflow.modifier']:
                obj_name = connected_node.evaluate(from_viewport=from_viewport)
            else:
                obj_name = connected_node.evaluate() 
            
            if obj_name:
                max_obj = rt.getNodeByName(obj_name)
                if max_obj:
                    current_mod_type = self.get_property('mod_type')
                    if current_mod_type == 'None': return obj_name

                    tag = f"[MF-{self.id[-4:]}]"
                    expected_full_name = f"{current_mod_type} {tag}"
                    
                    existing_mod = None
                    for mod in max_obj.modifiers:
                        if tag in mod.name:
                            existing_mod = mod
                            break
                    
                    if not existing_mod:
                        try:
                            mod_command = getattr(rt, current_mod_type)()
                            mod_command.name = expected_full_name 
                            rt.addModifier(max_obj, mod_command)
                            existing_mod = max_obj.modifiers[0] 
                        except Exception: pass
                    
                    if existing_mod:
                        for port_name, port in self.inputs().items():
                            if port_name == 'obj_in': continue
                            
                            val = None
                            if port.connected_ports():
                                val_node = port.connected_ports()[0].node()
                                val = val_node.evaluate()
                            else:
                                if from_viewport: continue 
                                
                                val = self.get_property(f"val_{port_name}")

                            if val is not None:
                                try:
                                    if rt.getProperty(existing_mod, port_name) != val:
                                        rt.setProperty(existing_mod, port_name, val)
                                except: pass
                return obj_name
        return None

    def jump_to_max_panel(self):
        rt = pymxs.runtime
        in_port = self.get_input('obj_in')
        if not in_port or not in_port.connected_ports(): return
        connected_node = in_port.connected_ports()[0].node()
        obj_name = connected_node.evaluate()
        if not obj_name: return
        max_obj = rt.getNodeByName(obj_name)
        if not max_obj: return
        rt.select(max_obj)
        rt.execute('max modify mode') 
        tag = f"[MF-{self.id[-4:]}]"
        for mod in max_obj.modifiers:
            if tag in mod.name:
                rt.modPanel.setCurrentObject(mod)
                break

    def edit_value(self):
        current_mod = self.get_property('mod_type')
        if current_mod == 'None':
            import qtmax
            dialog = ModifierSearchDialog(parent=qtmax.GetQMaxMainWindow(), current_mod=current_mod)
            if dialog.exec_():
                new_mod = dialog.selected_modifier
                show_adv = dialog.wants_advanced
                if new_mod:
                    self.set_property('mod_type', new_mod)
                    self.set_name(f"{new_mod} Modifier")
                    self.generate_dynamic_ports(new_mod, show_advanced=show_adv)
                    self.evaluate(from_viewport=False)
                    self.jump_to_max_panel()
        else:
            self.jump_to_max_panel()