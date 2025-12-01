"""Track model for Pipeline."""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Platform(Enum):
    """Supported music platforms."""
    SPOTIFY = "spotify"
    SUNO = "suno"
    SOUNDCLOUD = "soundcloud"


class TrackStatus(Enum):
    """Track verification status."""
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    MISSING = "missing"
    PENDING = "pending"


@dataclass
class Track:
    """
    Represents a music track with metadata.
    
    Attributes:
        title: Track title
        artist: Artist name
        platform: Source platform (Spotify, Suno, SoundCloud)
        platform_id: Unique identifier on the source platform
        duration_ms: Duration in milliseconds
        album: Album name (optional)
        isrc: International Standard Recording Code (optional)
        status: Verification status
        metadata: Additional metadata dictionary
    """
    title: str
    artist: str
    platform: Platform
    platform_id: str
    duration_ms: int = 0
    album: Optional[str] = None
    isrc: Optional[str] = None
    status: TrackStatus = TrackStatus.PENDING
    metadata: dict = field(default_factory=dict)
    
    def matches(self, other: "Track", tolerance_ms: int = 3000) -> bool:
        """
        Check if this track matches another track.
        
        Matching is based on title, artist, and duration within tolerance.
        
        Args:
            other: Another Track to compare against
            tolerance_ms: Duration tolerance in milliseconds (default 3 seconds)
            
        Returns:
            True if tracks are considered matching
        """
        title_match = self.title.lower().strip() == other.title.lower().strip()
        artist_match = self.artist.lower().strip() == other.artist.lower().strip()
        duration_match = abs(self.duration_ms - other.duration_ms) <= tolerance_ms
        
        # Also check ISRC if both tracks have it
        if self.isrc and other.isrc:
            return self.isrc == other.isrc
        
        return title_match and artist_match and duration_match
    
    def is_complete(self) -> bool:
        """Check if track has all required metadata."""
        return bool(
            self.title 
            and self.artist 
            and self.duration_ms > 0 
            and self.platform_id
        )
    
    def to_dict(self) -> dict:
        """Convert track to dictionary representation."""
        return {
            "title": self.title,
            "artist": self.artist,
            "platform": self.platform.value,
            "platform_id": self.platform_id,
            "duration_ms": self.duration_ms,
            "album": self.album,
            "isrc": self.isrc,
            "status": self.status.value,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Track":
        """Create a Track from dictionary representation."""
        return cls(
            title=data["title"],
            artist=data["artist"],
            platform=Platform(data["platform"]),
            platform_id=data["platform_id"],
            duration_ms=data.get("duration_ms", 0),
            album=data.get("album"),
            isrc=data.get("isrc"),
            status=TrackStatus(data.get("status", "pending")),
            metadata=data.get("metadata", {}),
        )
