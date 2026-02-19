"""
Compatibility module that redirects imports from posthook_processor to posthook
"""

import sys
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from actual module
from unified_framework.hooks.posthook import *

# Import necessary classes directly
from unified_framework.hooks.posthook import PosthookProcessor

# For compatibility with code expecting the old name
print(f"Redirecting import from posthook_processor to unified_framework.hooks.posthook")
