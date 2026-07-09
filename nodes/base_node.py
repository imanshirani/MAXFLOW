# nodes/base_node.py
from NodeGraphQt import BaseNode

class MaxFlowBaseNode(BaseNode):
    """MAXFLOW Core Node Base Class"""
    
    __identifier__ = 'com.maxflow.nodes'

    def __init__(self):
        BaseNode.__init__(self)
        
    def evaluate(self):
        #for next version
        pass