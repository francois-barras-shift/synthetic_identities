import copy
import random

from fakeidentities.noise.noiser import Noiser
import nlpaug.augmenter.char as nac

COMMON_EXTENSIONS = [ "com", "net", "org", "co" ]
EMAIL_SEP = ['.', '-', '_']

def random_extension() -> str:
    return random.choice(COMMON_EXTENSIONS)


def wrong_separator(original: str) -> str:
    for sep in EMAIL_SEP:
        if sep not in original:
            continue
        idx = original.index(sep)
        alternates = copy.copy(EMAIL_SEP)
        if idx > 0:
            alternates.remove(sep)
            new_sep = random.choice(alternates)
            return original[:idx] + new_sep + original[idx+1:]
    return original

class EmailNoiser(Noiser[str]):
    _keyboard_aug = nac.KeyboardAug(
        aug_char_p=0.15,            # Probability of a character being augmented
        include_upper_case=False,   # Avoid altering upper-case letters
        aug_char_min=1,             # Minimum number of characters to augment
        aug_char_max=3,             # Maximum number of characters to augment
        min_char=4,                  # Words with fewer than 4 characters won't be augmented
        include_special_char=False,
        include_numeric=False,
    )

    def noise(self, original: str) -> str:
        split = original.split('@')
        name = split[0]
        domain = split[1]
        last_dot = domain.rfind('.')
        tld = domain[:last_dot]
        ext = domain[last_dot+1:]
        # Common typos in emails:
        # 1. Use one diacritic for another (before @) (eg: some-one@gmail.com for some_one@gmail.com)
        # 2. Use the wrong country code in domain name (eg: gmail.fr instead of gmail.com)
        name_typo = random.random()
        if name_typo < 0.05: # small chance that a "big" typo happens (OCR)
            name = self._keyboard_aug.augment(name)[0] # TODO: this only augments chars before separator (dot)
            name = name.replace(' ', '')
        elif name_typo < 0.15:
            name = wrong_separator(name)

        ext_typo = random.random()
        if ext_typo < 0.15:
            ext = random_extension()

        tld_typo = random.random()
        if any(sep in tld for sep in EMAIL_SEP):
            if tld_typo < 0.1:
                tld = wrong_separator(tld)

        return name + '@' + tld + '.' + ext
