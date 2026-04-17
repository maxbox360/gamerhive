#!/usr/bin/env python
"""
Debug helper script for PyCharm Community Edition.

This script allows you to debug Django in PyCharm CE by running it as a regular Python script.

Usage in PyCharm:
1. Right-click this file → "Debug 'run_debug'"
2. Or set up a Run Configuration pointing to this file

Set breakpoints anywhere in your Django code and they will work!
"""
import os
import sys

# Add the backend directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gamerhive.settings")

# Load environment variables from .env file (located in parent directory)
from pathlib import Path
env_file = Path(BASE_DIR).parent / ".env"

if env_file.exists():
    print(f"Loading environment from: {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), value)
else:
    print(f"Warning: .env file not found at {env_file}")
    print("Make sure environment variables are set!")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    # Default to runserver if no arguments provided
    if len(sys.argv) == 1:
        sys.argv = ["manage.py", "runserver", "0.0.0.0:8000"]

    print(f"Running: {' '.join(sys.argv)}")
    print("-" * 50)

    execute_from_command_line(sys.argv)

