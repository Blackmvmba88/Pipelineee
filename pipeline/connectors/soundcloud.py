"""SoundCloud connector for Pipeline."""

from typing import List, Optional

from pipeline.connectors.base import BaseConnector
from pipeline.models.track import Track, Platform, TrackStatus
from pipeline.models.playlist import Playlist


class SoundCloudConnector(BaseConnector):
    """
    Connector for SoundCloud music platform.
    
    This connector interfaces with the SoundCloud API to fetch
    playlists and track information.
    
    Note: Requires SoundCloud API credentials.
    """
    
    def __init__(self):
        self._authenticated = False
        self._access_token: Optional[str] = None
        self._client_id: Optional[str] = None
        self._user_id: Optional[str] = None
    
    def authenticate(self, credentials: dict) -> bool:
        """
        Authenticate with SoundCloud API.
        
        Args:
            credentials: Dictionary containing:
                - client_id: SoundCloud application client ID
                - client_secret: SoundCloud application client secret
                - access_token: Pre-existing OAuth access token (optional)
                
        Returns:
            True if authentication was successful
        """
        if "access_token" in credentials:
            self._access_token = credentials["access_token"]
            self._authenticated = True
            return True
        
        if "client_id" in credentials:
            self._client_id = credentials["client_id"]
            # SoundCloud allows some API access with just client_id
            self._authenticated = True
            return True
        
        return False
    
    def get_playlists(self) -> List[Playlist]:
        """
        Fetch all user playlists from SoundCloud.
        
        Returns:
            List of Playlist objects
        """
        if not self.is_authenticated():
            return []
        
        # TODO: Implement actual API call
        # GET /users/{user_id}/playlists
        return []
    
    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """
        Fetch a specific playlist by ID.
        
        Args:
            playlist_id: SoundCloud playlist ID
            
        Returns:
            Playlist object if found, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        # TODO: Implement actual API call
        # GET /playlists/{playlist_id}
        return None
    
    def get_tracks(self, playlist_id: str) -> List[Track]:
        """
        Fetch all tracks from a SoundCloud playlist.
        
        Args:
            playlist_id: SoundCloud playlist ID
            
        Returns:
            List of Track objects
        """
        if not self.is_authenticated():
            return []
        
        # TODO: Implement actual API call
        # GET /playlists/{playlist_id}/tracks
        return []
    
    def get_track(self, track_id: str) -> Optional[Track]:
        """
        Fetch a specific track by ID.
        
        Args:
            track_id: SoundCloud track ID
            
        Returns:
            Track object if found, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        # TODO: Implement actual API call
        # GET /tracks/{track_id}
        return None
    
    def search_track(self, title: str, artist: str) -> List[Track]:
        """
        Search for tracks on SoundCloud.
        
        Args:
            title: Track title to search for
            artist: Artist name to search for
            
        Returns:
            List of matching Track objects
        """
        if not self.is_authenticated():
            return []
        
        # TODO: Implement actual API call
        # GET /tracks?q={title}+{artist}
        return []
    
    def get_user_tracks(self) -> List[Track]:
        """
        Fetch all tracks uploaded by the authenticated user.
        
        Returns:
            List of Track objects
        """
        if not self.is_authenticated():
            return []
        
        # TODO: Implement actual API call
        # GET /users/{user_id}/tracks
        return []
    
    @staticmethod
    def parse_track_data(data: dict) -> Track:
        """
        Parse SoundCloud API track data into a Track object.
        
        Args:
            data: Raw track data from SoundCloud API
            
        Returns:
            Track object
        """
        user = data.get("user", {})
        
        return Track(
            title=data.get("title", ""),
            artist=user.get("username", ""),
            platform=Platform.SOUNDCLOUD,
            platform_id=str(data.get("id", "")),
            duration_ms=data.get("duration", 0),  # SoundCloud uses milliseconds
            album=data.get("album"),
            isrc=data.get("isrc"),
            status=TrackStatus.COMPLETE if data.get("id") else TrackStatus.INCOMPLETE,
            metadata={
                "genre": data.get("genre"),
                "description": data.get("description"),
                "stream_url": data.get("stream_url"),
                "permalink_url": data.get("permalink_url"),
                "artwork_url": data.get("artwork_url"),
                "playback_count": data.get("playback_count"),
                "likes_count": data.get("likes_count"),
                "created_at": data.get("created_at"),
            }
        )
