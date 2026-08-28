import os
from pathlib import Path
from typing import Any
from git.local_git import (
    git_exists,
    is_directory_empty,
    git_status,
    git_current_branch,
    git_remote,
)
from langchain_mcp_adapters.client import MultiServerMCPClient

from dotenv import load_dotenv
from git.local_git import git_push as local_git_push

# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()
# ============================================================
# GITHUB MCP CONFIGURATION
# ============================================================

GITHUB_MCP_URL = os.getenv(
    "GITHUB_MCP_URL",
    "https://api.githubcopilot.com/mcp/"
)
GITHUB_OWNER = os.getenv(
    "GITHUB_OWNER"
)
GITHUB_REPOSITORY = os.getenv(
    "GITHUB_REPOSITORY"
)
GITHUB_BRANCH = os.getenv(
    "GITHUB_BRANCH",
    "main"
)
GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv(
    "GITHUB_PERSONAL_ACCESS_TOKEN"
)


# ============================================================
# GITHUB MCP CLIENT
# ============================================================

def create_github_mcp_client():
    if not GITHUB_PERSONAL_ACCESS_TOKEN:
        raise RuntimeError(
            "❌ GITHUB_PERSONAL_ACCESS_TOKEN manquant."
        )

    return MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": GITHUB_MCP_URL,
                "headers": {
                    "Authorization":
                        f"Bearer {GITHUB_PERSONAL_ACCESS_TOKEN}"
                },
            }
        }
    )


# ============================================================
# STEP 1 — INSPECT LOCAL REPOSITORY
# ============================================================

def inspect_local_repository(state):
    """
    Inspecte le projet local avant toute opération Git.
    Vérifie :
    1. Le dossier existe
    2. Le dossier est vide ou non
    3. Le dossier contient .git ou non
    4. Si .git existe :
       - git status
       - branche actuelle
       - remote
    """

    # ========================================================
    # PROJECT DIRECTORY
    # ========================================================

    project_dir = state.get("project_dir")

    if not project_dir:
        return {
            "error": "❌ PROJECT_DIR manquant."
        }

    # ========================================================
    # CHECK DIRECTORY
    # ========================================================

    path = Path(project_dir)

    if not path.exists():
        return {
            "error": f"❌ Le dossier n'existe pas : {project_dir}"
        }

    if not path.is_dir():
        return {
            "error": f"❌ Le chemin n'est pas un dossier : {project_dir}"
        }

    # ========================================================
    # LOCAL DIRECTORY
    # ========================================================

    local_empty = is_directory_empty(project_dir)

    # ========================================================
    # .GIT
    # ========================================================

    has_git = git_exists(project_dir)

    # ========================================================
    # RESULT
    # ========================================================

    result = {
        "project_dir": project_dir,
        "git_exists": has_git,
        "local_is_empty": local_empty,
        "local_repo_exists": has_git,
    }

    # ========================================================
    # IF GIT EXISTS
    # ========================================================

    if has_git:
        result["git_status"] = git_status(project_dir)
        result["git_current_branch"] = git_current_branch(project_dir)

        remote = git_remote(project_dir)
        result["git_has_remote"] = bool(remote)
        result["git_remote_url"] = remote
    else:
        result["git_status"] = ""
        result["git_current_branch"] = ""
        result["git_has_remote"] = False
        result["git_remote_url"] = None

    # ========================================================
    # LOG
    # ========================================================

    print("\n" + "=" * 60)
    print("🔎 GIT AGENT — LOCAL INSPECTION")
    print("=" * 60)
    print(f"📁 Project : {project_dir}")
    print(f"📦 .git : {'OUI' if has_git else 'NON'}")
    print(f"📄 Dossier vide : {'OUI' if local_empty else 'NON'}")

    if has_git:
        print(f"🌿 Branche : {result['git_current_branch']}")
        print(f"🔗 Remote : {'OUI' if result['git_has_remote'] else 'NON'}")

        if result["git_status"]:
            print("\n📝 Git status :")
            print(result["git_status"])
        else:
            print("\n✅ Aucun changement détecté.")

    print("=" * 60)

    return result


