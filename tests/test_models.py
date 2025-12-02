"""Tests for track and playlist models."""

import pytest
from datetime import datetime

from pipeline.models.track import Track, Platform, TrackStatus
from pipeline.models.playlist import Playlist


class TestTrack:
    """Tests for the Track model."""
    
    def test_track_creation(self):
        """Test creating a basic track."""
        track = Track(
            title="Test Song",
            artist="Test Artist",
            platform=Platform.SPOTIFY,
            platform_id="abc123",
            duration_ms=180000,
        )
        
        assert track.title == "Test Song"
        assert track.artist == "Test Artist"
        assert track.platform == Platform.SPOTIFY
        assert track.platform_id == "abc123"
        assert track.duration_ms == 180000
        assert track.status == TrackStatus.PENDING
    
    def test_track_with_full_metadata(self):
        """Test creating a track with all metadata."""
        track = Track(
            title="Complete Song",
            artist="Complete Artist",
            platform=Platform.SUNO,
            platform_id="xyz789",
            duration_ms=240000,
            album="Complete Album",
            isrc="USRC12345678",
            status=TrackStatus.COMPLETE,
            metadata={"genre": "Pop"},
        )
        
        assert track.album == "Complete Album"
        assert track.isrc == "USRC12345678"
        assert track.status == TrackStatus.COMPLETE
        assert track.metadata["genre"] == "Pop"
    
    def test_track_matches_same_track(self):
        """Test that identical tracks match."""
        track1 = Track(
            title="Same Song",
            artist="Same Artist",
            platform=Platform.SPOTIFY,
            platform_id="id1",
            duration_ms=180000,
        )
        track2 = Track(
            title="Same Song",
            artist="Same Artist",
            platform=Platform.SOUNDCLOUD,
            platform_id="id2",
            duration_ms=180000,
        )
        
        assert track1.matches(track2)
    
    def test_track_matches_with_tolerance(self):
        """Test track matching with duration tolerance."""
        track1 = Track(
            title="Same Song",
            artist="Same Artist",
            platform=Platform.SPOTIFY,
            platform_id="id1",
            duration_ms=180000,
        )
        track2 = Track(
            title="Same Song",
            artist="Same Artist",
            platform=Platform.SOUNDCLOUD,
            platform_id="id2",
            duration_ms=182000,  # 2 seconds difference
        )
        
        assert track1.matches(track2, tolerance_ms=3000)
    
    def test_track_does_not_match_different_title(self):
        """Test that tracks with different titles don't match."""
        track1 = Track(
            title="Song A",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="id1",
            duration_ms=180000,
        )
        track2 = Track(
            title="Song B",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="id2",
            duration_ms=180000,
        )
        
        assert not track1.matches(track2)
    
    def test_track_matches_by_isrc(self):
        """Test track matching by ISRC code."""
        track1 = Track(
            title="Different Title 1",
            artist="Different Artist 1",
            platform=Platform.SPOTIFY,
            platform_id="id1",
            duration_ms=180000,
            isrc="USRC12345678",
        )
        track2 = Track(
            title="Different Title 2",
            artist="Different Artist 2",
            platform=Platform.SOUNDCLOUD,
            platform_id="id2",
            duration_ms=200000,
            isrc="USRC12345678",
        )
        
        # ISRC match takes precedence
        assert track1.matches(track2)
    
    def test_track_is_complete(self):
        """Test track completeness check."""
        complete_track = Track(
            title="Complete",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="id1",
            duration_ms=180000,
        )
        
        incomplete_track = Track(
            title="Incomplete",
            artist="",
            platform=Platform.SPOTIFY,
            platform_id="id2",
            duration_ms=0,
        )
        
        assert complete_track.is_complete()
        assert not incomplete_track.is_complete()
    
    def test_track_to_dict(self):
        """Test track serialization to dictionary."""
        track = Track(
            title="Test Song",
            artist="Test Artist",
            platform=Platform.SPOTIFY,
            platform_id="abc123",
            duration_ms=180000,
            album="Test Album",
        )
        
        data = track.to_dict()
        
        assert data["title"] == "Test Song"
        assert data["artist"] == "Test Artist"
        assert data["platform"] == "spotify"
        assert data["platform_id"] == "abc123"
        assert data["duration_ms"] == 180000
        assert data["album"] == "Test Album"
    
    def test_track_from_dict(self):
        """Test track deserialization from dictionary."""
        data = {
            "title": "Test Song",
            "artist": "Test Artist",
            "platform": "suno",
            "platform_id": "xyz789",
            "duration_ms": 200000,
            "album": "Test Album",
            "isrc": "USRC12345678",
            "status": "complete",
            "metadata": {"key": "value"},
        }
        
        track = Track.from_dict(data)
        
        assert track.title == "Test Song"
        assert track.platform == Platform.SUNO
        assert track.isrc == "USRC12345678"
        assert track.status == TrackStatus.COMPLETE


