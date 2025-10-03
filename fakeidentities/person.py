import dataclasses
import datetime
from enum import Enum


class Sex(Enum):
    FEMALE = 1
    MALE = 2

@dataclasses.dataclass(frozen=True)
class Person:
    unique_id: str
    firstname: str
    middlename: str | None
    prefix: str | None
    suffix: str | None
    lastname: str
    date_of_birth: datetime.date
    raw_address: str
    social_security_number: str
    sex: Sex
    phone: str
    personal_email: str
    corporate_email: str | None

    @property
    def age(self):
        return datetime.date.today().year - self.date_of_birth.year

    def with_lastname(self, new_name: str) -> 'Person':
        return dataclasses.replace(self, lastname=new_name)

    def move_at(self, new_address):
        return dataclasses.replace(self, raw_address=new_address)


    @property
    def fullname(self) -> str:
        fn = ""
        if self.prefix:
            fn+= self.prefix + " "
        fn += self.firstname
        if self.middlename:
            fn += " " + self.middlename
        fn += " " + self.lastname
        if self.suffix:
            fn += " " + self.suffix
        return fn


@dataclasses.dataclass(frozen=True)
class InputPerson:
    unique_id: str
    full_name: str
    date_of_birth: datetime.date | None
    address: str | None
    social_security_number: str | None
    email: str | None
    phone: str | None
    