# ============================================================
# STEP 2 — INSPECT GITHUB MCP
# ============================================================
async def inspect_github_repository(state):
    """
    Inspecte le repository GitHub via GitHub MCP.

    ```
    Cette étape est strictement READ-ONLY.

    Elle vérifie :
    1. La connexion au GitHub MCP
    2. Le contenu de la racine du repository
    3. Si le repository distant est vide ou non

    Aucune modification GitHub n'est effectuée.
    """

    # ========================================================
    # CONFIGURATION
    # ========================================================

    if not GITHUB_OWNER:
        return {
            "error": "❌ GITHUB_OWNER manquant."
        }

    if not GITHUB_REPOSITORY:
        return {
            "error": "❌ GITHUB_REPOSITORY manquant."
        }

    print("\n" + "=" * 60)
    print("🔎 GIT AGENT — GITHUB MCP INSPECTION")
    print("=" * 60)

    print(f"👤 Owner : {GITHUB_OWNER}")
    print(f"📦 Repository : {GITHUB_REPOSITORY}")
    print(f"🌿 Branch : {GITHUB_BRANCH}")

    # ========================================================
    # CREATE MCP CLIENT
    # ========================================================

    client = create_github_mcp_client()

    try:

        # ====================================================
        # LOAD MCP TOOLS
        # ====================================================

        tools = await client.get_tools()

        print("\n🛠️ GitHub MCP tools disponibles :")

        for tool in tools:
            print(f"   • {tool.name}")

        # ====================================================
        # FIND get_file_contents
        # ====================================================

        get_file_contents_tool = None

        for tool in tools:

            if tool.name == "get_file_contents":

                get_file_contents_tool = tool
                break

        if get_file_contents_tool is None:

            return {
                "error":
                    "❌ L'outil MCP 'get_file_contents' "
                    "n'est pas disponible."
            }

        # ====================================================
        # CALL GITHUB MCP
        # ====================================================

        print("\n📡 Lecture du repository GitHub...")

        response = await get_file_contents_tool.ainvoke(
            {
                "owner": GITHUB_OWNER,
                "repo": GITHUB_REPOSITORY,
                "path": "/",
                "ref": f"refs/heads/{GITHUB_BRANCH}",
            }
        )

        # ====================================================
        # DISPLAY RESPONSE
        # ====================================================

        print("\n📦 Réponse GitHub MCP :")
        print(response)

            # ========================================================
        # DETERMINE REMOTE STATUS
        # ========================================================

        remote_empty = False

        response_text = str(response).lower()

        # --------------------------------------------------------
        # GitHub MCP indique explicitement que le repository
        # est vide.
        # --------------------------------------------------------

        if (
            "git repository is empty" in response_text
            or "repository is empty" in response_text
        ):

            remote_empty = True

        # --------------------------------------------------------
        # Réponse réellement vide
        # --------------------------------------------------------

        elif response is None:

            remote_empty = True

        elif isinstance(response, list):

            remote_empty = len(response) == 0

        elif isinstance(response, dict):

            remote_empty = len(response) == 0

        elif isinstance(response, str):

            remote_empty = not response.strip()

        # ====================================================
        # RESULT
        # ====================================================

        result = {

            "github_repo_exists": True,

            "github_owner":
                GITHUB_OWNER,

            "github_repository":
                GITHUB_REPOSITORY,

            "github_branch":
                GITHUB_BRANCH,

            "github_remote_is_empty":
                remote_empty,

            "github_remote_is_full":
                not remote_empty,

            "github_contents":
                response,
        }

        # ====================================================
        # LOG
        # ====================================================

        if remote_empty:

            print(
                "\n📭 Repository GitHub : VIDE"
            )

        else:

            print(
                "\n📦 Repository GitHub : PLEIN"
            )

        print("=" * 60)

        return result

    except Exception as e:

        print(
            f"\n❌ Erreur GitHub MCP : {e}"
        )

        return {
            "error":
                f"❌ Erreur GitHub MCP : {e}",

            "github_repo_exists":
                False
        }

    finally:

        print(
            "\n🔚 Inspection GitHub terminée."
        )












# ============================================================
# STEP 3 — GIT DECISION / ROUTER
# ============================================================

