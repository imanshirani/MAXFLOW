# core/max_utils.py
import pymxs

def get_max_modifiers():
    """Get a list of all modifiers in MAX."""
    try:
        mod_classes = pymxs.runtime.modifier.classes
        return sorted([str(m) for m in mod_classes])
    except:
        return ['Bend', 'Taper', 'Twist', 'TurboSmooth']

def cleanup_modifiers(obj_name, active_tags):
    """ Clean up modifiers that have been removed from the graph. """
    rt = pymxs.runtime
    max_obj = rt.getNodeByName(obj_name)
    if not max_obj: return
    
    mods_to_delete = []
    for i in range(max_obj.modifiers.count):
        mod = max_obj.modifiers[i]
        if "[MF-" in mod.name:
            is_active = any(tag in mod.name for tag in active_tags)
            if not is_active: mods_to_delete.append(mod)
            
    for mod in mods_to_delete:
        try: rt.deleteModifier(max_obj, mod)
        except: pass

def set_property_safe(obj_name, prop_name, val):
    """ edit a property in MAX """
    rt = pymxs.runtime
    max_obj = rt.getNodeByName(obj_name)
    if not max_obj: return False
    
    if '.' not in prop_name:
        try:
            curr_val = rt.getProperty(max_obj, prop_name)
            if curr_val != val: rt.setProperty(max_obj, prop_name, val)
            return True
        except: pass
    else:
        try:
            curr_val = rt.execute(f"$'{obj_name}'.{prop_name}")
            needs_update = False
            if type(curr_val) in [float, int] and type(val) in [float, int]:
                if abs(float(curr_val) - float(val)) > 0.001: needs_update = True
            elif str(curr_val) != str(val):
                needs_update = True
                
            if needs_update:
                rt.execute(f"$'{obj_name}'.{port_name} = {val}")
                return True
        except Exception: pass
    return False

def get_property_safe(obj_name, prop_name):
    """ Get a property from MAX """
    rt = pymxs.runtime
    max_obj = rt.getNodeByName(obj_name)
    if not max_obj: return 0.0
    try:
        val = max_obj
        for attr in prop_name.split('.'):
            val = getattr(val, attr)
        return float(val)
    except: return 0.0