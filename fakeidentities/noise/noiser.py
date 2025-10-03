import random
from abc import ABC, abstractmethod
from typing import TypeVar

from typing_extensions import Generic


# sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
# # Load a prebuilt dictionary file for SymSpell
# dictionary_path = config_file("frequency_dictionary_en_82_765.txt")
# sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
# def ocr_noise_text(text: str) -> list[str]:
#     return [sugg.term for sugg in sym_spell.lookup(text, Verbosity.CLOSEST, max_edit_distance=2)]
#

def abbrv_or_full(text: str, abbrv_to_full: dict[str, str], full_to_abbrv: dict[str, str], upper: bool) -> str:
    normalized_txt = text.lower()
    if normalized_txt.endswith('.'):
        normalized_txt = normalized_txt[:-1]
    if normalized_txt in abbrv_to_full:
        return abbrv_to_full[normalized_txt].capitalize()
    elif normalized_txt in full_to_abbrv:
        replacement = full_to_abbrv[normalized_txt].upper()
        if upper:
            return replacement.upper()
        else:
            return replacement.capitalize() + '.'


def typo_in_short_number(text: str) -> str:
    if len(text) < 2:
        return text
    chars = list(text)
    pos = random.randint(0, len(text) - 2)
    choice = random.random()
    if choice < 0.4:
        # miss one char
        del chars[pos]
    elif choice < 0.9:
        # swap 2 chars
        chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
    else:
        chars = chars[:pos] + [str(random.randint(0, 9))] + chars[pos+1:]
    return ''.join(chars)

T = TypeVar('T')
class Noiser(ABC, Generic[T]):
    @abstractmethod
    def noise(self, original: T) -> T:
        pass