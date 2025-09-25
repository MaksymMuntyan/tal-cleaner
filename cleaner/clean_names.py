# cleaner/clean_names.py
import pandas as pd
import re
from cleaner.utils import _is_likely_domain

# The definitive, expanded list of suffixes.
SUFFIXES_TO_REMOVE = [
    'Inc', 'Corp', 'Corporation', 'Incorporated', 'Company', 'Co', 'Technologies',
    'Holdings', 'Group', 'Solutions', 'Services', 'Systems', 'Associates',
    'LLC', 'Ltd', 'LLP', 'LP', 'PC', 'PLC', 'GmbH', 'AG', 'SARL', 'SA',
    'AB', 'BV', 'SpA', 'Srl', 'SL', 'SA de CV', 'Platforms', 'Stores',
    'Motors', 'Wholesale', 'Coffee', 'International', 'Service', 'Association',
    'Business'
]

# A dictionary for special capitalization cases that .title() gets wrong.
SPECIAL_CASES = {
    'Jpmorgan': 'JPMorgan',
    'Hp': 'HP',
    'Ibm': 'IBM'
}

def clean_company_name(name):
    """
    Cleans a single company name string using a robust, multi-pass process.
    """
    if pd.isna(name):
        return name

    # Pass 1: Initial, aggressive cleanup of junk characters and whitespace.
    name = str(name)
    name = re.sub(r'\s+', ' ', name).strip() # Normalize whitespace
    name = re.sub(r'\s*\(.*\)\s*$', '', name).strip() # Remove parentheticals
    name = re.sub(r'\s+[-–—]\s+.*', '', name).strip() # Remove dash separators

    # Pass 2: Handle the specific "The X Company" format.
    the_company_match = re.match(r'(?i)^The\s+(.+?)\s+Company$', name)
    if the_company_match:
        name = the_company_match.group(1).strip()

    # Pass 3: Iteratively remove known suffixes from the end of the string.
    # This is a more direct and reliable method than a single complex regex.
    # We loop multiple times to handle cases like "Company, Inc."
    for _ in range(2): # Allow for up to 2 suffix removals
        # Create the regex pattern dynamically inside the loop for the current name
        suffix_pattern = r'[\s,&\-]+\b(?:' + r'|'.join(re.escape(s) for s in SUFFIXES_TO_REMOVE) + r')\b\.?$'
        name = re.sub(suffix_pattern, '', name, flags=re.IGNORECASE).strip()

    # Pass 4: Final capitalization and special case fixes.
    name = name.title()
    name = re.sub(r"([A-Za-z])['’]S\b", r"\1's", name)

    # Apply special casing rules
    for wrong, right in SPECIAL_CASES.items():
        if wrong in name:
            name = name.replace(wrong, right)

    # Final check for any names that might be domains
    if _is_likely_domain(name):
        name = name.lower()

    return name

def clean_company_names(series: pd.Series) -> pd.Series:
    """
    Applies the robust cleaning function to an entire series of company names.
    """
    return series.apply(clean_company_name)