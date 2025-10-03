import dataclasses
import random
import nlpaug.augmenter.char as nac

from fakeidentities.noise.noiser import Noiser, abbrv_or_full, typo_in_short_number
from fakeidentities.parse.address_parser import parse_address, VALID_STREET_SUFFIXES, VALID_STREET_SUFFIXES_REVERSED, \
    DIRECTIONAL_TERMS, DIRECTIONAL_TERMS_REVERSED, OCCUPANCY_TYPES, OCCUPANCY_TYPES_REVERSED


@dataclasses.dataclass
class AddressNoiser(Noiser[str]):
    # TODO: config probabilities
    # Augmenter for typos
    _keyboard_aug = nac.KeyboardAug(
        aug_char_p=0.15,            # Probability of a character being augmented
        include_upper_case=False,   # Avoid altering upper-case letters
        aug_char_min=1,             # Minimum number of characters to augment
        aug_char_max=3,             # Maximum number of characters to augment
        min_char=4                  # Words with fewer than 4 characters won't be augmented
    )

    def augment(self, original: str) -> str:
        return self._keyboard_aug.augment(original)[0]

    def noise(self, original: str) -> str:
        # 1. Parse address
        parsed = parse_address(original)
        max_missing = 2
        total_missing = 0
        # 2. Noise components individually based on probs
        if parsed.house_number:
            housenumber_mistake = random.random()
            if housenumber_mistake < 0.1 and total_missing < max_missing: # missing
                total_missing += 1
                parsed = dataclasses.replace(parsed, house_number=None)
            elif housenumber_mistake < 0.2: # typo in numbers = swap_2_consecutive_chars
                parsed = dataclasses.replace(parsed, house_number=typo_in_short_number(parsed.house_number))

        streetname_mistake = random.random()
        if parsed.street_name and streetname_mistake < 0.15: # typo
            parsed = dataclasses.replace(parsed, street_name=self.augment(parsed.street_name))

        if parsed.street_suffix:
            suffix_mistake = random.random()
            if suffix_mistake < 0.1 and total_missing < max_missing: # missing
                total_missing += 1
                parsed = dataclasses.replace(parsed, street_suffix=None)
            elif suffix_mistake < 0.3: # use abbreviation or full if abbreviated
                parsed = dataclasses.replace(
                    parsed,
                    street_suffix=abbrv_or_full(
                        parsed.street_suffix,
                        VALID_STREET_SUFFIXES,
                        VALID_STREET_SUFFIXES_REVERSED,
                        upper=False,
                    )
                )

        if parsed.post_directional:
            direction_mistake = random.random()
            if direction_mistake < 0.1 and total_missing < max_missing: # missing
                total_missing += 1
                parsed = dataclasses.replace(parsed, post_directional=None)
            elif direction_mistake < 0.3: # use abbreviation or full if abbreviated
                parsed = dataclasses.replace(
                    parsed,
                    post_directional=abbrv_or_full(
                        parsed.post_directional,
                        DIRECTIONAL_TERMS,
                        DIRECTIONAL_TERMS_REVERSED,
                        upper=True
                    )
                )

        if parsed.occupancy_type:
            occupancy_mistake = random.random()
            if occupancy_mistake < 0.1 and total_missing < max_missing: # missing
                total_missing += 1
                parsed = dataclasses.replace(parsed, occupancy_type=None)
            elif occupancy_mistake < 0.3:
                parsed = dataclasses.replace(
                    parsed,
                    occupancy_type=abbrv_or_full(
                        parsed.occupancy_type,
                        OCCUPANCY_TYPES,
                        OCCUPANCY_TYPES_REVERSED,
                        upper=False,
                    )
                )

        if parsed.secondary_number:
            secondary_mistake = random.random()
            if secondary_mistake < 0.1 and total_missing < max_missing: # missing
                total_missing += 1
                parsed = dataclasses.replace(parsed, secondary_number=None)
            elif secondary_mistake < 0.2: # typo in numbers = swap_2_consecutive_chars
                parsed = dataclasses.replace(parsed, secondary_number=typo_in_short_number(parsed.secondary_number))

        if parsed.po_box_id:
            pobox_mistake = random.random()
            if pobox_mistake < 0.1: # typo in numbers = swap_2_consecutive_chars
                parsed = dataclasses.replace(parsed, po_box_id=typo_in_short_number(parsed.po_box_id))

        town_mistake = random.random()
        if town_mistake < 0.2: # typo in town, unlikely but can happen
            parsed = dataclasses.replace(parsed, town=self.augment(parsed.town))

        pocode_mistake = random.random()
        if pocode_mistake < 0.2: # typo in town, unlikely but can happen
            parsed = dataclasses.replace(parsed, postcode=typo_in_short_number(parsed.postcode))

        # TODO: shuffle address parts
        return parsed.to_line_str()
