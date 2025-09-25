# cleaner/clean_domains.py
import pandas as pd
import re

# A set of common multi-part public suffixes. This is necessary to correctly
# parse domains like 'google.co.uk' without an external library like tldextract.
MULTI_PART_SUFFIXES = {
    '.co.uk', '.org.uk', '.com.au', '.net.au', '.com.sa', '.com.br',
    '.com.mx', '.co.jp', '.co.za', '.co.in', '.com.cn', '.com.tw'
}

def clean_company_domains(series: pd.Series) -> pd.Series:
    """
    Cleans and extracts the root domain from a series of URLs or domains.
    e.g., 'http://www.google.co.uk/path' -> 'google.co.uk'
    """
    def clean_domain(domain):
        if pd.isna(domain):
            return pd.NA

        # 1. Basic cleaning: lowercase, strip whitespace.
        domain = str(domain).strip().lower()

        # 2. Remove protocol (http://, https://, etc.)
        domain = re.sub(r'^[a-z]+://', '', domain)

        # 3. Remove 'www' prefix.
        domain = re.sub(r'^www\d*\.', '', domain)

        # 4. Remove path, query parameters, fragments, etc.
        domain = domain.split('/')[0].split('?')[0].split('#')[0]

        # 5. Handle multi-part suffixes first (e.g., .co.uk, .com.sa)
        for suffix in MULTI_PART_SUFFIXES:
            if domain.endswith(suffix):
                # Remove the suffix to find the part before it
                base = domain[:-len(suffix)]
                # The main domain is the last part of the base
                main_domain_part = base.split('.')[-1]
                return main_domain_part + suffix

        # 6. If not a multi-part suffix, handle standard domains (e.g., .com, .org)
        parts = domain.split('.')
        if len(parts) >= 2:
            # Join the last two parts to form the domain
            return '.'.join(parts[-2:])

        # If all else fails, it's not a valid-looking domain.
        return pd.NA

    return series.apply(clean_domain)