import os

from IPython.display import Image, display

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from graph.state import AgentState

from agents.jira_agent_vf import (
    jira_agent_vf,
    create_mcp_client,
    get_mcp_tools,
    create_subtasks,
)

from agents.analysis_agent import (
    analysis_agent,
    classify_ticket,
    decompose_ticket,
)

from agents.prompt_agent import prompt_agent
from agents.opencode_agent import opencode_agent


# ============================================================
# CONFIGURATION
# ============================================================

AUTO_SPLIT_COMPLEX_TICKETS = os.getenv(
    "AUTO_SPLIT_COMPLEX_TICKETS",
    "true",
).lower() == "true"


# ============================================================
# NODE : CLASSIFICATION DU TICKET
# ============================================================

def classify_ticket_node(state: AgentState) -> AgentState:

    if not AUTO_SPLIT_COMPLEX_TICKETS:
        print(
            "📊 Automatic ticket splitting is disabled; "
            "treating ticket as SIMPLE"
        )

        return {
            "complexity": "SIMPLE"
        }

    ticket = state["ticket"]

    content = (
        f"{ticket.get('summary', '')}\n"
        f"{ticket.get('description', '')}"
    )

    print(
        f"📊 Classifying ticket "
        f"{ticket.get('key', 'UNKNOWN')}"
    )

    return {
        "complexity": classify_ticket(content)
    }


# ============================================================
# NODE : SPLIT DU TICKET COMPLEXE
# ============================================================

async def split_ticket_node(state: AgentState) -> AgentState:

    ticket = state["ticket"]

    content = (
        f"{ticket.get('summary', '')}\n"
        f"{ticket.get('description', '')}"
    )

    print(
        f"🧩 Split route selected for ticket "
        f"{ticket.get('key', 'UNKNOWN')}"
    )

    # --------------------------------------------------------
    # DECOMPOSE TICKET
    # --------------------------------------------------------

    drafts = decompose_ticket(content)

    print(
        f"🧩 Decomposition returned "
        f"{len(drafts)} drafts"
    )

    # --------------------------------------------------------
    # CREATE MCP CLIENT
    # --------------------------------------------------------

    mcp_client = await create_mcp_client()

    # --------------------------------------------------------
    # GET MCP TOOLS
    # --------------------------------------------------------

    mcp_tools = await get_mcp_tools(mcp_client)

    print(
        f"🔧 MCP tools available for split: "
        f"{[tool.name for tool in mcp_tools]}"
    )

    # --------------------------------------------------------
    # FIND CREATE JIRA ISSUE TOOL
    # --------------------------------------------------------

    create_tool = next(
        (
            tool
            for tool in mcp_tools
            if tool.name in (
                "createJiraIssue",
                "create_issue",
            )
        ),
        None,
    )

    if create_tool is not None:

        print(
            f"🔧 Create tool schema: "
            f"{getattr(create_tool, 'args_schema', 'unavailable')}"
        )

    # --------------------------------------------------------
    # CREATE SUBTASKS
    # --------------------------------------------------------

    created_ids = await create_subtasks(
        mcp_tools,
        ticket["key"],
        drafts,
    )

    print(
        f"✅ Parent ticket preserved: "
        f"{ticket['key']}; "
        f"child tickets: {created_ids}"
    )

    # --------------------------------------------------------
    # RETURN SUBTASKS
    # --------------------------------------------------------

    return {
        "subtasks": [
            {
                **draft,
                "key": key,
            }
            for draft, key in zip(drafts, created_ids)
        ]
    }


# ============================================================
# ROUTER : COMPLEXITY
# ============================================================

def route_complexity(state: AgentState) -> str:

    if state.get("complexity") == "COMPLEX":
        return "split"

    return "prompt"


# ============================================================
# WORKFLOW 1
#
# JIRA → ANALYSIS → CLASSIFICATION
#                   ↓
#              ┌────┴────┐
#              ↓         ↓
#           SIMPLE    COMPLEX
#              ↓         ↓
#           PROMPT      SPLIT
#
# ============================================================

def build_prompt_graph():

    graph = StateGraph(AgentState)

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    graph.add_node(
        "jira_agent_vf",
        jira_agent_vf,
    )

    graph.add_node(
        "analysis_agent",
        analysis_agent,
    )

    graph.add_node(
        "classify_ticket",
        classify_ticket_node,
    )

    graph.add_node(
        "split_ticket",
        split_ticket_node,
    )

    graph.add_node(
        "prompt_agent",
        prompt_agent,
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "jira_agent_vf",
    )

    graph.add_edge(
        "jira_agent_vf",
        "analysis_agent",
    )

    graph.add_edge(
        "analysis_agent",
        "classify_ticket",
    )

    # --------------------------------------------------------
    # CONDITIONAL EDGE
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "classify_ticket",
        route_complexity,
        {
            "prompt": "prompt_agent",
            "split": "split_ticket",
        },
    )

    # --------------------------------------------------------
    # END
    # --------------------------------------------------------

    graph.add_edge(
        "split_ticket",
        END,
    )

    graph.add_edge(
        "prompt_agent",
        END,
    )

    # --------------------------------------------------------
    # COMPILE
    # --------------------------------------------------------

    workflow = graph.compile()

    # --------------------------------------------------------
    # DISPLAY GRAPH
    # --------------------------------------------------------

    display(
        Image(
            workflow.get_graph().draw_mermaid_png()
        )
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return workflow


# ============================================================
# WORKFLOW 2
#
# START → OPENCODE → END
#
# ============================================================

def build_opencode_graph():

    graph = StateGraph(AgentState)

    # --------------------------------------------------------
    # NODE
    # --------------------------------------------------------

    graph.add_node(
        "opencode_agent",
        opencode_agent,
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "opencode_agent",
    )

    graph.add_edge(
        "opencode_agent",
        END,
    )

    # --------------------------------------------------------
    # COMPILE
    # --------------------------------------------------------

    workflow = graph.compile()

    # --------------------------------------------------------
    # DISPLAY GRAPH
    # --------------------------------------------------------

    display(
        Image(
            workflow.get_graph().draw_mermaid_png()
        )
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return workflow