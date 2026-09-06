# ============================================================
# agents/git_deploy_agent.py
#
# GIT DEPLOY AGENT
#
# RESPONSIBILITIES:
#
# 1. Verify Git repository
# 2. Check current branch
# 3. Check working tree
# 4. Git add
# 5. Git commit
# 6. Git fetch
# 7. Check EXACT remote branch
# 8. Pull --rebase if remote branch exists
# 9. Git push
#
# IMPORTANT:
#
# Git Preparation:
#     clone
#     fetch
#     main/master
#     pull
#     create/switch Jira branch
#
# Git Deploy:
#     add
#     commit
#     fetch
#     sync
#     push
#
# Branch convention:
#
#     KAN-1
#
# IMPORTANT:
#
# feature/KAN-1
#
# is NOT considered:
#
# KAN-1
#
# ============================================================

import os
import subprocess
from typing import Any, Dict

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# GET PROJECT DIRECTORY
# ============================================================

def get_project_dir() -> str:

    project_dir = os.getenv(
        "OPENCODE_PROJECT_DIR"
    )

    if not project_dir:

        raise ValueError(
            "La variable d'environnement "
            "OPENCODE_PROJECT_DIR n'est pas définie."
        )

    return os.path.abspath(
        project_dir
    )


# ============================================================
# RUN GIT COMMAND
# ============================================================

def run_git_command(
    project_dir: str,
    command: list[str]
) -> Dict[str, Any]:

    print()
    print(
        f"▶️ Commande : "
        f"{' '.join(command)}"
    )

    try:

        result = subprocess.run(

            command,

            cwd=project_dir,

            capture_output=True,

            text=True,

            encoding="utf-8",

            errors="replace",

            shell=False
        )

        stdout = (
            result.stdout or ""
        ).strip()

        stderr = (
            result.stderr or ""
        ).strip()

        print(
            f"   Return code : "
            f"{result.returncode}"
        )

        if stdout:

            print()
            print("   STDOUT :")
            print(stdout)

        if stderr:

            print()
            print("   STDERR :")
            print(stderr)

        return {

            "returncode":
                result.returncode,

            "stdout":
                stdout,

            "stderr":
                stderr
        }

    except Exception as e:

        print()
        print(
            f"❌ Exception Git : {e}"
        )

        return {

            "returncode":
                -1,

            "stdout":
                "",

            "stderr":
                str(e)
        }


# ============================================================
# ERROR STATE
# ============================================================

def git_error_state(
    stage: str,
    message: str,
    stdout: str = "",
    stderr: str = "",
) -> Dict[str, Any]:

    print()
    print("=" * 60)
    print("❌ GIT DEPLOY ERROR")
    print("=" * 60)

    print(
        f"📍 Stage : {stage}"
    )

    print(
        f"💬 Message : {message}"
    )

    if stdout:

        print()
        print("STDOUT :")
        print(stdout)

    if stderr:

        print()
        print("STDERR :")
        print(stderr)

    return {

        "success":
            False,

        "git_deploy_success":
            False,

        "stage":
            stage,

        "message":
            message,

        "stdout":
            stdout,

        "stderr":
            stderr
    }


# ============================================================
# VERIFY GIT REPOSITORY
# ============================================================

def verify_git_repository(
    project_dir: str
) -> Dict[str, Any]:

    git_dir = os.path.join(
        project_dir,
        ".git"
    )

    if not os.path.isdir(git_dir):

        return {

            "success":
                False,

            "message":
                "Le dossier n'est pas un repository Git."
        }

    return {

        "success":
            True,

        "message":
            "Repository Git détecté."
    }


# ============================================================
# GET CURRENT BRANCH
# ============================================================

def get_current_branch(
    project_dir: str
) -> Dict[str, Any]:

    result = run_git_command(

        project_dir,

        [
            "git",
            "branch",
            "--show-current"
        ]
    )

    if result["returncode"] != 0:

        return {

            "success":
                False,

            "stdout":
                result["stdout"],

            "stderr":
                result["stderr"],

            "branch":
                None
        }

    branch = (
        result["stdout"]
        .strip()
    )

    if not branch:

        return {

            "success":
                False,

            "stdout":
                result["stdout"],

            "stderr":
                result["stderr"],

            "branch":
                None
        }

    return {

        "success":
            True,

        "branch":
            branch,

        "stdout":
            result["stdout"],

        "stderr":
            result["stderr"]
    }


# ============================================================
# CHECK EXACT REMOTE BRANCH
# ============================================================

