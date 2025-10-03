import datetime
import math

import pandas as pd
from faker import Faker
import random

import networkx as nx
from matplotlib.lines import Line2D

from fakeidentities.person import Person, Sex
from fakeidentities.utils import out_data_file, sanitize_string

fake_US = Faker('en_US')
fake_MX = Faker('es_MX')
fake_IN = Faker('en_IN')

has_corp_email_prob = 0.4

def fake_mail(firstname: str, lastname: str, dob: datetime.date, is_corp: bool) -> str:
    base_mail = fake_US.company_email() if is_corp else fake_US.ascii_free_email()
    domain = base_mail.split("@")[1]
    email_pattern = random.random()
    sep = random.choice([".", "-", "_", ""])
    number_rnd = random.random()
    if is_corp:
        # pattern is closer to firstname-lastname or flastname or f.lastname
        if email_pattern < 0.5:
            return f"{sanitize_string(firstname)}{sep}{sanitize_string(lastname)}@{domain}"
        else:
            return f"{sanitize_string(firstname)[0]}{sep}{sanitize_string(lastname)}@{domain}"
    else:
        # harder pattern
        # it may include a number
        number = None
        if number_rnd < 0.33:
            number = int(random.random() * 100)
        elif number_rnd < 0.66:
            number = random.choice([dob.year, dob.year % 100])
        # then it may use firstname lastname or a nickname (anonymous address)
        uses_nickname = random.random() < 0.3
        if uses_nickname:
            identifier = fake_US.word() + fake_US.word()
        else:
            if email_pattern < 0.5:
                identifier = f"{sanitize_string(firstname)}{sep}{sanitize_string(lastname)}"
            else:
                identifier = f"{sanitize_string(firstname[0])}{sep}{sanitize_string(lastname)}"
        if number:
            identifier += str(number)
        return f"{identifier}@{domain}"

def base_individuals(size):
    population = []
    for _ in range(size):
        generator: Faker = random.choices([fake_US, fake_MX, fake_IN], weights=[0.7, 0.2, 0.1])[0] # a bit more diversity
        dob = generator.date_of_birth(minimum_age=18, maximum_age=90)
        sex = random.choice([Sex.MALE, Sex.FEMALE])
        has_middlename = random.choice([True, False])
        has_title = random.choices([True, False], weights=[0.2, 0.8])[0]
        has_prefix = has_title and random.choice([True, False])
        has_suffix = has_title and not has_prefix
        firstname = generator.first_name_male() if sex == Sex.MALE else generator.first_name_female()
        lastname = generator.last_name()
        address = fake_US.address().replace("\n", " ")
        """
        while not address:
            candidate = fake_US.address().replace("\n", " ")
            try:
                usaddress.tag(candidate)
                address = candidate
            except Exception:
                pass
        """
        person = Person(
            unique_id=generator.uuid4(),
            firstname=firstname,
            middlename=None if not has_middlename else generator.first_name_male() if sex == Sex.MALE else generator.first_name_female(),
            lastname=lastname,
            prefix=None if not has_prefix else generator.prefix_male() if sex == sex.MALE else generator.prefix_female(),
            suffix=None if not has_suffix else generator.suffix_male() if sex == sex.MALE else generator.suffix_female(),
            date_of_birth=dob,
            sex=sex,
            raw_address=address,
            social_security_number=fake_US.ssn(),
            personal_email=fake_mail(firstname, lastname, dob, False),
            corporate_email=fake_mail(firstname, lastname, dob, True) if random.random() < has_corp_email_prob else None,
            phone=fake_US.phone_number(),
        )
        population.append(person)
    return population

def expected_children(age: int, max_children=4, peak_age=30, sigma=10):
    # Gaussian-like curve for fertility
    return max_children * math.exp(-((age - peak_age) ** 2) / (2 * sigma ** 2))

def childless_probability(age: int, p0_max=0.6, age_start=20, decay_rate=5):
    """
    Calculates the probability of being childless based on age.
    """
    if age < age_start:
        return p0_max  # Maximum childless probability before childbearing years
    return p0_max * math.exp(-(age - age_start) / decay_rate)

def number_of_children_by_age(age):
    # Determine if couple is childless
    if random.random() < childless_probability(age):
        return 0

    # Expected number of children
    expected_kids = expected_children(age)

    # Randomly sample the number of children around the expected value
    num_kids = min(4, max(0, round(random.gauss(expected_kids, 0.5))))  # Add some noise
    return num_kids

