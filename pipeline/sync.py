"""Synchronization service for Pipeline."""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

from pipeline.models.track import Track, Platform, TrackStatus
from pipeline.models.playlist import Playlist


class SyncAction(Enum):
    """Types of synchronization actions."""
    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"
    NONE = "none"


@dataclass
class SyncResult:
    """Result of a synchronization comparison."""
    track: Track
    action: SyncAction
    source_platform: Platform
    target_platform: Optional[Platform] = None
    message: str = ""


@dataclass
class SyncReport:
    """Summary report of a synchronization operation."""
    total_tracks: int
    matched_tracks: int
    missing_tracks: int
    incomplete_tracks: int
    results: List[SyncResult]
    
    @property
    def match_rate(self) -> float:
        """Calculate the percentage of matched tracks."""
        if self.total_tracks == 0:
            return 0.0
        return (self.matched_tracks / self.total_tracks) * 100


class SyncService:
    """
    Service for synchronizing and verifying tracks across platforms.
    
    This service compares playlists and tracks from different platforms
    to identify missing, incomplete, or mismatched tracks.
    """
    
    def __init__(self, tolerance_ms: int = 3000):
        """
        Initialize the sync service.
        
        Args:
            tolerance_ms: Duration tolerance in milliseconds for matching tracks
        """
        self.tolerance_ms = tolerance_ms
    
    def compare_playlists(
        self, 
        source: Playlist, 
        target: Playlist
    ) -> SyncReport:
        """
        Compare two playlists and identify differences.
        
        Args:
            source: Source playlist to compare from
            target: Target playlist to compare against
            
        Returns:
            SyncReport with comparison results
        """
        results: List[SyncResult] = []
        matched = 0
        missing = 0
        incomplete = 0
        
        for source_track in source.tracks:
            match_found = False
            
            for target_track in target.tracks:
                if source_track.matches(target_track, self.tolerance_ms):
                    match_found = True
                    matched += 1
                    results.append(SyncResult(
                        track=source_track,
                        action=SyncAction.NONE,
                        source_platform=source.platform,
                        target_platform=target.platform,
                        message=f"Track '{source_track.title}' matched in both playlists"
                    ))
                    break
            
            if not match_found:
                if not source_track.is_complete():
                    incomplete += 1
                    results.append(SyncResult(
                        track=source_track,
                        action=SyncAction.UPDATE,
                        source_platform=source.platform,
                        message=f"Track '{source_track.title}' is incomplete (missing metadata)"
                    ))
                else:
                    missing += 1
                    results.append(SyncResult(
                        track=source_track,
                        action=SyncAction.ADD,
                        source_platform=source.platform,
                        target_platform=target.platform,
                        message=f"Track '{source_track.title}' missing in {target.platform.value}"
                    ))
        
        return SyncReport(
            total_tracks=len(source.tracks),
            matched_tracks=matched,
            missing_tracks=missing,
            incomplete_tracks=incomplete,
            results=results
        )
    
    def find_missing_tracks(
        self, 
        master: List[Track], 
        platforms: Dict[Platform, List[Track]]
    ) -> Dict[Platform, List[Track]]:
        """
        Find tracks that are in the master list but missing from each platform.
        
        Args:
            master: Master list of tracks that should exist on all platforms
            platforms: Dictionary mapping platforms to their track lists
            
        Returns:
            Dictionary mapping platforms to lists of missing tracks
        """
        missing: Dict[Platform, List[Track]] = {}
        
        for platform, platform_tracks in platforms.items():
            missing[platform] = []
            
            for master_track in master:
                found = False
                for platform_track in platform_tracks:
                    if master_track.matches(platform_track, self.tolerance_ms):
                        found = True
                        break
                
                if not found:
                    missing[platform].append(master_track)
        
        return missing
    
    def verify_track_completeness(self, tracks: List[Track]) -> Tuple[List[Track], List[Track]]:
        """
        Verify that all tracks have complete metadata.
        
        Args:
            tracks: List of tracks to verify
            
        Returns:
            Tuple of (complete_tracks, incomplete_tracks)
        """
        complete = []
        incomplete = []
        
        for track in tracks:
            if track.is_complete():
                track.status = TrackStatus.COMPLETE
                complete.append(track)
            else:
                track.status = TrackStatus.INCOMPLETE
                incomplete.append(track)
        
        return complete, incomplete
    
    def align_tracks(
        self, 
        source: List[Track], 
        target: List[Track]
    ) -> List[Tuple[Track, Optional[Track]]]:
        """
        Align tracks from source to target, pairing matching tracks.
        
        Args:
            source: Source track list
            target: Target track list to align with
            
        Returns:
            List of tuples (source_track, matched_target_track or None)
        """
        aligned: List[Tuple[Track, Optional[Track]]] = []
        used_target_indices: set = set()
        
        for source_track in source:
            match: Optional[Track] = None
            
            for i, target_track in enumerate(target):
                if i not in used_target_indices:
                    if source_track.matches(target_track, self.tolerance_ms):
                        match = target_track
                        used_target_indices.add(i)
                        break
            
            aligned.append((source_track, match))
        
        return aligned
    
    def cross_platform_sync(
        self, 
        playlists: Dict[Platform, Playlist]
    ) -> Dict[str, SyncReport]:
        """
        Perform a cross-platform sync comparison.
        
        Args:
            playlists: Dictionary mapping platforms to their playlists
            
        Returns:
            Dictionary mapping comparison names to SyncReports
        """
        reports: Dict[str, SyncReport] = {}
        platforms = list(playlists.keys())
        
        for i, source_platform in enumerate(platforms):
            for target_platform in platforms[i+1:]:
                comparison_name = f"{source_platform.value}_vs_{target_platform.value}"
                reports[comparison_name] = self.compare_playlists(
                    playlists[source_platform],
                    playlists[target_platform]
                )
        
        return reports
    
    def merge_playlists(
        self, 
        playlists: List[Playlist], 
        merged_name: str = "Merged Playlist"
    ) -> Playlist:
        """
        Merge multiple playlists into a single playlist.
        
        Tracks are added in order from each playlist. Duplicates are removed
        based on track matching (title, artist, duration).
        
        Args:
            playlists: List of playlists to merge
            merged_name: Name for the merged playlist
            
        Returns:
            A new Playlist containing all unique tracks from input playlists
        """
        if not playlists:
            raise ValueError("Cannot merge empty list of playlists")
        
        # Start with the first playlist
        merged = Playlist(
            name=merged_name,
            platform=playlists[0].platform,
            platform_id="merged",
            description=f"Merged from {len(playlists)} playlists",
        )
        
        # Merge each playlist
        for playlist in playlists:
            for track in playlist.tracks:
                is_duplicate = False
                for existing_track in merged.tracks:
                    if track.matches(existing_track, self.tolerance_ms):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    merged.add_track(track)
        
        return merged
