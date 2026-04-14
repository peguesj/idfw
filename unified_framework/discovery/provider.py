"""Abstract base class for project discovery providers."""

from __future__ import annotations

import abc
from typing import List

from .models import DiscoveredProject


class ProjectProvider(abc.ABC):
    """Base class all discovery providers must implement."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Unique identifier for this provider."""

    @abc.abstractmethod
    async def discover(self) -> List[DiscoveredProject]:
        """Return projects discovered by this provider."""

    @abc.abstractmethod
    async def is_available(self) -> bool:
        """Return True if this provider can currently operate."""
