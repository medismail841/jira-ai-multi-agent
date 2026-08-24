# ============================================================
# JIRA AI AGENT — MCP VERSION
#
# Architecture:
#
# FastAPI
#    ↓
# jira_agent()
#    ↓
# LangGraph
#    ↓
# Ollama
#    ↓
# MCP Tool : getJiraIssue
#    ↓
# Atlassian Rovo MCP
#    ↓
# Jira
#
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

import os
import json
import base64

from dotenv import load_dotenv

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from langchain_ollama import ChatOllama

from langgraph.graph import (
    StateGraph,
    END,
)

from langgraph.prebuilt import ToolNode

from langchain_mcp_adapters.client import (
    MultiServerMCPClient
)

from graph.state import AgentState


# ============================================================
# 2. ENVIRONMENT
# ============================================================

load_dotenv(
    override=True
)

print("✅ .env chargé")


# ============================================================
# 3. OLLAMA CONFIGURATION
# ============================================================

OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY"
)

if not OLLAMA_API_KEY:

    raise ValueError(
        "❌ OLLAMA_API_KEY manquante."
    )


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma4:31b-cloud"
)


# ============================================================
# 4. ATLASSIAN / JIRA CONFIGURATION
# ============================================================

JIRA_EMAIL = os.getenv(
    "JIRA_EMAIL"
)

ROVO_MCP_API_TOKEN = os.getenv(
    "ROVO_MCP_API_TOKEN"
)

JIRA_CLOUD_ID = os.getenv(
    "JIRA_CLOUD_ID"
)


if not JIRA_EMAIL:

    raise ValueError(
        "❌ JIRA_EMAIL manquant."
    )


if not ROVO_MCP_API_TOKEN:

    raise ValueError(
        "❌ ROVO_MCP_API_TOKEN manquant."
    )


if not JIRA_CLOUD_ID:

    raise ValueError(
        "❌ JIRA_CLOUD_ID manquant."
    )


print(
    "✅ Jira Cloud ID chargé :",
    JIRA_CLOUD_ID
)


# ============================================================
# 5. OLLAMA
# ============================================================

llm = ChatOllama(

    model=OLLAMA_MODEL,

    base_url="https://ollama.com",

    client_kwargs={

        "headers": {

            "Authorization":
                f"Bearer {OLLAMA_API_KEY}"

        }

    },

    temperature=0,

)


print(
    f"✅ Ollama configuré : {OLLAMA_MODEL}"
)


# ============================================================
# 6. TEST OLLAMA
# ============================================================

try:

    llm.invoke(
        "Réponds uniquement : connexion OK"
    )

    print(
        "✅ Connexion réussie à Ollama Cloud"
    )

except Exception as e:

    raise RuntimeError(
        f"❌ Erreur Ollama : {e}"
    )


# ============================================================
# 7. FORMAT TICKET
# ============================================================

def format_ticket(
    data: dict
) -> dict:

    """
    Transforme la réponse brute de getJiraIssue
    en ticket simplifié utilisable par les autres agents.
    """

    fields = data.get(
        "fields",
        {}
    )


    status = fields.get(
        "status",
        {}
    )


    issue_type = fields.get(
        "issuetype",
        {}
    )


    priority = fields.get(
        "priority",
        {}
    )


    project = fields.get(
        "project",
        {}
    )


    reporter = fields.get(
        "reporter",
        {}
    )


    assignee = fields.get(
        "assignee"
    )


    return {

        "key":
            data.get(
                "key"
            ),

        "summary":
            fields.get(
                "summary"
            ),

        "description":
            fields.get(
                "description"
            ),

        "status":
            status.get(
                "name"
            ) if isinstance(status, dict)
            else None,

        "issue_type":
            issue_type.get(
                "name"
            ) if isinstance(issue_type, dict)
            else None,

        "priority":
            priority.get(
                "name"
            ) if isinstance(priority, dict)
            else None,

        "project":
            project.get(
                "name"
            ) if isinstance(project, dict)
            else None,

        "project_key":
            project.get(
                "key"
            ) if isinstance(project, dict)
            else None,

        "reporter":
            reporter.get(
                "displayName"
            ) if isinstance(reporter, dict)
            else None,

        "assignee":
            assignee.get(
                "displayName"
            ) if isinstance(assignee, dict)
            else None,

        "created":
            fields.get(
                "created"
            ),

        "updated":
            fields.get(
                "updated"
            ),

    }


