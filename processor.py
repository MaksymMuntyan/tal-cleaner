# processor.py
import os
import pandas as pd

from cleaner import detect
from cleaner import clean_names
from cleaner import clean_domains
from cleaner.utils import save_clean_file

HEADER_KEYWORDS = {
    'account', 'company', 'name', 'domain', 'website', 'url', 'list', 
    'organization', 'customer', 'prospect'
}

# Global DataFrame to track TAL info
tal_info_columns = ['file_name', 'type', 'original_rows', 'cleaned_rows']
tal_info_df = pd.DataFrame(columns=tal_info_columns)

def _has_header(file_path: str) -> bool:
    """Peeks at the first row of a file to check for header keywords."""
    try:
        if file_path.endswith(('.xls', '.xlsx')):
            df_peek = pd.read_excel(file_path, header=None, nrows=1)
        else:
            df_peek = pd.read_csv(file_path, header=None, nrows=1, encoding='utf-8-sig')
        
        for val in df_peek.iloc[0].values:
            if not isinstance(val, str):
                continue
            for keyword in HEADER_KEYWORDS:
                if keyword in val.lower():
                    return True
        return False
    except Exception:
        return False

def process_single_file(file_path):
    """Process a single CSV/Excel file."""
    global tal_info_df

    header_row = 0 if _has_header(file_path) else None
    if file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path, header=header_row)
    else:
        df = pd.read_csv(file_path, header=header_row, encoding='utf-8-sig')

    main_col = detect.detect_column(df)
    original_row_count = df[main_col].notna().sum()
    col_type = detect.detect_type(df[main_col])

    if col_type == 'domain':
        df[main_col] = clean_domains.clean_company_domains(df[main_col])
    else:
        df[main_col] = clean_names.clean_company_names(df[main_col])

    is_not_duplicate = ~df[main_col].duplicated(keep='first')
    df[main_col] = df[main_col].where(is_not_duplicate, pd.NA)
    df.dropna(subset=[main_col], inplace=True)
    
    output_df = df[[main_col]]
    save_clean_file(file_path, output_df, make_new_folder=False)
    
    cleaned_rows_count = len(output_df)
    tal_info_df = append_tal_info(tal_info_df, file_path, col_type, original_row_count, cleaned_rows_count)

    tal_info_path = os.path.join(os.path.dirname(file_path), 'tal_info.xlsx')
    tal_info_df.to_excel(tal_info_path, index=False)
    print(f"TAL info saved to {tal_info_path}")

def process_folder(folder_path):
    """Process all CSV/Excel files in a folder."""
    global tal_info_df
    tal_info_df = pd.DataFrame(columns=tal_info_columns)

    for filename in os.listdir(folder_path):
        if filename.endswith(('.csv', '.xls', '.xlsx')):
            file_path = os.path.join(folder_path, filename)

            header_row = 0 if _has_header(file_path) else None
            if filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path, header=header_row)
            else:
                df = pd.read_csv(file_path, header=header_row, encoding='utf-8-sig')

            main_col = detect.detect_column(df)
            original_row_count = df[main_col].notna().sum()
            col_type = detect.detect_type(df[main_col])

            if col_type == 'domain':
                df[main_col] = clean_domains.clean_company_domains(df[main_col])
            else:
                df[main_col] = clean_names.clean_company_names(df[main_col])
            
            is_not_duplicate = ~df[main_col].duplicated(keep='first')
            df[main_col] = df[main_col].where(is_not_duplicate, pd.NA)
            df.dropna(subset=[main_col], inplace=True)
            
            output_df = df[[main_col]]
            save_clean_file(file_path, output_df, make_new_folder=True)

            cleaned_rows_count = len(output_df)
            tal_info_df = append_tal_info(tal_info_df, file_path, col_type, original_row_count, cleaned_rows_count)

    # **FIX:** The save path for the report now points to the 'clean_companies' subfolder.
    clean_folder_path = os.path.join(folder_path, 'clean_companies')
    os.makedirs(clean_folder_path, exist_ok=True)
    tal_info_path = os.path.join(clean_folder_path, 'tal_info.xlsx')
    
    tal_info_df.to_excel(tal_info_path, index=False)
    print(f"TAL info saved to {tal_info_path}")

def append_tal_info(tal_info_df, file_path, col_type, original_rows, cleaned_rows):
    """Add a row to the TAL info DataFrame."""
    file_name = os.path.basename(file_path)
    new_row = {
        'file_name': file_name,
        'type': col_type,
        'original_rows': original_rows,
        'cleaned_rows': cleaned_rows
    }
    return pd.concat([tal_info_df, pd.DataFrame([new_row])], ignore_index=True)