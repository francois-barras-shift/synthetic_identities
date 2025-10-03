from datetime import datetime
from random import random

from faker import Faker


from fakeidentities.person import Person
from fakeidentities.utils import raw_data_file, out_data_file
import pandas as pd

import csv


ALL_BABY_NAMES: pd.DataFrame = pd.read_csv(raw_data_file("baby-names.csv"))
NAMES_2010: pd.DataFrame = pd.read_csv(raw_data_file("Names_2010Census.csv"))
NAMES_ALTERNATIVES: pd.DataFrame = pd.read_parquet(out_data_file("name_alternatives.parquet"))

suffixes = { "MD", "DDS", "PhD", "DVM", "Jr.", "II", "III", "IV", "V" }
prefixes = { "Mrs.", "Ms.", "Miss", "Dr.", "Mr.", "Dr.", "Mx.", "Ind.", "Misc.", "Dr." }

type NameVariants = dict[str, set[str]]

def random_us_identity(fake: Faker):
    # Faker does not generate middle names, we'll be generating 20% of identities with middle names
    female = random() <= 0.508
    full_name = fake.name_female() if female else fake.name_male()
    name_parts = full_name.split()
    # Add a middle name with a certain probability (e.g., 15%)
    if random() < 0.15:  # 15% probability to add a middle name
        if random() < 0.6: # use a firstname as middle name: John Patrick Miller
            middle_name = fake.first_name_female() if female else fake.first_name_male()
        else: # use last name as middle name: John Miller Smith
            middle_name = fake.last_name()
        has_prefix = name_parts[0] in prefixes
        insert_idx = 2 if has_prefix else 1
        name_parts.insert(insert_idx, middle_name)
    return " ".join(name_parts)

def golden_record_persons(size: int, seed: int) -> pd.DataFrame:
    f = Faker(locale="en_US", seed=seed)
    names = [random_us_identity(f) for _ in range(size)]
    more_than_3 = [name for name in names if len(name.split()) > 3]
    return pd.DataFrame(more_than_3, columns=['name'])

def load_golden_records() -> list[Person]:
    def change_type(line) -> dict:
        line["date_of_birth"] = datetime.strptime(line["date_of_birth"], "%Y-%M-%d").date()
        return line

    with open(out_data_file("golden_records_nodes.csv")) as f:
        reader = csv.DictReader(f)
        return [Person(**change_type(line)) for line in reader]