def remote_branch_exists(
    project_dir: str,
    branch: str,
) -> Dict[str, Any]:
    """
    Vérifie EXACTEMENT :

        refs/heads/<branch>

    Exemple :

        KAN-1

    doit correspondre exactement à :

        refs/heads/KAN-1

    et PAS :

        refs/heads/feature/KAN-1
    """

    print()
    print(
        f"🔎 Vérification EXACTE de "
        f"origin/{branch}"
    )

    result = run_git_command(

        project_dir,

        [
            "git",
            "ls-remote",
            "--heads",
            "origin",
            f"refs/heads/{branch}"
        ]
    )

    if result["returncode"] != 0:

        return {

            "success":
                False,

            "exists":
                False,

            "stdout":
                result["stdout"],

            "stderr":
                result["stderr"]
        }

    exists = False

    expected_ref = (
        f"refs/heads/{branch}"
    )

    for line in result["stdout"].splitlines():

        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) < 2:
            continue

        remote_ref = parts[-1]

        # ====================================================
        # EXACT MATCH
        # ====================================================

        if remote_ref == expected_ref:

            exists = True
            break

    if exists:

        print()
        print(
            f"✅ Remote EXACT trouvé : "
            f"{expected_ref}"
        )

    else:

        print()
        print(
            f"ℹ️ Remote EXACT absent : "
            f"{expected_ref}"
        )

    return {

        "success":
            True,

        "exists":
            exists,

        "stdout":
            result["stdout"],

        "stderr":
            result["stderr"]
    }


# ============================================================
# GIT DEPLOY AGENT
# ============================================================

