"""
Test: File Watcher - One-Time Processing

This script tests the file watcher by processing existing files once and exiting.
It does NOT start continuous monitoring.

Usage:
    python examples/test_file_watcher_once.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.file_watcher import SQLFileWatcher


def main():
    """Test file watcher with one-time processing."""

    print("=" * 70)
    print("=== FILE WATCHER TEST - One-Time Processing ===")
    print("=" * 70)
    print()

    # Check for SQL files
    watch_dir = Path("./data/raw")
    sql_files = list(watch_dir.glob("*.sql"))

    if not sql_files:
        print("[INFO] No SQL files found in data/raw/")
        print("[INFO] Add SQL files to data/raw/ to test")
        print()
        print("Expected location:")
        print(f"  {watch_dir.absolute()}")
        return

    print(f"[INFO] Found {len(sql_files)} SQL file(s) in data/raw/:")
    for f in sql_files:
        print(f"  - {f.name}")
    print()

    # Create watcher
    print("[INFO] Creating file watcher...")
    watcher = SQLFileWatcher(
        watch_dir="./data/raw",
        output_dir="./data/separated_sql",
        add_metadata=True,
        overwrite_existing=True
    )
    print("[OK] File watcher created")
    print()

    # Process existing files (without starting continuous monitoring)
    print("[INFO] Processing existing files...")
    print("=" * 70)
    watcher._process_existing_files()
    print("=" * 70)
    print()

    # Print summary
    watcher.organizer.print_summary()
    print()

    print("[OK] Test completed successfully!")
    print()
    print("Next steps:")
    print("  1. Check output: data/separated_sql/")
    print("  2. Start continuous monitoring: python examples/start_file_watcher.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
