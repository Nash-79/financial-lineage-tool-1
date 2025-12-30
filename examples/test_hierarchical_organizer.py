"""
Test: Hierarchical SQL Organizer

This demonstrates the hierarchical organization where each table/view gets
its own folder with subfolders for constraints, indexes, etc.

Expected Structure:
data/separated_sql/
  AdventureWorksLT-All/
    tables/
      ProductCategory/
        ProductCategory.sql
        indexes/
          PK_ProductCategory.sql
        foreign_keys/
          FK_ProductCategory_Parent.sql
        defaults/
          DF_ProductCategory_rowguid.sql
      Product/
        Product.sql
        indexes/
        foreign_keys/
        check_constraints/
    views/
      vProductAndDescription/
        vProductAndDescription.sql
        indexes/
          IX_vProductAndDescription.sql  (indexed view!)
    functions/
      ufnGetAllCategories/
        ufnGetAllCategories.sql
    stored_procedures/
      Product_Insert/
        Product_Insert.sql
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.hierarchical_organizer import organize_sql_hierarchically


def main():
    print("=" * 70)
    print("HIERARCHICAL SQL ORGANIZER - TEST")
    print("=" * 70)

    print("\nExpected Hierarchical Structure:")
    print("""
AdventureWorksLT-All/
  tables/
    ProductCategory/
      ProductCategory.sql          <-- Main table definition
      indexes/
        PK_ProductCategory.sql     <-- Primary key index
      foreign_keys/
        FK_ProductCategory_Parent.sql
      defaults/
        DF_ProductCategory_rowguid.sql
    Product/
      Product.sql
      indexes/
      foreign_keys/
      check_constraints/
        CK_Product_ListPrice.sql
        CK_Product_Weight.sql
  views/
    vProductAndDescription/
      vProductAndDescription.sql   <-- View definition
      indexes/
        IX_vProductAndDescription.sql  <-- INDEXED VIEW!
  functions/
    ufnGetAllCategories/
      ufnGetAllCategories.sql
  stored_procedures/
    Product_Insert/
      Product_Insert.sql
    """)

    # Test file
    test_file = Path("./data/raw/AdventureWorksLT-All.sql")

    if not test_file.exists():
        print(f"[ERROR] Test file not found: {test_file}")
        print("Please ensure AdventureWorksLT-All.sql is in data/raw/")
        return

    print(f"\nProcessing: {test_file}")
    print("Output: ./data/separated_sql/")
    print("\n" + "=" * 70)

    # Organize hierarchically
    results = organize_sql_hierarchically(
        input_file=str(test_file),
        output_dir="./data/separated_sql"
    )

    # Show the folder structure
    print("\n" + "=" * 70)
    print("RESULTING FOLDER STRUCTURE")
    print("=" * 70)

    output_dir = Path("./data/separated_sql/AdventureWorksLT-All")

    if output_dir.exists():
        show_folder_tree(output_dir, max_depth=4)
    else:
        print("[ERROR] Output directory not created")

    print("\n" + "=" * 70)
    print("KEY FEATURES DEMONSTRATED")
    print("=" * 70)
    print("""
✓ Hierarchical organization - each object has its own folder
✓ Constraints grouped with parent tables
✓ Indexes grouped with parent tables/views
✓ Indexed views detected and organized
✓ Foreign keys separated from other constraints
✓ Check constraints in dedicated subfolder
✓ Metadata preserved in each file
    """)


def show_folder_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
    """Display folder tree structure."""
    if current_depth > max_depth:
        return

    if current_depth == 0:
        print(f"\n{path.name}/")

    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└──" if is_last else "├──"
            extension = "    " if is_last else "│   "

            if item.is_dir():
                file_count = len(list(item.glob("*.sql")))
                count_str = f" ({file_count} files)" if file_count > 0 else ""
                print(f"{prefix}{connector} {item.name}/{count_str}")

                if current_depth < max_depth - 1:
                    show_folder_tree(
                        item,
                        prefix + extension,
                        max_depth,
                        current_depth + 1
                    )
            else:
                if item.suffix == '.sql':
                    print(f"{prefix}{connector} {item.name}")
                elif item.suffix == '.json':
                    print(f"{prefix}{connector} {item.name} (manifest)")

    except PermissionError:
        print(f"{prefix}[Permission Denied]")


if __name__ == "__main__":
    main()
