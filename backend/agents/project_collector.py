# ============================================================
# PROJECT COLLECTOR
#
# Responsibility:
#
#   OpenCode
#       ↓
#   Local project
#       ↓
#   Project Collector
#       ↓
#   Git Agent
#       ↓
#   GitHub MCP
#
# IMPORTANT:
#
# - Ce composant INSPECTE uniquement le repository local.
# - Il ne fait PAS de commit.
# - Il ne fait PAS de push.
# - Il ne fait PAS de git add.
# - Il ne fait PAS de git reset.
# - Il ne modifie PAS les fichiers.
#
# Son rôle est de fournir au Git Agent :
#
#   - repository
#   - branch
#   - remote
#   - git status
#   - fichiers modifiés
#   - fichiers ajoutés
#   - fichiers supprimés
#   - fichiers untracked
#   - diff
#   - contenu des fichiers
#   - détection des fichiers sensibles
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

import os
import subprocess

from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv


# ============================================================
# 2. ENVIRONMENT
# ============================================================

# Charger le .env avant de lire les variables.
#
# Le .env se trouve à la racine du projet :
#
# multi-agents/
# ├── .env
# ├── backend/
# └── ...
#
load_dotenv(
    override=True
)


print(
    "✅ .env chargé pour Project Collector"
)


PROJECT_DIR = os.getenv(
    "OPENCODE_PROJECT_DIR"
)


if not PROJECT_DIR:

    raise ValueError(
        """
❌ OPENCODE_PROJECT_DIR n'est pas défini.

Ajoute dans ton .env :

OPENCODE_PROJECT_DIR=C:\\Users\\User\\Desktop\\Summer Internship AI\\Projects\\Formation\\multi-agents
"""
    )


PROJECT_PATH = Path(
    PROJECT_DIR
).expanduser().resolve()


if not PROJECT_PATH.exists():

    raise ValueError(
        f"""
❌ Le dossier du projet n'existe pas :

{PROJECT_PATH}
"""
    )


if not PROJECT_PATH.is_dir():

    raise ValueError(
        f"""
❌ OPENCODE_PROJECT_DIR doit pointer vers un dossier :

{PROJECT_PATH}
"""
    )


print(
    f"📁 Projet : {PROJECT_PATH}"
)


# ============================================================
# 3. RUN GIT COMMAND
# ============================================================

def run_git_command(
    command: List[str]
) -> str:

    """
    Exécute une commande Git en lecture seule.

    Commandes autorisées ici :

        git rev-parse
        git branch
        git remote
        git status
        git diff

    IMPORTANT :

    Project Collector ne doit jamais exécuter :

        git add
        git commit
        git push
        git reset
        git checkout
        git clean
        git restore
    """

    try:

        result = subprocess.run(

            command,

            cwd=PROJECT_PATH,

            capture_output=True,

            text=True,

            encoding="utf-8",

            errors="replace",

            check=False,

        )

    except Exception as e:

        raise RuntimeError(
            f"❌ Impossible d'exécuter Git : {e}"
        )


    if result.returncode != 0:

        raise RuntimeError(

            "❌ Commande Git échouée.\n"
            f"Commande : {' '.join(command)}\n"
            f"Erreur : {result.stderr.strip()}"

        )


    return result.stdout.strip()


# ============================================================
# 4. CHECK GIT REPOSITORY
# ============================================================

def check_git_repository() -> bool:

    """
    Vérifie que PROJECT_PATH est bien
    un repository Git.
    """

    try:

        result = run_git_command(

            [
                "git",
                "rev-parse",
                "--is-inside-work-tree"
            ]

        )

        return result.lower() == "true"

    except Exception:

        return False


# ============================================================
# 5. GET CURRENT BRANCH
# ============================================================

def get_current_branch() -> str:

    """
    Retourne la branche Git actuelle.
    """

    branch = run_git_command(

        [
            "git",
            "branch",
            "--show-current"
        ]

    )

    return branch.strip()


# ============================================================
# 6. GET GIT REMOTE
# ============================================================

def get_git_remote() -> str:

    """
    Retourne l'URL du remote origin.
    """

    return run_git_command(

        [
            "git",
            "remote",
            "get-url",
            "origin"
        ]

    )


