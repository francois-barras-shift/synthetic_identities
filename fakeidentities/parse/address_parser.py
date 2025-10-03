import dataclasses
from collections import defaultdict

import usaddress

DIRECTIONAL_TERMS = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "ne": "northeast",
    "se": "southeast",
    "nw": "northwest",
    "sw": "southwest",
}
DIRECTIONAL_TERMS_REVERSED = {v: k for k, v in DIRECTIONAL_TERMS.items()}

# List of valid street suffixes (USPS or authoritative source)
VALID_STREET_SUFFIXES = {
    "st": "street",
    "rd": "road",
    "ave": "avenue",
    "blvd": "boulevard",
    "ln": "lane",
    "dr": "drive",
    "ct": "court",
    "cir": "circle",
    "wy": "way",
    "pl": "place",
    "ter": "terrace",
    "hwy": "highway",
    "aly": "alley",
    "pkwy": "parkway",
}
VALID_STREET_SUFFIXES_REVERSED = {v: k for k, v in VALID_STREET_SUFFIXES.items()}

OCCUPANCY_TYPES = {
    "apt": "apartment",
    "bsmt": "basement",
    "bldg": "building",
    "dept": "department",
    "fl": "floor",
    "frnt": "front",
    "hngr": "hanger",
    "key": "key",
    "lbby": "lobby",
    "lot": "lot",
    "lowr": "lower",
    "ofc": "office",
    "ph": "penthouse",
    "pier": "pier",
    "rear": "rear",
    "rm": "room",
    "side": "side",
    "slip": "slip",
    "spc": "space",
    "stop": "stop",
    "ste": "suite",
    "trlr": "trailer",
    "unit": "unit",
    "uppr": "upper"
}

OCCUPANCY_TYPES_REVERSED = {v:k for k, v in OCCUPANCY_TYPES.items()}


def split_first_word_if_match(text: str, keywords: dict[str, str]) -> (str | None, str | None):
    if not text:
        return None, None
    words = text.split()
    fst = words[0].lower()
    if fst.endswith('.'):
        fst = fst[:-1]
    if fst in keywords:
        return keywords[fst].capitalize(), " ".join(words[1:]).strip(", ")
    elif fst in keywords.values():
        return words[0].capitalize(), " ".join(words[1:]).strip(", ")
    return None, text

@dataclasses.dataclass(frozen=True)
class ParsedUSAddress:
    raw: str
    house_number: str | None # 1234
    street_name: str | None # Lieutenant Williams
    street_suffix: str | None # St., Rd., Blvd
    post_directional: str | None # Western
    occupancy_type: str | None # Apt., Block
    secondary_number: str | None # 026
    po_box_type: str | None
    po_box_id: str | None
    town: str
    postcode: str
    state: str
    fpo_apo: str | None

    def to_line_str(self, sep = ","):
        if self.po_box_id:
            return f"{self.po_box_type.split()[0]} {self.po_box_id}{sep} {self.state} {self.postcode}"
        fields = [fld for fld in [
            self.house_number,
            self.street_name,
            self.street_suffix,
            self.occupancy_type,
            self.secondary_number,
            self.post_directional,
            self.town
        ] if fld]
        res = ' '.join(fields)
        if self.fpo_apo:
            res += ' ' + self.fpo_apo
        res += sep + ' ' + self.state + ' ' + self.postcode
        return res

def parse_address(raw: str) -> ParsedUSAddress:
    # Parse using both libs
    usaddr = defaultdict(str)
    for k, v in usaddress.parse(raw):
        usaddr[v] = (usaddr[v] + " " + k).strip().replace(',', '')
    # PlaceName from usaddr is more accurate to extract city, but sometimes includes the post-directional
    post_directional, town = split_first_word_if_match(usaddr['PlaceName'], DIRECTIONAL_TERMS)
    street_suffix, street_name = split_first_word_if_match(usaddr['StreetName'], VALID_STREET_SUFFIXES)
    if street_name is None:
        street_name = ''
    fpo_apo = None
    if 'StreetNamePostType' in usaddr and (post_type := usaddr['StreetNamePostType']):
        street_name += ' ' + post_type
    if not street_name and " DPO" in raw:
        fpo_apo = "DPO"
        town = raw[:raw.index(" DPO")]
    if not street_name and " APO" in raw:
        fpo_apo = "APO"
        town = raw[:raw.index(" APO")]
    if not street_name and " FPO" in raw:
        fpo_apo = "FPO"
        town = raw[:raw.index(" FPO")]
    return ParsedUSAddress(
        raw=raw,
        house_number=usaddr['AddressNumber'],
        street_name=street_name,
        street_suffix=street_suffix,
        post_directional=post_directional,
        occupancy_type=usaddr['OccupancyType'],
        secondary_number=usaddr['OccupancyIdentifier'],
        town=town,
        postcode=usaddr['ZipCode'],
        state=usaddr['StateName'],
        po_box_type=usaddr['USPSBoxType'],
        po_box_id=usaddr['USPSBoxID'],
        fpo_apo=fpo_apo
    )