"""
Enhanced tool for executing DAX queries against PowerBI with improved error handling and Euro formatting.
"""

import re
import logging
import time
from typing import Dict, Any, Type, List, Optional

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.powerbi.utils.powerbi_helper import PowerBIHelper
from app.powerbi.config import settings

# Configure logging
logger = logging.getLogger("finsight.tools.query")

# Define input schemas for the tool
class QueryPowerBIToolInput(BaseModel):
    """Input for the query PowerBI tool."""
    query: str = Field(..., description="The DAX query to execute against PowerBI tables.")

class QueryPowerBITool(BaseTool):
    """Enhanced tool for executing DAX queries with preprocessing and error handling."""
    name: str = "query_powerbi_tool"
    description: str = """Run a DAX query against PowerBI tables. Use DAX syntax, not SQL. 
All DAX queries must start with EVALUATE and must return a table expression. 
For simple calculations, use ROW() to wrap CALCULATE().
Always use predefined measures like [CA], [MB], [BUDGET] instead of raw table calculations."""
    args_schema: Type[BaseModel] = QueryPowerBIToolInput

    # Declare pbi_helper as a field
    pbi_helper: Any = Field(default=None, exclude=True)

    def __init__(self):
        """Initialize the query tool with PowerBI helper."""
        super().__init__()
        self.pbi_helper = PowerBIHelper(settings.DATASET_ID)

    def _format_financial_value(self, value, is_percentage=False):
        """Format financial values with proper Euro symbol and percentage handling."""
        if value is None:
            return "N/A"

        try:
            # Convert to float if it's a string
            if isinstance(value, str):
                # Remove any existing formatting
                clean_value = value.replace(',', '').replace('€', '').replace('%', '').strip()
                if clean_value == '' or clean_value.lower() in ['null', 'none', 'n/a']:
                    return "N/A"
                value = float(clean_value)

            # Handle percentage values
            if is_percentage:
                return f"{value:.1f}%"

            # Format financial values with Euro symbol
            if abs(value) >= 1_000_000:
                # Millions: €10.92M
                return f"€{value/1_000_000:.2f}M"
            elif abs(value) >= 1_000:
                # Thousands: €1,234.56
                return f"€{value:,.2f}"
            elif abs(value) >= 100:
                # Hundreds: €123.45
                return f"€{value:.2f}"
            elif abs(value) >= 1:
                # Units: €1.23
                return f"€{value:.2f}"
            else:
                # Less than 1 euro: €0.12
                return f"€{value:.2f}"

        except (ValueError, TypeError):
            return str(value)

    def _detect_financial_columns(self, columns):
        """Detect which columns contain financial data that should be formatted with Euro."""
        financial_keywords = [
            'revenue', 'revenu', 'ca', 'chiffre', 'affaires',
            'margin', 'marge', 'mb', 'gross', 'brute',
            'budget', 'actual', 'réel', 'reel',
            'cost', 'coût', 'cout', 'charge', 'expense',
            'profit', 'bénéfice', 'benefice', 'résultat', 'resultat', 'rex',
            'montant', 'amount', 'value', 'valeur',
            'total', 'sum', 'somme',
            'difference', 'différence', 'variance', 'écart', 'ecart',
            'price', 'prix', 'tarif'
        ]

        percentage_keywords = [
            'percentage', 'pourcentage', 'percent', 'pct', '%',
            'rate', 'taux', 'ratio', 'change', 'growth', 'croissance',
            'variation', 'evolution', 'évolution'
        ]

        financial_columns = []
        percentage_columns = []

        for col in columns:
            col_lower = col.lower()

            # Check for percentage indicators first (more specific)
            if (any(keyword in col_lower for keyword in percentage_keywords) or
                col_lower.endswith('(%)') or
                col_lower.endswith('%') or
                'change' in col_lower or
                'growth' in col_lower or
                'croissance' in col_lower):
                percentage_columns.append(col)
            # Check for financial indicators
            elif any(keyword in col_lower for keyword in financial_keywords):
                financial_columns.append(col)

        return financial_columns, percentage_columns

    def _format_time_series(self, results: List[Dict[str, Any]]) -> str:
        """Format time series data with proper Euro formatting."""
        formatted_output = "Time Series Results:\n\n"

        # Identify date/time column and financial columns
        time_cols = []
        all_columns = list(results[0].keys())

        for col in all_columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ["mois", "date", "month", "year", "année", "trimestre", "semestre", "jour", "day"]):
                time_cols.append(col)

        time_col = time_cols[0] if time_cols else all_columns[0]

        # Detect financial and percentage columns
        data_columns = [col for col in all_columns if col != time_col]
        financial_columns, percentage_columns = self._detect_financial_columns(data_columns)

        # Format as bullet points by time period
        for row in results:
            time_value = row[time_col]
            formatted_output += f"• {time_value}:\n"

            for col in data_columns:
                val = row.get(col)
                if col in percentage_columns:
                    formatted_value = self._format_financial_value(val, is_percentage=True)
                elif col in financial_columns:
                    formatted_value = self._format_financial_value(val, is_percentage=False)
                else:
                    # Non-financial data
                    if isinstance(val, (int, float)):
                        formatted_value = f"{val:,.2f}"
                    else:
                        formatted_value = str(val)

                formatted_output += f"  - {col}: {formatted_value}\n"
            formatted_output += "\n"

        return formatted_output

    def _format_table(self, results: List[Dict[str, Any]]) -> str:
        """Format general table data with Euro formatting."""
        formatted_output = "Query Results:\n\n"

        # Get all column names
        columns = list(results[0].keys())

        # Detect financial and percentage columns
        financial_columns, percentage_columns = self._detect_financial_columns(columns)

        # Format as bullet points
        for i, row in enumerate(results):
            formatted_output += f"• Row {i+1}:\n"
            for col in columns:
                value = row.get(col, "N/A")

                if col in percentage_columns:
                    formatted_value = self._format_financial_value(value, is_percentage=True)
                elif col in financial_columns:
                    formatted_value = self._format_financial_value(value, is_percentage=False)
                else:
                    # Non-financial data
                    if isinstance(value, (int, float)):
                        formatted_value = f"{value:,.2f}"
                    else:
                        formatted_value = str(value)

                formatted_output += f"  - {col}: {formatted_value}\n"
            formatted_output += "\n"

        return formatted_output

    # Enhanced _format_results method for backend/app/powerbi/tools/query_powerbi_tool.py

    def _format_results(self, result: Dict[str, Any]) -> str:
        """Format query results with enhanced presentation for analysis."""
        if isinstance(result, dict):
            if "error" in result:
                return f"Error executing query: {result['error']}"

            if "results" in result and len(result["results"]) > 0:
                results = result["results"]

                # Case 1: Single value result (scalar)
                if len(results) == 1 and len(results[0]) == 1:
                    key = list(results[0].keys())[0]
                    value = results[0][key]

                    # Detect if it's a financial or percentage value
                    key_lower = key.lower()
                    is_percentage = (any(keyword in key_lower for keyword in ['percentage', 'pourcentage', 'percent', 'pct', '%', 'change', 'growth', 'croissance']) or
                                     key_lower.endswith('(%)') or key_lower.endswith('%'))
                    is_financial = any(keyword in key_lower for keyword in ['revenue', 'revenu', 'ca', 'margin', 'marge', 'budget', 'cost', 'coût', 'montant', 'total'])

                    if is_percentage:
                        formatted_value = self._format_financial_value(value, is_percentage=True)
                    elif is_financial:
                        formatted_value = self._format_financial_value(value, is_percentage=False)
                    else:
                        # For unknown types, assume financial if it's a number
                        formatted_value = self._format_financial_value(value, is_percentage=False) if isinstance(value, (int, float)) else str(value)

                    return f"{key}: {formatted_value}"

                # Case 2: Time series data
                if len(results) > 1 and any(
                        any(term in col.lower() for term in ["mois", "date", "month", "year", "année"])
                        for col in results[0].keys()
                ):
                    return self._format_time_series_enhanced(results)

                # Case 3: Business Unit comparison data (enhanced for better analysis)
                if len(results) > 1 and any(
                        any(term in col.lower() for term in ["bu", "business", "unit", "variance", "budget"])
                        for col in results[0].keys()
                ):
                    return self._format_bu_comparison(results)

                # Case 4: General table data
                return self._format_table_enhanced(results)

            return "Query returned no results."

        return f"Query results:\n\n{str(result)}"

    def _format_bu_comparison(self, results: List[Dict[str, Any]]) -> str:
        """Enhanced formatting specifically for Business Unit comparisons."""
        formatted_output = "Business Unit Performance Analysis:\n\n"

        # Get all column names
        columns = list(results[0].keys())

        # Identify key columns
        bu_col = None
        revenue_cols = []
        budget_cols = []
        variance_cols = []

        for col in columns:
            col_lower = col.lower()
            if 'bu' in col_lower or 'business' in col_lower:
                bu_col = col
            elif 'revenue' in col_lower or 'ca' in col_lower or 'revenu' in col_lower:
                revenue_cols.append(col)
            elif 'budget' in col_lower:
                budget_cols.append(col)
            elif 'variance' in col_lower or 'difference' in col_lower or 'dif' in col_lower:
                variance_cols.append(col)

        # Sort results by a key metric if available (e.g., budget variance or revenue)
        sort_col = variance_cols[0] if variance_cols else revenue_cols[0] if revenue_cols else columns[1]

        try:
            # Sort by the metric, handling None values
            sorted_results = sorted(results,
                                    key=lambda x: x.get(sort_col, 0) if x.get(sort_col) is not None else 0,
                                    reverse=True)
        except:
            sorted_results = results

        # Format each Business Unit
        for i, row in enumerate(sorted_results):
            bu_name = row.get(bu_col, f"BU {i+1}")

            # Skip None/empty BU names
            if not bu_name or bu_name == "None":
                continue

            formatted_output += f"• **{bu_name}**:\n"

            for col in columns:
                if col == bu_col:
                    continue

                value = row.get(col, "N/A")

                # Enhanced formatting based on column type
                if isinstance(value, (int, float)) and value is not None:
                    # Detect if this is a financial value
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['revenue', 'budget', 'variance', 'ca', 'mb', 'montant']):
                        if 'variance' in col_lower or 'dif' in col_lower:
                            # Format variance with +/- indicator
                            formatted_value = self._format_financial_value(value, is_percentage=False)
                            if value > 0:
                                formatted_value = f"+{formatted_value}"
                        else:
                            formatted_value = self._format_financial_value(value, is_percentage=False)
                    else:
                        formatted_value = f"{value:,.2f}"
                else:
                    formatted_value = str(value) if value is not None else "N/A"

                formatted_output += f"  - {col}: {formatted_value}\n"

            formatted_output += "\n"

        return formatted_output

    def _format_table_enhanced(self, results: List[Dict[str, Any]]) -> str:
        """Enhanced general table formatting with better financial presentation."""
        formatted_output = "Query Results:\n\n"

        # Get all column names
        columns = list(results[0].keys())

        # Detect financial and percentage columns
        financial_columns, percentage_columns = self._detect_financial_columns(columns)

        # Format as bullet points with enhanced financial formatting
        for i, row in enumerate(results):
            formatted_output += f"• Row {i+1}:\n"
            for col in columns:
                value = row.get(col, "N/A")

                if col in percentage_columns:
                    formatted_value = self._format_financial_value(value, is_percentage=True)
                elif col in financial_columns:
                    formatted_value = self._format_financial_value(value, is_percentage=False)
                    # Add +/- for variance columns
                    if value is not None and isinstance(value, (int, float)) and 'variance' in col.lower():
                        if value > 0:
                            formatted_value = f"+{formatted_value}"
                else:
                    # Non-financial data
                    if isinstance(value, (int, float)) and value is not None:
                        formatted_value = f"{value:,.2f}"
                    else:
                        formatted_value = str(value) if value is not None else "N/A"

                formatted_output += f"  - {col}: {formatted_value}\n"
            formatted_output += "\n"

        return formatted_output

    def _format_time_series_enhanced(self, results: List[Dict[str, Any]]) -> str:
        """Enhanced time series formatting with trend indicators."""
        formatted_output = "Time Series Analysis:\n\n"

        # Identify date/time column and financial columns
        time_cols = []
        all_columns = list(results[0].keys())

        for col in all_columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ["mois", "date", "month", "year", "année", "trimestre", "semestre", "jour", "day"]):
                time_cols.append(col)

        time_col = time_cols[0] if time_cols else all_columns[0]

        # Detect financial and percentage columns
        data_columns = [col for col in all_columns if col != time_col]
        financial_columns, percentage_columns = self._detect_financial_columns(data_columns)

        # Calculate trends if there are multiple periods
        previous_values = {}

        # Format as bullet points by time period with trend indicators
        for i, row in enumerate(results):
            time_value = row[time_col]
            formatted_output += f"• {time_value}:\n"

            for col in data_columns:
                val = row.get(col)

                if col in percentage_columns:
                    formatted_value = self._format_financial_value(val, is_percentage=True)
                elif col in financial_columns:
                    formatted_value = self._format_financial_value(val, is_percentage=False)
                else:
                    # Non-financial data
                    if isinstance(val, (int, float)) and val is not None:
                        formatted_value = f"{val:,.2f}"
                    else:
                        formatted_value = str(val) if val is not None else "N/A"

                # Add trend indicator for financial values
                trend_indicator = ""
                if col in financial_columns and val is not None and isinstance(val, (int, float)):
                    if col in previous_values:
                        if val > previous_values[col]:
                            trend_indicator = " ↗️"
                        elif val < previous_values[col]:
                            trend_indicator = " ↘️"
                        else:
                            trend_indicator = " ➡️"
                    previous_values[col] = val

                formatted_output += f"  - {col}: {formatted_value}{trend_indicator}\n"
            formatted_output += "\n"

        return formatted_output

    def _clean_query(self, query: str) -> str:
        """Clean and prepare query string for execution."""
        # Remove leading/trailing whitespace
        query = query.strip()

        # Remove triple backticks and language identifiers
        if query.startswith("```"):
            # Find the first newline to skip the language identifier
            first_newline = query.find('\n')
            if first_newline > 0:
                # Remove everything before the first content line
                query = query[first_newline:].strip()
                # Also remove the closing backticks if present
                if query.endswith("```"):
                    query = query[:-3].strip()
        elif query.endswith("```"):
            query = query[:-3].strip()

        # Check if the query is wrapped in quotes and remove them
        if (query.startswith('"') and query.endswith('"')) or \
                (query.startswith("'") and query.endswith("'")):
            query = query[1:-1].strip()

        # Remove any language identifiers that appear after EVALUATE
        query = re.sub(r'EVALUATE\s+[A-Za-z]+\s+', 'EVALUATE ', query, flags=re.IGNORECASE)

        # Remove any nested EVALUATE statements
        if re.search(r'EVALUATE\s+EVALUATE', query, flags=re.IGNORECASE):
            query = re.sub(r'EVALUATE\s+', '', query, count=1, flags=re.IGNORECASE)

        # Ensure the query starts with EVALUATE
        if not re.search(r'^EVALUATE', query, re.IGNORECASE):
            query = "EVALUATE\n" + query

        # Replace escaped double quotes with single double quotes
        query = query.replace('""', '"')

        # Remove any tabs or irregular whitespace that could cause issues
        query = query.replace('\t', '    ')

        return query

    def _diagnose_syntax_error(self, query: str, error_message: str) -> str:
        """Diagnose common syntax errors and suggest corrections."""
        diagnoses = []

        # Check for language identifier after EVALUATE
        if re.search(r"EVALUATE\s+[A-Za-z]+\s+EVALUATE", query, re.IGNORECASE):
            diagnoses.append("Multiple EVALUATE statements or language identifier in query")

        # Check for missing RETURN in VAR queries
        if "VAR" in query.upper() and "RETURN" not in query.upper():
            diagnoses.append("Missing RETURN statement in VAR-based query")

        # Check for potentially unbalanced parentheses
        open_parens = query.count("(")
        close_parens = query.count(")")
        if open_parens != close_parens:
            diagnoses.append(f"Unbalanced parentheses: {open_parens} opening vs {close_parens} closing")

        # Check for potentially incorrect measure syntax
        double_bracket_pattern = r'\[\[[^\]]+\]\]'
        if re.search(double_bracket_pattern, query):
            diagnoses.append("Double brackets detected in measures, should use single brackets")

        # Check for potentially incorrect N-1 measure syntax
        incorrect_n1_pattern = r'\[[^\]]+\]/N-1'
        if re.search(incorrect_n1_pattern, query):
            diagnoses.append("Incorrect N-1 measure syntax: Use [CA/N-1] instead of [CA]/N-1")

        if diagnoses:
            return "Syntax issues detected:\n- " + "\n- ".join(diagnoses)

        return "No common syntax issues detected. See error message for details."

    def _is_potentially_invalid_table_expression(self, query: str) -> bool:
        """Check if this query might be an invalid table expression."""
        # Extract the part after EVALUATE
        if "EVALUATE" in query.upper():
            body = re.sub(r"EVALUATE\s+", "", query, flags=re.IGNORECASE, count=1).strip()

            # Patterns that suggest direct CALCULATE use without table context
            if body.upper().startswith("CALCULATE(") and not any(func in body.upper() for func in ["ROW(", "SUMMARIZE", "SUMMARIZECOLUMNS", "VALUES", "TOPN", "DISTINCT"]):
                return True

        return False

    def _fix_invalid_table_expression(self, query: str) -> str:
        """Fix a query that might be an invalid table expression."""
        # Extract the part after EVALUATE
        body = re.sub(r"EVALUATE\s+", "", query, flags=re.IGNORECASE, count=1).strip()

        # If it starts with CALCULATE, wrap it in ROW
        if body.upper().startswith("CALCULATE("):
            # Extract any comments before CALCULATE
            comments = ""
            calculate_start = body.upper().find("CALCULATE(")
            if calculate_start > 0:
                comments = body[:calculate_start]
                body = body[calculate_start:]

            fixed_query = f"EVALUATE\n{comments}ROW(\"Result\", {body})"
            return fixed_query

        return query

    def _run(self, query: str) -> str:
        """Execute a DAX query against PowerBI dataset with automatic correction."""
        logger.info(f"Running query of length {len(query)}")
        start_time = time.time()

        try:
            if not query:
                return "Error: Query is required."

            # Step 1: Clean the query
            original_query = query
            cleaned_query = self._clean_query(query)

            # Log both for debugging
            logger.debug(f"Original query: {original_query}")
            logger.debug(f"Cleaned query: {cleaned_query}")

            # Step 2: Check if this might be an invalid table expression
            if self._is_potentially_invalid_table_expression(cleaned_query):
                # Fix it proactively
                fixed_query = self._fix_invalid_table_expression(cleaned_query)
                if fixed_query != cleaned_query:
                    logger.debug(f"Corrected invalid table expression: {fixed_query}")
                    cleaned_query = fixed_query

            try:
                # Step 3: Execute the query
                logger.info("Executing query")
                result = self.pbi_helper.execute_query(cleaned_query)

                execution_time = time.time() - start_time
                logger.info(f"Query executed in {execution_time:.2f}s")

                return self._format_results(result)

            except Exception as first_error:
                # Step 4: If it fails with specific error, try to fix it
                error_message = str(first_error)
                logger.warning(f"Query execution error: {error_message}")

                # Diagnose the syntax error
                syntax_diagnosis = self._diagnose_syntax_error(cleaned_query, error_message)
                logger.debug(f"Diagnosis: {syntax_diagnosis}")

                if "not a valid table expression" in error_message:
                    logger.info("Attempting to fix invalid table expression")

                    # Try to fix the query
                    fixed_query = self._fix_invalid_table_expression(cleaned_query)
                    if fixed_query != cleaned_query:
                        logger.debug(f"Fixed query: {fixed_query}")

                        # Try again with the fixed query
                        try:
                            result = self.pbi_helper.execute_query(fixed_query)
                            return self._format_results(result)
                        except Exception as second_error:
                            logger.warning(f"Error with fixed query: {str(second_error)}")

                # If we can't fix it or it fails for another reason, return the original error with diagnosis
                return f"Error executing query: {error_message}\n\nDiagnosis: {syntax_diagnosis}\n\nAttempted query:\n{cleaned_query}"

        except Exception as e:
            logger.error(f"Error in query tool: {str(e)}")
            return f"Error executing query: {str(e)}\n\nAttempted query:\n{query}"
        finally:
            total_time = time.time() - start_time
            logger.info(f"Total query processing time: {total_time:.2f}s")

    def to_openai_function(self) -> Dict[str, Any]:
        """Convert the tool to an OpenAI function."""
        schema = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The DAX query to execute against PowerBI tables. Use DAX syntax, not SQL."
                    }
                },
                "required": ["query"]
            }
        }
        return schema