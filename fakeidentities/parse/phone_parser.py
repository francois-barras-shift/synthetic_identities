# Regex to match a phone number with optional country code and extension
import dataclasses
import re

phone_pattern = re.compile(r"""
        (?P<country_code>\+?1[- ]?)?            # Optional country code
        \(?(?P<area_code>\d{3})\)?[- ]?         # Area code
        (?P<first_part>\d{3})[- ]?              # First 3 digits of main number
        (?P<second_part>\d{4})                  # Last 4 digits of main number
        (?:x(?P<extension>\d+))?                # Optional extension
    """, re.VERBOSE)

@dataclasses.dataclass
class USPhoneNumber:
    country_code: str
    area_code: str
    first_part: str
    second_part: str
    extension: str

    def __init__(self, phone: str):
        match = phone_pattern.match(phone)
        if not match:
            raise Exception(f"Invalid phone number: {phone}")
        # Extract components
        self.country_code = match.group("country_code") or ""
        self.area_code = match.group("area_code")
        self.first_part = match.group("first_part")
        self.second_part = match.group("second_part")
        self.extension = match.group("extension")
