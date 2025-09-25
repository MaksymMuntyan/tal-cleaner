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
    The main detection engine. Finds the best column and its type based on a prioritized set of rules.
    """
    name_col, domain_col = None, None
    
    # Priority 1: Scan headers for keywords
    for col in df.columns:
        col_lower = str(col).lower()
        
        # Use an if/elif structure to prevent a single column from matching both types.
        # Domain keywords are typically more specific, so we check for them first.
        if not domain_col and any(keyword in col_lower for keyword in DOMAIN_KEYWORDS):
            domain_col = col
        elif not name_col and any(keyword in col_lower for keyword in NAME_KEYWORDS):
            name_col = col

    # Priority 2: Apply the decision logic
    if name_col and domain_col:
        name_count = df[name_col].notna().sum()
        domain_count = df[domain_col].notna().sum()
        
        if name_count > 0 and (domain_count / name_count) < 0.70:
            return name_col, 'name'
        else:
            return domain_col, 'domain'
            
    if domain_col:
        return domain_col, 'domain'
        
    if name_col:
        return name_col, 'name'
        
    # Case 4: No keyword matches, use the fallback method
    fallback_col = detect_column_by_content(df)
    fallback_type = detect_type_by_content(df[fallback_col])
    return fallback_col, fallback_type