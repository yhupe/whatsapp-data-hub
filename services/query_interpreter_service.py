import os
from typing import Optional, Dict, Any
import json
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()


class QueryInterpreterService:
    def __init__(self):
        # Loading the API key from .env
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        # Initialize OpenAI Client
        self.client = OpenAI(api_key=self.api_key)

        # openAI Model I want to use
        self.model_name = "gpt-4o-mini"

        # Definition of the database schema for the LLM
        self.db_schema = """
                
        You have access to the following database tables:

        Table: employees
        Description: Information about company employees.
        Columns:
        - id (UUID): Unique identifier for the employee.
        - name (Text): Full name of the employee.
        - phone_number (Text): Employee's phone number (e.g., +49... format).
        - telegram_id (BigInteger): Telegram user ID linked to the employee.
        - email (Text): Employee's email address.
        - role (Text): Employee's role (e.g., 'admin', 'general_user').
        - is_authenticated (Boolean): True if the employee's account is verified.
        - created_at (DateTime): Timestamp when the record was created.
        - updated_at (DateTime): Timestamp of the last update to the record.


        Table: products
        Description: Information about products offered.
        Columns:
        - id (UUID): Unique identifier for the product.
        - name (Text): Name of the product.
        - description (Text): Detailed description of the product.
        - product_manager_id (UUID): FOREIGN KEY to employees.id. This links a product to its responsible employee (product manager).
        - length (Numeric): Length of the product.
        - height (Numeric): Height of the product.
        - width (Numeric): Width of the product.
        - weight (Numeric): Weight of the product.
        - image_url (Text): URL to the product image.
        - price (Numeric): Price of the product.
        - stock_quantity (Integer): Current quantity of the product in stock.
        - is_active (Boolean): True if the product is currently active/available.
        - notes (Text): General notes about the product.
        - created_at (DateTime): Timestamp when the record was created.
        - updated_at (DateTime): Timestamp of the last update to the record.
                
        """

        self.system_prompt = """
                You are an AI assistant that translates natural language queries into structured JSON queries for a database.
                Your task is to understand the user's intent and create a JSON object containing the necessary information to query the database.

                {db_schema_placeholder}

                The JSON object MUST have the following format:
                {{
                    "table": "Name of the primary relevant table (employees, products)",
                    "action": "get_data",
                    "columns": ["List of requested columns or '*' for all columns"],
                    "filters": {{
                        "column_name": "value"
                    }},
                    "join_table": "Optional: Name of a table to join if data from a related table is needed (e.g., 'employees' if querying product manager name)",
                    "join_on": "Optional: Column on the primary table to join on (e.g., 'product_manager_id')",
                    "join_columns": ["Optional: Columns to select from the joined table (e.g., 'name' from employees)"],
                    "limit": "Optional maximum number of results (default: 1)",
                    "error": "Optional: An error message if the query is not understood or not applicable to the database"
                }}

                Important Rules:
                - ALWAYS select one of the two tables: employees, products as the primary 'table'.
                - If specific columns are requested (e.g., "email", "weight"), include them in 'columns'. If no specific column is mentioned and the request is for general information, use ['*'].
                - ALWAYS use 'filters' when conditions are mentioned (e.g., name, ID). Use the EXACT column names from the schema (e.g., 'first_name', 'last_name', 'name', 'phone_number').
                - Combine first and last names into 'name' for the 'employees' table when filtering (as per your schema). If the user provides "Max Mustermann", use {{"name": "Max Mustermann"}}.
                - When a query requires information from a related table (e.g., "Who is the product manager for product X?"), use 'join_table', 'join_on', and 'join_columns'.
                    - For 'join_on', always use the foreign key column from the PRIMARY table.
                    - For 'join_columns', specify the columns needed from the joined table.
                - If a query is unclear or cannot be applied to the database, set 'error' with an appropriate message.
                - ONLY generate the JSON object, no additional text or explanations BEFORE or AFTER the JSON.
                - All values in 'filters' must be strings.
                - If filtering on a column ending with '_id' (e.g., 'product_manager_id'), the value MUST be a UUID. 
                If the user provides a name (like "Hannes Pickel") for an _id column, set the 'error' field with a 
                message like "Cannot filter UUID column with a name. Please provide an ID or ask for the manager's name directly.

                Example requests and expected JSON:
                Request: 'show me the email of Max Mustermann.'
                JSON: {{"table": "employees", "action": "get_data", "columns": ["email"], "filters": {{"name": "Max Mustermann"}}}}

                User: 'How many products are in stock?'
                JSON: {{"table": "products", "action": "get_data", "columns": ["id"], "filters": {{}}}}
                # VERY IMPORTANT: For count queries like "How many X are there?", set "columns" to ["id"] and "filters" to {{}}, and DO NOT set the "error" field.

                Request: 'show me all products.'
                JSON: {{"table": "products", "action": "get_data", "columns": ["*"], "filters": {{}}, "limit": "50"}}

                Request: 'What is the price of Product A?'
                JSON: {{"table": "products", "action": "get_data", "columns": ["price"], "filters": {{"name": "Product A"}}, "limit": "1"}}

                Request: 'Who is the product manager for the product Cannabis?'
                JSON: {{"table": "products", "action": "get_data", "columns": ["name"], "filters": {{"name": "Cannabis"}}, "join_table": "employees", "join_on": "product_manager_id", "join_columns": ["name"], "limit": "1"}}

                Request: 'Give me the email of the product manager for "My Awesome Product".'
                JSON: {{"table": "products", "action": "get_data", "columns": ["name"], "filters": {{"name": "My Awesome Product"}}, "join_table": "employees", "join_on": "product_manager_id", "join_columns": ["email"], "limit": "1"}}

                """.format(db_schema_placeholder=self.db_schema)

    async def interpret_query(self, user_query: str) -> Dict[str, Any]:
        """
        Sends the user query to the LLM and interprets the JSON response.
        """
        try:
            escaped_user_query = user_query.replace('{', '{{').replace('}', '}}')
            print(f"Send query to OpenAI: '{escaped_user_query}' with model '{self.model_name}'")

            chat_completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_query}
                ],

                # requests the answer in JSON format
                response_format={"type": "json_object"}
            )

            # Parsing of the LLM answer
            # chat_completion.choices[0].message.content contains the JSON-String
            llm_response_content = chat_completion.choices[0].message.content
            print(f"OpenAI raw response: {llm_response_content}")

            # JSON string parsing into a Python dict
            parsed_response = json.loads(llm_response_content)

            # Extra validation of LLM response
            if not isinstance(parsed_response, dict):
                raise ValueError("LLM response is not a valid JSON object.")
            if "table" not in parsed_response or "action" not in parsed_response:
                raise ValueError("LLM response missing 'table' or 'action' key.")

            return parsed_response

        except json.JSONDecodeError as e:
            print(f"ERROR: OpenAI did not return valid JSON: {llm_response_content} - Error: {e}")
            return {
                "error": f"Internal error: The AI was not able to interpret the query as valid JSON: ({e})"}
        except Exception as e:
            print(f"ERROR: Failed during OpenAI query: {e}")
            return {"error": f"An error occurred while AI processing your query. ({e})"}
