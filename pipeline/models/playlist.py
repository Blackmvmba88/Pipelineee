"""Playlist model for Pipeline."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from pipeline.models.track import Track, Platform


@dataclass
class Playlist:
    """
    Represents a music playlist.
    
    Attributes:
        name: Playlist name
        platform: Source platform
        platform_id: Unique identifier on the source platform
        tracks: List of tracks in the playlist
        description: Playlist description (optional)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    name: str
    platform: Platform
    platform_id: str
    tracks: List[Track] = field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_track(self, track: Track) -> None:
        """Add a track to the playlist."""
        self.tracks.append(track)
        self.updated_at = datetime.now()
    
    def remove_track(self, platform_id: str) -> Optional[Track]:
        """Remove a track by platform_id."""
        for i, track in enumerate(self.tracks):
            if track.platform_id == platform_id:
                removed = self.tracks.pop(i)
                self.updated_at = datetime.now()
                return removed
        return None
    
    def get_track_count(self) -> int:
        """Get the number of tracks in the playlist."""
        return len(self.tracks)
    
    def get_total_duration_ms(self) -> int:
        """Get total duration of all tracks in milliseconds."""
        return sum(track.duration_ms for track in self.tracks)
    
    def find_incomplete_tracks(self) -> List[Track]:
        """Find all tracks that are incomplete."""
        return [track for track in self.tracks if not track.is_complete()]
    
    def to_dict(self) -> dict:
        """Convert playlist to dictionary representation."""
        return {
            "name": self.name,
            "platform": self.platform.value,
            "platform_id": self.platform_id,
            "tracks": [track.to_dict() for track in self.tracks],
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Playlist":
        """Create a Playlist from dictionary representation."""
        playlist = cls(
            name=data["name"],
            platform=Platform(data["platform"]),
            platform_id=data["platform_id"],
            description=data.get("description"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
        )
        for track_data in data.get("tracks", []):
            playlist.tracks.append(Track.from_dict(track_data))
        return playlist
