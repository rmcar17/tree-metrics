import random
from math import factorial

import matplotlib.pyplot as plt
from cogent3 import TreeNode, make_tree
import numpy as np


def _generate_tree(taxa: int) -> TreeNode:
    tree_builder = [f"t{i}" for i in range(taxa)]
    while len(tree_builder) > 1:
        tree_builder.append(
            (
                tree_builder.pop(random.randrange(len(tree_builder))),
                tree_builder.pop(random.randrange(len(tree_builder))),
            )
        )
    return make_tree(str(tree_builder[0])).sorted()


def number_of_rooted_trees(taxa: int) -> int:
    return factorial(2 * taxa - 3) // ((2 ** (taxa - 2)) * factorial(taxa - 2))


def experiment(taxa, trials):
    counts = {}
    for i in range(trials):
        print(f"\rIter {i + 1}/{trials}", end="")
        tree_str = _generate_tree(taxa).get_newick()
        counts[tree_str] = counts.get(tree_str, 0) + 1
    print()

    total_possibilities = number_of_rooted_trees(taxa)
    print(f"Total Trees: {total_possibilities}")
    bar_heights = np.zeros(total_possibilities)

    bar_heights[: len(counts)] = np.array(sorted(list(counts.values())))
    plt.bar(np.arange(total_possibilities), bar_heights)
    plt.savefig("tree_distribution.pdf")

    most_frequent = max(counts, key=lambda x: counts[x])
    least_frequent = min(counts, key=lambda x: counts[x])
    print(f"Most frequent: {counts[most_frequent]} - {most_frequent}")
    print(f"Least frequent: {counts[least_frequent]} - {least_frequent}")
    print(f"Expected: {trials / total_possibilities}")


if __name__ == "__main__":
    experiment(6, 1000000)
