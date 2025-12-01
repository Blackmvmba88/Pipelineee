"""Report generator for Pipeline."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

from pipeline.models.track import Track, Platform, TrackStatus
from pipeline.models.playlist import Playlist
from pipeline.sync import SyncReport


@dataclass
class LibraryStats:
    """Statistics about the music library."""
    total_tracks: int
    total_playlists: int
    total_duration_ms: int
    tracks_by_platform: Dict[Platform, int]
    tracks_by_status: Dict[TrackStatus, int]
    
    @property
    def total_duration_formatted(self) -> str:
        """Format total duration as HH:MM:SS."""
        total_seconds = self.total_duration_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass
class SyncSummary:
    """Summary of sync operations."""
    total_comparisons: int
    total_matched: int
    total_missing: int
    total_incomplete: int
    platform_coverage: Dict[Platform, float]


class ReportGenerator:
    """
    Generator for various Pipeline reports.
    
    Creates comprehensive reports about library status,
    sync results, and distribution readiness.
    """
    
    def generate_library_stats(
        self, 
        playlists: List[Playlist]
    ) -> LibraryStats:
        """
        Generate statistics about the music library.
        
        Args:
            playlists: List of playlists to analyze
            
        Returns:
            LibraryStats object with computed statistics
        """
        total_tracks = 0
        total_duration_ms = 0
        tracks_by_platform: Dict[Platform, int] = {}
        tracks_by_status: Dict[TrackStatus, int] = {
            TrackStatus.COMPLETE: 0,
            TrackStatus.INCOMPLETE: 0,
            TrackStatus.MISSING: 0,
            TrackStatus.PENDING: 0,
        }
        
        seen_track_ids: set = set()
        
        for playlist in playlists:
            for track in playlist.tracks:
                track_key = f"{track.platform.value}:{track.platform_id}"
                
                if track_key not in seen_track_ids:
                    seen_track_ids.add(track_key)
                    total_tracks += 1
                    total_duration_ms += track.duration_ms
                    
                    if track.platform not in tracks_by_platform:
                        tracks_by_platform[track.platform] = 0
                    tracks_by_platform[track.platform] += 1
                    
                    tracks_by_status[track.status] += 1
        
        return LibraryStats(
            total_tracks=total_tracks,
            total_playlists=len(playlists),
            total_duration_ms=total_duration_ms,
            tracks_by_platform=tracks_by_platform,
            tracks_by_status=tracks_by_status,
        )
    
    def generate_sync_summary(
        self, 
        sync_reports: Dict[str, SyncReport]
    ) -> SyncSummary:
        """
        Generate a summary of sync operations.
        
        Args:
            sync_reports: Dictionary of sync reports by comparison name
            
        Returns:
            SyncSummary object
        """
        total_matched = 0
        total_missing = 0
        total_incomplete = 0
        platform_totals: Dict[Platform, int] = {}
        platform_matched: Dict[Platform, int] = {}
        
        for report in sync_reports.values():
            total_matched += report.matched_tracks
            total_missing += report.missing_tracks
            total_incomplete += report.incomplete_tracks
            
            for result in report.results:
                platform = result.source_platform
                if platform not in platform_totals:
                    platform_totals[platform] = 0
                    platform_matched[platform] = 0
                
                platform_totals[platform] += 1
                if result.action.value == "none":
                    platform_matched[platform] += 1
        
        platform_coverage: Dict[Platform, float] = {}
        for platform, total in platform_totals.items():
            if total > 0:
                platform_coverage[platform] = (platform_matched[platform] / total) * 100
            else:
                platform_coverage[platform] = 0.0
        
        return SyncSummary(
            total_comparisons=len(sync_reports),
            total_matched=total_matched,
            total_missing=total_missing,
            total_incomplete=total_incomplete,
            platform_coverage=platform_coverage,
        )
    
    def generate_missing_tracks_report(
        self, 
        missing: Dict[Platform, List[Track]]
    ) -> Dict[str, any]:
        """
        Generate a report of missing tracks by platform.
        
        Args:
            missing: Dictionary mapping platforms to missing tracks
            
        Returns:
            Report dictionary
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "details": {},
        }
        
        total_missing = 0
        for platform, tracks in missing.items():
            count = len(tracks)
            total_missing += count
            report["summary"][platform.value] = count
            report["details"][platform.value] = [
                {
                    "title": track.title,
                    "artist": track.artist,
                    "original_platform": track.platform.value,
                }
                for track in tracks
            ]
        
        report["summary"]["total"] = total_missing
        return report
    
    def generate_distribution_readiness_report(
        self, 
        tracks: List[Track]
    ) -> Dict[str, any]:
        """
        Generate a report on distribution readiness.
        
        Checks if tracks have all required metadata for distribution:
        - Title and artist
        - ISRC code
        - Duration
        - Album information
        
        Args:
            tracks: List of tracks to check
            
        Returns:
            Report dictionary
        """
        ready = []
        not_ready = []
        
        for track in tracks:
            issues = []
            
            if not track.title:
                issues.append("Missing title")
            if not track.artist:
                issues.append("Missing artist")
            if not track.isrc:
                issues.append("Missing ISRC")
            if track.duration_ms <= 0:
                issues.append("Invalid duration")
            if not track.album:
                issues.append("Missing album")
            
            if issues:
                not_ready.append({
                    "track": track.to_dict(),
                    "issues": issues,
                })
            else:
                ready.append(track.to_dict())
        
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_tracks": len(tracks),
                "ready_for_distribution": len(ready),
                "not_ready": len(not_ready),
                "readiness_percentage": (len(ready) / len(tracks) * 100) if tracks else 0,
            },
            "ready_tracks": ready,
            "tracks_with_issues": not_ready,
        }
    
    def generate_full_report(
        self,
        playlists: List[Playlist],
        sync_reports: Optional[Dict[str, SyncReport]] = None,
        missing_tracks: Optional[Dict[Platform, List[Track]]] = None,
    ) -> Dict[str, any]:
        """
        Generate a comprehensive report.
        
        Args:
            playlists: All playlists in the library
            sync_reports: Optional sync comparison reports
            missing_tracks: Optional missing tracks by platform
            
        Returns:
            Complete report dictionary
        """
        library_stats = self.generate_library_stats(playlists)
        
        all_tracks = []
        for playlist in playlists:
            all_tracks.extend(playlist.tracks)
        
        distribution_report = self.generate_distribution_readiness_report(all_tracks)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "library": {
                "total_tracks": library_stats.total_tracks,
                "total_playlists": library_stats.total_playlists,
                "total_duration": library_stats.total_duration_formatted,
                "tracks_by_platform": {
                    p.value: c for p, c in library_stats.tracks_by_platform.items()
                },
                "tracks_by_status": {
                    s.value: c for s, c in library_stats.tracks_by_status.items()
                },
            },
            "distribution_readiness": distribution_report["summary"],
        }
        
        if sync_reports:
            sync_summary = self.generate_sync_summary(sync_reports)
            report["sync"] = {
                "total_comparisons": sync_summary.total_comparisons,
                "total_matched": sync_summary.total_matched,
                "total_missing": sync_summary.total_missing,
                "total_incomplete": sync_summary.total_incomplete,
                "platform_coverage": {
                    p.value: c for p, c in sync_summary.platform_coverage.items()
                },
            }
        
        if missing_tracks:
            missing_report = self.generate_missing_tracks_report(missing_tracks)
            report["missing_tracks"] = missing_report["summary"]
        
        return report
