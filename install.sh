#!/bin/bash

# NES Invoice Generator Installation Script
# Sets up the invoice generator on Ubuntu server

echo "🚀 Installing NES Invoice Generator..."
echo "=" * 50

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Please don't run this script as root"
   exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt-get install -y python3 python3-pip wkhtmltopdf git

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --user requests beautifulsoup4

# Make scripts executable
chmod +x generate-invoice

# Test the installation
echo "🧪 Testing installation..."
if command -v wkhtmltopdf &> /dev/null; then
    echo "✅ wkhtmltopdf installed successfully"
else
    echo "❌ wkhtmltopdf installation failed"
    exit 1
fi

if command -v python3 &> /dev/null; then
    echo "✅ Python 3 available"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Create output directory
mkdir -p output

echo ""
echo "🎉 Installation Complete!"
echo "=" * 50
echo "📁 Invoice generator installed in: $(pwd)"
echo "🚀 Generate invoices with: ./generate-invoice"
echo ""
echo "📋 Next steps:"
echo "1. Update config.json with your Google Sheets URL"
echo "2. Run: ./generate-invoice"
echo ""

