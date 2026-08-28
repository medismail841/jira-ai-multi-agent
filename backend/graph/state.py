from typing import TypedDict, Optional, Dict, Any, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


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
    # OPENCODE
    # ========================================================

    opencode_result: str

    opencode_return_code: Optional[int]

    # ========================================================
    # PROJECT
    # ========================================================

    # Dossier du projet sur lequel OpenCode travaille
    project_dir: str

    # Fichiers collectés dans le projet
    project_files: Dict[str, Any]

    # ========================================================
    # LOCAL GIT
    # ========================================================

    # --------------------------------------------------------
    # .git
    # --------------------------------------------------------

    # Est-ce que le dossier contient un dossier .git ?
    git_exists: bool

    # Le dossier local est-il vide ?
    local_is_empty: bool

    # Indique si le projet local est déjà un repository Git
    local_repo_exists: bool

    # --------------------------------------------------------
    # Git status
    # --------------------------------------------------------

    # Résultat de la commande git status
    git_status: str

    # Branche Git locale actuelle
    git_current_branch: str

    # --------------------------------------------------------
    # Remote local
    # --------------------------------------------------------

    # URL du remote Git local
    git_remote_url: Optional[str]

    # Est-ce qu'un remote est configuré ?
    git_has_remote: bool

    # ========================================================
    # GITHUB REMOTE
    # ========================================================

    # --------------------------------------------------------
    # Repository
    # --------------------------------------------------------

    # Est-ce que le repository existe sur GitHub ?
    github_repo_exists: bool

    # Owner GitHub
    github_owner: str

    # Nom du repository GitHub
    github_repository: str

    # Branche GitHub utilisée pour l'inspection
    github_branch: str

    # Branche principale du repository GitHub
    github_default_branch: str

    # --------------------------------------------------------
    # Repository content
    # --------------------------------------------------------

    # Est-ce que le repository GitHub est vide ?
    github_remote_is_empty: bool

    # Est-ce que le repository GitHub contient des fichiers ?
    github_remote_is_full: bool

    # Contenu retourné par get_file_contents
    github_contents: Any

    # Nombre de fichiers présents sur GitHub
    github_remote_files_count: int

    # Ancien nom conservé pour compatibilité éventuelle
    #
    # Attention :
    # Le Git Router utilise maintenant
    # github_remote_is_empty.
    #
    github_repo_empty: bool

    # ========================================================
    # GIT DECISION
    # ========================================================

    # Décision prise par le Git Router
    #
    # Exemples :
    #
    # init
    # clone
    # error
    # pull_request
    #
    git_action: str

    # Explication de la décision
    git_action_reason: str

    # ========================================================
    # GIT OPERATION RESULT
    # ========================================================

    # Nom de la nouvelle branche créée
    git_branch_name: Optional[str]

    # Message du commit
    git_commit_message: Optional[str]

    # Résultat du push
    git_push_result: Optional[str]

    # ========================================================
    # PULL REQUEST
    # ========================================================

    # Numéro de la Pull Request
    pull_request_number: Optional[int]

    # URL de la Pull Request
    pull_request_url: Optional[str]

    # ========================================================
    # ERROR
    # ========================================================

    # Message d'erreur général
    error: Optional[str]