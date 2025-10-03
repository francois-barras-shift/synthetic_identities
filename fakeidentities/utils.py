import os
import unicodedata
from pathlib import Path

import pandas as pd

PROJECT_ROOT_PATH = Path(__file__).parent.parent
DATA_RAW_PATH = os.path.join(PROJECT_ROOT_PATH, "data_raw")
DATA_OUT_PATH = os.path.join(PROJECT_ROOT_PATH, "data_out")
CONFIG_PATH = os.path.join(PROJECT_ROOT_PATH, "config")

def raw_data_file(file_name: str) -> str:
    return os.path.join(DATA_RAW_PATH, file_name)

def config_file(file_name: str) -> str:
    return os.path.join(CONFIG_PATH, file_name)

def out_data_file(file_name: str) -> str:
    return os.path.join(DATA_OUT_PATH, file_name)

def group_by_name_sorted_desc(df: pd.DataFrame) -> pd.DataFrame:
    by_name = df.groupby('name').size().reset_index(name="occurrences")
    return by_name.sort_values('occurrences', ascending=False)


def sanitize_string(input_string):
    # Normalize the string to NFKD form and remove diacritical marks
    normalized = unicodedata.normalize('NFKD', input_string)
    sanitized = ''.join(c for c in normalized if not unicodedata.combining(c))
    return sanitized.lower()  # Convert to lowercase