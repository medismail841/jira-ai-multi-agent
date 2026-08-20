import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from graph.state import AgentState


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(override=True)


# ============================================================
# OLLAMA
# ============================================================

OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY"
)


if not OLLAMA_API_KEY:

    raise ValueError(
        "❌ OLLAMA_API_KEY n'est pas défini."
    )


llm = ChatOllama(

    model="gemma4:31b-cloud",

    base_url="https://ollama.com",

    client_kwargs={

        "headers": {

            "Authorization":
                f"Bearer {OLLAMA_API_KEY}"

        }

    },

    temperature=0,

)


# ============================================================
# ANALYSIS AGENT
# ============================================================

def analysis_agent(
    state: AgentState
) -> AgentState:

    """
    LangGraph Node 2.

    Ticket Jira
         ↓
    Ollama / Gemma
         ↓
    Technical analysis
    """

    ticket = state.get(
        "ticket"
    )


    if not ticket:

        raise ValueError(
            "❌ Aucun ticket dans le State."
        )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "🧠 AGENT 2 — ANALYSIS"
    )

    print(
        "=" * 60
    )


    prompt = f"""

You are a senior software engineer.

Analyze the Jira ticket below.

Your ONLY responsibility is to understand
the technical requirements.

Do NOT implement anything.

Do NOT generate a coding prompt.

Do NOT modify files.

==================================================
JIRA TICKET
==================================================

Key:
{ticket.get("key")}

Summary:
{ticket.get("summary")}

Description:
{ticket.get("description")}

Issue Type:
{ticket.get("issue_type")}

Priority:
{ticket.get("priority")}

Status:
{ticket.get("status")}

Project:
{ticket.get("project")}

==================================================
ANALYSIS REQUIRED
==================================================

Provide:

1. Problem to solve
2. Expected behavior
3. Technical requirements
4. Frontend impact
5. Backend impact
6. Database impact
7. Existing functionality that should be reused
8. Acceptance criteria
9. Potential risks

Do not write implementation code.

"""


    try:

        response = llm.invoke(
            prompt
        )

    except Exception as e:

        raise RuntimeError(
            f"❌ Erreur Ollama pendant "
            f"l'analyse : {e}"
        )


    analysis = str(
        response.content
    ).strip()


    if not analysis:

        raise RuntimeError(
            "❌ Ollama n'a retourné aucune analyse."
        )


    print(
        "\n✅ Analyse générée."
    )


    print(
        "\n"
        + "-" * 60
    )

    print(
        analysis
    )

    print(
        "-" * 60
    )


    return {

        "analysis":
            analysis

    }