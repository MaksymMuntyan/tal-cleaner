# cleaner/utils.py
import os
import pandas as pd

def _is_likely_domain(s) -> bool:
    """
    Checks if a single string is likely a domain name by analyzing its structure,
    even if it's a full URL.
    """
    if not isinstance(s, str):
        return False
    
    s = s.strip().lower()

    # Temporarily remove the protocol for a cleaner check
    if '://' in s:
        s = s.split('://', 1)[1]

    # **THE FIX:** Isolate the domain part from any path, query, etc.
    domain_part = s.split('/')[0]

    # Now, run structural checks on just the domain part
    if ' ' in domain_part:
        return False
    if '.' not in domain_part:
        return False
        
    parts = domain_part.split('.')
    if len(parts) < 2:
        return False
        
    tld = parts[-1]
    if not tld or not tld.isalpha() or not (2 <= len(tld) <= 6):
        return False

    return True

def save_clean_file(original_path: str, df: pd.DataFrame, make_new_folder: bool = False):
    """
    Save cleaned DataFrame to CSV.
    """
    folder = os.path.dirname(original_path)
    filename = os.path.basename(original_path)
    name, ext = os.path.splitext(filename)
    new_name = f"{name}_clean.csv"

    if make_new_folder:
        clean_folder = os.path.join(folder, 'clean_companies')
        os.makedirs(clean_folder, exist_ok=True)
        save_path = os.path.join(clean_folder, new_name)
    else:
        save_path = os.path.join(folder, new_name)
        
    df.to_csv(save_path, index=False, header=False, encoding='utf-8-sig')
    print(f"Saved cleaned file: {save_path}")