"""
Demo: SQL File Organizer - Using data folder structure

This script demonstrates the SQL File Organizer with the proper folder structure:

data/
├── raw/              ← Input SQL files (source)
└── separated_sql/    ← Organized output
    ├── tables/
    ├── views/
    ├── functions/
    └── stored_procedures/
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.sql_file_organizer import SQLFileOrganizer, organize_sql_files


def demo_organize_from_raw():
    """Demo: Organize SQL files from data/raw/ folder."""
    print("\n" + "=" * 70)
    print("SQL FILE ORGANIZER - Organize from data/raw/")
    print("=" * 70)

    raw_dir = Path("./data/raw")
    output_dir = Path("./data/separated_sql")

    if not raw_dir.exists():
        print(f"[ERROR] Raw directory not found: {raw_dir}")
        print("Please create data/raw/ and add your SQL files there.")
        return

    # Count SQL files
    sql_files = list(raw_dir.glob("*.sql"))

    if not sql_files:
        print(f"[WARN] No SQL files found in {raw_dir}")
        print("Add .sql files to data/raw/ to organize them.")
        return

    print(f"\nFound {len(sql_files)} SQL file(s) in raw folder:")
    for f in sql_files:
        print(f"  - {f.name}")

    print(f"\nInput:  {raw_dir}")
    print(f"Output: {output_dir}")
    print("\nStarting organization...\n")
    print("=" * 70)

    # Organize all SQL files
    results = organize_sql_files(
        input_dir=str(raw_dir),
        output_dir=str(output_dir),
        dialect="tsql",
        pattern="*.sql"
    )

    # Show results
    print("\n" + "=" * 70)
    print("FOLDER STRUCTURE")
    print("=" * 70)

    if output_dir.exists():
        print(f"\n{output_dir}/")
        for folder in sorted(output_dir.iterdir()):
            if folder.is_dir():
                files = list(folder.glob("*.sql"))
                if files:
                    print(f"  {folder.name}/ ({len(files)} files)")
                    for file in sorted(files)[:3]:
                        print(f"    - {file.name}")
                    if len(files) > 3:
                        print(f"    ... and {len(files) - 3} more")

    # Show manifest
    manifest = output_dir / "separation_manifest.json"
    if manifest.exists():
        print(f"\n  {manifest.name}")

        import json
        with open(manifest, 'r') as f:
            data = json.load(f)

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Files Processed:   {data['statistics']['files_processed']}")
        print(f"Objects Separated: {data['statistics']['objects_separated']}")
        print("\nBy Type:")
        for obj_type, count in data['statistics']['by_type'].items():
            if count > 0:
                print(f"  {obj_type.upper():<15} {count}")


def show_folder_structure():
    """Show the expected folder structure."""
    print("\n" + "=" * 70)
    print("EXPECTED FOLDER STRUCTURE")
    print("=" * 70)
    print("""
financial-lineage-tool/
  data/
    raw/                       <-- Place your SQL files here
      schema1.sql
      schema2.sql
      procedures.sql

    separated_sql/             <-- Organized output (auto-generated)
      tables/
        customers.sql
        orders.sql
        products.sql
      views/
        vw_sales.sql
        vw_customers.sql
      functions/
        get_total.sql
      stored_procedures/
        usp_create_order.sql
        usp_update_customer.sql
      separation_manifest.json
    """)


def setup_instructions():
    """Show setup instructions."""
    print("\n" + "=" * 70)
    print("SETUP INSTRUCTIONS")
    print("=" * 70)
    print("""
1. Add your SQL files to: data/raw/

   Example:
   $ cp your_database_schema.sql data/raw/
   $ cp stored_procedures.sql data/raw/

2. Run this script:

   $ python examples/data_organizer_updated.py

3. Check organized files in: data/separated_sql/

   $ ls data/separated_sql/tables/
   $ ls data/separated_sql/views/
   $ ls data/separated_sql/stored_procedures/

4. Review the manifest:

   $ cat data/separated_sql/separation_manifest.json
    """)


def main():
    """Run the demo."""
    print("\n" + "=" * 70)
    print("SQL FILE ORGANIZER - NEW FOLDER STRUCTURE")
    print("=" * 70)

    # Show structure
    show_folder_structure()

    # Check if data exists
    data_dir = Path("./data")
    raw_dir = data_dir / "raw"

    if not data_dir.exists():
        print("\n[INFO] Creating data folder structure...")
        data_dir.mkdir(exist_ok=True)
        raw_dir.mkdir(exist_ok=True)
        (data_dir / "separated_sql").mkdir(exist_ok=True)
        print("[OK] Folder structure created!")

    if not raw_dir.exists():
        print("\n[INFO] Creating raw folder...")
        raw_dir.mkdir(exist_ok=True)

    # Run organization
    demo_organize_from_raw()

    # Show instructions
    setup_instructions()

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
✓ Folder structure is ready
✓ Add SQL files to data/raw/
✓ Run: python examples/data_organizer_updated.py
✓ Check output in data/separated_sql/

For automatic file watching (process new files automatically):
  → See FILE_WATCHER_GUIDE.md (coming next)
    """)


if __name__ == "__main__":
    main()
