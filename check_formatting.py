#!/usr/bin/env python3
"""
Check the formatting of rows 932-938 to understand the orange highlighting pattern
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sheets_reader_secure import SheetsReader
import json

def check_billed_formatting():
    """Check the formatting of the example billed rows."""
    try:
        # Load configuration
        with open("config_secure.json", 'r') as f:
            config = json.load(f)
        
        # Initialize sheets reader
        sheets_reader = SheetsReader(
            credentials_path=config["google_sheets"]["credentials_path"],
            spreadsheet_id=config["google_sheets"]["spreadsheet_id"]
        )
        
        print("🔍 Checking formatting of example billed rows (932-938)...")
        
        # Get the worksheet
        worksheet = sheets_reader.spreadsheet.worksheet("Sheet1")
        
        # Get data from rows 932-938
        range_name = "A932:G938"
        values = worksheet.get(range_name, value_render_option='FORMATTED_VALUE')
        
        print(f"\n📊 Data in rows 932-938:")
        for i, row in enumerate(values, start=932):
            if len(row) >= 7:
                date = row[0] if len(row) > 0 else ""
                hours = row[1] if len(row) > 1 else ""
                category = row[2] if len(row) > 2 else ""
                task = row[3] if len(row) > 3 else ""
                persons = row[4] if len(row) > 4 else ""
                invoice = row[5] if len(row) > 5 else ""
                paid = row[6] if len(row) > 6 else ""
                
                print(f"Row {i}: {date} | {hours}h | {category} | {task[:30]}... | {persons} | {invoice} | {paid}")
        
        # Try to get formatting information using the spreadsheet API
        print(f"\n🎨 Checking cell formatting...")
        
        # Get formatting for the range
        request = {
            'ranges': [range_name],
            'includeGridData': True
        }
        
        response = sheets_reader.spreadsheet.batch_get(ranges=[range_name], 
                                                      include_grid_data=True)
        
        if 'sheets' in response and len(response['sheets']) > 0:
            sheet_data = response['sheets'][0]
            if 'data' in sheet_data and len(sheet_data['data']) > 0:
                grid_data = sheet_data['data'][0]
                if 'rowData' in grid_data:
                    print(f"Found formatting data for {len(grid_data['rowData'])} rows")
                    
                    for i, row_data in enumerate(grid_data['rowData'], start=932):
                        if 'values' in row_data:
                            for j, cell_data in enumerate(row_data['values']):
                                if 'effectiveFormat' in cell_data:
                                    format_data = cell_data['effectiveFormat']
                                    if 'backgroundColor' in format_data:
                                        bg_color = format_data['backgroundColor']
                                        print(f"Row {i}, Col {j}: Background color: {bg_color}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking formatting: {e}")
        return False

if __name__ == "__main__":
    check_billed_formatting()

