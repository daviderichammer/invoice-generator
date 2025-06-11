#!/usr/bin/env python3
"""
Check the exact orange color from the reference rows and find all NES01-5541 entries
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sheets_reader_enhanced import SheetsReaderEnhanced
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

def get_reference_color_and_find_all_entries():
    """Get the exact orange color from reference rows and find all NES01-5541 entries."""
    try:
        # Load configuration
        with open("config_secure.json", 'r') as f:
            config = json.load(f)
        
        # Initialize enhanced sheets reader
        sheets_reader = SheetsReaderEnhanced(
            credentials_path=config["google_sheets"]["credentials_path"],
            spreadsheet_id=config["google_sheets"]["spreadsheet_id"]
        )
        
        print("🔍 Getting exact orange color from reference rows 932-938...")
        
        # Build the Sheets API service to get formatting
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
        
        reference_color = None
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
                            print(f"✅ Found reference orange color: {reference_color}")
        
        if not reference_color:
            print("⚠️  Could not get reference color, using default orange")
            reference_color = {"red": 1.0, "green": 0.8, "blue": 0.4, "alpha": 1.0}
        
        # Now find ALL entries for NES01-5541
        print(f"\n🔍 Finding ALL entries for NES01-5541...")
        
        worksheet = sheets_reader.spreadsheet.worksheet("Sheet1")
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        # Find column indices
        date_col = sheets_reader._find_column_index(headers, ['date'])
        hours_col = sheets_reader._find_column_index(headers, ['hours'])
        category_col = sheets_reader._find_column_index(headers, ['category'])
        task_col = sheets_reader._find_column_index(headers, ['task', 'work', 'task/work'])
        persons_col = sheets_reader._find_column_index(headers, ['persons'])
        invoice_col = sheets_reader._find_column_index(headers, ['invoice'])
        status_col = sheets_reader._find_column_index(headers, ['paid', 'status'])
        
        nes_5541_entries = []
        
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) > max(date_col, hours_col, category_col, task_col, persons_col, invoice_col, status_col):
                invoice = row[invoice_col].strip() if invoice_col < len(row) else ""
                status = row[status_col].strip().upper() if status_col < len(row) else ""
                
                # Look for entries with NES01-5541 invoice number that are still WIP
                if invoice == "NES01-5541" and status == "WIP":
                    try:
                        hours_str = row[hours_col].strip() if hours_col < len(row) else "0"
                        hours = float(hours_str)
                        
                        if hours > 0:
                            entry = {
                                "date": row[date_col].strip() if date_col < len(row) else "",
                                "hours": hours,
                                "category": row[category_col].strip() if category_col < len(row) else "Enhancement",
                                "description": row[task_col].strip() if task_col < len(row) else "",
                                "persons": row[persons_col].strip() if persons_col < len(row) else "",
                                "invoice": "NES01-5541",
                                "row_number": row_idx
                            }
                            nes_5541_entries.append(entry)
                            
                            print(f"Row {row_idx}: {entry['date']} | {entry['hours']}h | {entry['description'][:50]}... | Status: {status}")
                            
                    except ValueError:
                        continue
        
        if not nes_5541_entries:
            print("ℹ️  No remaining WIP entries found for NES01-5541")
            return True
        
        print(f"\n📊 Found {len(nes_5541_entries)} remaining WIP entries for NES01-5541")
        total_hours = sum(entry["hours"] for entry in nes_5541_entries)
        print(f"⏱️  Total Hours: {total_hours}")
        
        # Ask for confirmation to fix all entries
        print(f"\n🔧 Fix ALL {len(nes_5541_entries)} entries for NES01-5541 with correct orange color? (y/n): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            print("🔧 Fixing ALL NES01-5541 entries with correct orange color...")
            
            # Update using the correct reference color
            success = update_entries_with_correct_color(
                sheets_reader, 
                nes_5541_entries, 
                reference_color,
                config["google_sheets"]["credentials_path"],
                config["google_sheets"]["spreadsheet_id"]
            )
            
            if success:
                print("✅ Successfully fixed ALL NES01-5541 entries with correct orange color")
                print("🎨 All rows should now match the reference formatting exactly")
                return True
            else:
                print("⚠️  Warning: Could not fix all entries")
                return False
        else:
            print("ℹ️  Fix skipped")
            return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_entries_with_correct_color(sheets_reader, entries, reference_color, credentials_path, spreadsheet_id):
    """Update entries with the exact reference color."""
    try:
        worksheet = sheets_reader.spreadsheet.worksheet("Sheet1")
        
        # Get headers to find the 'Status' column
        headers = worksheet.row_values(1)
        status_col_index = sheets_reader._find_column_index(headers, ['paid', 'status']) + 1
        
        # Prepare batch updates
        value_updates = []
        format_requests = []
        
        for entry in entries:
            row_number = entry.get("row_number")
            if row_number:
                # Update the 'Status' column to 'Billed'
                cell_address = f"{chr(64 + status_col_index)}{row_number}"
                value_updates.append({
                    'range': cell_address,
                    'values': [['Billed']]
                })
                
                # Create format request for the entire row (columns A through G)
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
        
        if value_updates:
            # Batch update values
            worksheet.batch_update(value_updates)
            print(f"✅ Updated {len(value_updates)} entries from WIP to Billed")
            
            # Apply formatting using the Sheets API
            if format_requests:
                body = {
                    "requests": format_requests
                }
                
                # Build the Sheets API service
                credentials = Credentials.from_service_account_file(
                    credentials_path, 
                    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                )
                service = build('sheets', 'v4', credentials=credentials)
                
                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body
                ).execute()
                
                print(f"🎨 Applied correct orange highlighting to {len(format_requests)} rows")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error updating entries: {e}")
        return False

if __name__ == "__main__":
    get_reference_color_and_find_all_entries()

