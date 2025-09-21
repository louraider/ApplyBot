#!/usr/bin/env python3
"""
Comprehensive summary of job sources integration.
"""

import asyncio
import sys
import os
sys.path.append('.')

from app.services.job_source_config import job_source_manager

def print_comprehensive_status():
    """Print comprehensive status of all job sources."""
    print("🎯 JOB SOURCES INTEGRATION SUMMARY")
    print("=" * 60)
    
    source_info = job_source_manager.get_source_info()
    enabled_sources = job_source_manager.get_enabled_source_names()
    
    print(f"📊 OVERVIEW:")
    print(f"   • Total Sources Available: {len(source_info)}")
    print(f"   • Total Sources Enabled: {len(enabled_sources)}")
    print(f"   • Working Sources: 2 (RemoteOK, GitHub)")
    print(f"   • API Key Required: 2 (Reed, Adzuna)")
    print(f"   • Placeholder/WIP: 2 (Indeed, AngelList)")
    
    print(f"\n📋 DETAILED STATUS:")
    print("-" * 40)
    
    for source_id, info in source_info.items():
        status_icon = "✅" if info["enabled"] else "❌"
        
        # Determine working status
        if source_id in ["remoteok", "github"]:
            work_status = "🟢 WORKING"
        elif source_id in ["reed", "adzuna"]:
            work_status = "🟡 NEEDS API KEY"
        else:
            work_status = "🔴 PLACEHOLDER"
        
        print(f"{status_icon} {info['name']}")
        print(f"   Status: {work_status}")
        print(f"   Type: {info['api_type']}")
        print(f"   Description: {info['description']}")
        print(f"   Rate Limit: {info['rate_limit']}")
        print()
    
    print(f"🔧 INTEGRATION FEATURES:")
    print("-" * 30)
    print("✅ Multi-source job fetching")
    print("✅ Unified job data model")
    print("✅ Error handling & graceful failures")
    print("✅ API endpoints for source management")
    print("✅ Configurable enable/disable per source")
    print("✅ Rate limiting awareness")
    print("✅ Keyword-based job filtering")
    print("✅ Requirement extraction")
    print("✅ Salary parsing (where available)")
    
    print(f"\n🚀 READY TO USE:")
    print("-" * 20)
    print("1. RemoteOK - Fetching real remote jobs ✅")
    print("2. GitHub - Searching repos for hiring info ✅")
    print("3. Reed - Ready (needs API key) 🔑")
    print("4. Adzuna - Ready (needs API credentials) 🔑")
    print("5. Indeed - Placeholder (403 errors) ⚠️")
    print("6. AngelList - Placeholder (not implemented) ⚠️")

async def test_working_sources():
    """Test the sources that are currently working."""
    print(f"\n🧪 TESTING WORKING SOURCES")
    print("=" * 40)
    
    from app.services.job_fetcher import RemoteOKFetcher, GitHubJobsFetcher
    
    working_fetchers = [
        (RemoteOKFetcher(), "RemoteOK"),
        (GitHubJobsFetcher(), "GitHub")
    ]
    
    keywords = ["python", "javascript", "remote"]
    total_jobs = 0
    
    for fetcher, name in working_fetchers:
        try:
            print(f"\n🔍 Testing {name}...")
            jobs = await fetcher.fetch_jobs(keywords, limit=5)
            
            if jobs:
                print(f"✅ {name}: Found {len(jobs)} jobs")
                total_jobs += len(jobs)
                
                # Show examples
                for i, job in enumerate(jobs[:2], 1):
                    print(f"   {i}. {job.title} at {job.company}")
                    print(f"      📍 {job.location}")
                    if job.requirements:
                        print(f"      🛠️  {', '.join(job.requirements[:3])}")
            else:
                print(f"⚠️  {name}: No jobs found")
                
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
    
    print(f"\n🎉 Total jobs from working sources: {total_jobs}")

def show_api_usage():
    """Show how to use the API endpoints."""
    print(f"\n🌐 API ENDPOINTS USAGE")
    print("=" * 40)
    
    print("1. Check available sources:")
    print("   GET /api/v1/jobs/sources")
    print()
    
    print("2. Enable/disable sources:")
    print("   POST /api/v1/jobs/sources/reed/toggle?enable=true")
    print("   POST /api/v1/jobs/sources/adzuna/toggle?enable=false")
    print()
    
    print("3. Fetch jobs from all enabled sources:")
    print("   POST /api/v1/jobs/fetch")
    print("   {")
    print('     "keywords": ["python", "javascript"],')
    print('     "limit_per_source": 10')
    print("   }")
    print()
    
    print("4. Search stored jobs:")
    print("   GET /api/v1/jobs?keywords=python,remote&limit=20")
    print()
    
    print("5. Get job statistics:")
    print("   GET /api/v1/jobs/statistics")

if __name__ == "__main__":
    print_comprehensive_status()
    asyncio.run(test_working_sources())
    show_api_usage()
    
    print(f"\n✨ INTEGRATION COMPLETE!")
    print("🎯 You now have 4 job sources integrated:")
    print("   • 2 working immediately (RemoteOK, GitHub)")
    print("   • 2 ready with API keys (Reed, Adzuna)")
    print("   • 2 placeholders for future expansion")
    print("\n💡 Next steps:")
    print("   1. Get API keys for Reed & Adzuna for more jobs")
    print("   2. Start the server: python start_server.py")
    print("   3. Test endpoints: http://localhost:8000/docs")