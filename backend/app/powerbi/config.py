"""
Configuration settings for the PowerBI Agent.
"""
from typing import List, Dict, Optional
from pydantic_settings import BaseSettings
import os

class AppSettings(BaseSettings):
    """Application settings loaded from environment variables."""
    APP_NAME: str = "FinSight"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # API settings
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = ["*"]  # For production, specify actual origins

    # PowerBI settings
    DATASET_ID: str = "b715c872-443b-42a7-b5d0-4cc9f92bd88b"
    WORKSPACE_ID: str = "7ab6eef2-3720-409f-9dee-d5cd868c559e"

    # GPT API settings (load from environment variables in production)
    GPT_API_KEY: str = os.getenv("GPT_API_KEY", "placeholder_key")
    GPT_API_ENDPOINT: str = os.getenv(
        "GPT_API_ENDPOINT",
        "https://apigatewayinnovation.azure-api.net/openai-api/deployments"
    )
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-4o")
    GPT_API_VERSION: str = os.getenv("GPT_API_VERSION", "2024-02-01")

    # Known tables in the dataset
    KNOWN_TABLES: List[str] = [
        "PT", "DIM_CLIENT", "DIM_DATE", "DIM_SOCIETE", "DIM_BU",
        "TRI_POLE", "TRI_METIER", "DIM_MARGE", "TRI_MAPPING_MB_MN_FS",
        "MAPPING_ACTIVITE", "MAPPING_PRODUIT", "MAPPING_PROJET_MULTIBU",
        "MAPPING_PROJET_CDR", "MAPPING_COMPTE", "TRI_REGROUPEMENT_PPT",
        "INDICATEURS"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Agent configuration
AGENT_PREFIX = """You are a PowerBI assistant that helps users query and analyze data. 
You have access to a PowerBI dataset with tables containing financial and organizational data.
When answering questions, first gather information about the tables and their relationships, 
then formulate and execute appropriate queries to get the required information."""

AGENT_FORMAT_INSTRUCTIONS = """Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT EFFICIENCY RULES:
- For simple requests like "list tables", go directly to the appropriate tool.
- For financial questions (revenue, margin, budget), ALWAYS check which predefined measures to use first.
- For complex queries, ALWAYS check match_query_example_tool first before trying to create a query from scratch.
- If match_query_example_tool returns an EXACT_MATCH, use the provided query directly with query_powerbi_tool.
- If match_query_example_tool returns a SIMILAR_MATCH, adapt the template query by modifying only the necessary parameters.
- Only proceed with full data exploration if no matches are found.
- When writing DAX queries, ALWAYS use predefined measures ([CA], [MB], etc.) instead of raw table calculations.
- When writing DAX queries, avoid using CALCULATE directly in EVALUATE. Instead, wrap it in ROW() or use SUMMARIZECOLUMNS.

IMPORTANT FORMAT RULES:
- After each "Thought:", you MUST ALWAYS follow with either "Action:" or "Final Answer:".
- NEVER write a Thought without following it with either an Action or Final Answer.
- ALWAYS use "Final Answer:" when you have the information needed to answer the user's question.

EXAMPLE OF CORRECT DAX QUERY FORMAT:
Action: query_powerbi_tool
Action Input: 
EVALUATE
TOPN(
    3,
    SUMMARIZECOLUMNS(
        MAPPING_PRODUIT[Produit],
        "Total Revenue", [CA]
    ),
    [Total Revenue],
    DESC
)

Notice there are NO language identifiers, NO extra backticks, and only ONE EVALUATE statement.
Also notice the use of the predefined measure [CA] instead of SUM(GL[MONTANT]).

NEVER invent or answer questions the user didn't ask.
ALWAYS stay focused on the exact question the user is asking.
ALWAYS prioritize using predefined measures over raw table calculations.
"""

# Get settings instance
settings = AppSettings()