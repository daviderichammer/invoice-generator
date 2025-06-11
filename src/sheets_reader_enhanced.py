#!/usr/bin/env python3
"""
Enhanced Sheets Reader with formatting capabilities for updating billed entries
"""

import gspread
import json
import os
from typing import List, Dict, Any, Optional
from google.oauth2.service_account import Credentials

class SheetsReaderEnhanced:
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Initialize with service account credentials and spreadsheet ID.
        
        Args:
            credentials_path: Path to service account JSON credentials file
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None
        
        # Define the required scopes for Google Sheets and Drive access
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using service account credentials."""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
            
            # Load credentials from service account JSON file
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=self.scopes
            )
            
            # Create gspread client with authenticated credentials
            self.client = gspread.authorize(credentials)
            
            # Open the spreadsheet by ID
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            print(f"✅ Successfully authenticated and connected to spreadsheet")
            
        except FileNotFoundError as e:
            raise Exception(f"❌ Credentials file not found: {e}")
        except gspread.SpreadsheetNotFound:
            raise Exception(f"❌ Spreadsheet not found. Please check the spreadsheet ID and ensure it's shared with the service account.")
        except Exception as e:
            raise Exception(f"❌ Authentication failed: {e}")
    
    def get_service_account_email(self) -> str:
        """Get the service account email from credentials."""
        try:
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)
                return creds_data.get('client_email', 'Unknown')
        except Exception:
            return 'Unknown'
    
    def get_wip_entries(self, worksheet_name: str = "Sheet1") -> List[Dict[str, Any]]:
        """
        Extract WIP entries from Google Sheets.
        
        Args:
            worksheet_name: Name of the worksheet to read from
            
        Returns:
            List of WIP entries with their details
        """
        try:
            # Get the specified worksheet
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            
            # Get all values from the worksheet
            all_values = worksheet.get_all_values()
            
            if not all_values:
                return []
            
            # Assume first row contains headers
            headers = all_values[0]
            
            # Find column indices
            date_col = self._find_column_index(headers, ['date'])
            hours_col = self._find_column_index(headers, ['hours'])
            category_col = self._find_column_index(headers, ['category'])
            task_col = self._find_column_index(headers, ['task', 'work', 'task/work'])
            persons_col = self._find_column_index(headers, ['persons'])
            invoice_col = self._find_column_index(headers, ['invoice'])
            paid_col = self._find_column_index(headers, ['paid', 'status'])
            
            wip_entries = []
            
            # Process each row (skip header row)
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) <= max(date_col, hours_col, category_col, task_col, persons_col, invoice_col, paid_col):
                    continue  # Skip incomplete rows
                
                # Check if this is a WIP entry (not marked as "Paid")
                paid_status = row[paid_col].strip().upper() if paid_col < len(row) else ""
                
                if paid_status == "WIP":
                    try:
                        # Extract data from row
                        date = row[date_col].strip() if date_col < len(row) else ""
                        hours_str = row[hours_col].strip() if hours_col < len(row) else "0"
                        category = row[category_col].strip() if category_col < len(row) else "Enhancement"
                        description = row[task_col].strip() if task_col < len(row) else ""
                        persons = row[persons_col].strip() if persons_col < len(row) else ""
                        invoice = row[invoice_col].strip() if invoice_col < len(row) else ""
                        
                        # Parse hours (handle decimal values)
                        try:
                            hours = float(hours_str)
                        except ValueError:
                            print(f"⚠️  Warning: Invalid hours value '{hours_str}' in row {row_idx}, skipping")
                            continue
                        
                        # Skip entries with no hours or invalid data
                        if hours <= 0 or not date or not description:
                            continue
                        
                        wip_entry = {
                            "date": date,
                            "hours": hours,
                            "category": category,
                            "description": description,
                            "persons": persons,
                            "invoice": invoice,
                            "row_number": row_idx  # Store row number for potential updates
                        }
                        
                        wip_entries.append(wip_entry)
                        
                    except Exception as e:
                        print(f"⚠️  Warning: Error processing row {row_idx}: {e}")
                        continue
            
            print(f"📊 Found {len(wip_entries)} WIP entries")
            return wip_entries
            
        except gspread.WorksheetNotFound:
            raise Exception(f"❌ Worksheet '{worksheet_name}' not found in spreadsheet")
        except Exception as e:
            raise Exception(f"❌ Error reading WIP entries: {e}")
    
    def _find_column_index(self, headers: List[str], possible_names: List[str]) -> int:
        """Find the index of a column by checking possible header names."""
        headers_lower = [h.lower().strip() for h in headers]
        
        for name in possible_names:
            name_lower = name.lower().strip()
            if name_lower in headers_lower:
                return headers_lower.index(name_lower)
        
        # Return last index if not found (will be handled gracefully)
        return len(headers)
    
    def get_invoice_number(self, wip_entries: List[Dict[str, Any]]) -> str:
        """
        Extract invoice number from WIP entries.
        If multiple invoice numbers exist, use the most common one.
        """
        if not wip_entries:
            return "NES01-5541"  # Default fallback
        
        # Count invoice numbers
        invoice_counts = {}
        for entry in wip_entries:
            invoice = entry.get("invoice", "").strip()
            if invoice:
                invoice_counts[invoice] = invoice_counts.get(invoice, 0) + 1
        
        if invoice_counts:
            # Return the most common invoice number
            return max(invoice_counts.items(), key=lambda x: x[1])[0]
        
        return "NES01-5541"  # Default fallback
    
    def update_wip_to_billed_with_formatting(self, wip_entries: List[Dict[str, Any]], worksheet_name: str = "Sheet1") -> bool:
        """
        Update WIP entries to 'Billed' status and apply orange highlighting.
        
        Args:
            wip_entries: List of WIP entries that were billed
            worksheet_name: Name of the worksheet to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            
            # Get headers to find the 'Status' column
            headers = worksheet.row_values(1)
            status_col_index = self._find_column_index(headers, ['paid', 'status']) + 1  # gspread uses 1-based indexing
            
            if status_col_index > len(headers):
                print("⚠️  Warning: 'Status' column not found, cannot update status")
                return False
            
            # Prepare batch updates for both values and formatting
            value_updates = []
            format_requests = []
            
            # Orange color for highlighting (use exact reference color)
            orange_color = {
                "red": 1,
                "green": 0.6
            }
            
            for entry in wip_entries:
                row_number = entry.get("row_number")
                if row_number:
                    # Update the 'Status' column to 'Billed'
                    cell_address = f"{chr(64 + status_col_index)}{row_number}"  # Convert to A1 notation
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
                                    "backgroundColor": orange_color
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
                    
                    # Use the underlying service to make the batch update request
                    from googleapiclient.discovery import build
                    from google.oauth2.service_account import Credentials
                    
                    # Load credentials and build the Sheets API service
                    credentials = Credentials.from_service_account_file(
                        self.credentials_path, 
                        scopes=self.scopes
                    )
                    service = build('sheets', 'v4', credentials=credentials)
                    
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=self.spreadsheet_id,
                        body=body
                    ).execute()
                    
                    print(f"🎨 Applied orange highlighting to {len(format_requests)} rows")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error updating WIP entries: {e}")
            return False
    
    def get_spreadsheet_info(self) -> Dict[str, Any]:
        """Get basic information about the spreadsheet."""
        try:
            worksheets = self.spreadsheet.worksheets()
            
            info = {
                "title": self.spreadsheet.title,
                "id": self.spreadsheet.id,
                "url": self.spreadsheet.url,
                "worksheets": [{"title": ws.title, "rows": ws.row_count, "cols": ws.col_count} for ws in worksheets],
                "service_account_email": self.get_service_account_email()
            }
            
            return info
            
        except Exception as e:
            raise Exception(f"❌ Error getting spreadsheet info: {e}")

