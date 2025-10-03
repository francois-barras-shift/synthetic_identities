import dataclasses

import numpy as np
import pandas as pd

from fakeidentities.data import load_golden_records
from fakeidentities.names import build_firstnames_variants, build_lastnames_phonetics
from fakeidentities.noise.person import PersonNoiser
from fakeidentities.person import Person
from fakeidentities.utils import out_data_file


def print_compared(original: Person, noised: Person):
    print("----------")
    for field in dataclasses.fields(original):
        field_name = field.name
        original_value = getattr(original, field_name)
        noised_value = getattr(noised, field_name)
        print(f"{field_name}: {original_value} -> {noised_value}")


if __name__ == '__main__':
    mean = 10
    std_dev = 5
    persons = load_golden_records()
    variants, phonetics = build_firstnames_variants()
    noiser = PersonNoiser(
        firstname_variants=variants,
        firstname_phonetics=phonetics,
        lastname_phonetics=build_lastnames_phonetics()
    )
    out_data = []
    for p in persons:
        num_duplicates = max(5, int(np.random.normal(loc=mean, scale=std_dev)))
        for _ in range(num_duplicates):
            noised = noiser.noise(p)
            noised = noised.__dict__
            noised['original_id'] = p.unique_id
            out_data.append(noised)

    df = pd.DataFrame(out_data)
    df.to_csv(out_data_file("noisy_persons.csv"))