# ============================================================
# 7. GET GIT STATUS
# ============================================================

def get_git_status() -> str:

    """
    Retourne le statut Git.

    Exemple :

        M backend/main.py
        M backend/agents/git_agent.py
        ?? backend/test.py
    """

    return run_git_command(

        [
            "git",
            "status",
            "--short"
        ]

    )


# ============================================================
# 8. PARSE GIT STATUS
# ============================================================

def parse_git_status(
    status: str
) -> Dict[str, List[str]]:

    """
    Transforme :

        git status --short

    en structure Python.

    Exemple :

        {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": []
        }
    """

    modified = []
    added = []
    deleted = []
    untracked = []


    if not status:

        return {

            "modified": modified,

            "added": added,

            "deleted": deleted,

            "untracked": untracked,

        }


    for line in status.splitlines():

        if not line.strip():

            continue


        # Git status --short :
        #
        # XY filename
        #
        # Exemple :
        #
        #  M file.py
        # ?? test.py
        # A  file.py
        # D  file.py

        status_code = line[:2]

        file_path = line[2:].strip()


        if not file_path:

            continue


        # ----------------------------------------------------
        # Untracked
        # ----------------------------------------------------

        if status_code == "??":

            untracked.append(
                file_path
            )

            continue


        # ----------------------------------------------------
        # Deleted
        # ----------------------------------------------------

        if "D" in status_code:

            deleted.append(
                file_path
            )

            continue


        # ----------------------------------------------------
        # Added
        # ----------------------------------------------------

        if "A" in status_code:

            added.append(
                file_path
            )

            continue


        # ----------------------------------------------------
        # Modified
        # ----------------------------------------------------

        if "M" in status_code:

            modified.append(
                file_path
            )

            continue


    return {

        "modified": modified,

        "added": added,

        "deleted": deleted,

        "untracked": untracked,

    }


# ============================================================
# 9. COLLECT CHANGED FILES
# ============================================================

def collect_changed_files(
    parsed_status: Dict[str, List[str]]
) -> List[str]:

    """
    Regroupe tous les fichiers concernés
    par les changements.
    """

    files = []


    for category in [

        "modified",

        "added",

        "deleted",

        "untracked",

    ]:

        files.extend(

            parsed_status.get(
                category,
                []
            )

        )


    # Supprimer les doublons
    return list(
        dict.fromkeys(files)
    )


# ============================================================
# 10. GET GIT DIFF
# ============================================================

def get_git_diff() -> str:

    """
    Retourne le diff des fichiers suivis par Git.

    IMPORTANT :

    Cette commande est en lecture seule.
    """

    return run_git_command(

        [
            "git",
            "diff",
            "--no-ext-diff"
        ]

    )


# ============================================================
# 11. GET STAGED DIFF
# ============================================================

def get_git_staged_diff() -> str:

    """
    Retourne les changements déjà staged.

    Exemple :

        git add file.py

    Project Collector ne fait PAS le git add.

    Mais si OpenCode ou l'utilisateur a déjà
    staged des fichiers, nous pouvons les inspecter.
    """

    return run_git_command(

        [
            "git",
            "diff",
            "--cached",
            "--no-ext-diff"
        ]

    )


# ============================================================
# 12. GET FILE CONTENT
# ============================================================

def get_file_content(
    relative_path: str
) -> str:

    """
    Lit le contenu d'un fichier local.

    Security :
    le fichier doit rester à l'intérieur
    du repository.
    """

    file_path = (

        PROJECT_PATH
        / relative_path

    ).resolve()


    # --------------------------------------------------------
    # Security check
    # --------------------------------------------------------

    try:

        file_path.relative_to(
            PROJECT_PATH
        )

    except ValueError:

        raise RuntimeError(

            f"""
❌ Accès refusé.

Le fichier est en dehors du repository :

{relative_path}
"""

        )


    if not file_path.exists():

        raise FileNotFoundError(

            f"""
❌ Fichier introuvable :

{relative_path}
"""

        )


    if not file_path.is_file():

        raise RuntimeError(

            f"""
❌ Ce chemin n'est pas un fichier :

{relative_path}
"""

        )


    try:

        return file_path.read_text(

            encoding="utf-8",

            errors="replace"

        )

    except Exception as e:

        raise RuntimeError(

            f"""
❌ Impossible de lire :

{relative_path}

Erreur :
{e}
"""

        )


