import math
import random
from dataclasses import dataclass

import matplotlib.pyplot as plt
from cogent3 import TreeNode, make_tree


@dataclass(frozen=True)
class Triple:
    outgroup: str
    ingroup: tuple[str, str]

    def __post_init__(self):
        object.__setattr__(self, "ingroup", tuple(sorted(self.ingroup)))

    def __repr__(self) -> str:
        return f"({self.outgroup},({self.ingroup[0]},{self.ingroup[1]}));"


def tree_triple_similarity(tree_1: TreeNode, tree_2: TreeNode) -> float:
    triples_1 = make_triples(tree_1)
    triples_2 = make_triples(tree_2)

    return triple_similarity(triples_1, triples_2)


def optimise_tree_triple_similarity(fixed: TreeNode, rerootable: TreeNode) -> float:
    triples_fixed = make_triples(fixed)
    best_similarity = -1

    node: TreeNode
    for node in list(rerootable.traverse(include_self=False)):
        prospective_tree = root_at_node(node)
        similarity = triple_similarity(triples_fixed, make_triples(prospective_tree))
        # print(fixed)
        # print(prospective_tree)
        # print(similarity)
        # print()
        if similarity == 1.0:
            return similarity
        best_similarity = max(best_similarity, similarity)
    assert best_similarity > 0
    return best_similarity


def root_at_node(node: TreeNode) -> TreeNode:
    # Roots at edge connecting the node to its parent
    if node.parent is None:
        return node
    if node.parent.parent is None:
        return node.parent

    tree_tuple = (
        _root_at_node_helper(node.parent, node),
        _root_at_node_helper(node, node.parent),
    )
    return make_tree(str(tree_tuple))


def _root_at_node_helper(node: TreeNode, banned=None) -> tuple | str:
    if node.is_tip():
        return node.name

    tree_components = []
    for neighbour in node._getNeighboursExcept(banned):
        component = _root_at_node_helper(neighbour, banned=node)
        if isinstance(component, tuple) and len(component) == 1:
            # Happens when crossing the root
            component = component[0]
        tree_components.append(component)

    return tuple(tree_components)


def triple_similarity(triples_1: set[Triple], triples_2: set[Triple]) -> float:
    assert len(triples_1) == len(triples_2)
    return len(triples_1.intersection(triples_2)) / len(triples_1)


def make_triples(tree: TreeNode) -> set[Triple]:
    triples = set()

    taxa_set = set(tree.get_tip_names())

    for node in tree.postorder(include_self=False):
        if node.is_tip():
            node.params["descendants"] = [node.name]
        else:
            ingroup_taxa = []
            for child in node:
                ingroup_taxa.extend(child.params["descendants"])
                del child.params["descendants"]

            other_set = taxa_set.difference(ingroup_taxa)
            for outgroup in other_set:
                for i in range(1, len(ingroup_taxa)):
                    for j in range(i):
                        triples.add(
                            Triple(
                                outgroup, frozenset((ingroup_taxa[i], ingroup_taxa[j]))
                            )
                        )

            node.params["descendants"] = ingroup_taxa

    for child in tree:
        del child.params["descendants"]

    return triples


def _generate_tree(taxa: int) -> TreeNode:
    tree_builder = [f"t{i}" for i in range(taxa)]
    while len(tree_builder) > 1:
        tree_builder.append(
            (
                tree_builder.pop(random.randrange(len(tree_builder))),
                tree_builder.pop(random.randrange(len(tree_builder))),
            )
        )
    return make_tree(str(tree_builder[0]))


if __name__ == "__main__":
    trials = 100000
    results = []
    taxa = 10
    for _ in range(trials):
        trees = [_generate_tree(taxa) for _ in range(2)]
        results.append(triple_similarity(*trees))

    # There are (taxa choose 3) triples. Add 1 to include 0/possibilities results for similarity
    possibilities = math.comb(taxa, 3) + 1
    # print(results)

    plt.hist(
        results,
        bins=[
            i / (possibilities - 1) - (0.5 / (possibilities - 1))
            for i in range(possibilities + 1)
        ],
        density=True,
        width=1 / (1.2 * possibilities),
    )
    print(
        [
            i / (possibilities - 1) - (0.5 / (possibilities - 1))
            for i in range(possibilities + 1)
        ]
    )
    plt.xlabel("Similarity")
    plt.title(f"Distribution of triple similarity {taxa=}")
    plt.savefig("similarity.pdf")
    plt.close()
