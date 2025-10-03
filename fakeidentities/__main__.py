import csv
import os
import sys
from collections import defaultdict, Counter
from time import perf_counter

import pandas as pd

from fakeidentities.first_names import FirstNames
from fakeidentities.match import PureMatch, PhoneticMatch
from fakeidentities.utils import out_data_file

lookup = FirstNames()


def collect_typos(word: str) -> (str, str):
    nearest_neighbour = lookup.nearest_neighbour(word)
    if word:
        return nearest_neighbour, word

if __name__ == '__main__':
    before = perf_counter()
    os.environ['TOKENIZERS_PARALLELISM'] = "true"
    sample_size = 100_000
    seed = 1000
    # print(group_by_name_sorted_desc(random_lastname_sample(100_000, seed)))

    # print(group_by_name_sorted_desc(golden_record_persons(sample_size, seed)))
    middlenames = set()
    unknown = set()
    phonetics = defaultdict(list)
    matches = Counter()
    with open('../data_raw/US.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for i, line in enumerate(reader):
            first_name = line[0]
            if " " in first_name:
                splitt = first_name.split(" ")
                first_name = splitt[0]
                middlenames.add(splitt[1])

            match lookup.matches(first_name):
                case PhoneticMatch(matched):
                    phonetics[matched].append(first_name)
                case PureMatch(matched):
                    matches.update([matched])
                case None:
                    unknown.add(first_name)

#            if len(unknown) > 1_000_000:
#                break
            if i % 1000 == 0:
                sys.stdout.write(f"\r {i}")
                sys.stdout.flush()

    phonetics = { name: Counter(typed) for name, typed in phonetics.items() }
    for name, count in matches.items():
        if name in phonetics:
            phonetics[name].update({name: count})
        else:
            phonetics[name] = Counter({name: count})

    """
    with ProcessPoolExecutor(8) as executor:
        typo_pairs = [res for res in executor.map(collect_typos, unknown) if res is not None]
    
    after = perf_counter()
    print(f"Finished in {after - before}")

    typos = defaultdict(set)
    for intended, typed in typo_pairs:
        if intended is not None:
            typos[intended].add(typed)

    print("-----")
    print("Typos")
    for intended, typed in typos.items():
        print(f"{intended} -> {typed}")

    """
    rows = [
        {"name": name, "alternative_name": alt_name, "occurrences": count}
        for name, alternatives in phonetics.items()
        for alt_name, count in alternatives.items()
    ]

    name_alts = pd.DataFrame(rows)
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    name_alts.to_parquet(out_data_file("name_alternatives.parquet"), index=False)
