from collections import defaultdict, Counter

from fuzzy import DMetaphone
from jellyfish import soundex, nysiis
from unidecode import unidecode


class PhoneticDict:
    """
    Dictionary holding double metaphone encodings for a set of names.
    """
    _metaphone_dict: defaultdict[bytes, set[str]]
    _soundex_dict: defaultdict[str, set[str]]
    _nysiis_dict: defaultdict[str, set[str]]
    _metaphone = DMetaphone(4)

    def __init__(self):
        self._metaphone_dict = defaultdict(set)
        self._soundex_dict = defaultdict(set)
        self._nysiis_dict = defaultdict(set)

    def __add__(self, name: str) -> 'PhoneticDict':
        """
        Adds a name to the set of all variants
        :param name: the name to add to all variants
        :return: the dict, so that the call is fluent
        """
        for encoding in self._metaphone_encode(name):
            self._metaphone_dict[encoding].add(name)
        self._nysiis_dict[nysiis(name)].add(name)
        self._soundex_dict[soundex(name)].add(name)
        return self

    def __contains__(self, name: str) -> bool:
        for encoding in self._metaphone_encode(name):
            if encoding in self._metaphone_dict:
                return True
        return False

    def __getitem__(self, name: str) -> set[str]:
        """
        Returns a set of names matching the one passed as parameter
        "Matching" means a majority of encoders (2 out of 3) would match encodings
        for the returned names
        :param name: the name to look variants for
        :return: a set of variant names that are mostly pronounced the same (for 2 or more encoders)
        """
        counter = Counter()
        for encoding in self._metaphone_encode(name):
            counter.update(self._metaphone_dict.get(encoding, set()))
        counter.update(self._nysiis_dict.get(nysiis(name), set()))
        counter.update(self._soundex_dict.get(soundex(name), set()))
        return set([k for (k, v) in counter.items() if v >= 2])

    def _metaphone_encode(self, name: str) -> list[bytes]:
        sanitized = unidecode(name)
        return [e for e in self._metaphone(sanitized) if e is not None]


PHONETIC_MAP = {
    "ph": "f",  # ph -> f (e.g., 'Stephen' -> 'Stefen')
    "ie": "y",  # ie -> y (e.g., 'Gracie' -> 'Gracy')
    "oo": "u",  # oo -> u (e.g., 'Google' -> 'Gugle')
    "ck": "k",  # ck -> k (e.g., 'Mickey' -> 'Miky')
    "ght": "t",  # ght -> t (e.g., 'Knight' -> 'Knit')
    "tion": "shun",  # tion -> shun (e.g., 'Caution' -> 'Caushun')
    "ch": "k",  # ch -> k (e.g., 'Charlie' -> 'Karlie')
    "x": "z",  # x -> z (e.g., 'Xander' -> 'Zander')
    "z": "s",  # z -> s (e.g., 'Zoe' -> 'Soe')
    "w": "v",  # w -> v (e.g., 'William' -> 'Viliam')
    "v": "f",  # v -> f (e.g., 'Vera' -> 'Fera')
    "j": "g",  # j -> g (e.g., 'James' -> 'Games')
    "k": "c",  # k -> c (e.g., 'Kara' -> 'Cara')
    "c": "s",  # c -> s (e.g., 'Cynthia' -> 'Synthia')
    "d": "t",  # d -> t (e.g., 'David' -> 'Tavid')
    "b": "p",  # b -> p (e.g., 'Bob' -> 'Pop')
    "r": "l",  # r -> l (e.g., 'Rachel' -> 'Lachel')
    "m": "n",  # m -> n (e.g., 'Megan' -> 'Negan')
    "l": "r",  # l -> r (e.g., 'Lily' -> 'Rily')
    "n": "m",  # n -> m (e.g., 'Nina' -> 'Mina')
    "a": "e",  # a -> e (e.g., 'Sarah' -> 'Serah')
    "o": "a",  # o -> a (e.g., 'John' -> 'Jahn')
    "u": "o",  # u -> o (e.g., 'Lucas' -> 'Locas')
    "i": "e",  # i -> e (e.g., 'Lisa' -> 'Lesa')
    "y": "i",  # y -> i (e.g., 'Kathy' -> 'Kathi')
    "e": "i",  # e -> i (e.g., 'Becky' -> 'Bicky')
    "ae": "e",  # ae -> e (e.g., 'Raegan' -> 'Reagan')
    "ee": "i",  # ee -> i (e.g., 'Becky' -> 'Biky')
    "ea": "i",  # ea -> i (e.g., 'Dean' -> 'Din')
    "ei": "ie",  # ei -> ie (e.g., 'Heidi' -> 'Hiedi')
    "oi": "oy",  # oi -> oy (e.g., 'Joey' -> 'Joi')
    "ou": "ow",  # ou -> ow (e.g., 'George' -> 'Gorge')
    "aw": "ao",  # aw -> ao (e.g., 'Lawrence' -> 'Laorence')
    "ow": "au",  # ow -> au (e.g., 'Howard' -> 'Haud')
}