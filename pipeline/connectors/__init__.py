"""Platform connectors for Pipeline."""

from pipeline.connectors.base import BaseConnector
from pipeline.connectors.spotify import SpotifyConnector
from pipeline.connectors.suno import SunoConnector
from pipeline.connectors.soundcloud import SoundCloudConnector

__all__ = [
    "BaseConnector",
    "SpotifyConnector",
    "SunoConnector",
    "SoundCloudConnector",
]
