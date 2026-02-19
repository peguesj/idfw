"""
Compatibility module that redirects imports from prehook_processor to prehook
"""

import sys
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from actual module
from unified_framework.hooks.prehook import *

# For compatibility with code expecting the old name
print(f"Redirecting import from prehook_processor to unified_framework.hooks.prehook")
