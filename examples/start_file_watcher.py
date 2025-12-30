"""
Example: Start SQL File Watcher

This script demonstrates how to use the SQL file watcher to automatically
process SQL files when they are added or modified in the data/raw/ directory.

Usage:
    python examples/start_file_watcher.py

Features:
- Automatically processes existing SQL files on startup
- Watches for new SQL files added to data/raw/
- Watches for modifications to existing SQL files
- Organizes files hierarchically using SQL Server comment patterns
- Debounces rapid file changes to avoid duplicate processing

Testing:
1. Run this script
2. Copy a SQL file to data/raw/
3. Watch it automatically process
4. Modify the SQL file
5. Watch it reprocess
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion.file_watcher import SQLFileWatcher


def main():
    """Start the SQL file watcher."""

    print("""
    ===================================================================
    SQL FILE WATCHER - Automatic SQL File Processing
    ===================================================================

    This watcher will:
    1. Process all existing SQL files in data/raw/
    2. Watch for new SQL files
    3. Watch for modifications to existing files
    4. Automatically organize files hierarchically

    To test:
    - Copy a .sql file to data/raw/
    - Modify an existing .sql file in data/raw/
    - Watch the automatic processing

    Press Ctrl+C to stop
    ===================================================================
    """)

    # Initialize watcher
    watcher = SQLFileWatcher(
        watch_dir="./data/raw",
        output_dir="./data/separated_sql",
        add_metadata=True,
        overwrite_existing=True,
        debounce_seconds=2.0
    )

    # Start watching (will process existing files first)
    try:
        watcher.start(process_existing=True)
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
        watcher.stop()


if __name__ == "__main__":
    main()
