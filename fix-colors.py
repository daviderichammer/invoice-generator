#!/usr/bin/env python3
"""
Fix the color of the previously updated rows to match the reference
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sheets_reader_enhanced import SheetsReaderEnhanced
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

def fix_existing_billed_rows_color():
    """Fix the color of existing Billed rows for NES01-5541 to match reference."""
    try:
        # Load configuration
        with open("config_secure.json", 'r') as f:
            config = json.load(f)
        
        # Initialize enhanced sheets reader
        sheets_reader = SheetsReaderEnhanced(
            credentials_path=config["google_sheets"]["credentials_path"],
            spreadsheet_id=config["google_sheets"]["spreadsheet_id"]
        )
        
        print("🎨 Fixing color of existing Billed rows for NES01-5541...")
        
        # Get the correct reference color
        credentials = Credentials.from_service_account_file(
            config["google_sheets"]["credentials_path"], 
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        # Get formatting from reference row (932)
        response = service.spreadsheets().get(
            spreadsheetId=config["google_sheets"]["spreadsheet_id"],
            ranges=['Sheet1!A932:G932'],
            includeGridData=True
        ).execute()
        
        reference_color = {"red": 1, "green": 0.6}  # From previous detection
        if 'sheets' in response and len(response['sheets']) > 0:
            sheet_data = response['sheets'][0]
            if 'data' in sheet_data and len(sheet_data['data']) > 0:
                grid_data = sheet_data['data'][0]
                if 'rowData' in grid_data and len(grid_data['rowData']) > 0:
                    row_data = grid_data['rowData'][0]
                    if 'values' in row_data and len(row_data['values']) > 0:
                        cell_data = row_data['values'][0]
                        if 'effectiveFormat' in cell_data and 'backgroundColor' in cell_data['effectiveFormat']:
                            reference_color = cell_data['effectiveFormat']['backgroundColor']
        
        print(f"🎨 Using reference color: {reference_color}")
        
        # Find all Billed entries for NES01-5541
        worksheet = sheets_reader.spreadsheet.worksheet("Sheet1")
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        # Find column indices
        invoice_col = sheets_reader._find_column_index(headers, ['invoice'])
        status_col = sheets_reader._find_column_index(headers, ['paid', 'status'])
        
        billed_rows = []
        
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) > max(invoice_col, status_col):
                invoice = row[invoice_col].strip() if invoice_col < len(row) else ""
                status = row[status_col].strip().upper() if status_col < len(row) else ""
                
                # Look for entries with NES01-5541 invoice number that are Billed
                if invoice == "NES01-5541" and status == "BILLED":
                    billed_rows.append(row_idx)
                    print(f"Found Billed row {row_idx}: {row[0]} | {row[1]}h")
        
        if not billed_rows:
            print("ℹ️  No Billed entries found for NES01-5541")
            return True
        
        print(f"\n🎨 Fixing color for {len(billed_rows)} Billed rows...")
        
        # Create format requests for all billed rows
        format_requests = []
        
        for row_number in billed_rows:
            format_request = {
                "repeatCell": {
                    "range": {
                        "sheetId": 0,  # Assuming first sheet
                        "startRowIndex": row_number - 1,  # 0-based for API
                        "endRowIndex": row_number,
                        "startColumnIndex": 0,  # Column A
                        "endColumnIndex": 7   # Column G (0-based, so 7 means up to column G)
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": reference_color
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            }
            format_requests.append(format_request)
        
        if format_requests:
            body = {
                "requests": format_requests
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=config["google_sheets"]["spreadsheet_id"],
                body=body
            ).execute()
            
            print(f"✅ Fixed color for {len(format_requests)} Billed rows")
            print("🎨 All NES01-5541 rows should now have the correct orange color")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error fixing colors: {e}")
        return False

if __name__ == "__main__":
    fix_existing_billed_rows_color()

