from glob import glob
import pandas as pd

from constants import DATA_DIR

class Node:
    def __init__(self, method, depth):
        self.method = method
        self.depth = depth
        self.children = []
        self.parents = []
    
    def add_child(self, child):
        self.children.append(child)
    
    def add_parent(self, parent):
        self.parents.append(parent)
    
    def __str__(self):
        str = self.method + " "
        for c in self.children:
            str += c.__str__() + " "
        return str

def build_call_tree (call_graph, entry_method, max_depth = 5):
    def callee_helper(method, depth, ancestors):
        n = Node(method+"_"+str(depth), depth)
        if depth < max_depth:
            ancestors.append(n.method.split("_")[0])
            for c in [c[1] for c in call_graph if c[0] == method and c[1] not in ancestors]:
                c_node = callee_helper(c, depth+1, ancestors)
                n.add_child(c_node)
                c_node.add_parent(n)
        return n
    
    root = callee_helper(entry_method, 0, [])

    return root

def read_call_graph(full_method_name, up=False):
    method_name = full_method_name.split(":")[1].split("(")[0]
    f = open(f'{DATA_DIR}/call_graphs/callers_{method_name}_call_graph.txt', 'r') if up else \
        open(f'{DATA_DIR}/call_graphs/callees_{method_name}_call_graph.txt', 'r')
    edges = []
    visited = {}
    parent_methods = {0 : full_method_name}
    for l in f.readlines():
        num_indents = (len(l) - len(l.lstrip()))/4
        if num_indents < 5:
            l = l.lstrip().split(")")[0].replace(".", ":") + ")"
            parent_methods[num_indents+1] = l
            if parent_methods[num_indents] not in visited.keys() or \
                l not in visited[parent_methods[num_indents]]:
                edges.append([parent_methods[num_indents], l])
                if parent_methods[num_indents] in visited:
                    visited[parent_methods[num_indents]].append(l)
                else:
                    visited[parent_methods[num_indents]] = [l]
    f.close()
    if len(edges) == 0:
        return [[full_method_name, full_method_name]]
    return edges