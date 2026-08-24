# ============================================================
# agents/git_agent.py
# GITHUB DEPLOY AI AGENT — MCP VERSION
# ============================================================

import os

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
    MultiServerMCPClient,
)

from graph.state import AgentState


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(
    override=True
)

print("✅ .env chargé")


# ============================================================
# OLLAMA
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
# GITHUB MCP
# ============================================================

GIT_MCP_URL = os.getenv(
    "GIT_MCP_URL"
)

GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv(
    "GITHUB_PERSONAL_ACCESS_TOKEN"
)


if not GIT_MCP_URL:

    raise ValueError(
        "❌ GIT_MCP_URL manquante."
    )


if not GITHUB_PERSONAL_ACCESS_TOKEN:

    raise ValueError(
        "❌ GITHUB_PERSONAL_ACCESS_TOKEN manquant."
    )


print(
    "✅ Git MCP URL chargée"
)

print(
    "✅ GitHub Personal Access Token chargé"
)


# ============================================================
# GITHUB REPOSITORY
# ============================================================

GITHUB_REPOSITORY = os.getenv(
    "GITHUB_REPOSITORY"
)

GITHUB_BRANCH = os.getenv(
    "GITHUB_BRANCH",
    "main"
)


if not GITHUB_REPOSITORY:

    raise ValueError(
        "❌ GITHUB_REPOSITORY manquant."
    )


# ------------------------------------------------------------
# Parse owner / repository
# ------------------------------------------------------------

repository_parts = (
    GITHUB_REPOSITORY
    .strip()
    .strip("/")
    .split("/")
)


if len(repository_parts) != 2:

    raise ValueError(
        "❌ GITHUB_REPOSITORY doit avoir "
        "le format : owner/repository"
    )


GITHUB_OWNER = repository_parts[0]

GITHUB_REPO = repository_parts[1]


print(
    f"✅ GitHub Owner : {GITHUB_OWNER}"
)

print(
    f"✅ GitHub Repository : {GITHUB_REPO}"
)

print(
    f"✅ GitHub Branch : {GITHUB_BRANCH}"
)


# ============================================================
# MCP CLIENT
# ============================================================

async def create_git_mcp_client():

    print(
        "\n🔌 Connexion au serveur GitHub MCP..."
    )

    git_config = {

        "transport":
            "streamable_http",

        "url":
            GIT_MCP_URL,

        "headers": {

            "Authorization":
                f"Bearer {GITHUB_PERSONAL_ACCESS_TOKEN}"

        }

    }

    mcp_client = MultiServerMCPClient({

        "github":
            git_config

    })

    print(
        "✅ Client GitHub MCP créé"
    )

    return mcp_client


# ============================================================
# GET MCP TOOLS
# ============================================================

async def get_git_mcp_tools(
    mcp_client
):

    print(
        "\n🔧 Récupération des Tools GitHub MCP..."
    )

    try:

        tools = await mcp_client.get_tools()

    except Exception as e:

        raise RuntimeError(
            f"""
❌ Impossible de récupérer
les Tools GitHub MCP.

Erreur :

{e}
"""
        )


    if not tools:

        raise RuntimeError(
            "❌ Aucun Tool GitHub MCP disponible."
        )


    print(
        "\n🔧 Tools GitHub MCP disponibles :"
    )


    for tool in tools:

        print(
            f"   → {tool.name}"
        )


    print(
        f"\n✅ {len(tools)} Tool(s) GitHub MCP récupéré(s)."
    )


    return tools


# ============================================================
# GITHUB DEPLOY AGENT
# ============================================================

