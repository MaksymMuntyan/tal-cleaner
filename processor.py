# processor.py
import os
import pandas as pd

from cleaner import detect
from cleaner import clean_names
from cleaner import clean_domains
from cleaner.utils import save_clean_file, _is_likely_domain, format_tal_info_sheet

VALUES_TO_REMOVE = {
    'company', 'account', 'account name', 'name', 'organization', 'customer', 
    'prospect', 'client', 'domain', 'company domain', 'website', 'url', 
    'website url', 'web address'
}

# Global DataFrame to track TAL info
tal_info_columns = ['file_name', 'type', 'original_rows', 'cleaned_rows']
tal_info_df = pd.DataFrame(columns=tal_info_columns)

def _process_dataframe(df, file_path, make_new_folder, sheet_name=None):
    """A helper function to run the cleaning process on a single DataFrame."""
    global tal_info_df

    if df.empty:
        print(f"Skipping empty sheet/file: {sheet_name or os.path.basename(file_path)}")
        return

    main_col, col_type = detect.find_target_column_and_type(df)
    
    if main_col is None or main_col not in df.columns:
        print(f"Could not find a valid data column in {sheet_name or os.path.basename(file_path)}. Skipping.")
        return

    if pd.api.types.is_string_dtype(df[main_col]):
        valid_strings = df[main_col].dropna()
        mask = ~valid_strings.str.strip().str.lower().isin(VALUES_TO_REMOVE)
        df = df.loc[mask.index]

    original_row_count = df[main_col].notna().sum()

    if col_type == 'domain':
        df[main_col] = clean_domains.clean_company_domains(df[main_col])
    else:
        df[main_col] = clean_names.clean_company_names(df[main_col])

    is_not_duplicate = ~df[main_col].duplicated(keep='first')
    df[main_col] = df[main_col].where(is_not_duplicate, pd.NA)
    df.dropna(subset=[main_col], inplace=True)
    
    output_df = df[[main_col]]
    
    save_clean_file(file_path, output_df, col_type, make_new_folder=make_new_folder, sheet_name=sheet_name)
    
    cleaned_rows_count = len(output_df)
    
    report_filename = f"{os.path.basename(file_path)} ({sheet_name})" if sheet_name else os.path.basename(file_path)
    tal_info_df = append_tal_info(tal_info_df, report_filename, col_type, original_row_count, cleaned_rows_count)

def process_single_file(file_path):
    """Process a single file, handling multiple Excel sheets if they exist."""
    header_row = 0
    
    if file_path.endswith(('.xls', '.xlsx')):
        try:
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(file_path, header=header_row, sheet_name=sheet_name)
                current_sheet_name = sheet_name if len(xls.sheet_names) > 1 else None
                _process_dataframe(df, file_path, make_new_folder=False, sheet_name=current_sheet_name)
        except Exception:
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(file_path, header=None, sheet_name=sheet_name)
                current_sheet_name = sheet_name if len(xls.sheet_names) > 1 else None
                _process_dataframe(df, file_path, make_new_folder=False, sheet_name=current_sheet_name)
    else: # It's a CSV
        try:
            df = pd.read_csv(file_path, header=header_row, encoding='utf-8-sig')
            _process_dataframe(df, file_path, make_new_folder=False)
        except Exception:
            df = pd.read_csv(file_path, header=None, encoding='utf-8-sig')
            _process_dataframe(df, file_path, make_new_folder=False)

    # **NEW:** Rename columns for the report
    tal_info_df.rename(columns={
        'file_name': 'File Name',
        'type': 'Type',
        'original_rows': 'Original Rows',
        'cleaned_rows': 'Cleaned Rows'
    }, inplace=True)

    tal_info_path = os.path.join(os.path.dirname(file_path), 'tal_info.xlsx')
    tal_info_df.to_excel(tal_info_path, index=False)
    
    # **NEW:** Apply the formatting
    format_tal_info_sheet(tal_info_path)
    
    print(f"TAL info saved to {tal_info_path}")

def process_folder(folder_path):
    """Process all files in a folder, handling multiple Excel sheets."""
    global tal_info_df
    tal_info_df = pd.DataFrame(columns=tal_info_columns)

    for filename in os.listdir(folder_path):
        if filename.endswith(('.csv', '.xls', '.xlsx')):
            file_path = os.path.join(folder_path, filename)
            header_row = 0

            if filename.endswith(('.xls', '.xlsx')):
                try:
                    xls = pd.ExcelFile(file_path)
                    for sheet_name in xls.sheet_names:
                        df = pd.read_excel(file_path, header=header_row, sheet_name=sheet_name)
                        current_sheet_name = sheet_name if len(xls.sheet_names) > 1 else None
                        _process_dataframe(df, file_path, make_new_folder=True, sheet_name=current_sheet_name)
                except Exception:
                    xls = pd.ExcelFile(file_path)
                    for sheet_name in xls.sheet_names:
                        df = pd.read_excel(file_path, header=None, sheet_name=sheet_name)
                        current_sheet_name = sheet_name if len(xls.sheet_names) > 1 else None
                        _process_dataframe(df, file_path, make_new_folder=True, sheet_name=current_sheet_name)
            else: # It's a CSV
                try:
                    df = pd.read_csv(file_path, header=header_row, encoding='utf-8-sig')
                    _process_dataframe(df, file_path, make_new_folder=True)
                except Exception:
                    df = pd.read_csv(file_path, header=None, encoding='utf-8-sig')
                    _process_dataframe(df, file_path, make_new_folder=True)
                    
    # **NEW:** Rename columns for the report
    tal_info_df.rename(columns={
        'file_name': 'File Name',
        'type': 'Type',
        'original_rows': 'Original Rows',
        'cleaned_rows': 'Cleaned Rows'
    }, inplace=True)
                    
    clean_folder_path = os.path.join(folder_path, 'clean_companies')
    os.makedirs(clean_folder_path, exist_ok=True)
    tal_info_path = os.path.join(clean_folder_path, 'tal_info.xlsx')
    
    tal_info_df.to_excel(tal_info_path, index=False)

    # **NEW:** Apply the formatting
    format_tal_info_sheet(tal_info_path)
    
    print(f"TAL info saved to {tal_info_path}")

def append_tal_info(tal_info_df, file_name, col_type, original_rows, cleaned_rows):
    """Add a row to the TAL info DataFrame."""
    new_row = {
        'file_name': file_name,
        'type': col_type,
        'original_rows': original_rows,
        'cleaned_rows': cleaned_rows
    }
    return pd.concat([tal_info_df, pd.DataFrame([new_row])], ignore_index=True)