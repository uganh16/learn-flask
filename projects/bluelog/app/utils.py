import random


def random_split(n, k):
    if n < 0 or k <= 0:
        return []

    if k == 1:
        return [n]

    indices = [0] + sorted(random.sample(range(n + k), k - 1)) + [n + k]

    return [indices[i+1]-indices[i]-1 for i in range(len(indices) - 1)]
