import dataclasses
import random
import uuid

from fakeidentities.names import NameVariants
from fakeidentities.noise.address import AddressNoiser
from fakeidentities.noise.dob import DateOfBirthNoiser
from fakeidentities.noise.email_noiser import EmailNoiser
from fakeidentities.noise.names import FirstNameNoiser, LastNameNoiser
from fakeidentities.noise.noiser import Noiser
from fakeidentities.noise.phone import PhoneNoiser
from fakeidentities.person import Person, Sex
from fakeidentities.phonetics import PhoneticDict

@dataclasses.dataclass
class PersonNoiser(Noiser[Person]):
    firstname_variants: NameVariants
    firstname_phonetics: PhoneticDict
    lastname_phonetics: PhoneticDict
    p_missing_ssn: float = 0.4
    p_missing_middlename: float = 0.2
    p_missing_dob: float = 0.25
    p_missing_prefix: float = 0.2
    p_missing_suffix: float = 0.2
    p_missing_email: float = 0.2
    p_missing_sex: float = 0.3
    p_missing_phone: float = 0.2

    def __post_init__(self):
        self.firstname_noiser = FirstNameNoiser(
            variants=self.firstname_variants,
            phonetics=self.firstname_phonetics
        )
        self.middlename_noiser = FirstNameNoiser(
            variants=self.firstname_variants,
            phonetics=self.firstname_phonetics,
            p_initial=0.2,
            p_nickname=0.2,
        )
        self.lastname_denoiser = LastNameNoiser(phonetics=self.lastname_phonetics)
        self.address_noiser = AddressNoiser()
        self.email_noiser = EmailNoiser()
        self.dob_noiser = DateOfBirthNoiser()
        self.phone_noiser = PhoneNoiser()

    def noise(self, original: Person) -> Person:
        include_prefix = original.prefix and random.random() < self.p_missing_prefix
        include_suffix = original.suffix and random.random() < self.p_missing_suffix
        personal_email = original.personal_email
        corporate_email = original.corporate_email
        if personal_email and random.random() < self.p_missing_email:
            personal_email = None
        if corporate_email and random.random() < self.p_missing_email:
            corporate_email = None
        if personal_email:
            self.email_noiser.noise(personal_email)
        if corporate_email:
            self.email_noiser.noise(corporate_email)
        dob = original.date_of_birth
        if random.random() < self.p_missing_dob:
            dob = None
        if dob:
            dob = self.dob_noiser.noise(dob)
        sex = original.sex
        if random.random() < self.p_missing_sex:
            sex = None
        if sex and random.random() < 0.2: # p_wrong_sex
            sex = Sex.MALE if random.random() <= 0.5 else Sex.FEMALE
        phone = original.phone
        if random.random() < self.p_missing_phone:
            phone = None
        if phone:
            phone = self.phone_noiser.noise(phone)
        return Person(
            unique_id=str(uuid.uuid4()),
            firstname=self.firstname_noiser.noise(original.firstname),
            middlename=None if not original.middlename else self.middlename_noiser.noise(original.middlename),
            lastname=self.lastname_denoiser.noise(original.lastname),
            prefix=original.prefix if include_prefix else None,
            suffix=original.suffix if include_suffix else None,
            date_of_birth=dob,
            raw_address=self.address_noiser.noise(original.raw_address),
            # never change SSN, just set it to null sometimes
            social_security_number=None if random.random() < self.p_missing_ssn else original.social_security_number,
            sex=sex,
            phone=phone,
            personal_email=personal_email,
            corporate_email=corporate_email,
        )
