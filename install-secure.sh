#!/bin/bash
# Secure Installation Script for NES Invoice Generator

echo "🔐 Installing NES Invoice Generator (Secure Version)..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -y

# Install Python 3 and pip if not already installed
echo "🐍 Installing Python 3 and pip..."
sudo apt-get install -y python3 python3-pip

# Install wkhtmltopdf for PDF generation
echo "📄 Installing wkhtmltopdf for PDF generation..."
sudo apt-get install -y wkhtmltopdf

# Install required Python packages
echo "📚 Installing Python packages..."
pip3 install --upgrade gspread google-auth google-auth-oauthlib google-auth-httplib2

# Create credentials directory
echo "📁 Creating credentials directory..."
mkdir -p credentials

# Set permissions
echo "🔧 Setting permissions..."
chmod +x generate-invoice-secure
chmod 700 credentials  # Restrict access to credentials directory

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Follow the Google Service Account setup instructions"
echo "2. Download service account JSON credentials"
echo "3. Save credentials as: credentials/service_account_credentials.json"
echo "4. Share your Google Sheet with the service account email"
echo "5. Make your Google Sheet private (remove public access)"
echo "6. Run: ./generate-invoice-secure"
echo ""
echo "🔐 Security Notes:"
echo "- Credentials directory has restricted permissions (700)"
echo "- Never commit credentials to version control"
echo "- Service account provides secure, auditable access"
echo ""

