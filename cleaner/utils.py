# cleaner/utils.py
import os
import pandas as pd
import openpyxl
from openpyxl.styles import Border, Side, Font

def _is_likely_domain(s) -> bool:
    """
    Checks if a single string is likely a domain name by analyzing its structure,
    even if it's a full URL.
    """
    if not isinstance(s, str):
        return False
    
    s = s.strip().lower()

    if '://' in s:
        s = s.split('://', 1)[1]

    domain_part = s.split('/')[0]

    if ' ' in domain_part or '.' not in domain_part:
        return False
        
    parts = domain_part.split('.')
    if len(parts) < 2:
        return False
        
    tld = parts[-1]
    if not tld or not tld.isalpha() or not (2 <= len(tld) <= 6):
        return False

    return True

def save_clean_file(original_path: str, df: pd.DataFrame, col_type: str, make_new_folder: bool = False, sheet_name: str = None):
    """
    Save cleaned DataFrame to CSV with a dynamic name based on content type and sheet name.
    """
    folder = os.path.dirname(original_path)
    original_filename = os.path.basename(original_path)
    name, ext = os.path.splitext(original_filename)

    if sheet_name:
        new_name = f"{name}_{sheet_name}_clean_{col_type}.csv"
    else:
        new_name = f"{name}_clean_{col_type}.csv"

    if make_new_folder:
        clean_folder = os.path.join(folder, 'clean_companies')
        os.makedirs(clean_folder, exist_ok=True)
        save_path = os.path.join(clean_folder, new_name)
    else:
        save_path = os.path.join(folder, new_name)
        
    df.to_csv(save_path, index=False, header=False, encoding='utf-8-sig')
    print(f"Saved cleaned file: {save_path}")

def format_tal_info_sheet(file_path: str):
    """
    Applies advanced formatting to the tal_info.xlsx report.
    - Auto-fits column widths.
    - Adds borders to all cells with data.
    - Hides gridlines.
    """
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook.active
    
    # Define the border style
    thin_border = Border(left=Side(style='thin'), 
                         right=Side(style='thin'), 
                         top=Side(style='thin'), 
                         bottom=Side(style='thin'))
    
    # Auto-fit columns and apply borders
    for col in worksheet.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        for cell in col:
            # Apply border to any cell with a value
            if cell.value:
                cell.border = thin_border
            # Find the max length for column width
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        # Set column width with a little extra padding
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column].width = adjusted_width

    # Hide gridlines
    worksheet.sheet_view.showGridLines = False

    # Save the changes
    workbook.save(file_path)