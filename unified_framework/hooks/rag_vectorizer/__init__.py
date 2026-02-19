"""
Compatibility module that redirects imports from rag_vectorizer to vector_rag
"""

import sys
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from actual module
from unified_framework.hooks.vector_rag import *

# For compatibility with code expecting the old name
print(f"Redirecting import from rag_vectorizer to unified_framework.hooks.vector_rag")
