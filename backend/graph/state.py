""" le cœur de LangGraph : le State partagé. """


from typing import TypedDict, Optional, Dict, Any



class AgentState(TypedDict, total=False):

    # ========================================================
    # USER
    # ========================================================

    user_request: str # demande originale de l'utilisateur.

    # ========================================================
    # JIRA
    # ========================================================

    issue_key: str #clé Jira/ kan-1

    ticket: Dict[str, Any] #Le contenu récupéré depuis Jira.

    # ========================================================
    # ANALYSIS
    # ========================================================

    analysis: str #le résultat de l'analyse du ticket

    # ========================================================
    # PROMPT
    # ========================================================

    coding_instruction: str #l'instruction destinée à OpenCode

    prompt_file: str

    # ========================================================
    # OPENCODE
    # ========================================================

    opencode_result: str

    opencode_return_code: Optional[int]

    # ========================================================
    # ERROR
    # ========================================================

    error: Optional[str]