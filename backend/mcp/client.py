import os

from dotenv import load_dotenv

from langchain_mcp_adapters.client import (
    MultiServerMCPClient
)


load_dotenv(override=True)


async def create_mcp_client():

    """
    Crée le client MCP.

    La configuration exacte dépend
    de ton serveur MCP actuel.
    """

    mcp_url = os.getenv(
        "ATLASSIAN_MCP_URL"
    )


    if not mcp_url:

        raise ValueError(
            "❌ ATLASSIAN_MCP_URL "
            "n'est pas défini."
        )


    client = MultiServerMCPClient({

        "atlassian": {

            "transport":
                "streamable_http",

            "url":
                mcp_url,

        }

    })


    return client