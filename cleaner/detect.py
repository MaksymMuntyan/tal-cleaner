# cleaner/detect.py
import pandas as pd
from cleaner.utils import _is_likely_domain # Import the shared function

def detect_column(df: pd.DataFrame) -> str:
    """
    Detects the main column by selecting the one with the most non-null values.
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


def detect_type(series: pd.Series) -> str:
    """
    Determines if the series contains company names or domains using a robust structural heuristic.
    """
    series = series.dropna()
    if series.empty:
        return 'name'

    domain_count = series.apply(_is_likely_domain).sum()
    
    if (domain_count / len(series)) >= 0.5:
        return 'domain'
    else:
        return 'name'