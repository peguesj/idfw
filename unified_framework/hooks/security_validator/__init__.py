"""
Compatibility module that redirects imports from security_validator to security
"""

import sys
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from actual module
from unified_framework.hooks.security import *

# For compatibility with code expecting the old name
print(f"Redirecting import from security_validator to unified_framework.hooks.security")
