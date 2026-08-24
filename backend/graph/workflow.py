from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from graph.state import AgentState

from agents.jira_agent_vf import jira_agent_vf
from agents.analysis_agent import analysis_agent
from agents.prompt_agent import prompt_agent
from agents.opencode_agent import opencode_agent
from agents.git_agent import git_deploy_agent

# ============================================================
# WORKFLOW 1 : JIRA → ANALYSIS → PROMPT
# ============================================================

def build_prompt_graph():

    graph = StateGraph(AgentState)

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    graph.add_node(
    "jira_agent_vf",
    jira_agent_vf
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
        "jira_agent_vf"
    )

    graph.add_edge(
        "jira_agent_vf",
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









# ============================================================
# WORKFLOW 3
# GIT DEPLOYMENT
# ============================================================
#
# OpenCode → Git Deploy Agent
#
# Le Git Deploy Agent sera responsable de :
#
#   1. Vérifier le projet
#   2. Préparer les fichiers
#   3. Vérifier Git
#   4. Préparer le commit
#   5. Utiliser le MCP Client Git
#   6. Communiquer avec le MCP Server Git
#   7. Effectuer le push/deploiement
#
# ============================================================

def build_git_deploy_graph():

    graph = StateGraph(AgentState)

    # --------------------------------------------------------
    # NODE
    # --------------------------------------------------------

    graph.add_node(
        "git_deploy_agent",
        git_deploy_agent
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "git_deploy_agent"
    )

    graph.add_edge(
        "git_deploy_agent",
        END
    )

    # --------------------------------------------------------
    # COMPILE
    # --------------------------------------------------------

    return graph.compile()