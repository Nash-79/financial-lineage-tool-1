"""
This module provides the CodeParser class, which is responsible for parsing
source code files (e.g., SQL, Python) to extract lineage information.
It uses the sqlglot library to parse SQL and trace column-level lineage.
"""

from sqlglot import exp
from sqlglot import parse_one
import ast
import json
import logging
import re

logger = logging.getLogger(__name__)


class CodeParser:
    """
    Parses code to extract metadata, dependencies, and lineage.
    """

    def parse_sql(self, sql_content: str, dialect: str = "auto"):
        """
        Parses a SQL string to extract detailed lineage information, including
        tables, views, functions, and column-level transformations.

        Args:
            sql_content: The SQL script as a string.
            dialect: The SQL dialect to use (e.g., 'tsql', 'spark', 'bigquery'), or 'auto' for default.

        Returns:
            A dictionary containing structured information about the SQL script,
            or None if parsing fails.
        """
        try:
            # Resolve dialect using configuration
            from ..config.sql_dialects import resolve_dialect_for_parsing
            
            try:
                resolved_dialect = resolve_dialect_for_parsing(dialect)
            except ValueError as e:
                logger.warning(f"Dialect resolution failed: {e}. Using '{dialect}' as-is")
                resolved_dialect = dialect  # Fallback to original
            
            ast = parse_one(sql_content, read=resolved_dialect)
            if not ast:
                return None

            result = {
                "read": set(),
                "write": None,
                "columns": [],
                "functions_and_procedures": set(),
                "views": set(),
                "triggers": [],
                "synonyms": [],
                "materialized_views": set(),
                "procedure_calls": [],  # List of {"name": str, "target_tables": [str]}
            }

            # Define write AST types robustly (CreateTable might not exist in newer sqlglot)
            write_types = (exp.Insert, exp.Update, exp.Create)
            if hasattr(exp, "CreateTable"):
                write_types += (exp.CreateTable,)

            # Find write table/view/trigger/synonym/materialized view
            if isinstance(ast, write_types):
                kind = ast.args.get("kind", "").upper()
                if kind == "VIEW":
                    result["views"].add(ast.this.sql())
                    result["write"] = ast.this.sql()
                elif kind == "MATERIALIZED VIEW":
                    result["materialized_views"].add(ast.this.sql())
                    result["write"] = ast.this.sql()
                elif kind == "TRIGGER":
                    # Extract trigger name and target table
                    trigger_name = ast.this.sql()
                    target_table = ast.args.get("table")
                    target_table_name = target_table.sql() if target_table else None
                    result["triggers"].append({
                        "name": trigger_name,
                        "target_table": target_table_name
                    })
                elif kind == "SYNONYM":
                    # Extract synonym name and target object
                    synonym_name = ast.this.sql()
                    target_obj = ast.expression
                    target_obj_name = target_obj.sql() if target_obj else None
                    result["synonyms"].append({
                        "name": synonym_name,
                        "target_object": target_obj_name
                    })
                elif kind in ("FUNCTION", "PROCEDURE"):
                    result["functions_and_procedures"].add(ast.this.sql())
                elif isinstance(ast.this, exp.Table):
                    result["write"] = ast.this.sql()
            
            elif isinstance(ast, exp.Command):
                # Fallback for complex DDL that sqlglot parses as generic Command
                cmd_upper = ast.this.upper() if isinstance(ast.this, str) else str(ast.this).upper()
                expression = ast.expression.sql() if hasattr(ast.expression, "sql") else str(ast.expression)
                
                if cmd_upper == "CREATE":
                    # print(f"DEBUG: Checking Command fallback. Expression: '{expression}'")
                    # Check for Trigger: CREATE TRIGGER <name> ON <target>
                    trigger_match = re.search(r"(?i)TRIGGER\s+([^\s]+)\s+ON\s+([^\s]+)", expression)
                    if trigger_match:
                        result["triggers"].append({
                            "name": trigger_match.group(1),
                            "target_table": trigger_match.group(2)
                        })
                    
                    # Check for Synonym: CREATE SYNONYM <name> FOR <target>
                    synonym_match = re.search(r"(?i)SYNONYM\s+([^\s]+)\s+FOR\s+([^\s]+)", expression)
                    if synonym_match:
                        result["synonyms"].append({
                            "name": synonym_match.group(1),
                            "target_object": synonym_match.group(2)
                        })

            # Find all tables being read from
            for table in ast.find_all(exp.Table):
                # Ensure we don't add the write table to the read list
                if table.sql() != result["write"]:
                    result["read"].add(table.sql())
            
            # Extract procedure/function calls (EXEC, EXECUTE, function invocations)
            procedure_calls = self._extract_procedure_calls(ast)
            result["procedure_calls"].extend(procedure_calls)

            # Extract column level lineage if it's a SELECT statement
            if hasattr(ast, "expression") and isinstance(ast.expression, exp.Select):
                select_expression = ast.expression
                for projection in select_expression.find_all(exp.Alias):
                    target_col = projection.this
                    lineage = projection.expression.lineage()

                    source_cols = {col.sql() for col in lineage.find_all(exp.Column)}

                    result["columns"].append(
                        {
                            "target": target_col.sql(),
                            "sources": list(source_cols),
                            "transformation": projection.expression.sql(
                                dialect=dialect
                            ),
                        }
                    )
                # Handle columns without aliases
                for col in select_expression.selects:
                    if not isinstance(col, exp.Alias):
                        lineage = col.lineage()
                        source_cols = {c.sql() for c in lineage.find_all(exp.Column)}
                        result["columns"].append(
                            {
                                "target": col.this.sql(),
                                "sources": list(source_cols),
                                "transformation": col.sql(dialect=dialect),
                            }
                        )

            # Convert sets to lists for JSON serialization
            result["read"] = list(result["read"])
            result["functions_and_procedures"] = list(
                result["functions_and_procedures"]
            )
            result["views"] = list(result["views"])
            # result["triggers"] and result["synonyms"] are already lists of dicts
            # result["triggers"] = list(result["triggers"])
            # result["synonyms"] = list(result["synonyms"])
            result["materialized_views"] = list(result["materialized_views"])

            # If no specific write table, it might just be a select query
            if not result["write"] and (result["read"] or result["columns"]):
                result["write"] = "console"

            return result

        except Exception as e:
            # Optionally log the error
            print(f"Error parsing SQL with sqlglot: {e}")
            return None

    def _extract_procedure_calls(self, ast):
        """
        Extract procedure and function calls from SQL AST.
        
        Args:
            ast: sqlglot AST node
            
        Returns:
            List of procedure call dictionaries with name and potential target tables
        """
        calls = []
        
        # Look for Command nodes (EXEC/EXECUTE in T-SQL)
        if hasattr(exp, 'Command'):
            for command in ast.find_all(exp.Command):
                # Command nodes typically represent EXEC statements
                proc_name = command.this if hasattr(command, 'this') else str(command)
                calls.append({
                    "name": str(proc_name),
                    "type": "stored_procedure",
                    "target_tables": []  # Could be extracted from procedure body if available
                })
        
        # Look for function calls that might be stored procedures
        for func in ast.find_all(exp.Anonymous):
            # Anonymous function calls - common for UDFs and stored procedures
            func_name = func.this if hasattr(func, 'this') else str(func)
            if func_name and not func_name.upper() in ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CAST', 'CONVERT'):
                calls.append({
                    "name": str(func_name),
                    "type": "function_call",
                    "target_tables": []
                })
        
        return calls

    def parse_python(self, python_content: str):
        """
        Parses Python code to extract classes, functions, and imports.

        Args:
            python_content: Python source code.

        Returns:
            Dict with 'classes', 'functions', 'imports'.
        """
        try:
            tree = ast.parse(python_content)
            result = {
                "classes": [],
                "functions": [],
                "imports": [],
                "table_references": [],  # Heuristic: potential SQL table names
                "docstring": ast.get_docstring(tree),
            }
            
            # Extract heuristic table references from string literals
            table_refs = self._extract_python_table_references(python_content)
            result["table_references"] = table_refs

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    result["classes"].append(
                        {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "bases": [
                                b.id for b in node.bases if isinstance(b, ast.Name)
                            ],
                        }
                    )
                elif isinstance(node, ast.FunctionDef):
                    # We might want to track which class a method belongs to
                    # usage of 'ast.walk' flatly visits all nodes.
                    # For simple lineage, flat list of functions is okay for now.
                    result["functions"].append(
                        {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "args": [arg.arg for arg in node.args.args],
                        }
                    )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        result["imports"].append(f"{module}.{alias.name}")

            return result
        except Exception as e:
            print(f"Error parsing Python: {e}")
            return None

    def _extract_python_table_references(self, python_content: str):
        """
        Extract heuristic table references from Python code.
        Looks for common SQL patterns in strings.
        
        Args:
            python_content: Python source code
            
        Returns:
            List of potential table names
        """
        import re
        
        tables = set()
        
        # Pattern 1: FROM/JOIN clauses
        from_pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
        matches = re.findall(from_pattern, python_content, re.IGNORECASE)
        tables.update(matches)
        
        # Pattern 2: INSERT INTO
        insert_pattern = r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
        matches = re.findall(insert_pattern, python_content, re.IGNORECASE)
        tables.update(matches)
        
        # Pattern 3: UPDATE statements
        update_pattern = r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
        matches = re.findall(update_pattern, python_content, re.IGNORECASE)
        tables.update(matches)
        
        return list(tables)

    def parse_json(self, json_content: str):
        """
        Parses JSON content to extract structure.

        Args:
            json_content: JSON string.

        Returns:
            Dict representing the JSON structure or metadata.
        """
        try:
            data = json.loads(json_content)
            result = {"type": type(data).__name__, "keys": [], "array_length": 0}

            if isinstance(data, dict):
                result["keys"] = list(data.keys())
            elif isinstance(data, list):
                result["array_length"] = len(data)
                if len(data) > 0 and isinstance(data[0], dict):
                    # Heuristic: if list of dicts, capture keys of first item
                    result["keys"] = list(data[0].keys())

            return result
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return None


