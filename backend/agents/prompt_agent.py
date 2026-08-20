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
        "❌ OLLAMA_API_KEY manquante."
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
# LOAD SKILL
# ============================================================

def load_skill() -> str:

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


    skill_path = os.path.join(

        base_dir,

        "skills",

        "jira_to_prompt",

        "skill.md"

    )


    if not os.path.isfile(
        skill_path
    ):

        raise FileNotFoundError(
            f"""
❌ Skill introuvable :

{skill_path}
"""
        )


    with open(

        skill_path,

        "r",

        encoding="utf-8"

    ) as file:

        return file.read()


# ============================================================
# PROMPT AGENT
# ============================================================

def prompt_agent(
    state: AgentState
) -> AgentState:

    """
    LangGraph Node 3.

    Ticket
       +
    Analysis
       +
    Skill
       ↓
    Ollama
       ↓
    Coding instruction
    """

    ticket = state.get(
        "ticket"
    )


    analysis = state.get(
        "analysis"
    )


    if not ticket:

        raise ValueError(
            "❌ Ticket manquant."
        )


    if not analysis:

        raise ValueError(
            "❌ Analyse manquante."
        )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "📝 AGENT 3 — PROMPT"
    )

    print(
        "=" * 60
    )


    skill = load_skill()


    prompt = f"""

You are an expert software engineer.

Your job is to transform the Jira ticket
and its technical analysis into a DIRECT
EXECUTION INSTRUCTION for OpenCode.

The instruction will be given directly
to OpenCode.

Do NOT ask questions.

Do NOT create another prompt.

Do NOT create a PRD.

Do NOT explain prompt engineering.

Do NOT describe what a coding agent should do
at a high level.

Give concrete implementation instructions.

==================================================
JIRA TO PROMPT SKILL
==================================================

{skill}

==================================================
JIRA TICKET
==================================================

Key:
{ticket.get("key")}

Summary:
{ticket.get("summary")}

Description:
{ticket.get("description")}

==================================================
TECHNICAL ANALYSIS
==================================================

{analysis}

==================================================
OPEN CODE INSTRUCTIONS
==================================================

The instruction MUST tell OpenCode to:

1. Inspect the existing project.
2. Understand the current architecture.
3. Identify the minimum necessary changes.
4. Reuse existing components when possible.
5. Implement the Jira requirement.
6. Modify only necessary files.
7. Avoid unrelated refactoring.
8. Run relevant tests.
9. Verify the acceptance criteria.
10. Report the final changes and test results.

Start directly with the implementation instructions.

"""


    try:

        response = llm.invoke(
            prompt
        )

    except Exception as e:

        raise RuntimeError(
            f"❌ Erreur Ollama pendant "
            f"la génération du prompt : {e}"
        )


    coding_instruction = str(
        response.content
    ).strip()


    if not coding_instruction:

        raise RuntimeError(
            "❌ Aucune coding instruction générée."
        )


    print(
        "\n✅ Coding instruction générée."
    )


    return {

        "coding_instruction":
            coding_instruction

    }