"""Project discovery framework — pluggable providers with concurrent resolution."""

from .models import DiscoveredProject
from .provider import ProjectProvider
from .resolver import DiscoveryResolver
from .providers.filesystem import FilesystemProvider
from .providers.plane import PlaneProvider
from .providers.apm import APMProvider
from .providers.config import ConfigProvider

__all__ = [
    "DiscoveredProject",
    "ProjectProvider",
    "DiscoveryResolver",
    "FilesystemProvider",
    "PlaneProvider",
    "APMProvider",
    "ConfigProvider",
]
