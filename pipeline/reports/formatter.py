"""Report formatter for Pipeline."""

import json
from typing import Dict, Any
from datetime import datetime


class ReportFormatter:
    """
    Formats reports into various output formats.
    
    Supports plain text, Markdown, JSON, and HTML output.
    """
    
    @staticmethod
    def to_json(report: Dict[str, Any], indent: int = 2) -> str:
        """
        Format report as JSON.
        
        Args:
            report: Report dictionary
            indent: JSON indentation level
            
        Returns:
            JSON string
        """
        return json.dumps(report, indent=indent, default=str)
    
    @staticmethod
    def to_markdown(report: Dict[str, Any]) -> str:
        """
        Format report as Markdown.
        
        Args:
            report: Report dictionary
            
        Returns:
            Markdown string
        """
        lines = []
        
        # Header
        lines.append("# Pipeline Report")
        lines.append("")
        lines.append(f"*Generated: {report.get('generated_at', datetime.now().isoformat())}*")
        lines.append("")
        
        # Library section
        if "library" in report:
            lib = report["library"]
            lines.append("## Library Summary")
            lines.append("")
            lines.append(f"- **Total Tracks:** {lib.get('total_tracks', 0)}")
            lines.append(f"- **Total Playlists:** {lib.get('total_playlists', 0)}")
            lines.append(f"- **Total Duration:** {lib.get('total_duration', 'N/A')}")
            lines.append("")
            
            if "tracks_by_platform" in lib:
                lines.append("### Tracks by Platform")
                lines.append("")
                for platform, count in lib["tracks_by_platform"].items():
                    lines.append(f"- {platform}: {count}")
                lines.append("")
            
            if "tracks_by_status" in lib:
                lines.append("### Tracks by Status")
                lines.append("")
                for status, count in lib["tracks_by_status"].items():
                    lines.append(f"- {status}: {count}")
                lines.append("")
        
        # Sync section
        if "sync" in report:
            sync = report["sync"]
            lines.append("## Synchronization Summary")
            lines.append("")
            lines.append(f"- **Total Comparisons:** {sync.get('total_comparisons', 0)}")
            lines.append(f"- **Matched Tracks:** {sync.get('total_matched', 0)}")
            lines.append(f"- **Missing Tracks:** {sync.get('total_missing', 0)}")
            lines.append(f"- **Incomplete Tracks:** {sync.get('total_incomplete', 0)}")
            lines.append("")
            
            if "platform_coverage" in sync:
                lines.append("### Platform Coverage")
                lines.append("")
                for platform, coverage in sync["platform_coverage"].items():
                    lines.append(f"- {platform}: {coverage:.1f}%")
                lines.append("")
        
        # Distribution readiness section
        if "distribution_readiness" in report:
            dist = report["distribution_readiness"]
            lines.append("## Distribution Readiness")
            lines.append("")
            lines.append(f"- **Ready for Distribution:** {dist.get('ready_for_distribution', 0)}")
            lines.append(f"- **Not Ready:** {dist.get('not_ready', 0)}")
            lines.append(f"- **Readiness:** {dist.get('readiness_percentage', 0):.1f}%")
            lines.append("")
        
        # Missing tracks section
        if "missing_tracks" in report:
            missing = report["missing_tracks"]
            lines.append("## Missing Tracks")
            lines.append("")
            for platform, count in missing.items():
                lines.append(f"- {platform}: {count}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_text(report: Dict[str, Any]) -> str:
        """
        Format report as plain text.
        
        Args:
            report: Report dictionary
            
        Returns:
            Plain text string
        """
        lines = []
        
        # Header
        lines.append("=" * 50)
        lines.append("PIPELINE REPORT")
        lines.append("=" * 50)
        lines.append(f"Generated: {report.get('generated_at', datetime.now().isoformat())}")
        lines.append("")
        
        # Library section
        if "library" in report:
            lib = report["library"]
            lines.append("-" * 30)
            lines.append("LIBRARY SUMMARY")
            lines.append("-" * 30)
            lines.append(f"Total Tracks:    {lib.get('total_tracks', 0)}")
            lines.append(f"Total Playlists: {lib.get('total_playlists', 0)}")
            lines.append(f"Total Duration:  {lib.get('total_duration', 'N/A')}")
            lines.append("")
            
            if "tracks_by_platform" in lib:
                lines.append("Tracks by Platform:")
                for platform, count in lib["tracks_by_platform"].items():
                    lines.append(f"  {platform}: {count}")
                lines.append("")
        
        # Sync section
        if "sync" in report:
            sync = report["sync"]
            lines.append("-" * 30)
            lines.append("SYNCHRONIZATION SUMMARY")
            lines.append("-" * 30)
            lines.append(f"Total Comparisons:  {sync.get('total_comparisons', 0)}")
            lines.append(f"Matched Tracks:     {sync.get('total_matched', 0)}")
            lines.append(f"Missing Tracks:     {sync.get('total_missing', 0)}")
            lines.append(f"Incomplete Tracks:  {sync.get('total_incomplete', 0)}")
            lines.append("")
        
        # Distribution readiness section
        if "distribution_readiness" in report:
            dist = report["distribution_readiness"]
            lines.append("-" * 30)
            lines.append("DISTRIBUTION READINESS")
            lines.append("-" * 30)
            lines.append(f"Ready for Distribution: {dist.get('ready_for_distribution', 0)}")
            lines.append(f"Not Ready:              {dist.get('not_ready', 0)}")
            lines.append(f"Readiness:              {dist.get('readiness_percentage', 0):.1f}%")
            lines.append("")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    @staticmethod
    def to_html(report: Dict[str, Any]) -> str:
        """
        Format report as HTML.
        
        Args:
            report: Report dictionary
            
        Returns:
            HTML string
        """
        html_parts = []
        
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html>")
        html_parts.append("<head>")
        html_parts.append("  <title>Pipeline Report</title>")
        html_parts.append("  <style>")
        html_parts.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
        html_parts.append("    h1 { color: #333; }")
        html_parts.append("    h2 { color: #666; border-bottom: 1px solid #ddd; }")
        html_parts.append("    .stat { margin: 10px 0; }")
        html_parts.append("    .stat-label { font-weight: bold; }")
        html_parts.append("    .platform-list { list-style: none; padding-left: 20px; }")
        html_parts.append("    .timestamp { color: #999; font-size: 0.9em; }")
        html_parts.append("  </style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        html_parts.append("  <h1>Pipeline Report</h1>")
        html_parts.append(f"  <p class='timestamp'>Generated: {report.get('generated_at', '')}</p>")
        
        # Library section
        if "library" in report:
            lib = report["library"]
            html_parts.append("  <h2>Library Summary</h2>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Total Tracks:</span> {lib.get('total_tracks', 0)}</div>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Total Playlists:</span> {lib.get('total_playlists', 0)}</div>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Total Duration:</span> {lib.get('total_duration', 'N/A')}</div>")
            
            if "tracks_by_platform" in lib:
                html_parts.append("  <h3>Tracks by Platform</h3>")
                html_parts.append("  <ul class='platform-list'>")
                for platform, count in lib["tracks_by_platform"].items():
                    html_parts.append(f"    <li>{platform}: {count}</li>")
                html_parts.append("  </ul>")
        
        # Sync section
        if "sync" in report:
            sync = report["sync"]
            html_parts.append("  <h2>Synchronization Summary</h2>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Total Comparisons:</span> {sync.get('total_comparisons', 0)}</div>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Matched Tracks:</span> {sync.get('total_matched', 0)}</div>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Missing Tracks:</span> {sync.get('total_missing', 0)}</div>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Incomplete Tracks:</span> {sync.get('total_incomplete', 0)}</div>")
        
        # Distribution readiness section
        if "distribution_readiness" in report:
            dist = report["distribution_readiness"]
            html_parts.append("  <h2>Distribution Readiness</h2>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Ready for Distribution:</span> {dist.get('ready_for_distribution', 0)}</div>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Not Ready:</span> {dist.get('not_ready', 0)}</div>")
            html_parts.append(f"  <div class='stat'><span class='stat-label'>Readiness:</span> {dist.get('readiness_percentage', 0):.1f}%</div>")
        
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)
