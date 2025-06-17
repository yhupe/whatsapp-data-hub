from sqlalchemy.orm import Session, aliased, joinedload
from sqlalchemy import text
from typing import Dict, Any, List, Type, Optional, Tuple
from uuid import UUID
import datetime
from decimal import Decimal
from fastapi import Depends
from database.database import get_db

# Import of ORM Models
from database.models import Employee, Product
from database.database import Base

class DatabaseQueryBuilder:
    def __init__(self, db: Session):
        self.db = db
        # Mapping of table names (as expected from the LLM) to the ORM models
        self.model_map: Dict[str, Type[Base]] = {
            "employees": Employee,
            "products": Product
        }

    def _build_query(self, table_name: str,
                     filters: Dict[str, Any],
                     columns: List[str],
                     join_table: Optional[str] = None,
                     join_on: Optional[str] = None,
                     join_columns: Optional[List[str]] = None):
        """
        Builds a SQLAlchemy ORM query based on the LLM's parsed intent.
        """

        primary_model = self.model_map.get(table_name)
        if not primary_model:
            raise ValueError(f"Unknown primary table name: {table_name}")

        query_entities = []
        # If specific columns are requested from the primary table, add them.
        if columns and '*' not in columns:
            query_entities = [getattr(primary_model, col) for col in columns if hasattr(primary_model, col)]
        else:
            # If '*' is requested, select all columns from the primary model for explicit selection.
            query_entities = [c for c in primary_model.__table__.columns]  # type: ignore

        query = self.db.query(*query_entities)  # Start query with the explicitly selected primary model entities

        # Handle JOIN logic
        if join_table and join_on and join_columns is not None:
            joined_model = self.model_map.get(join_table)
            if not joined_model:
                raise ValueError(f"Unknown join_table name: {join_table}")

            # Determine the relationship name based on the foreign key column.
            # For 'product_manager_id' column, the relationship is typically 'product_manager'.
            relationship_name = join_on.replace('_id', '') if join_on.endswith('_id') else join_on

            if not hasattr(primary_model, relationship_name):
                raise ValueError(
                    f"Relationship '{relationship_name}' not found on primary table '{table_name}' for join.")

            # Perform the JOIN using the SQLAlchemy relationship. This is crucial for avoiding Cartesian products.
            query = query.join(getattr(primary_model, relationship_name))

            # Add columns from the joined table to the selected entities
            for col in join_columns:
                if hasattr(joined_model, col):
                    query_entities.append(getattr(joined_model, col))
                else:
                    raise ValueError(f"Requested join_column '{col}' not found in join_table '{join_table}'.")

            # Update the query with the combined list of selected entities from both tables
            query = query.with_entities(*query_entities)

        # Apply filters to the query.
        for col_name, value in filters.items():
            target_model = primary_model
            # Determine if the filter column belongs to the primary or joined model
            if not hasattr(primary_model, col_name) and join_table and hasattr(joined_model, col_name):
                target_model = joined_model

            if isinstance(value, str):
                query = query.filter(getattr(target_model, col_name).ilike(f"%{value}%"))
            elif isinstance(value, UUID):
                query = query.filter(getattr(target_model, col_name) == value)
            else:
                query = query.filter(getattr(target_model, col_name) == value)

        return query


    def execute_query(self, query_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes a database query based on the LLM's parsed intent and returns results.
        Returns a list of dictionaries, where each dict represents a row/object.
        """

        table_name = query_intent.get("table")
        action = query_intent.get("action")
        columns = query_intent.get("columns", ["*"])
        filters = query_intent.get("filters", {})
        raw_limit = query_intent.get("limit", None)

        join_table = query_intent.get("join_table")
        join_on = query_intent.get("join_on")
        join_columns = query_intent.get("join_columns")

        limit: Optional[int] = None
        if raw_limit is not None:
            try:
                if isinstance(raw_limit, str) and raw_limit.lower() == 'null':
                    limit = None
                else:
                    limit = int(raw_limit)
                    if limit <= 0:
                        raise ValueError("Limit must be a positive integer.")
            except ValueError:
                print(f"WARNING: Invalid limit value '{raw_limit}' from LLM. Using default limit of 1.")
                limit = None

        if action != "get_data":
            raise ValueError(f"Unsupported action: {action}. Only 'get_data' is supported.")
        if not table_name:
            raise ValueError("Query intent missing 'table' name.")

        try:
            primary_model = self.model_map.get(table_name)
            if not primary_model:  # Should ideally be caught by _build_query
                raise ValueError(f"Unknown table name: {table_name}")

            query = self._build_query(table_name, filters, columns, join_table, join_on, join_columns)

            if limit is not None and limit > 0:
                query = query.limit(limit)

            results = query.all()

            formatted_results = []
            # Logic to correctly format results, handling both tuples (from with_entities/joins)
            # and ORM objects (from simple '*' selects without joins).
            if join_table and join_on and join_columns is not None:
                # For JOIN queries, results are tuples. Reconstruct column names from intent.
                final_column_names = []
                if columns and '*' not in columns:
                    final_column_names.extend(columns)
                else:
                    final_column_names.extend([c.name for c in primary_model.__table__.columns])  # type: ignore
                if join_columns:
                    final_column_names.extend(join_columns)

                for result_tuple in results:
                    row_dict = {}
                    # Map tuple values to their corresponding column names.
                    for i, col_name in enumerate(final_column_names):
                        val = result_tuple[i]
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
                # For single-table queries, results might be ORM objects or tuples.
                for result_item in results:
                    row_dict = {}
                    if columns and '*' not in columns:
                        # Specific columns requested, result is a tuple.
                        for i, col_name in enumerate(columns):
                            val = result_item[i]  # Expecting a tuple here
                            if isinstance(val, UUID):
                                row_dict[col_name] = str(val)
                            elif isinstance(val, datetime.datetime):
                                row_dict[col_name] = val.isoformat()
                            elif isinstance(val, Decimal):
                                row_dict[col_name] = float(val)
                            else:
                                row_dict[col_name] = val
                    else:
                        # All columns ('*') requested, result is an ORM object.
                        for col in primary_model.__table__.columns:  # type: ignore
                            col_name = col.name
                            val = getattr(result_item, col_name)
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


def get_database_query_builder(db: Session = Depends(get_db)) -> DatabaseQueryBuilder:
    """Dependency that returns an instance of DatabaseQueryBuilder."""

    return DatabaseQueryBuilder(db)