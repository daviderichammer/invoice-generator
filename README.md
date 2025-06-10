# NES Invoice Generator

A streamlined invoice generation system for W3EVOLUTIONS that creates professional invoices from Google Sheets time tracking data.

## Features

- 🚀 **One-Command Generation**: Generate invoices with a single command
- 📊 **Google Sheets Integration**: Automatically pulls WIP data from your time tracking spreadsheet
- 🎨 **Professional Branding**: W3EVOLUTIONS logo and consistent formatting
- 📄 **Multiple Formats**: HTML, PDF, JSON output
- ✅ **Validation**: Built-in calculation verification
- 🔄 **Automated**: Handles invoice numbering and date calculations

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/daviderichammer/invoice-generator.git
cd invoice-generator

# Run the installation script
./install.sh
```

### Generate Invoice

```bash
# Generate invoice from WIP data
./generate-invoice
```

This will:
1. Scan your Google Sheets for WIP entries
2. Generate Invoice with proper numbering
3. Create HTML, PDF, and JSON formats
4. Validate all calculations
5. Save files to `output/` directory

## Configuration

Edit `config.json` to customize:
- Google Sheets URL
- Invoice settings
- Company information
- Output preferences

## File Structure

```
invoice-generator/
├── generate-invoice          # Main command script
├── src/
│   ├── invoice_generator.py  # Core invoice generation
│   ├── sheets_reader.py      # Google Sheets integration
│   └── pdf_converter.py      # PDF generation
├── assets/
│   └── logo.png             # W3EVOLUTIONS logo
├── templates/
│   └── invoice_template.html # Invoice HTML template
├── config.json              # Configuration file
└── output/                  # Generated invoices
```

## Requirements

- Python 3.8+
- wkhtmltopdf (for PDF generation)
- Internet connection (for Google Sheets access)

## License

Private - W3EVOLUTIONS Internal Use Only