# ============================================================
# 8. MCP CLIENT
# ============================================================

async def create_mcp_client():

    print(
        "\n🔌 Connexion au serveur Atlassian MCP..."
    )


    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    credentials = (
        f"{JIRA_EMAIL}:{ROVO_MCP_API_TOKEN}"
    )


    encoded_credentials = (
        base64.b64encode(
            credentials.encode("utf-8")
        ).decode("utf-8")
    )


    # --------------------------------------------------------
    # MCP Client
    # --------------------------------------------------------

    mcp_client = MultiServerMCPClient({

        "atlassian": {

            "transport":
                "streamable_http",

            "url":
                "https://mcp.atlassian.com/v1/mcp",

            "headers": {

                "Authorization":
                    f"Basic {encoded_credentials}"

            }

        }

    })


    print(
        "✅ Client Atlassian MCP créé"
    )


    return mcp_client


# ============================================================
# 9. RÉCUPÉRER LES TOOLS MCP
# ============================================================

async def get_mcp_tools(
    mcp_client
):

    print(
        "\n🔧 Récupération des Tools MCP..."
    )


    try:

        mcp_tools = await (
            mcp_client.get_tools()
        )

    except Exception as e:

        raise RuntimeError(
            f"""
❌ Impossible de récupérer les Tools Atlassian MCP.

Erreur :

{e}
"""
        )


    print(
        "\n🔧 Tools Atlassian MCP disponibles :"
    )


    for tool in mcp_tools:

        print(
            f"   -> {tool.name}"
        )


    return mcp_tools


# ============================================================
# 10. JIRA AGENT
# ============================================================

