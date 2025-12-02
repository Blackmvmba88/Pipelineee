"""Tests for sync service."""

import pytest

from pipeline.models.track import Track, Platform, TrackStatus
from pipeline.models.playlist import Playlist
from pipeline.sync import SyncService, SyncAction


class TestSyncService:
    """Tests for the SyncService."""
    
    def test_compare_identical_playlists(self):
        """Test comparing identical playlists."""
        service = SyncService()
        
        # Create source playlist
        source = Playlist(
            name="Source",
            platform=Platform.SPOTIFY,
            platform_id="source1",
        )
        source.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="s1",
            duration_ms=180000,
        ))
        
        # Create target playlist with matching track
        target = Playlist(
            name="Target",
            platform=Platform.SOUNDCLOUD,
            platform_id="target1",
        )
        target.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SOUNDCLOUD,
            platform_id="sc1",
            duration_ms=180000,
        ))
        
        report = service.compare_playlists(source, target)
        
        assert report.total_tracks == 1
        assert report.matched_tracks == 1
        assert report.missing_tracks == 0
        assert report.match_rate == 100.0
    
    def test_compare_playlists_with_missing_track(self):
        """Test comparing playlists where target is missing a track."""
        service = SyncService()
        
        source = Playlist(
            name="Source",
            platform=Platform.SPOTIFY,
            platform_id="source1",
        )
        source.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="s1",
            duration_ms=180000,
        ))
        source.add_track(Track(
            title="Song 2",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="s2",
            duration_ms=200000,
        ))
        
        target = Playlist(
            name="Target",
            platform=Platform.SOUNDCLOUD,
            platform_id="target1",
        )
        target.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SOUNDCLOUD,
            platform_id="sc1",
            duration_ms=180000,
        ))
        # Song 2 is missing from target
        
        report = service.compare_playlists(source, target)
        
        assert report.total_tracks == 2
        assert report.matched_tracks == 1
        assert report.missing_tracks == 1
        assert report.match_rate == 50.0
    
    def test_find_missing_tracks(self):
        """Test finding tracks missing from platforms."""
        service = SyncService()
        
        master = [
            Track(
                title="Song 1",
                artist="Artist",
                platform=Platform.SPOTIFY,
                platform_id="m1",
                duration_ms=180000,
            ),
            Track(
                title="Song 2",
                artist="Artist",
                platform=Platform.SPOTIFY,
                platform_id="m2",
                duration_ms=200000,
            ),
        ]
        
        platforms = {
            Platform.SOUNDCLOUD: [
                Track(
                    title="Song 1",
                    artist="Artist",
                    platform=Platform.SOUNDCLOUD,
                    platform_id="sc1",
                    duration_ms=180000,
                ),
            ],
            Platform.SUNO: [],
        }
        
        missing = service.find_missing_tracks(master, platforms)
        
        assert len(missing[Platform.SOUNDCLOUD]) == 1
        assert missing[Platform.SOUNDCLOUD][0].title == "Song 2"
        assert len(missing[Platform.SUNO]) == 2
    
    def test_verify_track_completeness(self):
        """Test verifying track completeness."""
        service = SyncService()
        
        tracks = [
            Track(
                title="Complete",
                artist="Artist",
                platform=Platform.SPOTIFY,
                platform_id="t1",
                duration_ms=180000,
            ),
            Track(
                title="Incomplete",
                artist="",
                platform=Platform.SPOTIFY,
                platform_id="t2",
                duration_ms=0,
            ),
        ]
        
        complete, incomplete = service.verify_track_completeness(tracks)
        
        assert len(complete) == 1
        assert len(incomplete) == 1
        assert complete[0].status == TrackStatus.COMPLETE
        assert incomplete[0].status == TrackStatus.INCOMPLETE
    
    def test_align_tracks(self):
        """Test aligning tracks between lists."""
        service = SyncService()
        
        source = [
            Track(
                title="Song A",
                artist="Artist",
                platform=Platform.SPOTIFY,
                platform_id="s1",
                duration_ms=180000,
            ),
            Track(
                title="Song B",
                artist="Artist",
                platform=Platform.SPOTIFY,
                platform_id="s2",
                duration_ms=200000,
            ),
        ]
        
        target = [
            Track(
                title="Song B",
                artist="Artist",
                platform=Platform.SOUNDCLOUD,
                platform_id="sc2",
                duration_ms=200000,
            ),
            Track(
                title="Song A",
                artist="Artist",
                platform=Platform.SOUNDCLOUD,
                platform_id="sc1",
                duration_ms=180000,
            ),
        ]
        
        aligned = service.align_tracks(source, target)
        
        assert len(aligned) == 2
        assert aligned[0][0].title == "Song A"
        assert aligned[0][1] is not None
        assert aligned[0][1].title == "Song A"
        assert aligned[1][0].title == "Song B"
        assert aligned[1][1] is not None
        assert aligned[1][1].title == "Song B"
    
    def test_cross_platform_sync(self):
        """Test cross-platform synchronization."""
        service = SyncService()
        
        spotify = Playlist(
            name="Spotify Playlist",
            platform=Platform.SPOTIFY,
            platform_id="sp1",
        )
        spotify.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="s1",
            duration_ms=180000,
        ))
        
        suno = Playlist(
            name="Suno Playlist",
            platform=Platform.SUNO,
            platform_id="su1",
        )
        suno.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SUNO,
            platform_id="sn1",
            duration_ms=180000,
        ))
        
        playlists = {
            Platform.SPOTIFY: spotify,
            Platform.SUNO: suno,
        }
        
        reports = service.cross_platform_sync(playlists)
        
        assert "spotify_vs_suno" in reports
        assert reports["spotify_vs_suno"].matched_tracks == 1
    
    def test_merge_playlists(self):
        """Test merging multiple playlists with SyncService."""
        service = SyncService()
        
        # Create first playlist
        playlist1 = Playlist(
            name="SoundCloud",
            platform=Platform.SOUNDCLOUD,
            platform_id="sc1",
        )
        playlist1.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SOUNDCLOUD,
            platform_id="sc1",
            duration_ms=180000,
        ))
        playlist1.add_track(Track(
            title="Song 2",
            artist="Artist",
            platform=Platform.SOUNDCLOUD,
            platform_id="sc2",
            duration_ms=200000,
        ))
        
        # Create second playlist
        playlist2 = Playlist(
            name="Suno",
            platform=Platform.SUNO,
            platform_id="suno1",
        )
        playlist2.add_track(Track(
            title="Song 2",  # Duplicate
            artist="Artist",
            platform=Platform.SUNO,
            platform_id="suno2",
            duration_ms=200000,
        ))
        playlist2.add_track(Track(
            title="Song 3",
            artist="Artist",
            platform=Platform.SUNO,
            platform_id="suno3",
            duration_ms=220000,
        ))
        
        merged = service.merge_playlists(
            [playlist1, playlist2], 
            "Merged Playlist"
        )
        
        assert merged.name == "Merged Playlist"
        assert merged.get_track_count() == 3  # 1, 2, 3 (no duplicate)
        
        # Check order is preserved
        assert merged.tracks[0].title == "Song 1"
        assert merged.tracks[1].title == "Song 2"
        assert merged.tracks[2].title == "Song 3"
    
    def test_merge_playlists_empty_list(self):
        """Test merging empty list raises error."""
        service = SyncService()
        
        with pytest.raises(ValueError, match="Cannot merge empty list"):
            service.merge_playlists([], "Test")
