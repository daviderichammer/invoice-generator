#!/usr/bin/env python3
"""
PDF Converter - Converts HTML invoices to PDF format
"""

import subprocess
import os
from typing import Optional

class PDFConverter:
    def __init__(self):
        """Initialize PDF converter."""
        pass
    
    def html_to_pdf(self, html_path: str, pdf_path: str) -> bool:
        """Convert HTML file to PDF using wkhtmltopdf."""
        try:
            # Check if wkhtmltopdf is available
            result = subprocess.run(['which', 'wkhtmltopdf'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("Warning: wkhtmltopdf not found. Installing...")
                self._install_wkhtmltopdf()
            
            # Convert HTML to PDF
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '0.75in',
                '--margin-right', '0.75in',
                '--margin-bottom', '0.75in',
                '--margin-left', '0.75in',
                '--encoding', 'UTF-8',
                '--quiet',
                html_path,
                pdf_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ PDF generated: {pdf_path}")
                return True
            else:
                print(f"❌ PDF generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ PDF conversion error: {e}")
            return False
    
    def _install_wkhtmltopdf(self):
        """Install wkhtmltopdf if not available."""
        try:
            print("Installing wkhtmltopdf...")
            subprocess.run(['sudo', 'apt-get', 'update', '-y'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'wkhtmltopdf'], check=True)
            print("✅ wkhtmltopdf installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install wkhtmltopdf: {e}")
            print("Please install manually: sudo apt-get install wkhtmltopdf")

