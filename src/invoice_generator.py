#!/usr/bin/env python3
"""
NES Invoice Generator - Core Module
Generates professional invoices from WIP data with W3EVOLUTIONS branding
"""

import json
import base64
import os
from datetime import datetime
from typing import List, Dict, Any

class InvoiceGenerator:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the invoice generator with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Load logo as base64
        self.logo_base64 = self._load_logo()
    
    def _load_logo(self) -> str:
        """Load the W3EVOLUTIONS logo as base64."""
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return ""
    
    def generate_invoice(self, wip_entries: List[Dict], invoice_number: str) -> Dict[str, Any]:
        """Generate invoice from WIP entries."""
        # Calculate totals
        total_hours = sum(entry["hours"] for entry in wip_entries)
        hourly_rate = self.config["invoice"]["hourly_rate"]  # This is the discounted rate ($126)
        discount_per_hour = self.config["invoice"]["discount"]  # $49 per hour discount
        original_rate = hourly_rate + discount_per_hour  # $175 original rate
        subtotal = total_hours * hourly_rate  # Use the discounted rate for total
        balance_due = subtotal  # No additional discount - rate already includes discount
        
        # Get invoice date (last work date)
        invoice_date = max(entry["date"] for entry in wip_entries)
        
        # Create invoice data
        invoice_data = {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "bill_to": self.config["client"],
            "sales_rep": self.config["sales_rep"],
            "terms": self.config["invoice"]["terms"],
            "work_entries": wip_entries,
            "summary": {
                "total_hours": total_hours,
                "hourly_rate": hourly_rate,
                "original_rate": original_rate,
                "discount_per_hour": discount_per_hour,
                "subtotal": subtotal,
                "balance_due": balance_due
            },
            "payment_info": self.config["company"]
        }
        
        return invoice_data
    
    def generate_html(self, invoice_data: Dict[str, Any]) -> str:
        """Generate HTML invoice."""
        wip_entries = invoice_data["work_entries"]
        total_hours = invoice_data["summary"]["total_hours"]
        hourly_rate = invoice_data["summary"]["hourly_rate"]
        original_rate = invoice_data["summary"]["original_rate"]
        discount_per_hour = invoice_data["summary"]["discount_per_hour"]
        subtotal = invoice_data["summary"]["subtotal"]
        balance_due = invoice_data["summary"]["balance_due"]
        invoice_date = invoice_data["invoice_date"]
        invoice_number = invoice_data["invoice_number"]
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice {invoice_number}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            color: #333;
            line-height: 1.4;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 30px;
        }}
        .logo {{
            max-width: 300px;
            height: auto;
        }}
        .invoice-title {{
            font-size: 48px;
            font-weight: bold;
            color: #666;
            text-align: right;
        }}
        .invoice-info {{
            margin-bottom: 20px;
        }}
        .invoice-info div {{
            margin-bottom: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        .amount {{
            text-align: right;
        }}
        .payment-info {{
            margin: 20px 0;
            line-height: 1.6;
        }}
        .totals-table {{
            width: 300px;
            float: right;
            margin-top: 20px;
        }}
        .time-details {{
            clear: both;
            margin-top: 40px;
        }}
        .time-details h2 {{
            font-size: 24px;
            margin-bottom: 15px;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="header">
        <img src="data:image/png;base64,{self.logo_base64}" alt="W3EVOLUTIONS" class="logo">
        <div class="invoice-title">INVOICE</div>
    </div>

    <div class="invoice-info">
        <div><strong>Invoice No.:</strong> {invoice_number}</div>
        <div><strong>Bill To:</strong> {invoice_data['bill_to']['name']}</div>
        <div>{invoice_data['bill_to']['address']}</div>
        <div>{invoice_data['bill_to']['city_state_zip']}</div>
        <div><strong>Customer ID:</strong> {invoice_data['bill_to']['customer_id']}</div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Invoice No.</th>
                <th>Sales Rep.</th>
                <th>Ship Via</th>
                <th>Terms</th>
                <th>Date Due</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{invoice_date}</td>
                <td>{invoice_number}</td>
                <td>{invoice_data['sales_rep']}</td>
                <td>Email</td>
                <td>{invoice_data['terms']}</td>
                <td>-</td>
            </tr>
        </tbody>
    </table>

    <table>
        <thead>
            <tr>
                <th>Quantity</th>
                <th>Item</th>
                <th>Description</th>
                <th>Discount</th>
                <th>Taxable</th>
                <th>Unit Price</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{total_hours}</td>
                <td>Enhancement</td>
                <td>See attached</td>
                <td>${discount_per_hour} / hr off<br>${original_rate} / hr</td>
                <td>No</td>
                <td>${hourly_rate}</td>
                <td>${balance_due:,.0f}</td>
            </tr>
            <tr>
                <td>-</td>
                <td>New Development</td>
                <td>See attached</td>
                <td>${discount_per_hour} / hr off<br>${original_rate} / hr</td>
                <td>No</td>
                <td>${hourly_rate}</td>
                <td>-</td>
            </tr>
        </tbody>
    </table>

    <div class="payment-info">
        <strong>Please make all checks payable to:</strong> {invoice_data['payment_info']['name']}<br>
        <strong>Please send checks to:</strong> {invoice_data['payment_info']['address']}<br>
        <strong>Zelle:</strong> {invoice_data['payment_info']['zelle']}
    </div>

    <table class="totals-table">
        <tbody>
            <tr>
                <td><strong>Subtotal:</strong></td>
                <td class="amount">${subtotal:,.0f}</td>
            </tr>
            <tr>
                <td><strong>Tax:</strong></td>
                <td class="amount">0.00</td>
            </tr>
            <tr>
                <td><strong>Balance Due:</strong></td>
                <td class="amount">${balance_due:,.0f}</td>
            </tr>
        </tbody>
    </table>

    <div class="time-details">
        <h2>Time Entry Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Hours</th>
                    <th>Category</th>
                    <th>Task/Work</th>
                    <th>Persons</th>
                </tr>
            </thead>
            <tbody>"""

        # Add all time entries
        for entry in wip_entries:
            html_content += f"""
                <tr>
                    <td>{entry['date']}</td>
                    <td>{entry['hours']}</td>
                    <td>Enhancement</td>
                    <td>{entry['description']}</td>
                    <td>{entry['persons']}</td>
                </tr>"""

        html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>"""

        return html_content
    
    def save_files(self, invoice_data: Dict[str, Any], html_content: str) -> Dict[str, str]:
        """Save invoice files to output directory."""
        output_dir = self.config["output"]["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        
        invoice_number = invoice_data["invoice_number"]
        files_created = {}
        
        # Save HTML
        if self.config["output"]["generate_html"]:
            html_path = f"{output_dir}/{invoice_number}.html"
            with open(html_path, 'w') as f:
                f.write(html_content)
            files_created["html"] = html_path
        
        # Save JSON
        if self.config["output"]["generate_json"]:
            json_path = f"{output_dir}/{invoice_number}.json"
            with open(json_path, 'w') as f:
                json.dump(invoice_data, f, indent=2)
            files_created["json"] = json_path
        
        return files_created

