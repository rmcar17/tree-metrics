from tree_metrics.triple import root_at_node, optimise_tree_triple_similarity
from cogent3 import make_tree


tree1 = make_tree("(a,((b,c),(d,e)));")
tree2 = make_tree("((a,b),(c,(d,e)));")
tree3 = make_tree("((e,((b,c),a)),d);")

print(optimise_tree_triple_similarity(tree1, tree3))
# nodes = list(tree.traverse())

# for node in nodes:
#     print("Node:", node)
#     print("Root:", root_at_node(node))
#     print()
