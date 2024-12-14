from typing import List
import random


def gen_distinct_labels(num_labels: int) -> List[int]:
    assert num_labels > 0 and num_labels <= 10000
    labels = set()
    while len(labels) < num_labels:
        new_label = random.randint(0, 2147483647)
        labels.add(new_label)
    return list(labels)

def gen_random_identifier() -> str:
    # Generate a random legal identifier using hash
    random_bytes = random.randbytes(16)
    hash_hex = hex(hash(random_bytes))[5:17] # Take 12 chars from hash
    # Ensure first char is letter/underscore
    first_char = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return first_char + hash_hex
