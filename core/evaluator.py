# core/evaluator.py
from nodes.scene_nodes import UniversalObjectNode
from nodes.modifier_nodes import ModifierNode

class GraphEvaluator:
    _is_updating = False

    @classmethod
    def evaluate_graph(cls, graph, from_viewport=False):
        
        if cls._is_updating: return
        cls._is_updating = True
        try:
            for node in graph.all_nodes():
                if isinstance(node, UniversalObjectNode) or isinstance(node, ModifierNode):
                    try: node.evaluate(from_viewport=from_viewport)
                    except: pass
        finally:
            cls._is_updating = False