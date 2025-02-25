from tree_metrics.triple import root_at_node
from cogent3 import make_tree


tree = make_tree("(a,((b,c),(d,e)));")
nodes = list(tree.traverse())

for node in nodes:
    print("Node:", node)
    print("Root:", root_at_node(node))
    print()
