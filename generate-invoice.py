#!/bin/bash
"""
NES Invoice Generator - Main Command
Generates professional invoices from WIP data with one command
"""

import sys
import os
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from invoice_generator import InvoiceGenerator
from sheets_reader import SheetsReader
from pdf_converter import PDFConverter

def main():
    """Main invoice generation function."""
    print("🚀 NES Invoice Generator")
    print("=" * 50)
    
    try:
        # Initialize components
        print("📊 Reading WIP data from Google Sheets...")
        config_path = "config.json"
        
        if not os.path.exists(config_path):
            print("❌ config.json not found. Please run from invoice-generator directory.")
            return 1
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        sheets_reader = SheetsReader(config["google_sheets"]["url"])
        invoice_generator = InvoiceGenerator(config_path)
        pdf_converter = PDFConverter()
        
        # Get WIP entries
        wip_entries = sheets_reader.get_wip_entries()
        
        if not wip_entries:
            print("❌ No WIP entries found in Google Sheets")
            return 1
        
        print(f"✅ Found {len(wip_entries)} WIP entries")
        
        # Get invoice number
        invoice_number = sheets_reader.get_invoice_number(wip_entries)
        print(f"📄 Generating Invoice: {invoice_number}")
        
        # Generate invoice data
        invoice_data = invoice_generator.generate_invoice(wip_entries, invoice_number)
        
        # Generate HTML
        html_content = invoice_generator.generate_html(invoice_data)
        
        # Save files
        files_created = invoice_generator.save_files(invoice_data, html_content)
        
        # Generate PDF if requested
        if config["output"]["generate_pdf"] and "html" in files_created:
            html_path = files_created["html"]
            pdf_path = html_path.replace('.html', '.pdf')
            
            print("📄 Converting to PDF...")
            if pdf_converter.html_to_pdf(html_path, pdf_path):
                files_created["pdf"] = pdf_path
        
        # Display results
        print("\n🎉 Invoice Generated Successfully!")
        print("=" * 50)
        print(f"📊 Invoice Number: {invoice_data['invoice_number']}")
        print(f"📅 Invoice Date: {invoice_data['invoice_date']}")
        print(f"⏰ Total Hours: {invoice_data['summary']['total_hours']}")
        print(f"💰 Total Amount: ${invoice_data['summary']['balance_due']:,.0f}")
        
        print(f"\n📁 Files Created:")
        for file_type, file_path in files_created.items():
            print(f"   {file_type.upper()}: {file_path}")
        
        print(f"\n✅ Invoice ready for delivery!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating invoice: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

