# Ubuntu Server Installation Guide

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/daviderichammer/invoice-generator.git
cd invoice-generator

# Run installation
./install.sh

# Generate invoice
./generate-invoice
```

## Manual Installation Steps

### 1. System Requirements
- Ubuntu 18.04+ or Debian 10+
- Python 3.8+
- Internet connection

### 2. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip wkhtmltopdf git
pip3 install --user requests beautifulsoup4
```

### 3. Clone Repository
```bash
git clone https://github.com/daviderichammer/invoice-generator.git
cd invoice-generator
```

### 4. Make Scripts Executable
```bash
chmod +x generate-invoice
chmod +x install.sh
```

### 5. Test Installation
```bash
./generate-invoice
```

## Configuration

Edit `config.json` to customize:
- Google Sheets URL
- Company information
- Client details
- Output preferences

## Usage

### Generate Invoice
```bash
./generate-invoice
```

### Output Files
Generated files are saved to `output/` directory:
- `NES01-XXXX.html` - Web viewable invoice
- `NES01-XXXX.pdf` - Print-ready PDF
- `NES01-XXXX.json` - Structured data

## Troubleshooting

### wkhtmltopdf Issues
```bash
sudo apt-get install -y wkhtmltopdf
```

### Permission Issues
```bash
chmod +x generate-invoice
```

### Python Dependencies
```bash
pip3 install --user requests beautifulsoup4
```

## Automation

### Add to PATH (Optional)
```bash
echo 'export PATH="$PATH:$(pwd)"' >> ~/.bashrc
source ~/.bashrc
```

Now you can run `generate-invoice` from anywhere.

### Cron Job (Optional)
```bash
# Edit crontab
crontab -e

# Add line to generate invoice daily at 9 AM
0 9 * * * cd /path/to/invoice-generator && ./generate-invoice
```

