"""Dashboard application for Pipeline."""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

from pipeline.models.track import Track, Platform
from pipeline.models.playlist import Playlist
from pipeline.connectors.base import BaseConnector
from pipeline.connectors.spotify import SpotifyConnector
from pipeline.connectors.suno import SunoConnector
from pipeline.connectors.soundcloud import SoundCloudConnector
from pipeline.sync import SyncService, SyncReport
from pipeline.reports.generator import ReportGenerator
from pipeline.reports.formatter import ReportFormatter
from pipeline.dashboard.views import (
    LibraryView,
    SyncView,
    DistributionView,
    MetadataView,
)


@dataclass
class DashboardState:
    """State management for the dashboard."""
    playlists: List[Playlist] = field(default_factory=list)
    sync_reports: Dict[str, SyncReport] = field(default_factory=dict)
    missing_tracks: Dict[Platform, List[Track]] = field(default_factory=dict)
    last_sync_time: Optional[str] = None


class Dashboard:
    """
    Main dashboard application for Pipeline.
    
    Provides a unified interface for managing music workflow,
    including library browsing, synchronization, metadata management,
    and distribution preparation.
    """
    
    def __init__(self):
        self.state = DashboardState()
        self.connectors: Dict[Platform, BaseConnector] = {}
        self.sync_service = SyncService()
        self.report_generator = ReportGenerator()
        self.report_formatter = ReportFormatter()
    
    def register_connector(self, platform: Platform, connector: BaseConnector) -> None:
        """
        Register a platform connector.
        
        Args:
            platform: Platform type
            connector: Connector instance
        """
        self.connectors[platform] = connector
    
    def initialize_connectors(self, credentials: Dict[Platform, dict]) -> Dict[Platform, bool]:
        """
        Initialize all platform connectors with credentials.
        
        Args:
            credentials: Dictionary mapping platforms to their credentials
            
        Returns:
            Dictionary mapping platforms to authentication success status
        """
        results: Dict[Platform, bool] = {}
        
        for platform, creds in credentials.items():
            if platform == Platform.SPOTIFY:
                connector = SpotifyConnector()
            elif platform == Platform.SUNO:
                connector = SunoConnector()
            elif platform == Platform.SOUNDCLOUD:
                connector = SoundCloudConnector()
            else:
                continue
            
            success = connector.authenticate(creds)
            if success:
                self.register_connector(platform, connector)
            results[platform] = success
        
        return results
    
    def refresh_playlists(self) -> int:
        """
        Refresh playlists from all connected platforms.
        
        Returns:
            Number of playlists loaded
        """
        self.state.playlists = []
        
        for platform, connector in self.connectors.items():
            if connector.is_authenticated():
                playlists = connector.get_playlists()
                self.state.playlists.extend(playlists)
        
        return len(self.state.playlists)
    
    def add_playlist(self, playlist: Playlist) -> None:
        """
        Add a playlist to the dashboard state.
        
        Args:
            playlist: Playlist to add
        """
        self.state.playlists.append(playlist)
    
    def run_sync(self) -> Dict[str, SyncReport]:
        """
        Run synchronization across all playlists.
        
        Returns:
            Dictionary of sync reports by comparison name
        """
        from datetime import datetime
        
        playlists_by_platform: Dict[Platform, Playlist] = {}
        
        # Group playlists by platform (take first of each for simplicity)
        for playlist in self.state.playlists:
            if playlist.platform not in playlists_by_platform:
                playlists_by_platform[playlist.platform] = playlist
        
        self.state.sync_reports = self.sync_service.cross_platform_sync(
            playlists_by_platform
        )
        self.state.last_sync_time = datetime.now().isoformat()
        
        return self.state.sync_reports
    
    def find_missing(self, master_tracks: List[Track]) -> Dict[Platform, List[Track]]:
        """
        Find tracks missing from each platform.
        
        Args:
            master_tracks: Master list of tracks
            
        Returns:
            Dictionary mapping platforms to missing tracks
        """
        platform_tracks: Dict[Platform, List[Track]] = {}
        
        for playlist in self.state.playlists:
            if playlist.platform not in platform_tracks:
                platform_tracks[playlist.platform] = []
            platform_tracks[playlist.platform].extend(playlist.tracks)
        
        self.state.missing_tracks = self.sync_service.find_missing_tracks(
            master_tracks, platform_tracks
        )
        
        return self.state.missing_tracks
    
    def get_library_view(self) -> Dict[str, Any]:
        """Get the library overview view."""
        view = LibraryView(self.state.playlists)
        return view.render()
    
    def get_sync_view(self) -> Dict[str, Any]:
        """Get the synchronization status view."""
        view = SyncView(self.state.sync_reports, self.state.missing_tracks)
        return view.render()
    
    def get_distribution_view(self) -> Dict[str, Any]:
        """Get the distribution readiness view."""
        all_tracks = []
        for playlist in self.state.playlists:
            all_tracks.extend(playlist.tracks)
        
        view = DistributionView(all_tracks)
        return view.render()
    
    def get_metadata_view(self) -> Dict[str, Any]:
        """Get the metadata management view."""
        all_tracks = []
        for playlist in self.state.playlists:
            all_tracks.extend(playlist.tracks)
        
        view = MetadataView(all_tracks)
        return view.render()
    
    def generate_report(self, format: str = "markdown") -> str:
        """
        Generate a full report in the specified format.
        
        Args:
            format: Output format (json, markdown, text, html)
            
        Returns:
            Formatted report string
        """
        report = self.report_generator.generate_full_report(
            self.state.playlists,
            self.state.sync_reports,
            self.state.missing_tracks,
        )
        
        if format == "json":
            return self.report_formatter.to_json(report)
        elif format == "markdown":
            return self.report_formatter.to_markdown(report)
        elif format == "text":
            return self.report_formatter.to_text(report)
        elif format == "html":
            return self.report_formatter.to_html(report)
        else:
            return self.report_formatter.to_json(report)
    
    def get_all_tracks(self) -> List[Track]:
        """Get all tracks from all playlists."""
        all_tracks = []
        for playlist in self.state.playlists:
            all_tracks.extend(playlist.tracks)
        return all_tracks
    
    def get_incomplete_tracks(self) -> List[Track]:
        """Get all incomplete tracks."""
        incomplete = []
        for playlist in self.state.playlists:
            incomplete.extend(playlist.find_incomplete_tracks())
        return incomplete
    
    def export_state(self) -> Dict[str, Any]:
        """
        Export the current dashboard state.
        
        Note: sync_reports and missing_tracks are included for informational purposes
        but will need to be regenerated when imported (by calling run_sync()).
        
        Returns:
            Dictionary representation of state
        """
        return {
            "playlists": [p.to_dict() for p in self.state.playlists],
            "sync_reports": {
                name: {
                    "total_tracks": r.total_tracks,
                    "matched_tracks": r.matched_tracks,
                    "missing_tracks": r.missing_tracks,
                    "incomplete_tracks": r.incomplete_tracks,
                }
                for name, r in self.state.sync_reports.items()
            },
            "missing_tracks": {
                p.value: [t.to_dict() for t in tracks]
                for p, tracks in self.state.missing_tracks.items()
            },
            "last_sync_time": self.state.last_sync_time,
        }
    
    def import_state(self, data: Dict[str, Any]) -> None:
        """
        Import dashboard state from a dictionary.
        
        Note: Only playlists and last_sync_time are restored. Sync reports and
        missing tracks need to be regenerated by calling run_sync() after import.
        
        Args:
            data: Previously exported state dictionary
        """
        self.state.playlists = [
            Playlist.from_dict(p) for p in data.get("playlists", [])
        ]
        self.state.last_sync_time = data.get("last_sync_time")
