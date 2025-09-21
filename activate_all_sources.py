#!/usr/bin/env python3
"""
Script to activate all job sources and test them.
"""

import asyncio
import sys
import os
sys.path.append('.')

from app.services.job_source_config import job_source_manager
from loguru import logger

# Configure simple logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {message}")

def activate_all_sources():
    """Enable all available job sources."""
    print("🔧 Activating All Job Sources")
    print("=" * 40)
    
    # Get current source info
    source_info = job_source_manager.get_source_info()
    
    # Enable all sources
    for source_id, info in source_info.items():
        if not info["enabled"]:
            success = job_source_manager.enable_source(source_id)
            if success:
                print(f"✅ Enabled {info['name']}")
            else:
                print(f"❌ Failed to enable {info['name']}")
        else:
            print(f"✅ {info['name']} already enabled")
    
    print(f"\n📊 Updated Configuration:")
    print("-" * 30)
    
    # Show updated status
    updated_info = job_source_manager.get_source_info()
    for source_id, info in updated_info.items():
        status = "✅ Enabled" if info["enabled"] else "⚠️  Disabled"
        print(f"{status} {info['name']}")
        if info['api_type'] == 'REST API' and 'requires' in info['description'].lower():
            print(f"   ⚠️  Note: Requires API credentials")

async def test_all_sources():
    """Test all enabled sources."""
    print(f"\n🧪 Testing All Enabled Sources")
    print("=" * 40)
    
    # Get enabled fetchers
    fetchers = job_source_manager.get_enabled_fetchers()
    
    if not fetchers:
        print("❌ No enabled fetchers found")
        return
    
    print(f"📡 Testing {len(fetchers)} sources...")
    
    # Test each fetcher
    keywords = ["python", "remote"]
    
    for fetcher in fetchers:
        source_name = fetcher.get_source_name()
        print(f"\n🔍 Testing {source_name}...")
        
        try:
            jobs = await fetcher.fetch_jobs(keywords, limit=2)
            
            if jobs:
                print(f"✅ {source_name}: Found {len(jobs)} jobs")
                
                # Show first job as example
                job = jobs[0]
                print(f"   📋 {job.title}")
                print(f"   🏢 {job.company}")
                print(f"   📍 {job.location}")
            else:
                print(f"⚠️  {source_name}: No jobs found (may need API keys)")
                
        except Exception as e:
            print(f"❌ {source_name}: Error - {str(e)}")

def show_api_key_instructions():
    """Show instructions for setting up API keys."""
    print(f"\n🔑 API Key Setup Instructions")
    print("=" * 40)
    
    print("To enable Reed and Adzuna with real data:")
    print()
    print("1. Reed API (UK Jobs):")
    print("   - Visit: https://www.reed.co.uk/developers")
    print("   - Sign up for free developer account")
    print("   - Get your API key")
    print("   - Set: export REED_API_KEY='your_api_key_here'")
    print()
    print("2. Adzuna API (Global Jobs):")
    print("   - Visit: https://developer.adzuna.com/")
    print("   - Sign up for free developer account")
    print("   - Create an app to get App ID and App Key")
    print("   - Set: export ADZUNA_APP_ID='your_app_id_here'")
    print("   - Set: export ADZUNA_APP_KEY='your_app_key_here'")
    print()
    print("3. After setting environment variables, restart the application")

if __name__ == "__main__":
    print("🚀 Job Sources Activation & Testing")
    print("=" * 50)
    
    # Activate all sources
    activate_all_sources()
    
    # Test all sources
    asyncio.run(test_all_sources())
    
    # Show API key instructions
    show_api_key_instructions()
    
    print(f"\n✨ Activation completed!")
    print("💡 Tip: Use the API endpoints to enable/disable sources dynamically:")
    print("   POST /api/v1/jobs/sources/reed/toggle?enable=true")
    print("   GET /api/v1/jobs/sources")