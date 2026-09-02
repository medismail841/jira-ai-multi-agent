# ============================================================
# graph/state.py
#
# SHARED AGENT STATE
# ============================================================

from typing import (
    TypedDict,
    Optional,
    Dict,
    Any,
    Annotated,
)

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


# ============================================================
# AGENT STATE
# ============================================================

class AgentState(TypedDict, total=False):

    # ========================================================
    # USER
    # ========================================================

    user_request: str


    # ========================================================
    # MESSAGES / LLM
    # ========================================================

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]


    # ========================================================
    # JIRA
    # ========================================================

    issue_key: str

    ticket: Dict[str, Any]


    # ========================================================
    # ANALYSIS
    # ========================================================

    analysis: str


    # ========================================================
    # PROMPT
    # ========================================================

    coding_instruction: str

    prompt_file: str


    # ========================================================
    # GITHUB
    # ========================================================

    github_url: Optional[str]

    repository_url: Optional[str]


    # ========================================================
    # LOCAL PROJECT
    # ========================================================

    project_dir: Optional[str]


    # ========================================================
    # GIT PREPARATION
    # ========================================================

    # Résultat de git status
    git_status: str

    # Branche finale
    git_branch: str

    # Branche principale détectée :
    # main ou master
    git_base_branch: str

    # True si la branche ISSUE vient d'être créée
    # False si elle existait déjà
    git_branch_created: bool

    # True lorsque le repository est prêt
    git_ready: bool

    # Erreur Git
    git_error: Optional[str]


    # ========================================================
    # OPENCODE
    # ========================================================

    opencode_result: Optional[str]

    opencode_return_code: Optional[int]


    # ========================================================
    # GIT DEPLOY
    # ========================================================

    git_deploy_success: bool

    git_deploy_skipped: bool

    git_deploy_error: Optional[str]

    commit_message: Optional[str]

    commit_success: bool

    push_success: bool

    pull_request_url: Optional[str]


    # ========================================================
    # GENERAL ERROR
    # ========================================================

    error: Optional[str]