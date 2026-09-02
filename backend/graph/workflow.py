# ============================================================
# graph/workflow.py
#
# LANGGRAPH WORKFLOWS
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from graph.state import AgentState


# ============================================================
# AGENTS
# ============================================================

from agents.git_agent import git_agent

from agents.jira_agent_vf import (
    jira_agent_vf
)

from agents.analysis_agent import (
    analysis_agent
)

from agents.prompt_agent import (
    prompt_agent
)

from agents.git_deploy_agent import (
    git_deploy_agent
)

from agents.opencode_agent import (
    opencode_agent
)


# ============================================================
# WORKFLOW A
#
# GIT PREPARATION
# ============================================================

def build_git_prepare_graph():
    """
    ========================================================
    WORKFLOW A — GIT PREPARATION
    ========================================================

        GitHub URL
             ↓
        GIT AGENT
             ↓
        git clone
             ↓
        dossier local
             ↓
        git status
             ↓
           .git ?
          /      \
        OUI      NON
         ↓        ↓
      continuer  ERROR
         ↓
      git fetch
         ↓
    detect main/master
         ↓
    switch main/master
         ↓
       git pull
         ↓
    issue branch
         ↓
    git_ready=True
         ↓
        END

    ========================================================

    Le Workflow A délègue tout le travail
    Git au Git Agent.

    Le Workflow A ne fait PAS :

        ❌ OpenCode
        ❌ git init
        ❌ git add
        ❌ git commit
        ❌ git push
        ❌ Pull Request
    """

    graph = StateGraph(
        AgentState
    )

    # ========================================================
    # NODE
    # ========================================================

    graph.add_node(
        "git_agent",
        git_agent
    )

    # ========================================================
    # EDGES
    # ========================================================

    graph.add_edge(
        START,
        "git_agent"
    )

    graph.add_edge(
        "git_agent",
        END
    )

    # ========================================================
    # COMPILE
    # ========================================================

    return graph.compile()


# ============================================================
# WORKFLOW B
#
# JIRA → ANALYSIS → PROMPT
# ============================================================

def build_prompt_graph():
    """
    ========================================================
    WORKFLOW B
    ========================================================

        START
          ↓
        Jira Agent
          ↓
        Analysis Agent
          ↓
        Prompt Agent
          ↓
        END
    """

    graph = StateGraph(
        AgentState
    )

    # ========================================================
    # NODES
    # ========================================================

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

    # ========================================================
    # EDGES
    # ========================================================

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

    # ========================================================
    # COMPILE
    # ========================================================

    return graph.compile()


# ============================================================
# WORKFLOW C
#
# GIT DEPLOY
# ============================================================

def build_git_deploy_graph():
    """
    ========================================================
    WORKFLOW C
    ========================================================

        START
          ↓
    Git Deploy Agent
          ↓
       git status
          ↓
       git add .
          ↓
       git commit
          ↓
       git push
          ↓
     Pull Request
          ↓
         END

    ========================================================

    Ce workflow est totalement séparé
    du Git Preparation Agent.
    """

    graph = StateGraph(
        AgentState
    )

    # ========================================================
    # NODE
    # ========================================================

    graph.add_node(
        "git_deploy_agent",
        git_deploy_agent
    )

    # ========================================================
    # EDGES
    # ========================================================

    graph.add_edge(
        START,
        "git_deploy_agent"
    )

    graph.add_edge(
        "git_deploy_agent",
        END
    )

    # ========================================================
    # COMPILE
    # ========================================================

    return graph.compile()


# ============================================================
# WORKFLOW D
#
# OPENCODE
# ============================================================

def build_opencode_graph():
    """
    ========================================================
    WORKFLOW D
    ========================================================

        START
          ↓
    OpenCode Agent
          ↓
        END

    Le repository doit avoir été
    préparé par Workflow A.
    """

    graph = StateGraph(
        AgentState
    )

    # ========================================================
    # NODE
    # ========================================================

    graph.add_node(
        "opencode_agent",
        opencode_agent
    )

    # ========================================================
    # EDGES
    # ========================================================

    graph.add_edge(
        START,
        "opencode_agent"
    )

    graph.add_edge(
        "opencode_agent",
        END
    )

    # ========================================================
    # COMPILE
    # ========================================================

    return graph.compile()


# ============================================================
# END OF FILE
# ============================================================