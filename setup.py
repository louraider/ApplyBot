#!/usr/bin/env python3
"""
Setup script for development environment.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Set up the development environment."""
    print("🚀 Setting up Job Application System development environment...")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        return False
    
    # Create necessary directories
    directories = ["logs", "uploads", "uploads/resumes", "uploads/cover_letters"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Copy environment file if it doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            run_command("copy .env.example .env", "Creating .env file from example")
        else:
            print("⚠️  Please create a .env file based on .env.example")
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Set up PostgreSQL database")
    print("3. Run: python run.py")
    print("4. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()