# ============================================================
# 13. SENSITIVE FILES
# ============================================================

SENSITIVE_FILES = {

    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.test",

    "credentials.json",
    "credential.json",

    "secrets.json",
    "secret.json",

    "id_rsa",
    "id_ed25519",

    "config.json",

}


SENSITIVE_EXTENSIONS = {

    ".pem",
    ".key",
    ".p12",
    ".pfx",

}


SENSITIVE_WORDS = {

    "secret",
    "secrets",
    "credential",
    "credentials",
    "password",
    "passwd",
    "token",

}


# ============================================================
# 14. CHECK SENSITIVE FILE
# ============================================================

def is_sensitive_file(
    relative_path: str
) -> bool:

    """
    Détermine si un fichier peut contenir
    des informations sensibles.
    """

    path = Path(
        relative_path
    )


    filename = path.name.lower()


    # --------------------------------------------------------
    # Exact filenames
    # --------------------------------------------------------

    if filename in {

        item.lower()
        for item in SENSITIVE_FILES

    }:

        return True


    # --------------------------------------------------------
    # .env files
    # --------------------------------------------------------

    if filename.startswith(
        ".env"
    ):

        return True


    # --------------------------------------------------------
    # Sensitive extensions
    # --------------------------------------------------------

    if path.suffix.lower() in {

        extension.lower()
        for extension in SENSITIVE_EXTENSIONS

    }:

        return True


    # --------------------------------------------------------
    # Sensitive words
    # --------------------------------------------------------

    for word in SENSITIVE_WORDS:

        if word in filename:

            return True


    return False


# ============================================================
# 15. SCAN SENSITIVE FILES
# ============================================================

def scan_sensitive_files(
    files: List[str]
) -> List[str]:

    """
    Retourne les fichiers potentiellement sensibles.
    """

    sensitive_files = []


    for file_path in files:

        if is_sensitive_file(
            file_path
        ):

            sensitive_files.append(
                file_path
            )


    return sensitive_files


# ============================================================
# 16. COLLECT FILE INFORMATION
# ============================================================

def collect_files_data(
    changed_files: List[str],
    sensitive_files: List[str],
    parsed_status: Dict[str, List[str]]
) -> List[Dict[str, Any]]:

    """
    Collecte les informations des fichiers modifiés.

    Aucun fichier sensible n'est lu.
    """

    files_data = []


    for file_path in changed_files:

        # ----------------------------------------------------
        # Deleted
        # ----------------------------------------------------

        if file_path in parsed_status.get(
            "deleted",
            []
        ):

            files_data.append({

                "path":
                    file_path,

                "status":
                    "deleted",

                "content":
                    None,

            })

            continue


        # ----------------------------------------------------
        # Sensitive
        # ----------------------------------------------------

        if file_path in sensitive_files:

            files_data.append({

                "path":
                    file_path,

                "status":
                    "sensitive",

                "content":
                    None,

            })

            continue


        # ----------------------------------------------------
        # Read file
        # ----------------------------------------------------

        try:

            content = get_file_content(
                file_path
            )


            files_data.append({

                "path":
                    file_path,

                "status":
                    "changed",

                "content":
                    content,

            })


        except Exception as e:

            files_data.append({

                "path":
                    file_path,

                "status":
                    "error",

                "content":
                    None,

                "error":
                    str(e),

            })


    return files_data


# ============================================================
# 17. COLLECT PROJECT CHANGES
# ============================================================

