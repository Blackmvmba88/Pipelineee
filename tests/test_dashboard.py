"""Tests for the Dashboard."""

import pytest

from pipeline.models.track import Track, Platform
from pipeline.models.playlist import Playlist
from pipeline.dashboard.app import Dashboard
from pipeline.dashboard.views import (
    LibraryView,
    SyncView,
    DistributionView,
    MetadataView,
)


class TestDashboard:
    """Tests for the Dashboard application."""
    
    def test_dashboard_creation(self):
        """Test creating a dashboard."""
        dashboard = Dashboard()
        
        assert dashboard.state.playlists == []
        assert dashboard.connectors == {}
    
    def test_add_playlist(self):
        """Test adding a playlist to the dashboard."""
        dashboard = Dashboard()
        
        playlist = Playlist(
            name="Test Playlist",
            platform=Platform.SPOTIFY,
            platform_id="p1",
        )
        
        dashboard.add_playlist(playlist)
        
        assert len(dashboard.state.playlists) == 1
    
    def test_get_all_tracks(self):
        """Test getting all tracks from dashboard."""
        dashboard = Dashboard()
        
        playlist = Playlist(
            name="Test",
            platform=Platform.SPOTIFY,
            platform_id="p1",
        )
        playlist.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
        ))
        
        dashboard.add_playlist(playlist)
        
        tracks = dashboard.get_all_tracks()
        
        assert len(tracks) == 1
        assert tracks[0].title == "Song 1"
    
    def test_export_import_state(self):
        """Test exporting and importing dashboard state."""
        dashboard = Dashboard()
        
        playlist = Playlist(
            name="Test Playlist",
            platform=Platform.SPOTIFY,
            platform_id="p1",
        )
        playlist.add_track(Track(
            title="Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
        ))
        
        dashboard.add_playlist(playlist)
        
        # Export
        state = dashboard.export_state()
        
        # Create new dashboard and import
        new_dashboard = Dashboard()
        new_dashboard.import_state(state)
        
        assert len(new_dashboard.state.playlists) == 1
        assert new_dashboard.state.playlists[0].name == "Test Playlist"
    
    def test_generate_report_markdown(self):
        """Test generating a markdown report."""
        dashboard = Dashboard()
        
        playlist = Playlist(
            name="Test Playlist",
            platform=Platform.SPOTIFY,
            platform_id="p1",
        )
        playlist.add_track(Track(
            title="Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
        ))
        
        dashboard.add_playlist(playlist)
        
        report = dashboard.generate_report(format="markdown")
        
        assert "# Pipeline Report" in report
        assert "## Library Summary" in report


class TestViews:
    """Tests for dashboard views."""
    
    def test_library_view(self):
        """Test library view rendering."""
        playlist = Playlist(
            name="Test Playlist",
            platform=Platform.SPOTIFY,
            platform_id="p1",
        )
        playlist.add_track(Track(
            title="Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
        ))
        
        view = LibraryView([playlist])
        data = view.render()
        
        assert data["view"] == "library"
        assert data["data"]["total_tracks"] == 1
        assert data["data"]["total_playlists"] == 1
    
    def test_distribution_view(self):
        """Test distribution view rendering."""
        ready_track = Track(
            title="Ready",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
            album="Album",
            isrc="USRC12345678",
        )
        
        view = DistributionView([ready_track])
        data = view.render()
        
        assert data["view"] == "distribution"
        assert data["data"]["ready_count"] == 1
    
    def test_metadata_view(self):
        """Test metadata view rendering."""
        track = Track(
            title="Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
        )
        
        view = MetadataView([track])
        data = view.render()
        
        assert data["view"] == "metadata"
        assert data["data"]["total_tracks"] == 1
