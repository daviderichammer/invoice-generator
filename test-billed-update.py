#!/usr/bin/env python3
"""
Test script to check current WIP entries and test the billed formatting update
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sheets_reader_enhanced import SheetsReaderEnhanced
import json

def test_billed_update():
    """Test updating specific rows to Billed status with orange formatting."""
    try:
        # Load configuration
        with open("config_secure.json", 'r') as f:
            config = json.load(f)
        
        # Initialize enhanced sheets reader
        sheets_reader = SheetsReaderEnhanced(
            credentials_path=config["google_sheets"]["credentials_path"],
            spreadsheet_id=config["google_sheets"]["spreadsheet_id"]
        )
        
        print("🔍 Checking for entries that should be marked as Billed for NES01-5541...")
        
        # Get the worksheet
        worksheet = sheets_reader.spreadsheet.worksheet("Sheet1")
        
        # Get all values to find the NES01-5541 entries
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        # Find column indices
        date_col = sheets_reader._find_column_index(headers, ['date'])
        hours_col = sheets_reader._find_column_index(headers, ['hours'])
        category_col = sheets_reader._find_column_index(headers, ['category'])
        task_col = sheets_reader._find_column_index(headers, ['task', 'work', 'task/work'])
        persons_col = sheets_reader._find_column_index(headers, ['persons'])
        invoice_col = sheets_reader._find_column_index(headers, ['invoice'])
        paid_col = sheets_reader._find_column_index(headers, ['paid'])
        
        # Find entries that should be for NES01-5541 (currently WIP)
        target_entries = []
        
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) <= max(date_col, hours_col, category_col, task_col, persons_col, invoice_col, paid_col):
                continue
            
            # Check if this entry should be for NES01-5541
            date = row[date_col].strip() if date_col < len(row) else ""
            paid_status = row[paid_col].strip().upper() if paid_col < len(row) else ""
            
            # Look for recent entries that are still WIP (should be for NES01-5541)
            if paid_status == "WIP" and date:
                try:
                    hours_str = row[hours_col].strip() if hours_col < len(row) else "0"
                    hours = float(hours_str)
                    category = row[category_col].strip() if category_col < len(row) else "Enhancement"
                    description = row[task_col].strip() if task_col < len(row) else ""
                    persons = row[persons_col].strip() if persons_col < len(row) else ""
                    
                    if hours > 0 and description:
                        entry = {
                            "date": date,
                            "hours": hours,
                            "category": category,
                            "description": description,
                            "persons": persons,
                            "invoice": "NES01-5541",
                            "row_number": row_idx
                        }
                        target_entries.append(entry)
                        
                        print(f"Row {row_idx}: {date} | {hours}h | {category} | {description[:50]}... | {persons}")
                        
                except ValueError:
                    continue
        
        if not target_entries:
            print("ℹ️  No WIP entries found that should be marked as Billed for NES01-5541")
            print("💡 This means the entries may have already been updated, or there are no matching entries")
            return True
        
        print(f"\n📊 Found {len(target_entries)} entries that should be marked as Billed for NES01-5541")
        total_hours = sum(entry["hours"] for entry in target_entries)
        print(f"⏱️  Total Hours: {total_hours}")
        
        # Ask for confirmation
        print(f"\n🔄 Update these {len(target_entries)} entries to 'Billed' status with orange highlighting? (y/n): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            print("🔄 Updating entries to Billed with orange highlighting...")
            success = sheets_reader.update_wip_to_billed_with_formatting(target_entries, "Sheet1")
            if success:
                print("✅ Successfully updated entries to Billed with orange highlighting")
                print("🎨 Rows are now highlighted in orange like the example in rows 932-938")
                return True
            else:
                print("⚠️  Warning: Could not update all entries")
                return False
        else:
            print("ℹ️  Entries left unchanged")
            return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_billed_update()