def collect_project_changes() -> Dict[str, Any]:

    """
    Fonction principale.

    Retourne toutes les informations
    nécessaires au Git Agent.

    IMPORTANT :

    Aucun changement n'est effectué
    dans le repository.
    """

    print(
        "\n"
        + "=" * 60
    )

    print(
        "📂 PROJECT COLLECTOR"
    )

    print(
        "=" * 60
    )


    print(
        f"📁 Project : {PROJECT_PATH}"
    )


    # ========================================================
    # 17.1 CHECK REPOSITORY
    # ========================================================

    if not check_git_repository():

        raise RuntimeError(

            f"""
❌ Le dossier suivant n'est pas un repository Git :

{PROJECT_PATH}
"""

        )


    print(
        "✅ Repository Git détecté."
    )


    # ========================================================
    # 17.2 BRANCH
    # ========================================================

    branch = get_current_branch()


    print(
        f"🌿 Branch : {branch}"
    )


    # ========================================================
    # 17.3 REMOTE
    # ========================================================

    remote = get_git_remote()


    print(
        f"🔗 Remote : {remote}"
    )


    # ========================================================
    # 17.4 STATUS
    # ========================================================

    status = get_git_status()


    print(
        "\n📊 Git Status:"
    )


    if status:

        print(
            status
        )

    else:

        print(
            "   Aucun changement."
        )


    # ========================================================
    # 17.5 PARSE STATUS
    # ========================================================

    parsed_status = parse_git_status(
        status
    )


    changed_files = collect_changed_files(
        parsed_status
    )


    print(
        f"\n📄 Fichiers concernés : "
        f"{len(changed_files)}"
    )


    for file_path in changed_files:

        print(
            f"   - {file_path}"
        )


    # ========================================================
    # 17.6 SECURITY
    # ========================================================

    sensitive_files = scan_sensitive_files(
        changed_files
    )


    if sensitive_files:

        print(
            "\n🚨 FICHIERS SENSIBLES DÉTECTÉS :"
        )


        for file_path in sensitive_files:

            print(
                f"   ❌ {file_path}"
            )


    else:

        print(
            "\n🔐 Aucun fichier sensible détecté."
        )


    # ========================================================
    # 17.7 WORKING TREE DIFF
    # ========================================================

    diff = get_git_diff()


    # ========================================================
    # 17.8 STAGED DIFF
    # ========================================================

    staged_diff = get_git_staged_diff()


    # ========================================================
    # 17.9 FILE CONTENT
    # ========================================================

    files_data = collect_files_data(

        changed_files,

        sensitive_files,

        parsed_status

    )


    # ========================================================
    # 17.10 RESULT
    # ========================================================

    result = {

        "project_dir":
            str(PROJECT_PATH),

        "branch":
            branch,

        "remote":
            remote,

        "status":
            status,

        "parsed_status":
            parsed_status,

        "changed_files":
            changed_files,

        "sensitive_files":
            sensitive_files,

        "security_ok":
            len(sensitive_files) == 0,

        "diff":
            diff,

        "staged_diff":
            staged_diff,

        "files":
            files_data,

        "changes_detected":
            len(changed_files) > 0,

    }


    # ========================================================
    # 17.11 DISPLAY SUMMARY
    # ========================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "✅ COLLECTE TERMINÉE"
    )

    print(
        "=" * 60
    )


    print(
        f"Changes detected : "
        f"{result['changes_detected']}"
    )


    print(
        f"Files            : "
        f"{len(changed_files)}"
    )


    print(
        f"Security OK      : "
        f"{result['security_ok']}"
    )


    return result


# ============================================================
# 18. SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    try:

        result = collect_project_changes()


        print(
            "\n"
            + "=" * 60
        )

        print(
            "📦 COLLECTOR RESULT"
        )

        print(
            "=" * 60
        )


        print(
            f"\nProject : "
            f"{result['project_dir']}"
        )


        print(
            f"Branch  : "
            f"{result['branch']}"
        )


        print(
            f"Remote  : "
            f"{result['remote']}"
        )


        print(
            "\nChanged files:"
        )


        if result["changed_files"]:

            for file_path in result[
                "changed_files"
            ]:

                print(
                    f"  - {file_path}"
                )

        else:

            print(
                "  Aucun changement."
            )


        if result[
            "sensitive_files"
        ]:

            print(
                "\n🚨 Sensitive files:"
            )


            for file_path in result[
                "sensitive_files"
            ]:

                print(
                    f"  ❌ {file_path}"
                )


        print(
            "\n"
            + "=" * 60
        )


    except Exception as e:

        print(
            "\n❌ PROJECT COLLECTOR ERROR:"
        )

        print(
            e
        )