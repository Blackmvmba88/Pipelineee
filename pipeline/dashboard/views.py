"""Dashboard views for Pipeline."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from pipeline.models.track import Track, Platform, TrackStatus
from pipeline.models.playlist import Playlist


@dataclass
class ViewData:
    """Base class for view data."""
    title: str
    description: str


class BaseView(ABC):
    """Base class for dashboard views."""
    
    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """Render the view data as a dictionary."""
        pass


class LibraryView(BaseView):
    """View for library overview and management."""
    
    def __init__(self, playlists: List[Playlist]):
        self.playlists = playlists
    
    def render(self) -> Dict[str, Any]:
        """Render library view data."""
        total_tracks = 0
        total_duration = 0
        platform_counts: Dict[str, int] = {}
        
        for playlist in self.playlists:
            for track in playlist.tracks:
                total_tracks += 1
                total_duration += track.duration_ms
                platform_key = track.platform.value
                if platform_key not in platform_counts:
                    platform_counts[platform_key] = 0
                platform_counts[platform_key] += 1
        
        return {
            "view": "library",
            "title": "Music Library",
            "description": "Overview of your music library across all platforms",
            "data": {
                "total_tracks": total_tracks,
                "total_playlists": len(self.playlists),
                "total_duration_ms": total_duration,
                "total_duration_formatted": self._format_duration(total_duration),
                "platforms": platform_counts,
                "playlists": [
                    {
                        "name": p.name,
                        "platform": p.platform.value,
                        "track_count": len(p.tracks),
                    }
                    for p in self.playlists
                ],
            },
        }
    
    @staticmethod
    def _format_duration(ms: int) -> str:
        """Format duration in milliseconds to HH:MM:SS."""
        seconds = ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


class SyncView(BaseView):
    """View for synchronization status and actions."""
    
    def __init__(
        self, 
        sync_reports: Optional[Dict[str, Any]] = None,
        missing_tracks: Optional[Dict[Platform, List[Track]]] = None
    ):
        self.sync_reports = sync_reports or {}
        self.missing_tracks = missing_tracks or {}
    
    def render(self) -> Dict[str, Any]:
        """Render sync view data."""
        total_matched = 0
        total_missing = 0
        comparisons = []
        
        for name, report in self.sync_reports.items():
            if hasattr(report, 'matched_tracks'):
                total_matched += report.matched_tracks
                total_missing += report.missing_tracks
                comparisons.append({
                    "name": name,
                    "matched": report.matched_tracks,
                    "missing": report.missing_tracks,
                    "incomplete": report.incomplete_tracks,
                    "match_rate": report.match_rate,
                })
        
        missing_summary = {}
        for platform, tracks in self.missing_tracks.items():
            missing_summary[platform.value] = {
                "count": len(tracks),
                "tracks": [
                    {"title": t.title, "artist": t.artist}
                    for t in tracks[:10]  # Limit to 10 tracks
                ],
            }
        
        return {
            "view": "sync",
            "title": "Synchronization Status",
            "description": "Track alignment and synchronization across platforms",
            "data": {
                "total_matched": total_matched,
                "total_missing": total_missing,
                "comparisons": comparisons,
                "missing_by_platform": missing_summary,
            },
        }


class DistributionView(BaseView):
    """View for distribution preparation status."""
    
    def __init__(self, tracks: List[Track]):
        self.tracks = tracks
    
    def render(self) -> Dict[str, Any]:
        """Render distribution view data."""
        ready_tracks = []
        not_ready_tracks = []
        
        for track in self.tracks:
            issues = self._check_distribution_requirements(track)
            if issues:
                not_ready_tracks.append({
                    "track": track.to_dict(),
                    "issues": issues,
                })
            else:
                ready_tracks.append(track.to_dict())
        
        total = len(self.tracks)
        ready_count = len(ready_tracks)
        
        return {
            "view": "distribution",
            "title": "Distribution Readiness",
            "description": "Preparation status for music distribution",
            "data": {
                "total_tracks": total,
                "ready_count": ready_count,
                "not_ready_count": len(not_ready_tracks),
                "readiness_percentage": (ready_count / total * 100) if total > 0 else 0,
                "ready_tracks": ready_tracks,
                "tracks_with_issues": not_ready_tracks[:20],  # Limit output
            },
        }
    
    @staticmethod
    def _check_distribution_requirements(track: Track) -> List[str]:
        """Check if a track meets distribution requirements."""
        issues = []
        
        if not track.title:
            issues.append("Missing title")
        if not track.artist:
            issues.append("Missing artist")
        if not track.isrc:
            issues.append("Missing ISRC code")
        if track.duration_ms <= 0:
            issues.append("Invalid or missing duration")
        if not track.album:
            issues.append("Missing album information")
        
        return issues


class MetadataView(BaseView):
    """View for metadata management and editing."""
    
    def __init__(self, tracks: List[Track]):
        self.tracks = tracks
    
    def render(self) -> Dict[str, Any]:
        """Render metadata view data."""
        complete_count = 0
        incomplete_count = 0
        missing_fields: Dict[str, int] = {
            "title": 0,
            "artist": 0,
            "album": 0,
            "isrc": 0,
            "duration": 0,
        }
        
        track_details = []
        
        for track in self.tracks:
            if track.is_complete():
                complete_count += 1
            else:
                incomplete_count += 1
            
            # Count missing fields
            if not track.title:
                missing_fields["title"] += 1
            if not track.artist:
                missing_fields["artist"] += 1
            if not track.album:
                missing_fields["album"] += 1
            if not track.isrc:
                missing_fields["isrc"] += 1
            if track.duration_ms <= 0:
                missing_fields["duration"] += 1
            
            track_details.append({
                "id": track.platform_id,
                "platform": track.platform.value,
                "title": track.title,
                "artist": track.artist,
                "album": track.album,
                "isrc": track.isrc,
                "duration_ms": track.duration_ms,
                "status": track.status.value,
                "is_complete": track.is_complete(),
            })
        
        return {
            "view": "metadata",
            "title": "Metadata Management",
            "description": "Track metadata overview and editing",
            "data": {
                "total_tracks": len(self.tracks),
                "complete_count": complete_count,
                "incomplete_count": incomplete_count,
                "completeness_percentage": (complete_count / len(self.tracks) * 100) if self.tracks else 0,
                "missing_fields_summary": missing_fields,
                "tracks": track_details[:50],  # Limit to 50 tracks
            },
        }
