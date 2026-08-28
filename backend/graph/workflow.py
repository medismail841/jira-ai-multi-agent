# ============================================================
# WORKFLOW.PY
#
# Architecture :
#
# WORKFLOW 1
# JIRA → ANALYSIS → PROMPT
#
# WORKFLOW 2
# OPENCODE
#
# WORKFLOW 3
# GIT AGENT
#
# GIT :
# inspect local
#      ↓
# inspect GitHub
#      ↓
# decide action
#      ↓
# create branch
#      ↓
# git add
#      ↓
# git commit
#      ↓
# git push
#      ↓
# create Pull Request
#
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from graph.state import AgentState


# ============================================================
# JIRA / ANALYSIS / PROMPT
# ============================================================

from agents.jira_agent_vf import jira_agent_vf
from agents.analysis_agent import analysis_agent
from agents.prompt_agent import prompt_agent


# ============================================================
# OPENCODE
# ============================================================

from agents.opencode_agent import opencode_agent


# ============================================================
# GIT AGENT
# ============================================================

from agents.git_agent import (
    inspect_local_repository,
    inspect_github_repository,
    decide_git_action,
    git_init,
    create_git_branch,
    git_add_files,
    git_commit,
    git_push,
    create_pull_request,
)


# ============================================================
# WORKFLOW 1
#
# JIRA → ANALYSIS → PROMPT
# ============================================================

def build_prompt_graph():

    graph = StateGraph(AgentState)

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
# WORKFLOW 2
#
# OPENCODE
# ============================================================
#
# Ce workflow est indépendant.
# OpenCode travaille sur le projet LOCAL.
# Il peut créer/modifier des fichiers.
#
# ============================================================

def build_opencode_graph():

    graph = StateGraph(AgentState)

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
# WORKFLOW 3
#
# GIT AGENT
# ============================================================
#
# Architecture :
#
# inspect_local_repository
#          ↓
# inspect_github_repository
#          ↓
# decide_git_action
#          ↓
#       ROUTER
#          │
#          ├── init → git_init → END
#          │
#          ├── error → END
#          │
#          └── pull_request
#                    ↓
#              create_git_branch
#                    ↓
#                git_add_files
#                    ↓
#                 git_commit
#                    ↓
#                  git_push
#                    ↓
#             create_pull_request
#                    ↓
#                   END
#
# ============================================================

def build_git_graph():

    graph = StateGraph(AgentState)

    # ========================================================
    # NODES
    # ========================================================

    # --------------------------------------------------------
    # STEP 1 : Inspect LOCAL repository
    # --------------------------------------------------------
    graph.add_node(
        "inspect_local_repository",
        inspect_local_repository
    )

    # --------------------------------------------------------
    # STEP 2 : Inspect GITHUB repository
    # --------------------------------------------------------
    graph.add_node(
        "inspect_github_repository",
        inspect_github_repository
    )

    # --------------------------------------------------------
    # STEP 3 : Decide Git action
    # --------------------------------------------------------
    graph.add_node(
        "decide_git_action",
        decide_git_action
    )

    # --------------------------------------------------------
    # STEP 4 : Git init
    # --------------------------------------------------------
    graph.add_node(
        "git_init",
        git_init
    )

    # --------------------------------------------------------
    # STEP 5 : Create branch
    # --------------------------------------------------------
    graph.add_node(
        "create_git_branch",
        create_git_branch
    )

    # --------------------------------------------------------
    # STEP 6 : Git add
    # --------------------------------------------------------
    graph.add_node(
        "git_add_files",
        git_add_files
    )

    # --------------------------------------------------------
    # STEP 7 : Git commit
    # --------------------------------------------------------
    graph.add_node(
        "git_commit",
        git_commit
    )

    # --------------------------------------------------------
    # STEP 8 : Git push
    # --------------------------------------------------------
    graph.add_node(
        "git_push",
        git_push
    )

    # --------------------------------------------------------
    # STEP 9 : Create Pull Request
    # --------------------------------------------------------
    graph.add_node(
        "create_pull_request",
        create_pull_request
    )

    # ========================================================
    # NORMAL EDGES — INSPECTION
    # ========================================================

    graph.add_edge(
        START,
        "inspect_local_repository"
    )

    graph.add_edge(
        "inspect_local_repository",
        "inspect_github_repository"
    )

    graph.add_edge(
        "inspect_github_repository",
        "decide_git_action"
    )

    # ========================================================
    # GIT ROUTER
    # ========================================================

    def route_git_action(state):

        action = state.get("git_action")

        print("\n" + "=" * 60)
        print("🔀 LANGGRAPH — GIT ROUTER")
        print("=" * 60)

        print(f"➡️ Action sélectionnée : {action}")

        # ----------------------------------------------------
        # CASE 1 — INIT
        # ----------------------------------------------------
        if action == "init":
            print("➡️ Direction : git_init")
            return "git_init"

        # ----------------------------------------------------
        # CASE 2 — PULL REQUEST
        # ----------------------------------------------------
        if action == "pull_request":
            print("➡️ Direction : create_git_branch")
            return "create_git_branch"

        # ----------------------------------------------------
        # CASE 3 — ERROR
        # ----------------------------------------------------
        if action == "error":
            print("❌ Direction : END")
            return "end"

        # ----------------------------------------------------
        # CASE 4 — ACTION NON IMPLÉMENTÉE
        # ----------------------------------------------------
        print(f"⚠️ Action non encore implémentée : {action}")
        return "end"

    # ========================================================
    # CONDITIONAL EDGES
    # ========================================================

    graph.add_conditional_edges(
        "decide_git_action",
        route_git_action,
        {
            "git_init": "git_init",
            "create_git_branch": "create_git_branch",
            "end": END,
        }
    )

    # ========================================================
    # INIT → END
    # ========================================================

    graph.add_edge(
        "git_init",
        END
    )

    # ========================================================
    # PULL REQUEST WORKFLOW
    # ========================================================

    graph.add_edge(
        "create_git_branch",
        "git_add_files"
    )

    graph.add_edge(
        "git_add_files",
        "git_commit"
    )

    graph.add_edge(
        "git_commit",
        "git_push"
    )

    graph.add_edge(
        "git_push",
        "create_pull_request"
    )

    graph.add_edge(
        "create_pull_request",
        END
    )

    # ========================================================
    # COMPILE
    # ========================================================

    return graph.compile()