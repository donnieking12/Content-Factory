#!/usr/bin/env python3
"""
Content Factory AI - Project Setup Script
This script sets up the project environment and verifies all components.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(message):
    print("\n" + "="*60)
    print(f" {message}")
    print("="*60)

def print_step(step, message):
    print(f"\nStep {step}: {message}")
    print("-" * 40)

def run_command(command, check=True, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=check, 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} found")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} found")
        print("  Python 3.10+ is required")
        return False

def setup_virtual_environment():
    """Create and set up virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    success, stdout, stderr = run_command([sys.executable, "-m", "venv", "venv"])
    
    if success:
        print("✓ Virtual environment created successfully")
        return True
    else:
        print(f"✗ Failed to create virtual environment: {stderr}")
        return False

def install_dependencies():
    """Install project dependencies"""
    # Determine the correct pip path based on OS
    if platform.system() == "Windows":
        pip_path = Path("venv/Scripts/pip.exe")
    else:
        pip_path = Path("venv/bin/pip")
    
    if not pip_path.exists():
        print("✗ Virtual environment pip not found")
        return False
    
    print("Installing dependencies...")
    success, stdout, stderr = run_command([str(pip_path), "install", "-r", "requirements.txt"])
    
    if success:
        print("✓ Dependencies installed successfully")
        return True
    else:
        print(f"✗ Failed to install dependencies: {stderr}")
        return False

def check_env_file():
    """Check if .env file exists and has basic configuration"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("✗ .env file not found")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    required_vars = [
        "SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=your_" in content or f"{var}=https://your-" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠ .env file exists but needs configuration for: {', '.join(missing_vars)}")
        return False
    else:
        print("✓ .env file configured")
        return True

def setup_database():
    """Set up database tables"""
    # Determine the correct python path based on OS
    if platform.system() == "Windows":
        python_path = Path("venv/Scripts/python.exe")
    else:
        python_path = Path("venv/bin/python")
    
    if not python_path.exists():
        print("✗ Virtual environment python not found")
        return False
    
    print("Setting up database tables...")
    success, stdout, stderr = run_command([str(python_path), "setup_db.py"])
    
    if success:
        print("✓ Database tables created successfully")
        return True
    else:
        print(f"⚠ Database setup failed (this is expected if Supabase credentials are not configured): {stderr}")
        return False

def test_application():
    """Test if the application can start"""
    # Determine the correct python path based on OS
    if platform.system() == "Windows":
        python_path = Path("venv/Scripts/python.exe")
    else:
        python_path = Path("venv/bin/python")
    
    if not python_path.exists():
        print("✗ Virtual environment python not found")
        return False
    
    print("Testing application startup...")
    # Test import of main modules
    success, stdout, stderr = run_command([
        str(python_path), "-c", 
        "from app.main import app; from app.core.config import settings; print('✓ Application modules load successfully')"
    ])
    
    if success:
        print("✓ Application can be imported successfully")
        return True
    else:
        print(f"✗ Application import failed: {stderr}")
        return False

def main():
    """Main setup function"""
    print_header("Content Factory AI - Project Setup")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success_count = 0
    total_steps = 6
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    if check_python_version():
        success_count += 1
    
    # Step 2: Set up virtual environment
    print_step(2, "Setting up virtual environment")
    if setup_virtual_environment():
        success_count += 1
    
    # Step 3: Install dependencies
    print_step(3, "Installing dependencies")
    if install_dependencies():
        success_count += 1
    
    # Step 4: Check environment configuration
    print_step(4, "Checking environment configuration")
    if check_env_file():
        success_count += 1
    
    # Step 5: Set up database
    print_step(5, "Setting up database")
    if setup_database():
        success_count += 1
    
    # Step 6: Test application
    print_step(6, "Testing application")
    if test_application():
        success_count += 1
    
    # Final report
    print_header("Setup Complete!")
    print(f"Successfully completed {success_count}/{total_steps} setup steps")
    
    if success_count == total_steps:
        print("\n🎉 Project setup completed successfully!")
        print("\nNext steps:")
        print("1. Configure your API keys in the .env file")
        print("2. Activate virtual environment:")
        if platform.system() == "Windows":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("3. Start the application:")
        print("   python run.py")
    else:
        print(f"\n⚠ Setup completed with {total_steps - success_count} issues")
        print("Please resolve the issues above and run this script again")
    
    return success_count == total_steps

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error during setup: {e}")
        sys.exit(1)