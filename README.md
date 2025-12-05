# Synthetic Identity Data Generation - Technical Documentation

## Overview

This repository (`fakeidentities`) implements a comprehensive synthetic identity data generation system designed to create realistic US-based identity records with controlled variations and noise. The system is specifically designed for testing identity matching, entity resolution, and record linkage algorithms.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Base Identity Generation](#base-identity-generation)
3. [Family & Relationship Graph](#family--relationship-graph)
4. [Identity Distortions (Noise)](#identity-distortions-noise)
5. [Phonetic Matching System](#phonetic-matching-system)
6. [Data Sources](#data-sources)
7. [Output Format](#output-format)

---

## Architecture Overview

The system follows a two-stage approach:

1. **Golden Record Generation**: Creates clean, authoritative identity records including individuals and family relationships
2. **Noise Injection**: Applies realistic distortions to create multiple variations of the same latent entity

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA GENERATION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐  │
│  │ Base Individual │ ──▶ │ Family/Relation  │ ──▶ │   Noiser     │  │
│  │   Generator     │     │     Pairing      │     │  (Multiple   │  │
│  │   (Faker)       │     │   (NetworkX)     │     │  Variations) │  │
│  └─────────────────┘     └──────────────────┘     └──────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Base Identity Generation

### Person Data Model (`fakeidentities/person.py`)

Each synthetic person includes the following attributes:

| Field | Type | Description |
|-------|------|-------------|
| `unique_id` | UUID | Unique identifier |
| `firstname` | string | First name |
| `middlename` | string (optional) | Middle name |
| `prefix` | string (optional) | Title prefix (Mr., Mrs., Dr., etc.) |
| `suffix` | string (optional) | Name suffix (Jr., III, MD, etc.) |
| `lastname` | string | Last name |
| `date_of_birth` | date | Birth date |
| `raw_address` | string | Full US address |
| `social_security_number` | string | SSN |
| `sex` | enum | MALE or FEMALE |
| `phone` | string | Phone number |
| `personal_email` | string | Personal email address |
| `corporate_email` | string (optional) | Work email address |

### Generation Process (`fakeidentities/golden_records.py`)

**1. Multi-locale Diversity**

The system uses multiple Faker locales to generate ethnically diverse names:
- US English (70% weight)
- Mexican Spanish (20% weight)
- Indian English (10% weight)

```python
generator: Faker = random.choices([fake_US, fake_MX, fake_IN], weights=[0.7, 0.2, 0.1])[0]
```

**2. Name Components**

- **Prefixes**: Mr., Mrs., Ms., Miss, Dr., Mx., Ind. (Individual), Misc. (20% probability)
- **Suffixes**: MD, DDS, PhD, DVM, Jr., II, III, IV, V (if prefix not present)
- **Middle names**: 50% of individuals have a middle name

**3. Email Generation**

Two types of emails are generated with realistic patterns:

**Corporate Email** (40% have one):
- Pattern 1 (50%): `firstname.lastname@company.com`
- Pattern 2 (50%): `f.lastname@company.com`

**Personal Email**:
- May include birth year or random number
- 30% use a nickname/anonymous pattern
- Various separators (`.`, `-`, `_`, none)

---

## Family & Relationship Graph

### Adjacent Entity Types

The system creates realistic family relationships using NetworkX graphs:

#### 1. Couples (`relationship="couple"`)

**Pairing Logic**:
- Adults aged 25-50 and 50+ are paired separately
- 75% coupling probability for each age group
- Partners are matched by sex (male-female pairs)

**Marriage Effects**:
- 75% stay married (shared address)
- 25% divorce rate
- Name changes for married women:
  - 50%: Takes partner's lastname entirely
  - 30%: Hyphenated name (`original_name + partner_name`)
  - 20%: Keeps maiden name

**Shared Attributes**:
- Married couples share the same address

#### 2. Parent-Child (`relationship="parent"`)

**Child Generation**:
- Number of children determined by Gaussian distribution based on mother's age
- Peak fertility around age 30
- Maximum 4 children per couple
- Childless probability decreases with age

**Child Attributes**:
- **Lastname**: 
  - 75%: Father's lastname
  - 25%: Hyphenated (`father_lastname + mother_lastname`)
- **Address**: Same as parents (if not divorced) or one parent's address (if divorced)
- Children under 25 are not paired into couples

### Graph Structure

```
                    [Partner M]
                       │
           couple      │      parent
    ┌──────────────────┼──────────────────┐
    │                  │                  │
[Partner F]        [Child 1]          [Child 2]
```

---

## Identity Distortions (Noise)

The noise system (`fakeidentities/noise/`) creates multiple variations of the same entity to simulate real-world data quality issues.

### PersonNoiser Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `p_missing_ssn` | 0.4 | Probability SSN is null |
| `p_missing_middlename` | 0.2 | Probability middle name is null |
| `p_missing_dob` | 0.25 | Probability DOB is missing |
| `p_missing_prefix` | 0.2 | Probability title prefix is missing |
| `p_missing_suffix` | 0.2 | Probability suffix is missing |
| `p_missing_email` | 0.2 | Probability email is null |
| `p_missing_sex` | 0.3 | Probability sex is null |
| `p_missing_phone` | 0.2 | Probability phone is null |

### Distortion Types by Field

#### 1. Name Distortions (`names.py`)

**First Name Variations**:

| Distortion Type | Probability | Example |
|-----------------|-------------|---------|
| Nickname | 15% | `William` → `Bill`, `Robert` → `Bob` |
| Name variant | 15% | `Katherine` → `Catherine`, `Steven` → `Stephen` |
| Phonetic similar | 15% | `Cynthia` → `Synthia` |
| Typo (keyboard) | 15% | `Michael` → `Micheal` |
| Initial (middle names only) | 20% | `James` → `J.` |

**Middle Name Variations**:
- Same as first names but with 20% probability of being reduced to initial

**Last Name Variations**:

| Distortion Type | Probability | Example |
|-----------------|-------------|---------|
| Phonetic similar | 15% | `Smith` → `Smyth` |
| Typo | 15% | `Brown` → `Brovnn` |
| Case variation | 50% | `Smith` → `SMITH` |

**Phonetic Replacement Rules**:

Common phonetic substitutions applied with 50% probability:
```
ph → f     (Stephen → Stefen)
ie → y     (Gracie → Gracy)
ck → k     (Mickey → Miky)
ch → k     (Charlie → Karlie)
w → v      (William → Viliam)
k → c      (Kara → Cara)
c → s      (Cynthia → Synthia)
```

**Character Duplication**:
- 20% chance to remove duplicate letters (`ll` → `l`)
- 10% chance to add duplicate letters (`l` → `ll`)

#### 2. Date of Birth Distortions (`dob.py`)

| Distortion Type | Probability | Example |
|-----------------|-------------|---------|
| Set to default | 25% | Any date → `1970-01-01` |
| Swap month/day | 15% | `03/15/1990` → `15/03/1990` |
| Swap day digits | 10% | `23` → `32` (if valid) |
| Off by one year | 10% | `1990` → `1989` or `1991` |

#### 3. Address Distortions (`address.py`)

Addresses are parsed into components and distorted individually:

| Component | Distortion Type | Probability | Example |
|-----------|-----------------|-------------|---------|
| House number | Missing | 10% | `123` → ∅ |
| House number | Digit typo | 10% | `123` → `132` |
| Street name | Keyboard typo | 15% | `Main` → `Maim` |
| Street suffix | Missing | 10% | `St.` → ∅ |
| Street suffix | Abbreviation toggle | 20% | `Street` ↔ `St.` |
| Direction | Missing | 10% | `NW` → ∅ |
| Direction | Abbreviation toggle | 20% | `Northwest` ↔ `NW` |
| Occupancy type | Missing | 10% | `Apt` → ∅ |
| Occupancy type | Abbreviation toggle | 20% | `Apartment` ↔ `Apt` |
| Secondary number | Missing | 10% | `101` → ∅ |
| Town | Keyboard typo | 20% | `Seattle` → `Seatrle` |
| Postcode | Digit typo | 20% | `98101` → `98110` |

**Supported Address Formats**:
- Standard street addresses
- PO Box addresses
- APO/FPO/DPO military addresses

#### 4. Phone Distortions (`phone.py`)

| Distortion Type | Probability | Example |
|-----------------|-------------|---------|
| Digit swap | 20% per iteration | `555-1234` → `555-1324` |

Two swap iterations are performed, potentially creating multiple swaps.

#### 5. Email Distortions (`email_noiser.py`)

| Distortion Type | Probability | Example |
|-----------------|-------------|---------|
| Keyboard typo in name | 5% | `john.doe` → `johm.doe` |
| Wrong separator | 10% | `john.doe` → `john-doe` |
| Wrong TLD | 15% | `.net` → `.com` |
| Wrong separator in domain | 10% | (if applicable) |

#### 6. Sex Distortions

| Distortion Type | Probability | Description |
|-----------------|-------------|-------------|
| Missing | 30% | Sex set to null |
| Wrong sex | 20% | Random sex assigned |

---

## Phonetic Matching System

### PhoneticDict (`phonetics.py`)

The system uses multiple phonetic encoding algorithms to find similar-sounding names:

1. **Double Metaphone** (primary)
2. **NYSIIS** (secondary)
3. **Soundex** (tertiary)

A name is considered a phonetic match if **2 out of 3** encoders agree:

```python
# Example: Finding phonetic variants of "Steven"
metaphone("Steven") → ['STFN']
soundex("Steven") → 'S315'
nysiis("Steven") → 'STAFAN'

# Matches: Stephen, Stefan, Stephan, etc.
```

### FirstNames Matching (`first_names.py`)

The FirstNames class provides hierarchical matching:

1. **Pure Match**: Exact match in baby names database
2. **Nickname Match**: Lookup in nickname reverse dictionary
3. **Phonetic Match**: Using PhoneticDict

Uses RapidFuzz for string similarity when multiple candidates exist.

---

## Data Sources

### Raw Data Files (`data_raw/`)

| File | Description | Source |
|------|-------------|--------|
| `Names_2010Census.csv` | US Census last names with demographic data | US Census Bureau |
| `baby-names.csv` | Historical US baby names (1880-present) | SSA Baby Names |
| `btn_givennames_synonyms.txt` | Name variants and synonyms | Behind The Name |

### Generated Data (`data_out/`)

| File | Description |
|------|-------------|
| `golden_records_nodes.csv` | Clean identity records |
| `golden_records_edges.csv` | Relationship edges (couples, parent-child) |
| `noisy_persons.csv` | Multiple noisy variations per golden record |
| `name_alternatives.parquet` | Phonetic name variants with occurrence counts |

---

## Output Format

### Generation Configuration

The default noise generation creates multiple variations per entity:

```python
mean = 10        # Average duplicates per person
std_dev = 5      # Standard deviation
min_duplicates = 5  # Minimum duplicates per person
```

### Output Schema

**noisy_persons.csv columns**:
- All Person fields (with distortions)
- `original_id`: Links back to the golden record UUID

**golden_records_edges.csv**:
| Column | Description |
|--------|-------------|
| `src` | Source person UUID |
| `dst` | Destination person UUID |
| `relationship` | Type: "couple" or "parent" |

---

## Usage Example

### Generating Golden Records

```python
from fakeidentities.golden_records import base_individuals, random_families

# Generate 1000 base individuals
base_pop = base_individuals(1000)

# Create family relationships
population = random_families(base_pop)
```

### Generating Noisy Records

```python
from fakeidentities.names import build_firstnames_variants, build_lastnames_phonetics
from fakeidentities.noise.person import PersonNoiser

# Build phonetic dictionaries
variants, phonetics = build_firstnames_variants()

# Initialize noiser
noiser = PersonNoiser(
    firstname_variants=variants,
    firstname_phonetics=phonetics,
    lastname_phonetics=build_lastnames_phonetics()
)

# Generate variations
for person in golden_records:
    for _ in range(num_duplicates):
        noisy_person = noiser.noise(person)
```

---

## Dependencies

Key libraries used:

| Library | Purpose |
|---------|---------|
| `Faker` | Base identity generation |
| `NetworkX` | Family relationship graphs |
| `fuzzy` | Double Metaphone encoding |
| `jellyfish` | Soundex, NYSIIS encoding |
| `nicknames` | Nickname lookup |
| `nlpaug` | Keyboard-based typo generation |
| `RapidFuzz` | String similarity matching |
| `usaddress` | US address parsing |

---

## Summary

This repository provides a robust framework for generating synthetic identity data with:

1. **Diverse base identities** using multi-locale Faker
2. **Realistic family structures** with couples and children
3. **Comprehensive noise injection** covering:
   - Names (phonetic, nicknames, typos)
   - Dates (format errors, digit swaps)
   - Addresses (typos, abbreviations, missing components)
   - Contact information (emails, phones)
   - Missing data simulation

The generated data is ideal for:
- Testing entity resolution algorithms
- Benchmarking record linkage systems
- Training ML models for identity matching
- Evaluating data quality tools