async def jira_agent_vf(
    state: AgentState
) -> dict:

    """
    Récupère un ticket Jira via Atlassian MCP.

    Retourne :

    {
        "issue_key": "KAN-1",
        "ticket": {...}
    }
    """

    # ========================================================
    # RÉCUPÉRER ISSUE KEY DEPUIS LE STATE
    # ========================================================

    issue_key = state["issue_key"]

    # ========================================================
    # NORMALISATION
    # ========================================================

    issue_key = (
        issue_key
        .strip()
        .upper()
    )

    if not issue_key:

        raise ValueError(
            "❌ Issue key manquante."
        )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "🔎 JIRA AGENT — MCP"
    )

    print(
        "=" * 60
    )

    print(
        f"Ticket : {issue_key}"
    )


    # ========================================================
    # MCP CLIENT
    # ========================================================

    mcp_client = await create_mcp_client()


    # ========================================================
    # MCP TOOLS
    # ========================================================

    mcp_tools = await get_mcp_tools(
        mcp_client
    )


    # ========================================================
    # LLM + TOOLS
    # ========================================================

    print(
        "\n🧠 Connexion des Tools au LLM..."
    )


    llm_with_tools = llm.bind_tools(
        mcp_tools
    )


    print(
        "✅ Ollama peut utiliser les Tools MCP."
    )


    # ========================================================
    # AGENT NODE
    # ========================================================

    def agent_node(
        state: AgentState
    ):

        print(
            "\n"
            + "-" * 60
        )

        print(
            "🤖 AI AGENT NODE"
        )

        print(
            "-" * 60
        )


        response = (
            llm_with_tools.invoke(
                state["messages"]
            )
        )


        # ----------------------------------------------------
        # DEBUG TOOL CALL
        # ----------------------------------------------------

        if response.tool_calls:

            print(
                f"\n🔧 Le LLM demande "
                f"{len(response.tool_calls)} Tool(s)"
            )


            for tool_call in response.tool_calls:

                print(
                    f"\n   Tool : "
                    f"{tool_call['name']}"
                )

                print(
                    f"   Args : "
                    f"{tool_call['args']}"
                )


        else:

            print(
                "\n💬 Le LLM répond directement."
            )


        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        #
        # On ne cherche PAS encore le ToolMessage ici.
        #
        # Le ToolNode va d'abord exécuter getJiraIssue.
        #
        # Ensuite LangGraph reviendra dans agent_node.
        #
        # ----------------------------------------------------

        return {

            "messages": [
                response
            ]

        }


    # ========================================================
    # TOOL NODE
    # ========================================================

    tool_node = ToolNode(
        mcp_tools
    )


    # ========================================================
    # DECISION
    # ========================================================

    def should_continue(
        state: AgentState
    ):

        last_message = (
            state["messages"][-1]
        )


        if last_message.tool_calls:

            print(
                "\n🔀 Décision : use_tool"
            )

            return "use_tool"


        print(
            "\n🔀 Décision : END"
        )

        return END


    # ========================================================
    # BUILD GRAPH
    # ========================================================

    graph = StateGraph(
        AgentState
    )


    graph.add_node(
        "agent",
        agent_node
    )


    graph.add_node(
        "use_tool",
        tool_node
    )


    graph.set_entry_point(
        "agent"
    )


    graph.add_conditional_edges(

        "agent",

        should_continue,

        {

            "use_tool":
                "use_tool",

            END:
                END,

        }

    )


    graph.add_edge(

        "use_tool",

        "agent"

    )


    app = graph.compile()


    print(
        "\n✅ LangGraph compilé !"
    )


    # ========================================================
    # SYSTEM MESSAGE
    # ========================================================

    messages = [

        SystemMessage(

            content=f"""

Tu es un AI Agent spécialisé dans Jira.

Tu peux utiliser les Tools Atlassian MCP.

Pour récupérer un ticket Jira :

1. Utilise obligatoirement le Tool getJiraIssue.
2. Le ticket demandé est : {issue_key}
3. Pour cloudId utilise obligatoirement :

{JIRA_CLOUD_ID}

4. Ne mets jamais "your-cloud-id".
5. Récupère les données du ticket.
6. Ne prétends jamais avoir récupéré
   un ticket si le Tool MCP n'a pas retourné
   les données.

"""

        ),

        HumanMessage(

            content=
                f"Récupère le ticket {issue_key}"

        )

    ]


    # ========================================================
    # EXECUTION LANGGRAPH
    # ========================================================

    result = await app.ainvoke({

        "messages":
            messages,

        "issue_key":
            issue_key

    })


    # ========================================================
    # RÉCUPÉRER LE TOOL MESSAGE
    # ========================================================

    ticket = None


    print(
        "\n📦 Analyse des messages LangGraph..."
    )


    for message in result["messages"]:

        print(
            "\nTYPE :",
            type(message)
        )


        # ----------------------------------------------------
        # TOOL MESSAGE
        # ----------------------------------------------------

        if message.type == "tool":

            print(
                "🔧 ToolMessage détecté."
            )


            try:

                tool_content = (
                    message.content
                )


                # ------------------------------------------------
                # MCP retourne une liste
                # ------------------------------------------------

                if isinstance(
                    tool_content,
                    list
                ):

                    json_text = (
                        tool_content[0]["text"]
                    )

                else:

                    json_text = (
                        tool_content
                    )


                # ------------------------------------------------
                # JSON string → dict
                # ------------------------------------------------

                raw_ticket = json.loads(
                    json_text
                )


                # ------------------------------------------------
                # FORMAT
                # ------------------------------------------------

                ticket = format_ticket(
                    raw_ticket
                )


                print(
                    "\n🎫 TICKET FORMATÉ :"
                )

                print(
                    ticket
                )


                break


            except Exception as e:

                print(
                    "\n❌ Erreur format_ticket :"
                )

                print(
                    e
                )


    # ========================================================
    # VALIDATION
    # ========================================================

    if not ticket:

        raise RuntimeError(
            "❌ Le ticket Jira n'a pas pu être récupéré."
        )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "issue_key":
            issue_key,

        "ticket":
            ticket

    }