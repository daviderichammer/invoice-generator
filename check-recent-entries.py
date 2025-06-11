#!/usr/bin/env python3
"""
Find and show recent entries to understand the current state
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sheets_reader_enhanced import SheetsReaderEnhanced
import json

def check_recent_entries():
    """Check recent entries to understand current state."""
    try:
        # Load configuration
        with open("config_secure.json", 'r') as f:
            config = json.load(f)
        
        # Initialize enhanced sheets reader
        sheets_reader = SheetsReaderEnhanced(
            credentials_path=config["google_sheets"]["credentials_path"],
            spreadsheet_id=config["google_sheets"]["spreadsheet_id"]
        )
        
        print("🔍 Checking recent entries in the spreadsheet...")
        
        # Get the worksheet
        worksheet = sheets_reader.spreadsheet.worksheet("Sheet1")
        
        # Get the last 20 rows to see recent entries
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        print(f"📊 Headers: {headers}")
        print(f"📊 Total rows: {len(all_values)}")
        
        # Show last 20 rows
        print(f"\n📋 Last 20 entries:")
        recent_rows = all_values[-20:] if len(all_values) > 20 else all_values[1:]
        
        for i, row in enumerate(recent_rows):
            row_num = len(all_values) - len(recent_rows) + i + 1
            if len(row) >= 7:
                date = row[0] if len(row) > 0 else ""
                hours = row[1] if len(row) > 1 else ""
                category = row[2] if len(row) > 2 else ""
                task = row[3] if len(row) > 3 else ""
                persons = row[4] if len(row) > 4 else ""
                invoice = row[5] if len(row) > 5 else ""
                paid = row[6] if len(row) > 6 else ""
                
                print(f"Row {row_num}: {date} | {hours}h | {category} | {task[:30]}... | {persons} | {invoice} | {paid}")
        
        # Look for any WIP entries
        print(f"\n🔍 Looking for WIP entries...")
        wip_count = 0
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) > 6:
                paid_status = row[6].strip().upper()
                if paid_status == "WIP":
                    wip_count += 1
                    if wip_count <= 10:  # Show first 10 WIP entries
                        date = row[0] if len(row) > 0 else ""
                        hours = row[1] if len(row) > 1 else ""
                        task = row[3] if len(row) > 3 else ""
                        print(f"WIP Row {row_idx}: {date} | {hours}h | {task[:40]}...")
        
        print(f"\n📊 Total WIP entries found: {wip_count}")
        
        # If there are WIP entries, let's create some test entries for NES01-5541
        if wip_count > 0:
            print(f"\n🧪 Creating test entries for NES01-5541 update...")
            
            # Find some WIP entries to use as test data
            test_entries = []
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) > 6 and row[6].strip().upper() == "WIP":
                    if len(test_entries) < 3:  # Take first 3 WIP entries as test
                        try:
                            hours = float(row[1]) if row[1] else 0
                            if hours > 0:
                                entry = {
                                    "date": row[0],
                                    "hours": hours,
                                    "category": row[2] if len(row) > 2 else "Enhancement",
                                    "description": row[3] if len(row) > 3 else "",
                                    "persons": row[4] if len(row) > 4 else "",
                                    "invoice": "NES01-5541",
                                    "row_number": row_idx
                                }
                                test_entries.append(entry)
                        except ValueError:
                            continue
            
            if test_entries:
                print(f"\n📋 Test entries for NES01-5541 update:")
                total_hours = 0
                for entry in test_entries:
                    print(f"Row {entry['row_number']}: {entry['date']} | {entry['hours']}h | {entry['description'][:40]}...")
                    total_hours += entry['hours']
                
                print(f"⏱️  Total Hours: {total_hours}")
                
                # Ask for confirmation to test the update
                print(f"\n🧪 Test updating these {len(test_entries)} entries to 'Billed' with orange highlighting? (y/n): ", end="")
                response = input().strip().lower()
                
                if response in ['y', 'yes']:
                    print("🔄 Testing Billed update with orange highlighting...")
                    success = sheets_reader.update_wip_to_billed_with_formatting(test_entries, "Sheet1")
                    if success:
                        print("✅ Successfully tested Billed update with orange highlighting")
                        print("🎨 Check the spreadsheet - these rows should now be highlighted in orange")
                        return True
                    else:
                        print("⚠️  Warning: Could not complete the test update")
                        return False
                else:
                    print("ℹ️  Test skipped")
                    return True
            else:
                print("ℹ️  No suitable WIP entries found for testing")
        else:
            print("ℹ️  No WIP entries found in the spreadsheet")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_recent_entries()

