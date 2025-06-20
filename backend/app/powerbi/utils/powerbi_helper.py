# backend/app/powerbi/utils/powerbi_helper.py
"""
Enhanced PowerBI Helper with fixed response parsing and token caching
"""
import requests
import urllib.parse
from azure.identity import InteractiveBrowserCredential
from app.powerbi.config import settings
import threading
from datetime import datetime, timedelta
import time
import json

class PowerBIAuthManager:
    """Singleton class to manage PowerBI authentication and token caching"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PowerBIAuthManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.credential = None
        self.token = None
        self.token_expires_at = None
        self.token_lock = threading.Lock()

    def _initialize_credential(self):
        """Initialize the credential only once"""
        if self.credential is None:
            self.credential = InteractiveBrowserCredential(
                timeout=300,  # 5 minutes timeout
            )

    def get_token(self, force_refresh=False):
        """Get a valid token, refreshing if necessary"""
        with self.token_lock:
            current_time = datetime.now()

            # Check if we have a valid token (with 5-minute buffer)
            if (not force_refresh and
                    self.token and
                    self.token_expires_at and
                    current_time < (self.token_expires_at - timedelta(minutes=5))):
                return self.token

            # Initialize credential if needed
            self._initialize_credential()

            try:
                # Get new token
                token_obj = self.credential.get_token("https://analysis.windows.net/powerbi/api/.default")
                self.token = token_obj.token

                # Calculate expiration time (tokens typically last 1 hour)
                if hasattr(token_obj, 'expires_on'):
                    self.token_expires_at = datetime.fromtimestamp(token_obj.expires_on)
                else:
                    # Default to 50 minutes from now if expires_on not available
                    self.token_expires_at = current_time + timedelta(minutes=50)

                print(f"Token refreshed successfully. Expires at: {self.token_expires_at}")
                return self.token

            except Exception as e:
                print(f"Error getting token: {str(e)}")
                # Reset token info on error
                self.token = None
                self.token_expires_at = None
                raise

# Global auth manager instance
_auth_manager = PowerBIAuthManager()

class PowerBIHelper:
    def __init__(self, dataset_id=None, table_names=None):
        """Initialize the PowerBI Helper with dataset ID and shared credentials."""
        self.dataset_id = dataset_id or settings.DATASET_ID
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        self.table_names = table_names or settings.KNOWN_TABLES

        # Use the global auth manager
        self.auth_manager = _auth_manager

    def get_token(self):
        """Get authentication token using the shared auth manager."""
        return self.auth_manager.get_token()

    def get_headers(self):
        """Get headers for API requests including authentication token."""
        token = self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def refresh_token_if_needed(self, response):
        """Refresh token if response indicates authentication issues."""
        if response.status_code == 401:
            try:
                # Force refresh the token
                self.auth_manager.get_token(force_refresh=True)
                return True
            except Exception as e:
                print(f"Error refreshing token: {str(e)}")
                return False
        return False

    def execute_query_with_retry(self, endpoint, data=None, method='POST', max_retries=1):
        """Execute API request with automatic token refresh retry"""
        headers = self.get_headers()

        for attempt in range(max_retries + 1):
            try:
                if method.upper() == 'POST':
                    response = requests.post(endpoint, json=data, headers=headers)
                else:
                    response = requests.get(endpoint, headers=headers)

                # If unauthorized and not the last attempt, try to refresh token
                if response.status_code == 401 and attempt < max_retries:
                    print(f"Authentication failed (attempt {attempt + 1}), refreshing token...")
                    if self.refresh_token_if_needed(response):
                        headers = self.get_headers()  # Get new headers with refreshed token
                        continue

                return response

            except Exception as e:
                if attempt == max_retries:
                    raise
                print(f"Request failed (attempt {attempt + 1}): {str(e)}")
                time.sleep(1)  # Brief delay before retry

        return response

    def execute_query(self, query):
        """Execute a DAX query against the PowerBI dataset with proper response parsing."""
        try:
            endpoint = f"{self.base_url}/datasets/{self.dataset_id}/executeQueries"

            body = {
                "queries": [
                    {
                        "query": query
                    }
                ],
                "serializerSettings": {
                    "includeNulls": True
                }
            }

            response = self.execute_query_with_retry(endpoint, body)

            if response.status_code != 200:
                return {"error": f"Failed to execute query: {response.status_code} - {response.text}"}

            # Process the response
            result = response.json()

            if "results" in result and len(result["results"]) > 0:
                query_result = result["results"][0]

                if "tables" in query_result and len(query_result["tables"]) > 0:
                    table_data = query_result["tables"][0]

                    # Get column names and rows
                    columns = table_data.get("columns", [])
                    rows = table_data.get("rows", [])

                    if not columns:
                        # If no columns metadata, return raw rows
                        return {"results": rows}

                    # Convert rows to dictionaries using column names
                    results = []
                    for row in rows:
                        row_dict = {}
                        for i, column in enumerate(columns):
                            column_name = column.get("name", f"Column{i+1}")
                            if i < len(row):
                                row_dict[column_name] = row[i]
                            else:
                                row_dict[column_name] = None
                        results.append(row_dict)

                    return {"results": results}

                # Fallback: if no tables structure, try direct access
                elif "rows" in query_result:
                    return {"results": query_result["rows"]}
                else:
                    return {"results": [query_result]}

            return {"results": []}

        except Exception as e:
            return {"error": f"Error executing query: {str(e)}"}

    def get_table_schema(self, table_name):
        """Get schema information for a specific table using DAX query."""
        try:
            query = f"""
            EVALUATE
            TOPN(1, {table_name})
            """

            result = self.execute_query(query)

            if isinstance(result, dict) and "error" in result:
                return {"error": f"Failed to execute query: {result['error']}"}

            # Process the results to extract column information
            columns = []
            if "results" in result and result["results"] and len(result["results"]) > 0:
                row = result["results"][0]
                for col_name, value in row.items():
                    data_type = "string"  # Default
                    if isinstance(value, (int, float)):
                        data_type = "number"
                    elif isinstance(value, bool):
                        data_type = "boolean"
                    elif isinstance(value, dict) and value.get("__type__") == "datetime":
                        data_type = "datetime"

                    columns.append({
                        "name": col_name,
                        "dataType": data_type
                    })

            return {"columns": columns}
        except Exception as e:
            return {"error": f"Error getting schema: {str(e)}"}

    def list_tables(self):
        """List all tables in the PowerBI dataset."""
        try:
            endpoint = f"{self.base_url}/datasets/{self.dataset_id}/tables"
            response = self.execute_query_with_retry(endpoint, method='GET')

            if response.status_code != 200:
                return {"error": f"Failed to execute API request: {response.status_code} - {response.text}"}

            tables_data = response.json()
            tables = tables_data.get("value", [])
            table_list = [table.get("name", "") for table in tables]
            return table_list
        except Exception as e:
            return {"error": f"Error listing tables: {str(e)}"}

    def debug_powerbi_response(self, query):
        """Debug method to understand PowerBI API response structure."""
        try:
            endpoint = f"{self.base_url}/datasets/{self.dataset_id}/executeQueries"

            body = {
                "queries": [
                    {
                        "query": query
                    }
                ],
                "serializerSettings": {
                    "includeNulls": True
                }
            }

            response = self.execute_query_with_retry(endpoint, body)

            if response.status_code == 200:
                result = response.json()
                print("\n=== DEBUG: PowerBI API Response Structure ===")
                print(f"Response keys: {list(result.keys())}")

                if "results" in result:
                    print(f"Results length: {len(result['results'])}")
                    if len(result["results"]) > 0:
                        query_result = result["results"][0]
                        print(f"Query result keys: {list(query_result.keys())}")

                        if "tables" in query_result:
                            print(f"Tables length: {len(query_result['tables'])}")
                            if len(query_result["tables"]) > 0:
                                table_data = query_result["tables"][0]
                                print(f"Table data keys: {list(table_data.keys())}")

                                if "columns" in table_data:
                                    print(f"Columns: {table_data['columns']}")
                                if "rows" in table_data:
                                    print(f"First few rows: {table_data['rows'][:2]}")

                print("=== Full Response (first 1000 chars) ===")
                print(str(result)[:1000])
                print("=======================================\n")

            return response.json()

        except Exception as e:
            print(f"Debug error: {str(e)}")
            return None