def decide_git_action(state):
    """
    Décide de l'opération Git à effectuer en fonction de :
    LOCAL :
        - .git existe ou non
        - dossier vide ou non
        - remote local existe ou non

    GITHUB :
        - repository existe ou non
        - repository vide ou plein

    Actions possibles :
        init
        init_and_push
        clone
        error
        pull_request
    """

    # ========================================================
    # READ STATE
    # ========================================================

    git_exists_value = state.get(
        "git_exists",
        False
    )

    local_is_empty = state.get(
        "local_is_empty",
        True
    )

    git_has_remote = state.get(
        "git_has_remote",
        False
    )

    github_repo_exists = state.get(
        "github_repo_exists",
        False
    )

    github_remote_is_empty = state.get(
        "github_remote_is_empty",
        False
    )

    github_remote_is_full = state.get(
        "github_remote_is_full",
        False
    )

    # ========================================================
    # LOG
    # ========================================================

    print("\n" + "=" * 60)
    print("🧠 GIT AGENT — DECISION")
    print("=" * 60)

    print(f"📄 Local vide        : {'OUI' if local_is_empty else 'NON'}")
    print(f"📦 Local .git        : {'OUI' if git_exists_value else 'NON'}")
    print(f"🔗 Remote configuré  : {'OUI' if git_has_remote else 'NON'}")
    print(f"☁️ GitHub Repo Exists: {'OUI' if github_repo_exists else 'NON'}")
    print(f"☁️ Remote vide       : {'OUI' if github_remote_is_empty else 'NON'}")
    print(f"☁️ Remote plein      : {'OUI' if github_remote_is_full else 'NON'}")

    # ========================================================
    # CASE 1 : INIT
    # Local vide, pas de .git, remote GitHub vide
    # ========================================================

    if (
        not git_exists_value
        and local_is_empty
        and github_remote_is_empty
    ):
        action = "init"
        reason = (
            "Local vide + .git absent + "
            "repository GitHub vide."
        )

        print("\n➡️ ACTION : INIT")
        print(f"💡 {reason}")
        print("=" * 60)

        return {
            "git_action": action,
            "git_action_reason": reason,
        }

    # ========================================================
    # CASE 2 : INIT_AND_PUSH
    # Local plein, pas de .git, remote GitHub vide
    # ========================================================

    if (
        not git_exists_value
        and not local_is_empty
        and github_remote_is_empty
    ):
        action = "init_and_push"
        reason = (
            "Local contient des fichiers + .git absent + "
            "repository GitHub vide. Initialisation locale et push vers remote requis."
        )

        print("\n➡️ ACTION : INIT_AND_PUSH")
        print(f"💡 {reason}")
        print("=" * 60)

        return {
            "git_action": action,
            "git_action_reason": reason,
        }

    # ========================================================
    # CASE 3 : CLONE
    # Local vide, pas de .git, remote GitHub plein
    # ========================================================

    if (
        not git_exists_value
        and local_is_empty
        and github_remote_is_full
    ):
        action = "clone"
        reason = (
            "Local vide + .git absent + "
            "repository GitHub plein. Clonnage du projet distant requis."
        )

        print("\n➡️ ACTION : CLONE")
        print(f"💡 {reason}")
        print("=" * 60)

        return {
            "git_action": action,
            "git_action_reason": reason,
        }

    # ========================================================
    # CASE 4 : CONFLIT / ERROR
    # Local plein, pas de .git, remote GitHub plein
    # ========================================================

    if (
        not git_exists_value
        and not local_is_empty
        and github_remote_is_full
    ):
        action = "error"
        reason = (
            "Le dossier local contient des fichiers non suivis "
            "et le repository distant contient déjà un projet. Conflit détecté."
        )

        print("\n❌ ACTION : ERROR")
        print(f"💡 {reason}")
        print("=" * 60)

        return {
            "git_action": action,
            "git_action_reason": reason,
            "error": reason,
        }

