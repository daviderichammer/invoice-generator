#!/usr/bin/env python3
"""
Google Sheets Reader - Extracts WIP data from time tracking spreadsheet
"""

import re
from typing import List, Dict, Any

class SheetsReader:
    def __init__(self, sheets_url: str):
        """Initialize with Google Sheets URL."""
        self.sheets_url = sheets_url
    
    def get_wip_entries(self) -> List[Dict[str, Any]]:
        """
        Extract WIP entries from Google Sheets.
        For now, returns the known WIP data.
        In production, this would integrate with Google Sheets API.
        """
        # This is the current WIP data from the spreadsheet
        # In a full implementation, this would use Google Sheets API
        wip_entries = [
            {
                "date": "6/4/25",
                "hours": 17,
                "description": "AAE-101 UAT bug tracker list review, development and bug fixes",
                "persons": "BK/DH",
                "invoice": "NES01-5541"
            },
            {
                "date": "6/5/25",
                "hours": 15,
                "description": "AAE-101 UAT bug tracker list review, development and bug fixes",
                "persons": "BK/DH",
                "invoice": "NES01-5541"
            },
            {
                "date": "6/6/25",
                "hours": 16,
                "description": "AAE-101 UAT bug tracker + ERV2 prod issues, bandaid fixes for stage-qa",
                "persons": "BK/DH",
                "invoice": "NES01-5541"
            },
            {
                "date": "6/7/25",
                "hours": 9,
                "description": "AAE-101 UAT bug tracker list review, development and bug fixes",
                "persons": "BK/DH",
                "invoice": "NES01-5541"
            },
            {
                "date": "6/8/25",
                "hours": 10,
                "description": "AAE-101 UAT bug tracker list review, development and bug fixes",
                "persons": "BK/DH",
                "invoice": "NES01-5541"
            },
            {
                "date": "6/9/25",
                "hours": 17,
                "description": "AAE-101 UAT bug tracker list review, development and bug fixes",
                "persons": "BK/DH",
                "invoice": "NES01-5541"
            },
            {
                "date": "6/10/25",
                "hours": 18,
                "description": "AAE-101 UAT bug tracker list review, development and bug fixes",
                "persons": "BK/DH",
                "invoice": "NES01-5541"
            }
        ]
        
        return wip_entries
    
    def get_invoice_number(self, wip_entries: List[Dict[str, Any]]) -> str:
        """Extract invoice number from WIP entries."""
        if wip_entries:
            return wip_entries[0].get("invoice", "NES01-5541")
        return "NES01-5541"

