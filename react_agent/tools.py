import os
import re
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain.agents import Tool
from typing import Any, Callable, List
from langchain_core.tools import tool
from sympy import sympify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Validate required environment variables
required_vars = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_ADMIN_KEY"
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Environment variable {var} is missing. Please set it in your .env file.")

# Azure configurations
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_api_version = "2023-05-15"
azure_deployment = "text-embedding-ada-002"

vector_store_address = os.getenv("AZURE_SEARCH_ENDPOINT")
vector_store_password = os.getenv("AZURE_SEARCH_ADMIN_KEY")

# Initialize embeddings
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=azure_deployment,
    openai_api_version=azure_openai_api_version,
    azure_endpoint=azure_endpoint,
    api_key=azure_openai_api_key,
)

# Initialize vector store for contracts
contract_index_name = "sample-vector5"

vector_store = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=contract_index_name,
    embedding_function=embeddings.embed_query,
    additional_search_client_options={"retry_total": 4},
)

# Initialize vector store for invoices
invoice_index_name = "sample-vector6"

invoice_vector_store = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=invoice_index_name,
    embedding_function=embeddings.embed_query,
    additional_search_client_options={"retry_total": 4},
)

# Define the vector search tool for contracts
@tool
def contract_search_tool(query: str) -> str:
    """
    Perform a vector search using Azure Cognitive Search and return formatted results.
    """
    try:
        results = vector_store.similarity_search(query=query, k=1, search_type="similarity")

        response = "🔍 **Contract Search Results:**\n"
        for idx, result in enumerate(results, start=1):
            response += f"{idx}. {result.page_content}\n\n"

        logging.info("Contract search completed successfully.")
        return response
    except Exception as e:
        logging.exception("Error during contract search.")
        return f"⚠️ An error occurred during the contract search: {str(e)}"

# Define the vector search tool for invoices
@tool
def invoice_search_tool(query: str) -> str:
    """
    Perform a vector search on the invoice vector store and return formatted results.
    """
    try:
        results = invoice_vector_store.similarity_search(query=query, k=1, search_type="similarity")

        response = "**Invoice Search Results:**\n"
        for idx, result in enumerate(results, start=1):
            response += f"{idx}. {result.page_content}\n\n"

        logging.info("Invoice search completed successfully.")
        return response
    except Exception as e:
        logging.exception("Error during invoice search.")
        return f"⚠️ An error occurred during the invoice search: {str(e)}"


@tool
def calculate(expression: str, decimals: int = 2) -> str:
    """
    Perform basic mathematical calculations and return the result.

    Supports addition, subtraction, multiplication, division, and percentage.

    Args:
        expression: A string representing the mathematical expression.
        decimals: Number of decimal places for the result.
    Example:
        calculate("2 + 3 * 5") -> "17.00"
        calculate("20% of 150") -> "30.00"
    """
    try:
        # Handle percentages: Convert "20% of 150" to "20/100 * 150"
        expression = re.sub(r'(\d+)% of (\d+)', r'(\1/100) * \2', expression)

        # Convert the expression into a symbolic format and evaluate
        result = sympify(expression).evalf()

        # Format the result with the specified number of decimal places
        logging.info("Calculation completed successfully.")
        return f"{float(result):.{decimals}f}"
    except Exception as e:
        logging.exception("Error during calculation.")
        return f"Error evaluating expression: {e}"

# List of tools for the ReAct agent
TOOLS: List[Callable[..., Any]] = [contract_search_tool, invoice_search_tool, calculate]