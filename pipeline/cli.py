"""Command-line interface for Pipeline."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from pipeline import __version__
from pipeline.models.track import Platform
from pipeline.models.playlist import Playlist
from pipeline.dashboard.app import Dashboard


def main():
    """Main entry point for the Pipeline CLI."""
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Pipeline - Music Workflow Automation Tool",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show library status"
    )
    status_parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format"
    )
    
    # Sync command
    sync_parser = subparsers.add_parser(
        "sync",
        help="Synchronize playlists across platforms"
    )
    sync_parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["spotify", "suno", "soundcloud"],
        help="Platforms to sync"
    )
    
    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate reports"
    )
    report_parser.add_argument(
        "--type",
        choices=["full", "missing", "distribution"],
        default="full",
        help="Report type"
    )
    report_parser.add_argument(
        "--format",
        choices=["text", "json", "markdown", "html"],
        default="markdown",
        help="Output format"
    )
    report_parser.add_argument(
        "--output",
        type=str,
        help="Output file path"
    )
    
    # Import command
    import_parser = subparsers.add_parser(
        "import",
        help="Import playlist data"
    )
    import_parser.add_argument(
        "file",
        type=str,
        help="JSON file to import"
    )
    
    # Export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export library data"
    )
    export_parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    dashboard = Dashboard()
    
    if args.command == "status":
        return cmd_status(dashboard, args)
    elif args.command == "sync":
        return cmd_sync(dashboard, args)
    elif args.command == "report":
        return cmd_report(dashboard, args)
    elif args.command == "import":
        return cmd_import(dashboard, args)
    elif args.command == "export":
        return cmd_export(dashboard, args)
    
    return 0


def cmd_status(dashboard: Dashboard, args) -> int:
    """Handle the status command."""
    view = dashboard.get_library_view()
    
    if args.format == "json":
        print(json.dumps(view, indent=2))
    elif args.format == "markdown":
        data = view["data"]
        print(f"# {view['title']}")
        print(f"\n{view['description']}")
        print(f"\n- Total Tracks: {data['total_tracks']}")
        print(f"- Total Playlists: {data['total_playlists']}")
        print(f"- Total Duration: {data['total_duration_formatted']}")
    else:
        data = view["data"]
        print("=" * 40)
        print(view["title"])
        print("=" * 40)
        print(f"Total Tracks:    {data['total_tracks']}")
        print(f"Total Playlists: {data['total_playlists']}")
        print(f"Total Duration:  {data['total_duration_formatted']}")
    
    return 0


def cmd_sync(dashboard: Dashboard, args) -> int:
    """Handle the sync command."""
    print("Running synchronization...")
    
    reports = dashboard.run_sync()
    
    if not reports:
        print("No playlists to sync. Import playlists first.")
        return 0
    
    for name, report in reports.items():
        print(f"\n{name}:")
        print(f"  Matched:    {report.matched_tracks}")
        print(f"  Missing:    {report.missing_tracks}")
        print(f"  Incomplete: {report.incomplete_tracks}")
        print(f"  Match Rate: {report.match_rate:.1f}%")
    
    return 0


def cmd_report(dashboard: Dashboard, args) -> int:
    """Handle the report command."""
    report_content = dashboard.generate_report(format=args.format)
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report_content)
        print(f"Report saved to: {args.output}")
    else:
        print(report_content)
    
    return 0


def cmd_import(dashboard: Dashboard, args) -> int:
    """Handle the import command."""
    input_path = Path(args.file)
    
    if not input_path.exists():
        print(f"Error: File not found: {args.file}")
        return 1
    
    try:
        data = json.loads(input_path.read_text())
        dashboard.import_state(data)
        print(f"Imported {len(dashboard.state.playlists)} playlists")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return 1
    except Exception as e:
        print(f"Error importing data: {e}")
        return 1
    
    return 0


def cmd_export(dashboard: Dashboard, args) -> int:
    """Handle the export command."""
    output_path = Path(args.output)
    
    try:
        state = dashboard.export_state()
        output_path.write_text(json.dumps(state, indent=2))
        print(f"Exported to: {args.output}")
    except Exception as e:
        print(f"Error exporting data: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
