# ============================================================
# JIRA AI AGENT
#
# Architecture:
#
# User
#   ↓
# LangGraph
#   ↓
# AI Agent
#   ↓
# Ollama
#   ↓
# MCP Tool
#   ↓
# Atlassian Rovo MCP
#   ↓
# Jira
#
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================
import json
import os
import asyncio
import base64

#from typing import TypedDict, Annotated

from dotenv import load_dotenv

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from langchain_ollama import ChatOllama

from langgraph.graph import (
    StateGraph,
    END,
)

#from langgraph.graph.message import add_messages

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
# 4. JIRA / ATLASSIAN CONFIGURATION
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
print(
    "✅ Jira Cloud ID chargé :",
    JIRA_CLOUD_ID
)
if not JIRA_CLOUD_ID:
    raise ValueError(
        "❌ JIRA_CLOUD_ID manquant."
    )
    
if not JIRA_EMAIL:

    raise ValueError(
        "❌ JIRA_EMAIL manquant."
    )


if not ROVO_MCP_API_TOKEN:

    raise ValueError(
        "❌ ROVO_MCP_API_TOKEN manquant."
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

    response = llm.invoke(
        "Réponds uniquement : connexion OK"
    )

    print(
        "✅ Connexion réussie à Ollama Cloud"
    )

except Exception as e:

    raise RuntimeError(
        f"❌ Erreur Ollama : {e}"
    )

















def format_ticket(data: dict) -> dict:

    fields = data.get("fields", {})

    return {
        "key": data.get("key"),

        "summary": fields.get("summary"),

        "description": fields.get("description"),

        "status": fields.get("status", {}).get("name"),

        "issue_type": fields.get("issuetype", {}).get("name"),

        "priority": fields.get("priority", {}).get("name"),

        "project": fields.get("project", {}).get("name"),

        "project_key": fields.get("project", {}).get("key"),

        "reporter": fields.get("reporter", {}).get("displayName"),

        "assignee": (
            fields.get("assignee", {}).get("displayName")
            if fields.get("assignee")
            else None
        ),

        "created": fields.get("created"),

        "updated": fields.get("updated"),
    }
# ============================================================
# 7. LANGGRAPH STATE
# ============================================================

""" class AgentState(TypedDict):

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ] """


# ============================================================
# 8. MAIN
# ============================================================

async def main():

    # ========================================================
    # 8.1 AUTHENTIFICATION ATLASSIAN MCP
    # ========================================================

    credentials = (
        f"{JIRA_EMAIL}:{ROVO_MCP_API_TOKEN}"
    )

    encoded_credentials = (
        base64.b64encode(
            credentials.encode("utf-8")
        ).decode("utf-8")
    )


    # ========================================================
    # 8.2 CONNEXION MCP
    # ========================================================

    print(
        "\n🔌 Connexion au serveur Atlassian MCP..."
    )


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


    # ========================================================
    # 8.3 RÉCUPÉRATION DES TOOLS MCP
    # ========================================================

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


    # ========================================================
    # 8.4 AFFICHAGE DES TOOLS
    # ========================================================

    print(
        "\n🔧 Tools Atlassian MCP disponibles :"
    )


    if not mcp_tools:

        print(
            "   Aucun Tool MCP disponible."
        )

    else:

        for tool in mcp_tools:

            print(
                f"   -> {tool.name}"
            )


    # ========================================================
    # 8.5 LLM + MCP TOOLS
    # ========================================================

    print(
        "\n🧠 Connexion des Tools au LLM..."
    )


    llm_with_tools = llm.bind_tools(
        mcp_tools
    )


    print(
        "✅ Ollama peut maintenant utiliser "
        "les Tools MCP."
    )


    # ========================================================
    # 8.6 AGENT NODE
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

        # ========================================================
    # DEBUG TEMPORAIRE
    # ========================================================

        print("\n📦 MESSAGES ACTUELS :")

        for message in state["messages"]:

            print("\nTYPE :", type(message))

            print(
                "CONTENT :",
                message.content
            )

            if hasattr(message, "tool_calls"):

                print(
                    "TOOL CALLS :",
                    message.tool_calls
                )
                
                
            
        response = (
            llm_with_tools.invoke(
                state["messages"]
            )
        )


        # ----------------------------------------------------
        # LE LLM VEUT UTILISER UN TOOL
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
        # RÉCUPÉRER LE TICKET JIRA
        # ----------------------------------------------------

        ticket = None

        for message in state["messages"]:

            if message.type == "tool":

                try:

                    # Contenu retourné par MCP
                    tool_content = message.content

                    # Récupérer le texte JSON
                    json_text = tool_content[0]["text"]

                    # Transformer le JSON string en dict
                    raw_ticket = json.loads(json_text)

                    # Nettoyer le ticket
                    ticket = format_ticket(
                        raw_ticket
                    )

                    print("\n🎫 TICKET FORMATÉ :")
                    print(ticket)

                except Exception as e:

                    print(
                        "\n❌ Erreur format_ticket :"
                    )

                    print(e)
                    
                    
                    
                    
                    
                    
        return {

            "messages": [
                response
            ],
            "ticket": ticket

        }


    # ========================================================
    # 8.7 TOOL NODE
    # ========================================================

    tool_node = ToolNode(
        mcp_tools
    )


    # ========================================================
    # 8.8 DÉCISION
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
    # 8.9 CRÉATION DU GRAPH
    # ========================================================

    graph = StateGraph(
        AgentState
    )


    # --------------------------------------------------------
    # NODE 1
    # --------------------------------------------------------

    graph.add_node(
        "agent",
        agent_node
    )


    # --------------------------------------------------------
    # NODE 2
    # --------------------------------------------------------

    graph.add_node(
        "use_tool",
        tool_node
    )


    # ========================================================
    # 8.10 ENTRY POINT
    # ========================================================

    graph.set_entry_point(
        "agent"
    )


    # ========================================================
    # 8.11 CONDITIONAL EDGE
    # ========================================================

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


    # ========================================================
    # 8.12 TOOL → AGENT
    # ========================================================

    graph.add_edge(

        "use_tool",

        "agent"

    )


    # ========================================================
    # 8.13 COMPILE
    # ========================================================

    app = graph.compile()


    print(
        "\n✅ LangGraph compilé !"
    )


    # ========================================================
    # 9. SYSTEM MESSAGE
    # ========================================================

    messages = [

      SystemMessage(
    content=f"""
Tu es un AI Agent spécialisé dans Jira.

Tu peux utiliser les Tools Atlassian MCP.

Informations de connexion Jira :

Cloud ID :
{JIRA_CLOUD_ID}

Lorsque l'utilisateur demande des informations
sur un ticket Jira, utilise les Tools MCP.

Pour récupérer un ticket Jira :

1. Identifie la clé du ticket.
2. Utilise le Tool MCP Atlassian approprié.
3. Pour le paramètre cloudId, utilise TOUJOURS exactement :
   {JIRA_CLOUD_ID}
4. Ne mets JAMAIS "your-cloud-id".
5. Récupère les informations du ticket.
6. Analyse le résultat.
7. Donne une réponse claire.

Ne prétends jamais avoir récupéré un ticket
si le Tool MCP n'a pas retourné les données.

Si le Tool demande un paramètre cloudId,
utilise obligatoirement :

{JIRA_CLOUD_ID}
"""
)   ]


    # ========================================================
    # 10. INTERACTIVE LOOP
    # ========================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "🚀 JIRA AI AGENT MCP PRÊT"
    )

    print(
        "=" * 60
    )

    print(
        "\nExemple :"
    )

    print(
        "Récupère le ticket KAN-1"
    )

    print(
        "\nTape 'exit' pour quitter."
    )


    while True:

        user_input = input(
            "\nUser : "
        ).strip()


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() in [

            "exit",
            "quit",
            "stop"

        ]:

            print(
                "\n👋 Agent arrêté."
            )

            break


        if not user_input:

            continue


        # ----------------------------------------------------
        # USER MESSAGE
        # ----------------------------------------------------

        messages.append(

            HumanMessage(
                content=user_input
            )

        )


        # ----------------------------------------------------
        # LANGGRAPH
        # ----------------------------------------------------

        try:

            result = await app.ainvoke({

                "messages":
                    messages

            })

        except Exception as e:

            print(
                "\n❌ Erreur LangGraph :"
            )

            print(e)

            continue


        # ----------------------------------------------------
        # UPDATE STATE
        # ----------------------------------------------------

        messages = result[
            "messages"
        ]


        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        print(
            "\n"
            + "=" * 60
        )

        print(
            "🤖 Assistant :"
        )

        print(
            "=" * 60
        )

        print(
            messages[-1].content
        )


# ============================================================
# 11. START
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
    
    
    
    
    
    
    
    """ getJiraIssue = récupérer
                 ↓
            data brut
                 ↓
format_ticket = nettoyer/sélectionner
                 ↓
            ticket propre
                 ↓
         State["ticket"] """