def git_deploy_agent(
    state: Dict[str, Any]
) -> Dict[str, Any]:

    print()
    print("=" * 70)
    print("🚀 GIT DEPLOY AGENT")
    print("=" * 70)

    # ========================================================
    # ISSUE KEY
    # ========================================================

    issue_key = state.get(
        "issue_key"
    )

    if not issue_key:

        return git_error_state(

            stage="validation",

            message="issue_key est obligatoire."
        )

    issue_key = str(
        issue_key
    ).strip().upper()

    print()
    print(
        f"🎫 Ticket : {issue_key}"
    )

    # ========================================================
    # PROJECT DIRECTORY
    # ========================================================

    try:

        project_dir = get_project_dir()

    except Exception as e:

        return git_error_state(

            stage="project_directory",

            message=str(e)
        )

    print()
    print(
        f"📁 Project directory : "
        f"{project_dir}"
    )

    # ========================================================
    # VERIFY DIRECTORY
    # ========================================================

    if not os.path.isdir(project_dir):

        return git_error_state(

            stage="project_directory",

            message=(
                f"Le dossier projet n'existe pas : "
                f"{project_dir}"
            )
        )

    # ========================================================
    # VERIFY GIT
    # ========================================================

    repository_check = verify_git_repository(
        project_dir
    )

    if not repository_check["success"]:

        return git_error_state(

            stage="verify_repository",

            message=(
                repository_check["message"]
            )
        )

    print()
    print(
        "✅ Repository Git détecté."
    )

    # ========================================================
    # 1. CURRENT BRANCH
    # ========================================================

    print()
    print("-" * 60)
    print("1️⃣ CHECK CURRENT BRANCH")
    print("-" * 60)

    branch_result = get_current_branch(
        project_dir
    )

    if not branch_result["success"]:

        return git_error_state(

            stage="current_branch",

            message=(
                "Impossible de récupérer "
                "la branche actuelle."
            ),

            stdout=branch_result["stdout"],

            stderr=branch_result["stderr"]
        )

    current_branch = (
        branch_result["branch"]
    )

    print()
    print(
        f"🌿 Branche actuelle : "
        f"{current_branch}"
    )

    # ========================================================
    # VERIFY ISSUE BRANCH
    # ========================================================

    if current_branch != issue_key:

        return git_error_state(

            stage="branch_validation",

            message=(
                f"La branche actuelle est "
                f"'{current_branch}', "
                f"mais la branche attendue est "
                f"'{issue_key}'."
            )
        )

    print()
    print(
        f"✅ Bonne branche : "
        f"{current_branch}"
    )

    # ========================================================
    # 2. GIT STATUS
    # ========================================================

    print()
    print("-" * 60)
    print("2️⃣ GIT STATUS")
    print("-" * 60)

    status_result = run_git_command(

        project_dir,

        [
            "git",
            "status",
            "--short"
        ]
    )

    if status_result["returncode"] != 0:

        return git_error_state(

            stage="git_status",

            message="git status a échoué.",

            stdout=status_result["stdout"],

            stderr=status_result["stderr"]
        )

    status_output = (
        status_result["stdout"]
    )

    if status_output:

        print()
        print(
            "📝 Modifications détectées :"
        )

        print(
            status_output
        )

    else:

        print()
        print(
            "ℹ️ Aucune modification locale détectée."
        )

    # ========================================================
    # 3. GIT ADD
    # ========================================================

    print()
    print("-" * 60)
    print("3️⃣ GIT ADD")
    print("-" * 60)

    if status_output:

        add_result = run_git_command(

            project_dir,

            [
                "git",
                "add",
                "."
            ]
        )

        if add_result["returncode"] != 0:

            return git_error_state(

                stage="git_add",

                message="git add a échoué.",

                stdout=add_result["stdout"],

                stderr=add_result["stderr"]
            )

        print()
        print(
            "✅ git add terminé."
        )

    else:

        print()
        print(
            "⏭️ git add ignoré."
        )

    # ========================================================
    # 4. GIT COMMIT
    # ========================================================

    print()
    print("-" * 60)
    print("4️⃣ GIT COMMIT")
    print("-" * 60)

    if status_output:

        commit_message = (
            f"feat({issue_key}): "
            f"implement Jira issue {issue_key}"
        )

        print()
        print(
            f"💬 Commit message : "
            f"{commit_message}"
        )

        commit_result = run_git_command(

            project_dir,

            [
                "git",
                "commit",
                "-m",
                commit_message
            ]
        )

        if commit_result["returncode"] != 0:

            return git_error_state(

                stage="git_commit",

                message="git commit a échoué.",

                stdout=commit_result["stdout"],

                stderr=commit_result["stderr"]
            )

        print()
        print(
            "✅ Commit créé avec succès."
        )

    else:

        print()
        print(
            "⏭️ Aucun commit nécessaire."
        )

    # ========================================================
    # 5. FETCH
    # ========================================================

    print()
    print("-" * 60)
    print("5️⃣ GIT FETCH")
    print("-" * 60)

    fetch_result = run_git_command(

        project_dir,

        [
            "git",
            "fetch",
            "origin"
        ]
    )

    if fetch_result["returncode"] != 0:

        return git_error_state(

            stage="git_fetch",

            message="git fetch a échoué.",

            stdout=fetch_result["stdout"],

            stderr=fetch_result["stderr"]
        )

    print()
    print(
        "✅ git fetch terminé."
    )

    # ========================================================
    # 6. CHECK EXACT REMOTE BRANCH
    # ========================================================

    print()
    print("-" * 60)
    print("6️⃣ CHECK EXACT REMOTE BRANCH")
    print("-" * 60)

    remote_result = remote_branch_exists(

        project_dir,

        current_branch
    )

    if not remote_result["success"]:

        return git_error_state(

            stage="remote_branch_check",

            message=(
                f"Impossible de vérifier "
                f"la branche distante "
                f"'{current_branch}'."
            ),

            stdout=remote_result["stdout"],

            stderr=remote_result["stderr"]
        )

    # ========================================================
    # REMOTE EXISTS
    # ========================================================

    if remote_result["exists"]:

        print()
        print(
            f"🌐 Branche distante EXACTE "
            f"'origin/{current_branch}' existe."
        )

        # ====================================================
        # 7. PULL REBASE
        # ====================================================

        print()
        print("-" * 60)
        print("7️⃣ GIT PULL --REBASE")
        print("-" * 60)

        pull_result = run_git_command(

            project_dir,

            [
                "git",
                "pull",
                "--rebase",
                "origin",
                current_branch
            ]
        )

        if pull_result["returncode"] != 0:

            print()
            print(
                "❌ git pull --rebase a échoué."
            )

            return git_error_state(

                stage="git_pull_rebase",

                message=(
                    f"Impossible de synchroniser "
                    f"'{current_branch}' "
                    f"avec origin/{current_branch}."
                ),

                stdout=pull_result["stdout"],

                stderr=pull_result["stderr"]
            )

        print()
        print(
            "✅ Rebase terminé."
        )

    else:

        print()
        print(
            f"ℹ️ Branche distante EXACTE "
            f"'origin/{current_branch}' "
            f"n'existe pas."
        )

        print()
        print(
            "➡️ Elle sera créée par git push."
        )

    # ========================================================
    # 8. GIT PUSH
    # ========================================================

    print()
    print("-" * 60)
    print("8️⃣ GIT PUSH")
    print("-" * 60)

    push_result = run_git_command(

        project_dir,

        [
            "git",
            "push",
            "-u",
            "origin",
            current_branch
        ]
    )

    if push_result["returncode"] != 0:

        return git_error_state(

            stage="git_push",

            message=(
                f"git push a échoué "
                f"pour la branche "
                f"'{current_branch}'."
            ),

            stdout=push_result["stdout"],

            stderr=push_result["stderr"]
        )

    print()
    print(
        "✅ git push terminé avec succès."
    )

    # ========================================================
    # FINAL SUCCESS
    # ========================================================

    print()
    print("=" * 70)
    print("🎉 GIT DEPLOY TERMINÉ")
    print("=" * 70)

    print()
    print(
        f"🎫 Ticket : {issue_key}"
    )

    print(
        f"🌿 Branch : {current_branch}"
    )

    print(
        f"📁 Project : {project_dir}"
    )

    print(
        "📤 Push : SUCCESS"
    )

    return {

        "success":
            True,

        "git_deploy_success":
            True,

        "stage":
            "completed",

        "message":
            (
                "Déploiement Git terminé avec succès "
                f"sur la branche {current_branch}."
            ),

        "issue_key":
            issue_key,

        "branch":
            current_branch,

        "project_dir":
            project_dir,

        "push_success":
            True,

        "push_stdout":
            push_result["stdout"],

        "push_stderr":
            push_result["stderr"]
    }


# ============================================================
# END OF FILE
# ============================================================