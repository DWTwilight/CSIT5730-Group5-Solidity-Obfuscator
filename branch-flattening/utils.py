from typing import List
import random

def gen_dintinct_labels(num_labels: int) -> List[int]:
    assert num_labels > 0 and num_labels <= 10000
    labels = set()
    while len(labels) < num_labels:
        new_label = random.randint(0, 1000000)
        labels.add(new_label)
    return list(labels)