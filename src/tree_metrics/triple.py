import math
import random
from dataclasses import dataclass

import matplotlib.pyplot as plt
from cogent3 import TreeNode, make_tree


def triple_similarity(tree1: TreeNode, tree2: TreeNode) -> float:
    triples_1 = make_triples(tree1)
    triples_2 = make_triples(tree2)

    assert len(triples_1) == len(triples_2)

    return len(triples_1.intersection(triples_2)) / len(triples_1)


@dataclass(frozen=True)
class Triple:
    outgroup: str
    ingroup: tuple[str, str]

    def __post_init__(self):
        object.__setattr__(self, "ingroup", tuple(sorted(self.ingroup)))

    def __repr__(self) -> str:
        return f"({self.outgroup},({self.ingroup[0]},{self.ingroup[1]}));"


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
