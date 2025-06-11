#!/usr/bin/env python3
"""
Test script for secure Google Sheets authentication
"""

import os
import sys
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_credentials_file():
    """Test if credentials file exists and is valid JSON."""
    print("🧪 Testing credentials file...")
    
    credentials_path = "credentials/service_account_credentials.json"
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        print("💡 Please create service account credentials and save them to this location")
        return False
    
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ Invalid credentials file. Missing fields: {missing_fields}")
            return False
        
        if creds_data.get('type') != 'service_account':
            print("❌ Invalid credentials type. Must be 'service_account'")
            return False
        
        print(f"✅ Credentials file is valid")
        print(f"📧 Service Account Email: {creds_data.get('client_email')}")
        print(f"🏗️  Project ID: {creds_data.get('project_id')}")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

def test_config_file():
    """Test if configuration file exists and is valid."""
    print("\n🧪 Testing configuration file...")
    
    config_path = "config_secure.json"
    
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check required sections
        required_sections = ['google_sheets', 'client', 'company', 'invoice']
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            print(f"❌ Invalid configuration. Missing sections: {missing_sections}")
            return False
        
        # Check Google Sheets configuration
        gs_config = config['google_sheets']
        if 'spreadsheet_id' not in gs_config or not gs_config['spreadsheet_id']:
            print("❌ Missing or empty spreadsheet_id in configuration")
            return False
        
        print("✅ Configuration file is valid")
        print(f"📊 Spreadsheet ID: {gs_config['spreadsheet_id']}")
        print(f"📋 Worksheet: {gs_config.get('worksheet_name', 'Sheet1')}")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in configuration file")
        return False
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False

def test_authentication():
    """Test Google Sheets authentication."""
    print("\n🧪 Testing Google Sheets authentication...")
    
    try:
        from sheets_reader_secure import SheetsReader
        
        # Load configuration
        with open("config_secure.json", 'r') as f:
            config = json.load(f)
        
        # Initialize sheets reader
        sheets_reader = SheetsReader(
            credentials_path=config["google_sheets"]["credentials_path"],
            spreadsheet_id=config["google_sheets"]["spreadsheet_id"]
        )
        
        # Get spreadsheet info
        info = sheets_reader.get_spreadsheet_info()
        
        print("✅ Authentication successful!")
        print(f"📊 Spreadsheet: {info['title']}")
        print(f"🔗 URL: {info['url']}")
        print(f"📋 Worksheets: {len(info['worksheets'])}")
        for ws in info['worksheets']:
            print(f"   - {ws['title']}: {ws['rows']} rows × {ws['cols']} columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure service account credentials are valid")
        print("2. Check that spreadsheet ID is correct")
        print("3. Verify spreadsheet is shared with service account email")
        print("4. Make sure Google Sheets API is enabled in Google Cloud Console")
        return False

def test_wip_reading():
    """Test reading WIP entries from spreadsheet."""
    print("\n🧪 Testing WIP entry reading...")
    
    try:
        from sheets_reader_secure import SheetsReader
        
        # Load configuration
        with open("config_secure.json", 'r') as f:
            config = json.load(f)
        
        # Initialize sheets reader
        sheets_reader = SheetsReader(
            credentials_path=config["google_sheets"]["credentials_path"],
            spreadsheet_id=config["google_sheets"]["spreadsheet_id"]
        )
        
        # Get WIP entries
        wip_entries = sheets_reader.get_wip_entries(config["google_sheets"]["worksheet_name"])
        
        if not wip_entries:
            print("ℹ️  No WIP entries found")
            print("💡 Make sure some entries are marked as 'WIP' in the Paid column")
            return True
        
        print(f"✅ Found {len(wip_entries)} WIP entries")
        
        # Show summary
        total_hours = sum(entry["hours"] for entry in wip_entries)
        categories = {}
        for entry in wip_entries:
            category = entry.get("category", "Enhancement")
            categories[category] = categories.get(category, 0) + entry["hours"]
        
        print(f"⏱️  Total Hours: {total_hours}")
        for category, hours in categories.items():
            print(f"   - {category}: {hours} hours")
        
        # Show first few entries
        print("\n📋 Sample WIP entries:")
        for i, entry in enumerate(wip_entries[:3]):
            print(f"   {i+1}. {entry['date']}: {entry['hours']}h - {entry['description'][:50]}...")
        
        if len(wip_entries) > 3:
            print(f"   ... and {len(wip_entries) - 3} more entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading WIP entries: {e}")
        return False

def main():
    """Run all tests."""
    print("🔐 NES Invoice Generator - Secure Authentication Test\n")
    
    tests = [
        ("Credentials File", test_credentials_file),
        ("Configuration File", test_config_file),
        ("Google Sheets Authentication", test_authentication),
        ("WIP Entry Reading", test_wip_reading)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your secure authentication is ready to use.")
        print("🚀 Run: ./generate-invoice-secure")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before proceeding.")
        print("📋 Follow the setup instructions to configure authentication properly.")

if __name__ == "__main__":
    main()

