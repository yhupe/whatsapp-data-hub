from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List, Type, Optional
from uuid import UUID
import datetime
from decimal import Decimal

# Import of ORM Models
from database.models import Employee, Product, Partner
from database.database import Base

class DatabaseQueryBuilder:
    def __init__(self, db: Session):
        self.db = db
        # Mapping of table names (as expected from the LLM) to the ORM models
        self.model_map: Dict[str, Type[Base]] = {
            "employees": Employee,
            "partners": Partner,
            "products": Product
        }

    def _build_query(self, table_name: str, filters: Dict[str, Any], columns: List[str]):
        """
        Builds a SQLAlchemy ORM query based on the LLM's parsed intent.
        """
        model = self.model_map.get(table_name)
        if not model:
            raise ValueError(f"Unknown table name: {table_name}")

        query = self.db.query(model)

        # Apply filters
        for col_name, value in filters.items():
            # Check if the column exists in the model
            if not hasattr(model, col_name):
                raise ValueError(f"Column '{col_name}' not found in table '{table_name}'.")

            # Dynamically apply filter based on column type or specific needs
            if isinstance(value, str):

                # For string columns: Case-insensitive search using LIKE for partial matches
                query = query.filter(getattr(model, col_name).ilike(f"%{value}%"))
            elif isinstance(value, UUID):

                # For UUID columns, exact match
                query = query.filter(getattr(model, col_name) == value)

            else:
                # For other types (e.g., numbers, booleans), exact match
                query = query.filter(getattr(model, col_name) == value)

        # Select specific columns if requested, otherwise select the full object
        if columns and '*' not in columns:
            selected_columns = []
            for col in columns:
                if hasattr(model, col):
                    selected_columns.append(getattr(model, col))
                else:
                    raise ValueError(f"Requested column '{col}' not found in table '{table_name}'.")
            query = query.with_entities(*selected_columns)

        return query


    def execute_query(self, query_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes a database query based on the LLM's parsed intent and returns results.
        Returns a list of dictionaries, where each dict represents a row/object.
        """

        table_name = query_intent.get("table")
        action = query_intent.get("action")
        columns = query_intent.get("columns", ["*"])  # Default to all columns
        filters = query_intent.get("filters", {})
        raw_limit = query_intent.get("limit", 1)  # Default limit to 1
        limit: Optional[int] = None

        if raw_limit is not None:
            try:
                limit = int(raw_limit)
                if limit <= 0:
                    raise ValueError("Limit must be a positive integer.")
            except ValueError:
                # Handle the case where limit is not a valid integer string
                print(f"WARNING: Invalid limit value '{raw_limit}' from LLM. Using default limit of 1.")
                limit = 1
        else:
            limit = 1


        if action != "get_data":
            # currently only get_data is supported
            raise ValueError(f"Unsupported action: {action}. Only 'get_data' is supported.")

        if not table_name:
            raise ValueError("Query intent missing 'table' name.")

        try:
            query = self._build_query(table_name, filters, columns)

            # Apply limit
            if limit is not None and limit > 0:
                query = query.limit(limit)

            results = query.all()

            # Format results into a list of dictionaries
            formatted_results = []
            for result in results:
                if columns and '*' not in columns:
                    # If specific columns were selected, result might be a tuple
                    # Reconstruct dict from column names and values
                    row_dict = {}
                    for i, col_name in enumerate(columns):
                        # This part can be tricky if the model's attribute name differs from its column name
                        # For now, we assume attribute name == column_name.
                        val = result[i] if isinstance(result, tuple) else getattr(result, col_name)
                        # Handle UUIDs and other non-JSON serializable types
                        if isinstance(val, UUID):
                            row_dict[col_name] = str(val)
                        elif isinstance(val, datetime.datetime):
                            row_dict[col_name] = val.isoformat()
                        elif isinstance(val, Decimal):
                            row_dict[col_name] = float(val)
                        else:
                            row_dict[col_name] = val
                    formatted_results.append(row_dict)
                else:
                    # If full objects were selected, convert ORM object to dict
                    row_dict = {}
                    # Get all attributes that are columns (excluding relationships and internal SQLAlchemy fields)
                    for col in model.__table__.columns: #type: ignore
                        col_name = col.name
                        val = getattr(result, col_name)
                        if isinstance(val, UUID):
                            row_dict[col_name] = str(val)
                        elif isinstance(val, datetime.datetime):
                            row_dict[col_name] = val.isoformat()
                        elif isinstance(val, Decimal):
                            row_dict[col_name] = float(val)
                        else:
                            row_dict[col_name] = val
                    formatted_results.append(row_dict)

            print(f"Database query successful! Result: {formatted_results}")
            return formatted_results

        except ValueError as ve:
            print(f"ERROR: Failed during building/ processing the query (ValueError): {ve}")
            return [{"error": str(ve)}]
        except Exception as e:
            print(f"ERROR: Unexpected error during database query: {e}")
            return [{"error": f"An unexpected database error occurred: {e}"}]
