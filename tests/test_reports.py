"""Tests for report generation."""

import pytest

from pipeline.models.track import Track, Platform, TrackStatus
from pipeline.models.playlist import Playlist
from pipeline.sync import SyncService
from pipeline.reports.generator import ReportGenerator
from pipeline.reports.formatter import ReportFormatter


class TestReportGenerator:
    """Tests for the ReportGenerator."""
    
    def test_generate_library_stats(self):
        """Test generating library statistics."""
        generator = ReportGenerator()
        
        playlist = Playlist(
            name="Test Playlist",
            platform=Platform.SPOTIFY,
            platform_id="p1",
        )
        playlist.add_track(Track(
            title="Song 1",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
            status=TrackStatus.COMPLETE,
        ))
        playlist.add_track(Track(
            title="Song 2",
            artist="Artist",
            platform=Platform.SUNO,
            platform_id="t2",
            duration_ms=200000,
            status=TrackStatus.INCOMPLETE,
        ))
        
        stats = generator.generate_library_stats([playlist])
        
        assert stats.total_tracks == 2
        assert stats.total_playlists == 1
        assert stats.total_duration_ms == 380000
        assert stats.tracks_by_platform[Platform.SPOTIFY] == 1
        assert stats.tracks_by_platform[Platform.SUNO] == 1
    
    def test_library_stats_duration_format(self):
        """Test duration formatting in library stats."""
        generator = ReportGenerator()
        
        playlist = Playlist(
            name="Test",
            platform=Platform.SPOTIFY,
            platform_id="p1",
        )
        playlist.add_track(Track(
            title="Long Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=3661000,  # 1 hour, 1 minute, 1 second
        ))
        
        stats = generator.generate_library_stats([playlist])
        
        assert stats.total_duration_formatted == "01:01:01"
    
    def test_generate_distribution_readiness_report(self):
        """Test generating distribution readiness report."""
        generator = ReportGenerator()
        
        ready_track = Track(
            title="Ready Song",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t1",
            duration_ms=180000,
            album="Album",
            isrc="USRC12345678",
        )
        
        not_ready_track = Track(
            title="Not Ready",
            artist="Artist",
            platform=Platform.SPOTIFY,
            platform_id="t2",
            duration_ms=0,  # Invalid duration
        )
        
        report = generator.generate_distribution_readiness_report([ready_track, not_ready_track])
        
        assert report["summary"]["total_tracks"] == 2
        assert report["summary"]["ready_for_distribution"] == 1
        assert report["summary"]["not_ready"] == 1
        assert report["summary"]["readiness_percentage"] == 50.0
    
    def test_generate_missing_tracks_report(self):
        """Test generating missing tracks report."""
        generator = ReportGenerator()
        
        missing = {
            Platform.SOUNDCLOUD: [
                Track(
                    title="Missing Song",
                    artist="Artist",
                    platform=Platform.SPOTIFY,
                    platform_id="t1",
                    duration_ms=180000,
                ),
            ],
            Platform.SUNO: [],
        }
        
        report = generator.generate_missing_tracks_report(missing)
        
        assert report["summary"]["soundcloud"] == 1
        assert report["summary"]["suno"] == 0
        assert report["summary"]["total"] == 1
    
    def test_generate_full_report(self):
        """Test generating a complete report."""
        generator = ReportGenerator()
        
        playlist = Playlist(
            name="Test Playlist",
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
        
        report = generator.generate_full_report([playlist])
        
        assert "generated_at" in report
        assert "library" in report
        assert "distribution_readiness" in report
        assert report["library"]["total_tracks"] == 1
        assert report["library"]["total_playlists"] == 1


class TestReportFormatter:
    """Tests for the ReportFormatter."""
    
    def test_to_json(self):
        """Test JSON formatting."""
        report = {"test": "value", "number": 42}
        
        json_output = ReportFormatter.to_json(report)
        
        assert '"test": "value"' in json_output
        assert '"number": 42' in json_output
    
    def test_to_markdown(self):
        """Test Markdown formatting."""
        report = {
            "generated_at": "2024-01-01T00:00:00",
            "library": {
                "total_tracks": 10,
                "total_playlists": 2,
                "total_duration": "01:00:00",
            },
        }
        
        md_output = ReportFormatter.to_markdown(report)
        
        assert "# Pipeline Report" in md_output
        assert "## Library Summary" in md_output
        assert "**Total Tracks:** 10" in md_output
    
    def test_to_text(self):
        """Test plain text formatting."""
        report = {
            "generated_at": "2024-01-01T00:00:00",
            "library": {
                "total_tracks": 10,
                "total_playlists": 2,
            },
        }
        
        text_output = ReportFormatter.to_text(report)
        
        assert "PIPELINE REPORT" in text_output
        assert "LIBRARY SUMMARY" in text_output
        assert "Total Tracks:    10" in text_output
    
    def test_to_html(self):
        """Test HTML formatting."""
        report = {
            "generated_at": "2024-01-01T00:00:00",
            "library": {
                "total_tracks": 10,
                "total_playlists": 2,
            },
        }
        
        html_output = ReportFormatter.to_html(report)
        
        assert "<!DOCTYPE html>" in html_output
        assert "<title>Pipeline Report</title>" in html_output
        assert "<h2>Library Summary</h2>" in html_output