# ========================================================
    # CASE 5 : ERROR
    #
    # Repository Git local existe
    # MAIS aucun remote local n'est configuré
    #
    # Impossible de synchroniser avec GitHub.
    # ========================================================

    if (
        git_exists_value
        and not git_has_remote
    ):
        action = "error"
        reason = (
            "Le repository Git local existe, "
            "mais aucun remote Git n'est configuré. "
            "Impossible de synchroniser avec GitHub "
            "ou de créer une Pull Request."
        )

        print("\n❌ ACTION : ERROR")
        print(f"💡 {reason}")
        print("=" * 60)

        return {
            "git_action": action,
            "git_action_reason": reason,
            "error": reason,
        }

    # ========================================================
    # CASE 6 : PULL_REQUEST
    #
    # Repository Git local existe
    # ET remote local existe
    #
    # → Nouvelle branche
    # → Commit
    # → Push
    # → Pull Request
    # ========================================================

    if (
        git_exists_value
        and git_has_remote
    ):
        action = "pull_request"
        reason = (
            "Repository Git local déjà existant "
            "avec un remote configuré. "
            "Création d'une nouvelle branche, "
            "commit, push et Pull Request."
        )

        print("\n➡️ ACTION : PULL_REQUEST")
        print(f"💡 {reason}")
        print("=" * 60)

        return {
            "git_action": action,
            "git_action_reason": reason,
        }


  # ========================================================
    # FALLBACK / UNKNOWN
    # ========================================================

    action = "error"
    reason = "Combinaison d'état non reconnue."

    print("\n❌ ACTION : ERROR")
    print(f"💡 {reason}")
    print("=" * 60)

    return {
        "git_action": action,
        "git_action_reason": reason,
        "error": reason,
    }
    
    
    
    
    
    
    
    
    
    
    # ============================================================
# STEP 4 — GIT INIT
# ============================================================

def git_init(state):
    """
    Initialise un repository Git dans le dossier local.
    Cette fonction est exécutée uniquement lorsque
    git_action == "init".

    Opération effectuée :
        git init

    Aucune autre opération n'est réalisée ici.
    """

    import subprocess
    from git.local_git import git_exists

    # ========================================================
    # PROJECT DIRECTORY
    # ========================================================

    project_dir = state.get("project_dir")

    if not project_dir:
        return {
            "error": "❌ PROJECT_DIR manquant.",
            "git_action": "error",
        }

    # ========================================================
    # VERIFY ACTION
    # ========================================================

    git_action = state.get("git_action")

    if git_action != "init":
        return {
            "error": (
                f"❌ git_init() appelé avec une action invalide : "
                f"{git_action}"
            ),
            "git_action": "error",
        }

    # ========================================================
    # CHECK IF .GIT ALREADY EXISTS
    # ========================================================

    if git_exists(project_dir):
        print("\n⚠️ Repository Git déjà initialisé.")

        return {
            "git_exists": True,
            "error": None,
        }

    # ========================================================
    # LOG
    # ========================================================

    print("\n" + "=" * 60)
    print("🚀 GIT AGENT — GIT INIT")
    print("=" * 60)

    print(f"📁 Project : {project_dir}")
    print("⚙️ Exécution : git init")

    # ========================================================
    # EXECUTE GIT INIT
    # ========================================================

    try:
        result = subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            return {
                "error": f"❌ Erreur lors de git init : {result.stderr.strip()}",
                "git_action": "error",
            }

        print("✅ Repository Git initialisé avec succès.")
        print("=" * 60)

        return {
            "git_exists": True,
            "git_status": "",
            "git_current_branch": "main",
            "error": None,
        }

    except Exception as e:
        return {
            "error": f"❌ Exception lors de git init : {e}",
            "git_action": "error",
        }
        
        
        
# ============================================================
# GIT AGENT — CREATE BRANCH
# ============================================================

