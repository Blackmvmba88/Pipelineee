"""Base connector interface for music platforms."""

from abc import ABC, abstractmethod
from typing import List, Optional

from pipeline.models.track import Track
from pipeline.models.playlist import Playlist


class BaseConnector(ABC):
    """
    Abstract base class for music platform connectors.
    
    All platform-specific connectors should inherit from this class
    and implement the required abstract methods.
    """
    
    @abstractmethod
    def authenticate(self, credentials: dict) -> bool:
        """
        Authenticate with the platform.
        
        Args:
            credentials: Platform-specific authentication credentials
            
        Returns:
            True if authentication was successful
        """
        pass
    
    @abstractmethod
    def get_playlists(self) -> List[Playlist]:
        """
        Fetch all playlists from the platform.
        
        Returns:
            List of Playlist objects
        """
        pass
    
    @abstractmethod
    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """
        Fetch a specific playlist by ID.
        
        Args:
            playlist_id: Platform-specific playlist identifier
            
        Returns:
            Playlist object if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_tracks(self, playlist_id: str) -> List[Track]:
        """
        Fetch all tracks from a playlist.
        
        Args:
            playlist_id: Platform-specific playlist identifier
            
        Returns:
            List of Track objects
        """
        pass
    
    @abstractmethod
    def get_track(self, track_id: str) -> Optional[Track]:
        """
        Fetch a specific track by ID.
        
        Args:
            track_id: Platform-specific track identifier
            
        Returns:
            Track object if found, None otherwise
        """
        pass
    
    @abstractmethod
    def search_track(self, title: str, artist: str) -> List[Track]:
        """
        Search for tracks matching title and artist.
        
        Args:
            title: Track title to search for
            artist: Artist name to search for
            
        Returns:
            List of matching Track objects
        """
        pass
    
    def is_authenticated(self) -> bool:
        """Check if connector is currently authenticated."""
        return getattr(self, "_authenticated", False)
