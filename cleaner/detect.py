# cleaner/detect.py
import pandas as pd
from cleaner.utils import _is_likely_domain

# --- Keyword sets for header detection ---
NAME_KEYWORDS = {
    'name', 'account', 'company', 'organization', 'customer', 'prospect', 'client'
}
DOMAIN_KEYWORDS = {
    'domain', 'website', 'url', 'web address'
}

def detect_column_by_content(df: pd.DataFrame) -> str:
    """
    FALLBACK METHOD: Detects the main column by selecting the one
    with the most non-null values.
    """
    max_count = -1
    main_col = None
    for col in df.columns:
        count = df[col].notna().sum()
        if count > max_count:
            max_count = count
            main_col = col
    if main_col is None and not df.columns.empty:
        main_col = df.columns[0]
    return main_col

def detect_type_by_content(series: pd.Series) -> str:
    """
    FALLBACK METHOD: Determines if a series contains names or domains
    by analyzing its content.
    """
    series = series.dropna()
    if series.empty:
        return 'name'
    domain_count = series.apply(_is_likely_domain).sum()
    if (domain_count / len(series)) >= 0.5:
        return 'domain'
    else:
        return 'name'

def find_target_column_and_type(df: pd.DataFrame) -> tuple:
    """
    The main detection engine with added print statements for debugging.
    """
    print("\n--- Starting Column Detection ---")
    print(f"Scanning headers: {df.columns.tolist()}")
    name_col, domain_col = None, None
    
    # Priority 1: Scan headers for keywords
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in NAME_KEYWORDS):
            name_col = col
        if any(keyword in col_lower for keyword in DOMAIN_KEYWORDS):
            domain_col = col

    print(f"Found potential name column: '{name_col}'")
    print(f"Found potential domain column: '{domain_col}'")

    # Priority 2: Apply the decision logic
    if name_col and domain_col:
        print("\n--- Both column types found, applying 70% rule ---")
        name_count = df[name_col].notna().sum()
        domain_count = df[domain_col].notna().sum()
        
        print(f"Count of non-empty names in '{name_col}': {name_count}")
        print(f"Count of non-empty domains in '{domain_col}': {domain_count}")
        
        if name_count > 0:
            ratio = domain_count / name_count
            print(f"Ratio (Domains / Names): {ratio:.2f}")
            if ratio < 0.70:
                print("Decision: Ratio is < 0.70. Using NAMES column.")
                return name_col, 'name'
            else:
                print("Decision: Ratio is >= 0.70. Using DOMAINS column.")
                return domain_col, 'domain'
        else: # Handle case with no names
            print("Decision: No names found. Defaulting to DOMAINS column.")
            return domain_col, 'domain'
            
    if domain_col:
        print("Decision: Only domain column found.")
        return domain_col, 'domain'
        
    if name_col:
        print("Decision: Only name column found.")
        return name_col, 'name'
        
    print("\n--- No keyword matches found, using fallback method ---")
    fallback_col = detect_column_by_content(df)
    fallback_type = detect_type_by_content(df[fallback_col])
    print(f"Fallback decision: Chose column '{fallback_col}' with type '{fallback_type}'")
    return fallback_col, fallback_type