def breed(partner_m: Person, partner_f: Person) -> Person:
    generator: Faker = random.choices([fake_US, fake_MX, fake_IN], weights=[0.7, 0.2, 0.1])[0] # a bit more diversity
    max_child_age = min(partner_f.age - 18, 25)  # Children’s ages must fit within parents' plausible range
    child_age = random.randint(0, max_child_age)
    dob = fake_US.date_of_birth(minimum_age=child_age, maximum_age=child_age)
    sex = random.choice([Sex.MALE, Sex.FEMALE])
    has_middlename = random.choice([True, False])
    firstname = generator.first_name_male() if sex == Sex.MALE else generator.first_name_female()
    lastname = random.choices([partner_m.lastname, partner_m.lastname + " " + partner_f.lastname], weights=[0.75, 0.25])[0]
    return Person(
        unique_id=generator.uuid4(),
        firstname=firstname,
        middlename=None if not has_middlename else generator.first_name_male() if sex == Sex.MALE else generator.first_name_female(),
        lastname=lastname,
        prefix=None,
        suffix=None,
        date_of_birth=dob,
        sex=sex,
        raw_address=partner_m.raw_address,
        social_security_number=fake_US.ssn(),
        personal_email=fake_mail(firstname, lastname, dob, False),
        corporate_email=None,
        phone=fake_US.phone_number()
    )

    

def assign_children(partner_m: Person, partner_f: Person) -> list[Person]:
    num_kids = number_of_children_by_age(partner_f.age)
    return [breed(partner_m, partner_f) for _ in range(num_kids)]

def assign_address(kid: Person, partner_M: Person, partner_F: Person) -> Person:
    new_address = random.choice([partner_M, partner_F]).raw_address
    return kid.move_at(new_address)


def pair_couples(couple_percent: float, pop_m: set[Person], pop_f: set[Person]) -> nx.Graph:
    population = nx.Graph()
    while pop_m:
        current_person = pop_m.pop()
        will_marry = random.random() < couple_percent
        if will_marry and pop_f:
            # try to find a partner
            partner = pop_f.pop()
            # assign children
            kids = assign_children(current_person, partner)
            # have they divorced? (discarding re-marriage)
            divorced = random.random() < 0.25
            if not divorced:
                choice = random.random()
                if choice < 0.5:
                    partner = partner.with_lastname(current_person.lastname)
                elif choice < 0.8:
                    partner = partner.with_lastname(partner.lastname + " " + current_person.lastname)
                # let them live at the same place
                partner = partner.move_at(current_person.raw_address)
            else:
                # kids will live with one parent
                kids = [ assign_address(kid, current_person, partner) for kid in kids ]

            population.add_node(partner)
            if not divorced:
                population.add_edge(current_person, partner, relationship="couple")
            for kid in kids:
                population.add_node(kid)
                population.add_edge(current_person, kid, relationship="parent")

        population.add_node(current_person)

    # leftovers
    for single in pop_f.union(pop_m):
        population.add_node(single)

    return population


def random_families(individuals):
    """Pairs individuals into couples where possible."""
    # untouched people
    population = nx.Graph()
    males_middle_age: set[Person] = set()
    females_middle_age: set[Person] = set()
    males_old: set[Person] = set()
    females_old: set[Person] = set()
    for p in individuals:
        if p.age < 25:
            population.add_node(p)
        elif 25 <= p.age < 50:
            if p.sex == Sex.MALE:
                males_middle_age.add(p)
            else:
                females_middle_age.add(p)
        elif p.sex == Sex.MALE:
            males_old.add(p)
        else:
            females_old.add(p)

    couple_percent = 0.75
    # try to pair middle age persons
    population = nx.union(population, pair_couples(couple_percent, males_middle_age, females_middle_age))
    population = nx.union(population, pair_couples(couple_percent, males_old, females_old))
    return population

def visualize_population(graph):
    import matplotlib.pyplot as plt
    """Visualizes the population graph with NetworkX and Matplotlib."""
    plt.figure(figsize=(15, 15))

    # Position nodes using a spring layout for clarity
    pos = nx.spring_layout(graph, seed=42)

    # Separate edges by relationship type for coloring
    couple_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["relationship"] == "couple"]
    child_edges = [(u, v) for u, v, d in graph.edges(data=True) if d["relationship"] == "child"]

    # Draw nodes
    nx.draw_networkx_nodes(graph, pos, node_size=300, node_color="skyblue")

    # Draw edges with different colors for relationships
    nx.draw_networkx_edges(graph, pos, edgelist=couple_edges, edge_color="green", label="Couple")
    nx.draw_networkx_edges(graph, pos, edgelist=child_edges, edge_color="orange", label="Parent-Child")

    # Create labels using the `Person` dataclass attributes
    labels = {
        node: node.fullname
        for node in graph.nodes
    }
    nx.draw_networkx_labels(graph, pos, labels, font_size=8)

    # Add legend for edge colors
    legend_elements = [
        Line2D([0], [0], color="green", lw=2, label="Couple"),
        Line2D([0], [0], color="orange", lw=2, label="Parent-Child")
    ]
    plt.legend(handles=legend_elements, loc="upper right")
    plt.title("Population Graph", fontsize=16)
    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    base_pop = base_individuals(1000)
    population: nx.Graph = random_families(base_pop)
    persons = pd.DataFrame(population.nodes)
    relationships = pd.DataFrame([(src.unique_id, dst.unique_id) for (src, dst) in population.edges], columns=["src", "dst"])
    persons.to_csv(out_data_file("golden_records_nodes.csv"), index=False)
    relationships.to_csv(out_data_file("golden_records_edges.csv"), index=False)
