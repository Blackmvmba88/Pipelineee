"""Test for get_suno_tracks functionality."""

from pipeline.models.track import Track, Platform
from pipeline.models.playlist import Playlist
from pipeline.dashboard.app import Dashboard


def test_get_suno_tracks():
    """Test getting only Suno tracks from dashboard."""
    dashboard = Dashboard()
    
    # Create Suno playlist with tracks
    suno_playlist = Playlist(
        name="Suno Creations",
        platform=Platform.SUNO,
        platform_id="suno_p1",
    )
    suno_playlist.add_track(Track(
        title="Electric Dreams",
        artist="AI Generated",
        platform=Platform.SUNO,
        platform_id="suno_t1",
        duration_ms=180000,
    ))
    suno_playlist.add_track(Track(
        title="Midnight Jazz",
        artist="Suno AI",
        platform=Platform.SUNO,
        platform_id="suno_t2",
        duration_ms=240000,
    ))
    
    # Create Spotify playlist
    spotify_playlist = Playlist(
        name="Spotify Favorites",
        platform=Platform.SPOTIFY,
        platform_id="spotify_p1",
    )
    spotify_playlist.add_track(Track(
        title="Regular Song",
        artist="Regular Artist",
        platform=Platform.SPOTIFY,
        platform_id="spotify_t1",
        duration_ms=200000,
    ))
    
    # Add both playlists
    dashboard.add_playlist(suno_playlist)
    dashboard.add_playlist(spotify_playlist)
    
    # Get only Suno tracks
    suno_tracks = dashboard.get_suno_tracks()
    
    # Verify we got only Suno tracks
    assert len(suno_tracks) == 2
    assert all(track.platform == Platform.SUNO for track in suno_tracks)
    assert suno_tracks[0].title == "Electric Dreams"
    assert suno_tracks[1].title == "Midnight Jazz"


def test_get_suno_tracks_empty():
    """Test getting Suno tracks when there are none."""
    dashboard = Dashboard()
    
    # Create only Spotify playlist
    spotify_playlist = Playlist(
        name="Spotify Only",
        platform=Platform.SPOTIFY,
        platform_id="spotify_p1",
    )
    spotify_playlist.add_track(Track(
        title="Regular Song",
        artist="Regular Artist",
        platform=Platform.SPOTIFY,
        platform_id="spotify_t1",
        duration_ms=200000,
    ))
    
    dashboard.add_playlist(spotify_playlist)
    
    # Get Suno tracks (should be empty)
    suno_tracks = dashboard.get_suno_tracks()
    
    assert len(suno_tracks) == 0


def test_get_tracks_by_platform():
    """Test getting tracks by any platform."""
    dashboard = Dashboard()
    
    # Create playlists for different platforms
    platforms_data = [
        (Platform.SUNO, "Suno Track", "suno_t1"),
        (Platform.SPOTIFY, "Spotify Track", "spotify_t1"),
        (Platform.SOUNDCLOUD, "SoundCloud Track", "sc_t1"),
    ]
    
    for platform, title, track_id in platforms_data:
        playlist = Playlist(
            name=f"{platform.value} Playlist",
            platform=platform,
            platform_id=f"{platform.value}_p1",
        )
        playlist.add_track(Track(
            title=title,
            artist="Test Artist",
            platform=platform,
            platform_id=track_id,
            duration_ms=180000,
        ))
        dashboard.add_playlist(playlist)
    
    # Test getting tracks for each platform
    suno_tracks = dashboard.get_tracks_by_platform(Platform.SUNO)
    assert len(suno_tracks) == 1
    assert suno_tracks[0].title == "Suno Track"
    
    spotify_tracks = dashboard.get_tracks_by_platform(Platform.SPOTIFY)
    assert len(spotify_tracks) == 1
    assert spotify_tracks[0].title == "Spotify Track"
    
    soundcloud_tracks = dashboard.get_tracks_by_platform(Platform.SOUNDCLOUD)
    assert len(soundcloud_tracks) == 1
    assert soundcloud_tracks[0].title == "SoundCloud Track"


if __name__ == "__main__":
    # Run tests
    test_get_suno_tracks()
    test_get_suno_tracks_empty()
    test_get_tracks_by_platform()
    print("All tests passed!")