class TestPlaylist:
    """Tests for the Playlist model."""
    
    def test_playlist_creation(self):
        """Test creating a basic playlist."""
        playlist = Playlist(
            name="My Playlist",
            platform=Platform.SPOTIFY,
            platform_id="playlist123",
        )
        
        assert playlist.name == "My Playlist"
        assert playlist.platform == Platform.SPOTIFY
        assert playlist.get_track_count() == 0
    
    def test_playlist_add_track(self):
        """Test adding tracks to a playlist."""
        playlist = Playlist(
            name="My Playlist",
            platform=Platform.SPOTIFY,
            platform_id="playlist123",
        )
        
        track = Track(
            title="Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="track123",
            duration_ms=180000,
        )
        
        playlist.add_track(track)
        
        assert playlist.get_track_count() == 1
        assert playlist.tracks[0].title == "Song"
    
    def test_playlist_remove_track(self):
        """Test removing tracks from a playlist."""
        playlist = Playlist(
            name="My Playlist",
            platform=Platform.SPOTIFY,
            platform_id="playlist123",
        )
        
        track = Track(
            title="Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="track123",
            duration_ms=180000,
        )
        
        playlist.add_track(track)
        removed = playlist.remove_track("track123")
        
        assert removed is not None
        assert removed.title == "Song"
        assert playlist.get_track_count() == 0
    
    def test_playlist_total_duration(self):
        """Test calculating total playlist duration."""
        playlist = Playlist(
            name="My Playlist",
            platform=Platform.SPOTIFY,
            platform_id="playlist123",
        )
        
        track1 = Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="track1",
            duration_ms=180000,
        )
        track2 = Track(
            title="Song 2",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="track2",
            duration_ms=200000,
        )
        
        playlist.add_track(track1)
        playlist.add_track(track2)
        
        assert playlist.get_total_duration_ms() == 380000
    
    def test_playlist_find_incomplete_tracks(self):
        """Test finding incomplete tracks in a playlist."""
        playlist = Playlist(
            name="My Playlist",
            platform=Platform.SPOTIFY,
            platform_id="playlist123",
        )
        
        complete_track = Track(
            title="Complete",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="track1",
            duration_ms=180000,
        )
        incomplete_track = Track(
            title="Incomplete",
            artist="",  # Missing artist
            platform=Platform.SPOTIFY,
            platform_id="track2",
            duration_ms=0,  # Invalid duration
        )
        
        playlist.add_track(complete_track)
        playlist.add_track(incomplete_track)
        
        incomplete = playlist.find_incomplete_tracks()
        
        assert len(incomplete) == 1
        assert incomplete[0].title == "Incomplete"
    
    def test_playlist_serialization(self):
        """Test playlist serialization and deserialization."""
        playlist = Playlist(
            name="My Playlist",
            platform=Platform.SPOTIFY,
            platform_id="playlist123",
            description="Test playlist",
        )
        
        track = Track(
            title="Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="track123",
            duration_ms=180000,
        )
        playlist.add_track(track)
        
        # Serialize
        data = playlist.to_dict()
        
        # Deserialize
        restored = Playlist.from_dict(data)
        
        assert restored.name == "My Playlist"
        assert restored.platform == Platform.SPOTIFY
        assert restored.get_track_count() == 1
        assert restored.tracks[0].title == "Song"
    
    def test_playlist_merge_with(self):
        """Test merging two playlists."""
        # Create first playlist
        playlist1 = Playlist(
            name="SoundCloud Playlist",
            platform=Platform.SOUNDCLOUD,
            platform_id="sc1",
        )
        playlist1.add_track(Track(
            title="Song A",
            artist="Artist 1",
            platform=Platform.SOUNDCLOUD,
            platform_id="sc_a",
            duration_ms=180000,
        ))
        playlist1.add_track(Track(
            title="Song B",
            artist="Artist 2",
            platform=Platform.SOUNDCLOUD,
            platform_id="sc_b",
            duration_ms=200000,
        ))
        
        # Create second playlist
        playlist2 = Playlist(
            name="Suno Playlist",
            platform=Platform.SUNO,
            platform_id="suno1",
        )
        playlist2.add_track(Track(
            title="Song B",  # Duplicate
            artist="Artist 2",
            platform=Platform.SUNO,
            platform_id="suno_b",
            duration_ms=200000,
        ))
        playlist2.add_track(Track(
            title="Song C",
            artist="Artist 3",
            platform=Platform.SUNO,
            platform_id="suno_c",
            duration_ms=220000,
        ))
        
        # Merge playlists
        merged = playlist1.merge_with(playlist2)
        
        # Check merged playlist
        assert merged.name == "SoundCloud Playlist + Suno Playlist"
        assert merged.get_track_count() == 3  # A, B (no duplicate), C
        
        # Check order is preserved
        assert merged.tracks[0].title == "Song A"
        assert merged.tracks[1].title == "Song B"
        assert merged.tracks[2].title == "Song C"
        
        # Check platforms are preserved
        assert merged.tracks[0].platform == Platform.SOUNDCLOUD
        assert merged.tracks[1].platform == Platform.SOUNDCLOUD
        assert merged.tracks[2].platform == Platform.SUNO
    
    def test_playlist_merge_with_no_duplicates(self):
        """Test merging playlists with no duplicates."""
        playlist1 = Playlist(
            name="Playlist 1",
            platform=Platform.SPOTIFY,
            platform_id="p1",
        )
        playlist1.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
        ))
        
        playlist2 = Playlist(
            name="Playlist 2",
            platform=Platform.SOUNDCLOUD,
            platform_id="p2",
        )
        playlist2.add_track(Track(
            title="Song 2",
            artist="Artist",
            platform=Platform.SOUNDCLOUD,
            platform_id="t2",
            duration_ms=200000,
        ))
        
        merged = playlist1.merge_with(playlist2)
        
        assert merged.get_track_count() == 2