if __name__ == "__main__":
    # Example Usage
    parser = CodeParser()
    import json

    def print_json(data):
        print(json.dumps(data, indent=2))

    print("--- Example 1: CREATE TABLE AS SELECT (Column Lineage) ---")
    sql1 = """
    CREATE TABLE target_db.dbo.fact_sales AS
    SELECT
        s.sale_id as sale_identifier,
        p.product_name,
        c.customer_name,
        CAST(s.sale_date AS DATE) as event_date,
        s.quantity * p.price as total_amount
    FROM staging.sales s
    JOIN staging.products p ON s.product_id = p.product_id
    JOIN staging.customers c ON s.customer_id = c.customer_id
    WHERE s.status = 'COMPLETED';
    """
    lineage1 = parser.parse_sql(sql1, dialect="duckdb")
    print_json(lineage1)

    print("\n--- Example 2: CREATE VIEW ---")
    sql2 = """
    CREATE VIEW reporting.vw_customer_summary AS
    SELECT
        customer_id,
        COUNT(order_id) as number_of_orders,
        SUM(total_amount) as total_spent
    FROM fact_orders
    GROUP BY 1;
    """
    lineage2 = parser.parse_sql(sql2, dialect="tsql")
    print_json(lineage2)

    print("\n--- Example 3: CREATE FUNCTION ---")
    sql3 = """
    CREATE FUNCTION dbo.get_full_name(@first_name VARCHAR(50), @last_name VARCHAR(50))
    RETURNS VARCHAR(101) AS
    BEGIN
        RETURN @first_name + ' ' + @last_name;
    END;
    """
    lineage3 = parser.parse_sql(sql3, dialect="tsql")
    print_json(lineage3)

    print("\n--- Example 4: CREATE PROCEDURE ---")
    sql4 = """
    CREATE OR ALTER PROCEDURE dbo.usp_update_stock
        @product_id INT,
        @quantity_sold INT
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE products.stock
        SET quantity = quantity - @quantity_sold
        WHERE product_id = @product_id;
    END;
    """
    lineage4 = parser.parse_sql(sql4, dialect="tsql")
    print_json(lineage4)

    print("\n--- Example 5: Simple SELECT with transformation ---")
    sql5 = """
    SELECT
        CONCAT(first_name, ' ', last_name) as full_name,
        customer_id
    FROM raw.customers
    """
    lineage5 = parser.parse_sql(sql5, dialect="tsql")
    print_json(lineage5)