def create_git_branch(state):
    """
    Crée une nouvelle branche Git locale.

    Exemple :
        master
           ↓
        feature/KAN-1

    Cette fonction fait uniquement :
        git checkout -b <branch>

    Elle ne fait PAS :
        - git add
        - git commit
        - git push
        - Pull Request
    """

    project_dir = state.get("project_dir")

    if not project_dir:
        return {
            "error": "❌ PROJECT_DIR manquant."
        }

    # ========================================================
    # NOM DE LA BRANCHE
    # ========================================================

    issue_key = state.get("issue_key")

    if issue_key:
        branch_name = f"feature/{issue_key}"
    else:
        branch_name = "feature/git-agent"

    # ========================================================
    # LOG
    # ========================================================

    print("\n" + "=" * 60)
    print("🌿 GIT AGENT — CREATE BRANCH")
    print("=" * 60)

    print(f"📁 Project : {project_dir}")
    print(f"🌿 Nouvelle branche : {branch_name}")

    # ========================================================
    # EXECUTION
    # ========================================================

    try:

        import subprocess

        result = subprocess.run(
            [
                "git",
                "checkout",
                "-b",
                branch_name
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        # ====================================================
        # ERREUR
        # ====================================================

        if result.returncode != 0:

            error = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Erreur inconnue lors de la création de la branche."
            )

            print(f"❌ Erreur : {error}")
            print("=" * 60)

            return {
                "git_branch_name": branch_name,
                "error": error
            }

        # ====================================================
        # SUCCESS
        # ====================================================

        print("✅ Branche créée avec succès.")
        print(f"🌿 Branche actuelle : {branch_name}")
        print("=" * 60)

        return {
            "git_branch_name": branch_name,
            "git_current_branch": branch_name,
            "error": None
        }

    except Exception as e:

        print(f"❌ Exception : {e}")
        print("=" * 60)

        return {
            "git_branch_name": branch_name,
            "error": str(e)
        }
        
        
        
# ============================================================
# GIT AGENT — GIT ADD
# ============================================================

def git_add_files(state):
    """
    Ajoute tous les fichiers du projet dans la staging area.

    Équivalent à :

        git add .

    Cette fonction ne fait PAS :
        - git commit
        - git push
        - Pull Request
    """

    project_dir = state.get("project_dir")

    if not project_dir:
        return {
            "error": "❌ PROJECT_DIR manquant."
        }

    print("\n" + "=" * 60)
    print("📦 GIT AGENT — GIT ADD")
    print("=" * 60)

    print(f"📁 Project : {project_dir}")
    print("⚙️ Exécution : git add .")

    try:

        import subprocess

        result = subprocess.run(
            [
                "git",
                "add",
                "."
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:

            error = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Erreur inconnue lors de git add."
            )

            print(f"❌ Erreur : {error}")
            print("=" * 60)

            return {
                "error": error
            }

        print("✅ Fichiers ajoutés à la staging area.")
        print("=" * 60)

        return {
            "error": None
        }

    except Exception as e:

        print(f"❌ Exception : {e}")
        print("=" * 60)

        return {
            "error": str(e)
        }
        
        




# ============================================================
# GIT AGENT — GIT COMMIT
# ============================================================

def git_commit(state):
    """
    Crée un commit Git local avec les fichiers présents
    dans la staging area.

    Équivalent à :

        git commit -m "<message>"

    Cette fonction ne fait PAS :
        - git push
        - Pull Request
    """

    project_dir = state.get("project_dir")

    if not project_dir:
        return {
            "error": "❌ PROJECT_DIR manquant."
        }

    # ========================================================
    # COMMIT MESSAGE
    # ========================================================

    issue_key = state.get("issue_key")

    if issue_key:
        commit_message = f"feat({issue_key}): implement changes"
    else:
        commit_message = "feat: implement changes"

    # ========================================================
    # LOG
    # ========================================================

    print("\n" + "=" * 60)
    print("💾 GIT AGENT — GIT COMMIT")
    print("=" * 60)

    print(f"📁 Project : {project_dir}")
    print(f"📝 Commit message : {commit_message}")

    # ========================================================
    # EXECUTION
    # ========================================================

    try:

        import subprocess

        result = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                commit_message
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        # ====================================================
        # ERROR
        # ====================================================

        if result.returncode != 0:

            error = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Erreur inconnue lors du commit."
            )

            print(f"❌ Erreur : {error}")
            print("=" * 60)

            return {
                "git_commit_message": commit_message,
                "error": error
            }

        # ====================================================
        # SUCCESS
        # ====================================================

        print("✅ Commit créé avec succès.")

        if result.stdout.strip():
            print("\n📦 Git :")
            print(result.stdout.strip())

        print("=" * 60)

        return {
            "git_commit_message": commit_message,
            "error": None
        }

    except Exception as e:

        print(f"❌ Exception : {e}")
        print("=" * 60)

        return {
            "git_commit_message": commit_message,
            "error": str(e)
        }
        
        
        
        
        
        
        
        
        
        
        
        # ============================================================
# GIT AGENT
# STEP — GIT PUSH
# ============================================================

def git_push(state):
    """
    Pousse la branche Git locale vers le repository distant.

    Utilise :
        - project_dir
        - git_branch_name
        - origin

    Exemple :
        git push -u origin feature/KAN-1
    """

    project_dir = state.get("project_dir")
    branch_name = state.get("git_branch_name")

    if not project_dir:
        return {
            "error": "❌ PROJECT_DIR manquant."
        }

    if not branch_name:
        return {
            "error": "❌ Nom de branche Git manquant."
        }

    remote = "origin"

    print("\n" + "=" * 60)
    print("🚀 GIT AGENT — GIT PUSH")
    print("=" * 60)

    print(f"📁 Project : {project_dir}")
    print(f"🌿 Branche : {branch_name}")
    print(f"🔗 Remote  : {remote}")
    print(
        f"⚙️ Exécution : git push -u {remote} {branch_name}"
    )

    try:

        result = local_git_push(
            project_dir,
            remote,
            branch_name
        )

        print("✅ Push effectué avec succès.")

        print("\n📦 Git :")
        print(result)

        print("=" * 60)

        return {
            "git_push_result": result,
            "error": None
        }

    except Exception as e:

        error = str(e)

        print(f"❌ Erreur : {error}")
        print("=" * 60)

        return {
            "git_push_result": None,
            "error": error
        }
        
        
        
        
# ============================================================
# GIT AGENT — CREATE PULL REQUEST
# ============================================================

async def create_pull_request(state):
    """
    Crée ou récupère une Pull Request GitHub via GitHub MCP.

    Cas gérés :

        1. PR créée
        2. PR déjà existante
        3. Erreur réelle
    """

    import re

    # ========================================================
    # READ STATE
    # ========================================================

    branch_name = state.get("git_branch_name")
    issue_key = state.get("issue_key")

    # ========================================================
    # VALIDATION
    # ========================================================

    if not branch_name:
        return {
            "pull_request_number": None,
            "pull_request_url": None,
            "error": "❌ Nom de branche Git manquant."
        }

    if not GITHUB_OWNER:
        return {
            "pull_request_number": None,
            "pull_request_url": None,
            "error": "❌ GITHUB_OWNER manquant."
        }

    if not GITHUB_REPOSITORY:
        return {
            "pull_request_number": None,
            "pull_request_url": None,
            "error": "❌ GITHUB_REPOSITORY manquant."
        }

    if not GITHUB_BRANCH:
        return {
            "pull_request_number": None,
            "pull_request_url": None,
            "error": "❌ GITHUB_BRANCH manquant."
        }

    # ========================================================
    # TITLE
    # ========================================================

    title = (
        f"feat({issue_key}): implement changes"
        if issue_key
        else "feat: implement changes"
    )

    # ========================================================
    # BODY
    # ========================================================

    body = (
        f"## Implementation\n\n"
        f"Implementation generated by the Git Agent"
        f"{f' for Jira issue **{issue_key}**' if issue_key else ''}.\n\n"
        f"### Git workflow\n"
        f"- Branch: `{branch_name}`\n"
        f"- Target: `{GITHUB_BRANCH}`\n"
        f"- Commit: `{title}`\n"
    )

    # ========================================================
    # LOG
    # ========================================================

    print("\n" + "=" * 60)
    print("🔵 GIT AGENT — CREATE PULL REQUEST")
    print("=" * 60)

    print(f"👤 Owner       : {GITHUB_OWNER}")
    print(f"📦 Repository  : {GITHUB_REPOSITORY}")
    print(f"🌿 Source      : {branch_name}")
    print(f"🎯 Target      : {GITHUB_BRANCH}")
    print(f"📝 Title       : {title}")

    try:

        # ====================================================
        # CREATE MCP CLIENT
        # ====================================================

        client = create_github_mcp_client()

        tools = await client.get_tools()

        # ====================================================
        # FIND TOOLS
        # ====================================================

        create_pr_tool = next(
            (
                tool
                for tool in tools
                if tool.name == "create_pull_request"
            ),
            None
        )

        list_pr_tool = next(
            (
                tool
                for tool in tools
                if tool.name == "list_pull_requests"
            ),
            None
        )

        if create_pr_tool is None:

            error = (
                "❌ L'outil MCP "
                "'create_pull_request' "
                "n'est pas disponible."
            )

            print(error)

            return {
                "pull_request_number": None,
                "pull_request_url": None,
                "error": error
            }

        # ====================================================
        # TRY TO CREATE PR
        # ====================================================

        print(
            "\n📡 Création de la Pull Request "
            "via GitHub MCP..."
        )

        response = await create_pr_tool.ainvoke(
            {
                "owner": GITHUB_OWNER,
                "repo": GITHUB_REPOSITORY,
                "title": title,
                "body": body,
                "head": branch_name,
                "base": GITHUB_BRANCH,
            }
        )

        print("\n📦 Réponse GitHub MCP :")
        print(response)

        response_text = str(response)

        # ====================================================
        # CASE 1 — PR CREATED
        # ====================================================

        url_match = re.search(
            r'"url"\s*:\s*"([^"]+/pull/(\d+))"',
            response_text
        )

        if url_match:

            pull_request_url = url_match.group(1)
            pull_request_number = int(url_match.group(2))

            print(
                "\n✅ Pull Request créée avec succès."
            )

            print(
                f"🔢 PR Number : #{pull_request_number}"
            )

            print(
                f"🔗 URL : {pull_request_url}"
            )

            print("=" * 60)

            return {
                "pull_request_number": pull_request_number,
                "pull_request_url": pull_request_url,
                "error": None,
            }

        # ====================================================
        # CASE 2 — PR ALREADY EXISTS
        # ====================================================

        if "already exists" in response_text:

            print(
                "\n🔄 La Pull Request existe déjà."
            )

            if list_pr_tool is None:

                error = (
                    "❌ La Pull Request existe déjà, "
                    "mais 'list_pull_requests' "
                    "n'est pas disponible."
                )

                print(error)

                return {
                    "pull_request_number": None,
                    "pull_request_url": None,
                    "error": error
                }

            print(
                "🔎 Recherche de la Pull Request existante..."
            )

            # ------------------------------------------------
            # FILTER DIRECTLY BY HEAD + BASE
            # ------------------------------------------------

            existing_prs = await list_pr_tool.ainvoke(
                {
                    "owner": GITHUB_OWNER,
                    "repo": GITHUB_REPOSITORY,
                    "head": branch_name,
                    "base": GITHUB_BRANCH,
                    "state": "open",
                    "fields": [
                        "number",
                        "html_url",
                        "head",
                        "base",
                    ],
                }
            )

            print(
                "\n📦 Résultat list_pull_requests :"
            )

            print(existing_prs)

            existing_text = str(existing_prs)

            # ------------------------------------------------
            # EXTRACT URL
            # ------------------------------------------------

            existing_url_match = re.search(
                r'"html_url"\s*:\s*"([^"]+/pull/(\d+))"',
                existing_text
            )

            if not existing_url_match:

                existing_url_match = re.search(
                    r'"url"\s*:\s*"([^"]+/pull/(\d+))"',
                    existing_text
                )

            # ------------------------------------------------
            # PR FOUND
            # ------------------------------------------------

            if existing_url_match:

                pull_request_url = (
                    existing_url_match.group(1)
                )

                pull_request_number = int(
                    existing_url_match.group(2)
                )

                print(
                    "\n✅ Pull Request existante récupérée."
                )

                print(
                    f"🔢 PR Number : #{pull_request_number}"
                )

                print(
                    f"🔗 URL : {pull_request_url}"
                )

                print("=" * 60)

                return {
                    "pull_request_number": pull_request_number,
                    "pull_request_url": pull_request_url,
                    "error": None,
                }

            # ------------------------------------------------
            # PR EXISTS BUT NOT FOUND
            # ------------------------------------------------

            error = (
                "❌ GitHub indique que la Pull Request "
                "existe déjà, mais impossible de récupérer "
                "son numéro et son URL."
            )

            print(error)

            return {
                "pull_request_number": None,
                "pull_request_url": None,
                "error": error
            }

        # ====================================================
        # CASE 3 — REAL ERROR
        # ====================================================

        error = (
            "❌ Erreur GitHub MCP lors de la création "
            "de la Pull Request.\n"
            f"Réponse : {response_text}"
        )

        print(error)

        return {
            "pull_request_number": None,
            "pull_request_url": None,
            "error": error
        }

    # ========================================================
    # EXCEPTION
    # ========================================================

    except Exception as e:

        error = (
            "❌ Exception lors de la création "
            f"de la Pull Request : {str(e)}"
        )

        print(error)

        return {
            "pull_request_number": None,
            "pull_request_url": None,
            "error": error
        }