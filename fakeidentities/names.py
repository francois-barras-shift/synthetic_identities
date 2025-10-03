import csv

from fakeidentities.phonetics import PhoneticDict
from fakeidentities.utils import raw_data_file

suffixes = { "MD", "DDS", "PhD", "DVM", "Jr.", "II", "III", "IV", "V" }
prefixes = { "Mrs.", "Ms.", "Miss", "Dr.", "Mr.", "Dr.", "Mx.", "Ind.", "Misc.", "Dr." }

NameVariants = dict[str, set[str]]

def make_name(name: str) -> str:
    return ' '.join([part.capitalize() for part in name.split(' ')])

def lastnames() -> list[str]:
    with open(raw_data_file('Names_2010Census.csv'), 'r') as f:
        reader = csv.DictReader(f)
        return [entry['name'] for entry in reader]

def givennames_synonyms() -> NameVariants:
    res = {}
    with open(raw_data_file("btn_givennames_synonyms.txt"), mode='r') as synonyms:
        reader = csv.reader(synonyms, delimiter="\t")
        for line in reader:
            name = line[0].lower()
            alternates = [alt.lower().strip() for alt in line[2].split(',')]
            if not alternates or alternates == ['']:
                continue
            if name not in res:
                res[name] = set()
            res[name] = res[name].union(set(alternates))
            for alt in alternates:
                if alt not in res:
                    res[alt] = set()
                others = set(alternates)
                others.remove(alt)
                others.add(name)
                res[alt] = res[alt].union(others)
    return res

def build_firstnames_variants() -> (NameVariants, PhoneticDict):
    synonyms = givennames_synonyms()
    all_given_names = givennames_synonyms().keys()
    names_by_phonetics = PhoneticDict()
    for name in all_given_names:
        names_by_phonetics += name
    return synonyms, names_by_phonetics

def build_lastnames_phonetics() -> PhoneticDict:
    names_by_phonetics = PhoneticDict()
    for name in lastnames():
        names_by_phonetics += name.lower()
    return names_by_phonetics