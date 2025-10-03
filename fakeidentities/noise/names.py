import dataclasses
import re
from abc import abstractmethod

from fakeidentities.names import NameVariants, make_name
from fakeidentities.noise.noiser import Noiser
from fakeidentities.phonetics import PhoneticDict, PHONETIC_MAP
from nicknames import NickNamer
import random
import nlpaug.augmenter.char as nac

dup_chars = ["l", "n", "s", "t", "p", "e"]
dup_letter_pattern = re.compile(r"(.)\1")

class AbstractNameNoiser(Noiser[str]):
    p_phonetic_replacement: float = 0.5
    p_rem_duplicate_char: float = 0.2
    p_add_duplicate_char: float = 0.1
    p_random_augment: float = 0.35
    _keyboard_aug = nac.KeyboardAug(
        aug_char_p=0.15,            # Probability of a character being augmented
        include_upper_case=False,   # Avoid altering upper-case letters
        aug_char_min=1,             # Minimum number of characters to augment
        aug_char_max=3,             # Maximum number of characters to augment
        min_char=4                  # Words with fewer than 4 characters won't be augmented
    )

    @abstractmethod
    def noise(self, original: str) -> str:
        pass

    def typo(self, name: str) -> str:
        # Only use augmenter as last resort, introduce some common mispellings before
        # Step 1: Apply the phonetic rules with probability (not guaranteed to be applied)
        for phonetic, replacement in PHONETIC_MAP.items():
            if random.random() < self.p_phonetic_replacement:  # 50% chance to apply this rule
                new_name = name.replace(phonetic, replacement)
                if new_name != name:
                    name = new_name
                    break
        # Step 2: Handle doubled letters (simulate typo by removing one with 20% chance)
        choice = random.random()
        if dup_letter_pattern.match(name) and choice < self.p_rem_duplicate_char:  # 20% chance to remove a duplicate letter
            name = dup_letter_pattern.sub(repl=r"\1", string=name, count=1)
        elif choice < self.p_rem_duplicate_char + self.p_add_duplicate_char:  # 10% chance to duplicate a character
            random.shuffle(dup_chars)
            for char in dup_chars:
                if char * 2 in name:
                    name = name.replace(char * 2, char)
                    break
                elif char in name:
                    name = name.replace(char, char * 2, 1)
                    break
        elif choice < 0.35:  # 35% chance to insert a totally random typo
            name = self._keyboard_aug.augment(name)[0]

        return name

@dataclasses.dataclass
class LastNameNoiser(AbstractNameNoiser):
    phonetics: PhoneticDict
    p_phonetic: float = 0.15
    p_typo: float = 0.15

    def noise(self, original: str) -> str:
        lookup = original.lower()
        choice = random.random()
        name = original
        if lookup in self.phonetics and self.phonetics[lookup]:
            if choice < self.p_phonetic:
                name = random.choice(list(self.phonetics[lookup]))
            elif choice < self.p_phonetic + self.p_typo:
                name = self.typo(original)
        elif choice < self.p_typo:
            name = self.typo(original)
        normalized = make_name(name)
        if random.random() <= 0.5:
            return normalized.upper()
        else:
            return normalized


@dataclasses.dataclass
class FirstNameNoiser(AbstractNameNoiser):
    variants: NameVariants
    phonetics: PhoneticDict
    nicknames = NickNamer()
    p_initial: float = 0
    p_nickname: float = 0.15
    p_variant: float = 0.15
    p_phonetic: float = 0.15
    p_typo: float = 0.15

    def noise(self, original: str) -> str:
        lookup = original.lower()
        # 1. Use nickname
        use_nickname = random.random()
        nicknames = self.nicknames.nicknames_of(original)
        canonical = self.nicknames.canonicals_of(original)
        if nicknames and use_nickname < self.p_nickname:
            return make_name(random.choice(list(nicknames)))
        elif canonical and use_nickname < self.p_nickname:
            return make_name(random.choice(list(canonical)))
        use_initial = random.random()
        if use_initial < self.p_initial:
            return original[0].upper() + '.'
        choice = random.random()
        # TODO: refactor this in a better way
        # 2. Use common variant
        if lookup in self.variants and self.variants[lookup] and choice < self.p_phonetic:
            name = random.choice(list(self.variants[lookup]))
        # 3. Phonetic similarity name
        elif lookup in self.phonetics and self.phonetics[lookup] and choice < self.p_variant + self.p_phonetic:
            name = random.choice(list(self.phonetics[lookup]))
        # 4. Maybe Typo
        elif choice < self.p_typo:
            name = self.typo(original)
        else:
            name = original
        return make_name(name)
