"""Spotify connector for Pipeline."""

from typing import List, Optional

from pipeline.connectors.base import BaseConnector
from pipeline.models.track import Track, Platform, TrackStatus
from pipeline.models.playlist import Playlist


class SpotifyConnector(BaseConnector):
    """
    Connector for Spotify music platform.
    
    This connector interfaces with the Spotify Web API to fetch
    playlists and track information.
    
    Note: Requires Spotify Developer credentials (client_id, client_secret).
    """
    
    def __init__(self):
        self._authenticated = False
        self._access_token: Optional[str] = None
        self._user_id: Optional[str] = None
    
    def authenticate(self, credentials: dict) -> bool:
        """
        Authenticate with Spotify API.
        
        Args:
            credentials: Dictionary containing:
                - client_id: Spotify application client ID
                - client_secret: Spotify application client secret
                - redirect_uri: OAuth redirect URI (optional)
                - access_token: Pre-existing access token (optional)
                
        Returns:
            True if authentication was successful
        """
        # In production, this would use the Spotify OAuth flow
        # For now, we accept a pre-existing access token
        if "access_token" in credentials:
            self._access_token = credentials["access_token"]
            self._authenticated = True
            return True
        
        # TODO: Implement full OAuth flow
        # Required: client_id and client_secret
        if "client_id" in credentials and "client_secret" in credentials:
            # Would make API call to get access token
            self._authenticated = True
            return True
        
        return False
    
    def get_playlists(self) -> List[Playlist]:
        """
        Fetch all user playlists from Spotify.
        
        Returns:
            List of Playlist objects
        """
        if not self.is_authenticated():
            return []
        
        # TODO: Implement actual API call
        # GET /v1/me/playlists
        return []
    
    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """
        Fetch a specific playlist by ID.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            Playlist object if found, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        # TODO: Implement actual API call
        # GET /v1/playlists/{playlist_id}
        return None
    
    def get_tracks(self, playlist_id: str) -> List[Track]:
        """
        Fetch all tracks from a Spotify playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            List of Track objects
        """
        if not self.is_authenticated():
            return []
        
        # TODO: Implement actual API call
        # GET /v1/playlists/{playlist_id}/tracks
        return []
    
    def get_track(self, track_id: str) -> Optional[Track]:
        """
        Fetch a specific track by ID.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track object if found, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        # TODO: Implement actual API call
        # GET /v1/tracks/{track_id}
        return None
    
    def search_track(self, title: str, artist: str) -> List[Track]:
        """
        Search for tracks on Spotify.
        
        Args:
            title: Track title to search for
            artist: Artist name to search for
            
        Returns:
            List of matching Track objects
        """
        if not self.is_authenticated():
            return []
        
        # TODO: Implement actual API call
        # GET /v1/search?q=track:{title}+artist:{artist}&type=track
        return []
    
    @staticmethod
    def parse_track_data(data: dict) -> Track:
        """
        Parse Spotify API track data into a Track object.
        
        Args:
            data: Raw track data from Spotify API
            
        Returns:
            Track object
        """
        artists = data.get("artists", [])
        artist_name = artists[0].get("name", "") if artists else ""
        
        album = data.get("album", {})
        album_name = album.get("name")
        
        return Track(
            title=data.get("name", ""),
            artist=artist_name,
            platform=Platform.SPOTIFY,
            platform_id=data.get("id", ""),
            duration_ms=data.get("duration_ms", 0),
            album=album_name,
            isrc=data.get("external_ids", {}).get("isrc"),
            status=TrackStatus.COMPLETE if data.get("id") else TrackStatus.INCOMPLETE,
            metadata={
                "popularity": data.get("popularity"),
                "explicit": data.get("explicit"),
                "preview_url": data.get("preview_url"),
                "external_urls": data.get("external_urls", {}),
            }
        )