async def git_deploy_agent(
    state: AgentState
) -> dict:

    print(
        "\n"
        + "=" * 60
    )

    print(
        "🚀 GITHUB DEPLOY AI AGENT"
    )

    print(
        "=" * 60
    )


    # ========================================================
    # STATE
    # ========================================================

    issue_key = state.get(
        "issue_key",
        ""
    )

    opencode_result = state.get(
        "opencode_result",
        ""
    )

    coding_instruction = state.get(
        "coding_instruction",
        ""
    )


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
        f"Ticket     : {issue_key}"
    )

    print(
        f"Repository : {GITHUB_REPOSITORY}"
    )

    print(
        f"Branch     : {GITHUB_BRANCH}"
    )


    # ========================================================
    # MCP CLIENT
    # ========================================================

    mcp_client = await (
        create_git_mcp_client()
    )


    # ========================================================
    # MCP TOOLS
    # ========================================================

    mcp_tools = await (
        get_git_mcp_tools(
            mcp_client
        )
    )


    # ========================================================
    # TOOL CHECK
    # ========================================================

    available_tool_names = {

        tool.name
        for tool in mcp_tools

    }


    print(
        "\n🔎 Vérification des Tools nécessaires..."
    )


    if "push_files" in available_tool_names:

        print(
            "   ✅ push_files disponible"
        )

    else:

        print(
            "   ⚠️ push_files indisponible"
        )


    if "get_file_contents" in available_tool_names:

        print(
            "   ✅ get_file_contents disponible"
        )

    else:

        print(
            "   ⚠️ get_file_contents indisponible"
        )


    # ========================================================
    # LLM + MCP TOOLS
    # ========================================================

    print(
        "\n🧠 Connexion des Tools au LLM..."
    )


    llm_with_tools = llm.bind_tools(
        mcp_tools
    )


    print(
        "✅ Ollama connecté aux Tools MCP"
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
            "🤖 GITHUB AI AGENT NODE"
        )

        print(
            "-" * 60
        )


        messages = state.get(
            "messages",
            []
        )


        if not messages:

            raise ValueError(
                "❌ Aucun message dans AgentState."
            )


        response = (
            llm_with_tools.invoke(
                messages
            )
        )


        # ----------------------------------------------------
        # TOOL CALL DEBUG
        # ----------------------------------------------------

        if response.tool_calls:

            print(
                f"\n🔧 {len(response.tool_calls)} Tool(s) demandé(s)"
            )


            for tool_call in response.tool_calls:

                print(
                    f"   Tool : {tool_call['name']}"
                )

                print(
                    f"   Args : {tool_call['args']}"
                )

        else:

            print(
                "\n💬 Le LLM répond directement."
            )


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
    # ROUTER
    # ========================================================

    def should_continue(
        state: AgentState
    ):

        messages = state.get(
            "messages",
            []
        )


        if not messages:

            return END


        last_message = messages[-1]


        if getattr(
            last_message,
            "tool_calls",
            None
        ):

            return "use_tool"


        return END


    # ========================================================
    # LANGGRAPH
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


    github_graph = graph.compile()


    print(
        "\n✅ LangGraph GitHub compilé"
    )


    # ========================================================
    # SYSTEM MESSAGE
    # ========================================================

    system_message = SystemMessage(

        content=f"""

Tu es un AI Agent spécialisé dans
la publication de projets sur GitHub.

Tu disposes de Tools GitHub MCP.

==================================================
REPOSITORY
==================================================

Owner :

{GITHUB_OWNER}

Repository :

{GITHUB_REPO}

Branch :

{GITHUB_BRANCH}

==================================================
TICKET
==================================================

{issue_key}

==================================================
MISSION
==================================================

Tu dois publier sur GitHub le travail
réalisé par OpenCode.

Tu dois utiliser exclusivement les
Tools GitHub MCP disponibles.

==================================================
IMPORTANT
==================================================

Les Tools GitHub MCP manipulent
directement GitHub.

Ils ne donnent pas nécessairement accès
au filesystem local du projet.

Tu ne dois donc jamais prétendre avoir
inspecté les fichiers locaux si tu ne les
as pas réellement reçus.

==================================================
OPERATIONS
==================================================

1. Vérifier le repository.

2. Vérifier les fichiers ou informations
   accessibles avec les Tools MCP.

3. Déterminer les opérations nécessaires.

4. Si les fichiers à publier sont disponibles,
   utiliser le Tool approprié.

5. Pour plusieurs fichiers, privilégier
   push_files lorsqu'il est disponible.

6. Créer un commit professionnel.

7. Publier réellement les changements.

8. Retourner uniquement les opérations
   réellement effectuées.

==================================================
REGLES DE SECURITE
==================================================

- Ne jamais inventer une opération.

- Ne jamais prétendre avoir effectué
  un push sans Tool MCP.

- Ne jamais prétendre avoir effectué
  un commit sans Tool MCP.

- Ne jamais révéler de token.

- Ne jamais travailler sur un autre repository.

- Ne jamais travailler sur une autre branch.

==================================================
RESULTAT OPENCODE
==================================================

{opencode_result}

==================================================
INSTRUCTION
==================================================

{coding_instruction}

"""

    )


    # ========================================================
    # HUMAN MESSAGE
    # ========================================================

    human_message = HumanMessage(

        content=f"""

Publie le résultat du travail OpenCode
sur GitHub.

Ticket :

{issue_key}

Repository :

{GITHUB_OWNER}/{GITHUB_REPO}

Branch :

{GITHUB_BRANCH}

Utilise les Tools GitHub MCP.

Effectue uniquement les opérations
que tu peux réellement effectuer.

À la fin, retourne :

- les Tools utilisés
- les opérations effectuées
- le commit créé
- le résultat du push
- les éventuelles erreurs

Ne simule aucune opération.

"""

    )


    # ========================================================
    # INITIAL STATE
    # ========================================================

    initial_state = {

        "messages": [

            system_message,

            human_message

        ],

        "issue_key":
            issue_key,

        "opencode_result":
            opencode_result,

        "coding_instruction":
            coding_instruction,

        "git_repo":
            GITHUB_REPOSITORY,

        "git_branch":
            GITHUB_BRANCH,

    }


    # ========================================================
    # EXECUTION
    # ========================================================

    print(
        "\n🚀 Exécution du GitHub AI Agent..."
    )


    try:

        result = await (
            github_graph.ainvoke(
                initial_state
            )
        )

    except Exception as e:

        print(
            f"\n❌ Erreur GitHub Agent : {e}"
        )

        return {

            "git_repo":
                GITHUB_REPOSITORY,

            "git_branch":
                GITHUB_BRANCH,

            "git_push_result":
                str(e),

            "git_return_code":
                1,

            "error":
                str(e),

        }


    # ========================================================
    # RESULT
    # ========================================================

    messages = result.get(
        "messages",
        []
    )


    if not messages:

        git_result = (
            "Aucune réponse du GitHub AI Agent."
        )

        return_code = 1

    else:

        last_message = messages[-1]

        git_result = getattr(
            last_message,
            "content",
            ""
        )

        return_code = 0


    # ========================================================
    # RETURN
    # ========================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "✅ GITHUB DEPLOY AGENT TERMINÉ"
    )

    print(
        "=" * 60
    )


    print(
        git_result
    )


    return {

        "git_repo":
            GITHUB_REPOSITORY,

        "git_branch":
            GITHUB_BRANCH,

        "git_push_result":
            git_result,

        "git_return_code":
            return_code,

    }