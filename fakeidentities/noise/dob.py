import dataclasses
import datetime
import random

from fakeidentities.noise.noiser import Noiser

@dataclasses.dataclass
class DateOfBirthNoiser(Noiser[datetime.date]):
    p_not_set: float = 0.25
    p_swap_month_date: float = 0.15
    p_swap_days: float = 0.1
    p_off_year: float = 0.1

    def noise(self, original: datetime.date) -> datetime.date:
        day = original.day
        month = original.month
        year = original.year
        choice = random.random()
        if choice < self.p_not_set:
            return datetime.date(day=1, month=1, year=1970)
        elif choice < self.p_not_set + self.p_swap_month_date and day <= 12:
            return datetime.date(day=month, month=day, year=year)
        elif choice < self.p_not_set + self.p_swap_month_date + self.p_swap_days:
            part_1 = day // 10
            part_2 = day % 10
            if part_2 <= 2: # if we can swap, swap
                return datetime.date(day=part_2 * 10 + part_1, month=month, year=year)
            elif 2 < day < 27: # make it safe
                if random.random() <= 0.5:
                    return datetime.date(day=day + 1, month=month, year=year)
                else:
                    return datetime.date(day=day + 1, month=month, year=year)
        elif choice < self.p_not_set + self.p_swap_month_date + self.p_swap_days + self.p_off_year:
            if random.random() <= 0.5:
                return datetime.date(day=day, month=month, year=year + 1)
            else:
                return datetime.date(day=day, month=month, year=year - 1)
        else:
            return datetime.date(day=day, month=month, year=year)