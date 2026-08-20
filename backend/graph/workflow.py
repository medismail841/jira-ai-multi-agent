from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from graph.state import AgentState

from agents.jira_agent import jira_agent
from agents.analysis_agent import analysis_agent
from agents.prompt_agent import prompt_agent
from agents.opencode_agent import opencode_agent


# ============================================================
# WORKFLOW 1 : JIRA → ANALYSIS → PROMPT
# ============================================================

def build_prompt_graph():

    graph = StateGraph(AgentState)

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    graph.add_node(
        "jira_agent",
        jira_agent
    )

    graph.add_node(
        "analysis_agent",
        analysis_agent
    )

    graph.add_node(
        "prompt_agent",
        prompt_agent
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "jira_agent"
    )

    graph.add_edge(
        "jira_agent",
        "analysis_agent"
    )

    graph.add_edge(
        "analysis_agent",
        "prompt_agent"
    )

    graph.add_edge(
        "prompt_agent",
        END
    )

    # --------------------------------------------------------
    # COMPILE
    # --------------------------------------------------------

    return graph.compile()


# ============================================================
# WORKFLOW 2 : OPENCODE
# ============================================================

def build_opencode_graph():

    graph = StateGraph(AgentState)

    # --------------------------------------------------------
    # NODE
    # --------------------------------------------------------

    graph.add_node(
        "opencode_agent",
        opencode_agent
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "opencode_agent"
    )

    graph.add_edge(
        "opencode_agent",
        END
    )

    # --------------------------------------------------------
    # COMPILE
    # --------------------------------------------------------

    return graph.compile()