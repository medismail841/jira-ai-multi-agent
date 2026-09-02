# ============================================================
# agents/git_agent.py
#
# GIT PREPARATION AGENT
#
# RESPONSABILITÉ :
#
# GitHub URL
#      ↓
# git clone
#      ↓
# dossier local
#      ↓
# git status
#      ↓
# .git ?
#   /      \
# OUI      NON
#  ↓        ↓
# continuer ERROR
#           "projet n'est pas git"
#  ↓
# git fetch origin
#  ↓
# détecter main / master
#  ↓
# git switch main/master
#  ↓
# git pull origin main/master
#  ↓
# vérifier branche ISSUE
#  ↓
# créer / switch ISSUE
#  ↓
# git_ready = True
#
# IMPORTANT :
#
# ❌ Pas de git init
# ❌ Pas de git add
# ❌ Pas de git commit
# ❌ Pas de git push
# ❌ Pas de Pull Request
# ❌ Pas d'OpenCode
#
# Le Git Agent est responsable du CLONE
# et de la préparation de la branche Jira.
#
# ============================================================

import os
import subprocess

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

PROJECT_DIR = os.getenv(
    "OPENCODE_PROJECT_DIR"
)


# ============================================================
# HELPER : RUN GIT COMMAND
# ============================================================

def run_git_command(
    command: list[str],
    cwd: str
) -> dict:

    try:

        print(
            "\n▶️ Commande : "
            + " ".join(command)
        )

        result = subprocess.run(
            command,
            cwd=cwd,
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

            print("\n   STDOUT :")
            print(stdout)

        if stderr:

            print("\n   STDERR :")
            print(stderr)

        return {

            "success":
                result.returncode == 0,

            "stdout":
                stdout,

            "stderr":
                stderr,

            "return_code":
                result.returncode
        }

    except Exception as e:

        print(
            f"\n❌ Exception Git : {e}"
        )

        return {

            "success":
                False,

            "stdout":
                "",

            "stderr":
                str(e),

            "return_code":
                -1
        }


# ============================================================
# HELPER : ERROR STATE
# ============================================================

def git_error_state(
    project_dir: str | None,
    github_url: str | None,
    issue_key: str | None,
    message: str,
    git_status: str = "",
    git_branch: str = ""
) -> dict:

    print(
        "\n❌ GIT ERROR : "
        + message
    )

    return {

        "git_ready":
            False,

        "project_dir":
            project_dir,

        "github_url":
            github_url,

        "repository_url":
            github_url,

        "issue_key":
            issue_key,

        "git_status":
            git_status,

        "git_branch":
            git_branch,

        "git_branch_created":
            False,

        "git_error":
            message,

        "error":
            message
    }


# ============================================================
# GET PROJECT DIRECTORY
# ============================================================

def get_project_dir() -> str | None:

    if not PROJECT_DIR:
        return None

    return os.path.abspath(
        PROJECT_DIR
    )


# ============================================================
# STEP 1 — GIT CLONE
# ============================================================

def clone_repository(
    repository_url: str
) -> dict:

    print("\n" + "=" * 70)
    print("📥 STEP 1 — GIT CLONE")
    print("=" * 70)

    if not repository_url:

        return {

            "success":
                False,

            "error":
                "URL GitHub manquante."
        }

    repository_url = str(
        repository_url
    ).strip()

    print(
        f"\n🔗 GitHub URL : "
        f"{repository_url}"
    )

    project_dir = get_project_dir()

    if not project_dir:

        return {

            "success":
                False,

            "error":
                (
                    "OPENCODE_PROJECT_DIR "
                    "n'est pas défini dans .env."
                )
        }

    print(
        f"📁 Destination : "
        f"{project_dir}"
    )

    # ========================================================
    # DESTINATION
    # ========================================================

    if os.path.exists(project_dir):

        if not os.path.isdir(project_dir):

            return {

                "success":
                    False,

                "error":
                    (
                        "OPENCODE_PROJECT_DIR "
                        "existe mais ce n'est pas "
                        "un dossier."
                    )
            }

        try:

            items = os.listdir(
                project_dir
            )

        except Exception as e:

            return {

                "success":
                    False,

                "error":
                    (
                        "Impossible de lire "
                        f"le dossier local : {e}"
                    )
            }

        if items:

            return {

                "success":
                    False,

                "error":
                    (
                        "Impossible de faire git clone : "
                        "le dossier local existe déjà "
                        "et n'est pas vide."
                    ),

                "project_directory":
                    project_dir
            }

    else:

        parent_dir = os.path.dirname(
            project_dir
        )

        try:

            os.makedirs(
                parent_dir,
                exist_ok=True
            )

        except Exception as e:

            return {

                "success":
                    False,

                "error":
                    (
                        "Impossible de créer "
                        f"le dossier parent : {e}"
                    )
            }

    # ========================================================
    # CLONE
    # ========================================================

    clone_result = run_git_command(

        [
            "git",
            "clone",
            repository_url,
            project_dir
        ],

        os.path.dirname(
            project_dir
        )
    )

    if not clone_result["success"]:

        return {

            "success":
                False,

            "repository_url":
                repository_url,

            "project_directory":
                project_dir,

            "error":
                (
                    clone_result["stderr"]
                    or "git clone a échoué."
                ),

            "stdout":
                clone_result["stdout"],

            "stderr":
                clone_result["stderr"],

            "return_code":
                clone_result["return_code"]
        }

    if not os.path.isdir(project_dir):

        return {

            "success":
                False,

            "repository_url":
                repository_url,

            "project_directory":
                project_dir,

            "error":
                (
                    "git clone semble avoir réussi "
                    "mais le dossier local n'existe pas."
                )
        }

    print(
        "\n✅ git clone terminé."
    )

    return {

        "success":
            True,

        "repository_url":
            repository_url,

        "project_directory":
            project_dir,

        "message":
            "Repository cloné avec succès."
    }


# ============================================================
# STEP 2 — VERIFY .GIT
# ============================================================

def verify_git_repository(
    project_dir: str
) -> dict:

    print("\n" + "=" * 70)
    print("🔎 STEP 2 — VERIFY .GIT")
    print("=" * 70)

    git_dir = os.path.join(
        project_dir,
        ".git"
    )

    if not os.path.exists(git_dir):

        return {

            "success":
                False,

            "error":
                (
                    "Le projet n'est pas git : "
                    "le dossier .git est absent."
                )
        }

    print(
        "\n✅ .git trouvé."
    )

    return {

        "success":
            True,

        "git_directory":
            git_dir
    }


# ============================================================
# STEP 3 — GIT STATUS
# ============================================================

def get_git_status(
    project_dir: str
) -> dict:

    print("\n" + "=" * 70)
    print("📊 STEP 3 — GIT STATUS")
    print("=" * 70)

    result = run_git_command(

        [
            "git",
            "status"
        ],

        project_dir
    )

    if not result["success"]:

        return {

            "success":
                False,

            "error":
                (
                    "git status a échoué.\n"
                    + result["stderr"]
                ),

            "git_status":
                result["stdout"]
        }

    return {

        "success":
            True,

        "git_status":
            result["stdout"]
    }


# ============================================================
# STEP 4 — FETCH ORIGIN
# ============================================================

def fetch_origin(
    project_dir: str
) -> dict:

    print("\n" + "=" * 70)
    print("🌐 STEP 4 — GIT FETCH ORIGIN")
    print("=" * 70)

    result = run_git_command(

        [
            "git",
            "fetch",
            "origin"
        ],

        project_dir
    )

    if not result["success"]:

        return {

            "success":
                False,

            "error":
                (
                    "git fetch origin a échoué.\n"
                    + result["stderr"]
                )
        }

    print(
        "\n✅ git fetch origin terminé."
    )

    return {

        "success":
            True
    }


# ============================================================
# STEP 5 — DETECT MAIN / MASTER
# ============================================================

def detect_main_branch(
    project_dir: str
) -> dict:

    print("\n" + "=" * 70)
    print("🌿 STEP 5 — DETECT MAIN / MASTER")
    print("=" * 70)

    # ========================================================
    # ORIGIN HEAD
    # ========================================================

    head_result = run_git_command(

        [
            "git",
            "symbolic-ref",
            "--short",
            "refs/remotes/origin/HEAD"
        ],

        project_dir
    )

    if head_result["success"]:

        remote_head = (
            head_result["stdout"]
            .strip()
        )

        if remote_head.startswith(
            "origin/"
        ):

            branch = remote_head[
                len("origin/"):
            ]

            if branch in (
                "main",
                "master"
            ):

                print(
                    f"\n✅ Branche principale : "
                    f"{branch}"
                )

                return {

                    "success":
                        True,

                    "branch":
                        branch
                }

    # ========================================================
    # ORIGIN MAIN
    # ========================================================

    main_result = run_git_command(

        [
            "git",
            "show-ref",
            "--verify",
            "--quiet",
            "refs/remotes/origin/main"
        ],

        project_dir
    )

    if main_result["success"]:

        print(
            "\n✅ Branche principale : main"
        )

        return {

            "success":
                True,

            "branch":
                "main"
        }

    # ========================================================
    # ORIGIN MASTER
    # ========================================================

    master_result = run_git_command(

        [
            "git",
            "show-ref",
            "--verify",
            "--quiet",
            "refs/remotes/origin/master"
        ],

        project_dir
    )

    if master_result["success"]:

        print(
            "\n✅ Branche principale : master"
        )

        return {

            "success":
                True,

            "branch":
                "master"
        }

    return {

        "success":
            False,

        "error":
            (
                "Aucune branche principale "
                "origin/main ou origin/master "
                "n'a été trouvée."
            )
    }


# ============================================================
# STEP 6 — SWITCH MAIN / MASTER
# ============================================================

def switch_to_main_branch(
    project_dir: str,
    base_branch: str
) -> dict:

    print("\n" + "=" * 70)
    print(
        f"🔀 STEP 6 — SWITCH "
        f"{base_branch.upper()}"
    )
    print("=" * 70)

    # ========================================================
    # LOCAL BRANCH
    # ========================================================

    switch_result = run_git_command(

        [
            "git",
            "switch",
            base_branch
        ],

        project_dir
    )

    if switch_result["success"]:

        print(
            f"\n✅ Branche "
            f"{base_branch} sélectionnée."
        )

        return {

            "success":
                True,

            "branch":
                base_branch
        }

    # ========================================================
    # CREATE FROM REMOTE
    # ========================================================

    create_result = run_git_command(

        [
            "git",
            "switch",
            "-c",
            base_branch,
            "--track",
            f"origin/{base_branch}"
        ],

        project_dir
    )

    if not create_result["success"]:

        return {

            "success":
                False,

            "error":
                (
                    f"Impossible de faire "
                    f"git switch {base_branch}.\n"
                    + create_result["stderr"]
                )
        }

    print(
        f"\n✅ Branche "
        f"{base_branch} créée."
    )

    return {

        "success":
            True,

        "branch":
            base_branch
    }


# ============================================================
# STEP 7 — GIT PULL
# ============================================================

def pull_main_branch(
    project_dir: str,
    base_branch: str
) -> dict:

    print("\n" + "=" * 70)
    print(
        f"⬇️ STEP 7 — GIT PULL "
        f"{base_branch.upper()}"
    )
    print("=" * 70)

    result = run_git_command(

        [
            "git",
            "pull",
            "origin",
            base_branch
        ],

        project_dir
    )

    if not result["success"]:

        return {

            "success":
                False,

            "error":
                (
                    f"git pull origin "
                    f"{base_branch} a échoué.\n"
                    + result["stderr"]
                )
        }

    print(
        "\n✅ git pull terminé."
    )

    return {

        "success":
            True
    }


# ============================================================
# STEP 8A — CHECK EXACT REMOTE ISSUE BRANCH
# ============================================================

def remote_issue_branch_exists(
    project_dir: str,
    issue_key: str
) -> dict:
    """
    Vérifie l'existence EXACTE de :

        refs/heads/KAN-1

    Important :

        feature/KAN-1

    NE DOIT PAS être considéré comme :

        KAN-1
    """

    print("\n" + "=" * 70)
    print(
        f"🌐 CHECK REMOTE BRANCH : "
        f"{issue_key}"
    )
    print("=" * 70)

    result = run_git_command(

        [
            "git",
            "ls-remote",
            "--heads",
            "origin",
            f"refs/heads/{issue_key}"
        ],

        project_dir
    )

    if not result["success"]:

        return {

            "success":
                False,

            "exists":
                False,

            "error":
                (
                    "Impossible de vérifier "
                    f"la branche distante {issue_key}.\n"
                    + result["stderr"]
                )
        }

    exists = False

    for line in result["stdout"].splitlines():

        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) >= 2:

            remote_ref = parts[-1]

            if remote_ref == (
                f"refs/heads/{issue_key}"
            ):

                exists = True
                break

    if exists:

        print(
            f"\n✅ Branche distante EXACTE "
            f"'{issue_key}' trouvée."
        )

    else:

        print(
            f"\nℹ️ Branche distante EXACTE "
            f"'{issue_key}' absente."
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
# STEP 8B — ISSUE BRANCH
# ============================================================

def prepare_issue_branch(
    project_dir: str,
    issue_key: str
) -> dict:
    """
    Prépare EXACTEMENT la branche Jira.

    Exemple :

        KAN-1

    Logique :

        remote KAN-1 existe ?
              |
          +---+---+
          |       |
         OUI     NON
          |       |
       switch   créer
       KAN-1    KAN-1
          |       |
          +---+---+
              |
          KAN-1
    """

    print("\n" + "=" * 70)
    print(
        f"🎫 STEP 8 — ISSUE BRANCH : "
        f"{issue_key}"
    )
    print("=" * 70)

    # ========================================================
    # CHECK REMOTE EXACT
    # ========================================================

    remote_result = remote_issue_branch_exists(

        project_dir,
        issue_key
    )

    if not remote_result["success"]:

        return {

            "success":
                False,

            "error":
                remote_result["error"]
        }

    # ========================================================
    # REMOTE EXISTS
    # ========================================================

    if remote_result["exists"]:

        print(
            f"\n🌐 Remote '{issue_key}' existe."
        )

        # ----------------------------------------------------
        # Vérifier si branche locale existe
        # ----------------------------------------------------

        local_result = run_git_command(

            [
                "git",
                "branch",
                "--list",
                issue_key
            ],

            project_dir
        )

        if not local_result["success"]:

            return {

                "success":
                    False,

                "error":
                    (
                        f"Impossible de vérifier "
                        f"la branche locale {issue_key}.\n"
                        + local_result["stderr"]
                    )
            }

        # ----------------------------------------------------
        # LOCAL EXISTS
        # ----------------------------------------------------

        if local_result["stdout"].strip():

            print(
                f"\n✅ Branche locale "
                f"{issue_key} existe."
            )

            switch_result = run_git_command(

                [
                    "git",
                    "switch",
                    issue_key
                ],

                project_dir
            )

            if not switch_result["success"]:

                return {

                    "success":
                        False,

                    "error":
                        (
                            f"Impossible de sélectionner "
                            f"{issue_key}.\n"
                            + switch_result["stderr"]
                        )
                }

            # ------------------------------------------------
            # Synchroniser avec remote
            # ------------------------------------------------

            pull_result = run_git_command(

                [
                    "git",
                    "pull",
                    "--rebase",
                    "origin",
                    issue_key
                ],

                project_dir
            )

            if not pull_result["success"]:

                return {

                    "success":
                        False,

                    "error":
                        (
                            f"Impossible de synchroniser "
                            f"{issue_key} avec GitHub.\n"
                            + pull_result["stderr"]
                        )
                }

            return {

                "success":
                    True,

                "branch":
                    issue_key,

                "created":
                    False
            }

        # ----------------------------------------------------
        # LOCAL ABSENT → TRACK REMOTE
        # ----------------------------------------------------

        print(
            f"\n➡️ Création de la branche locale "
            f"{issue_key} depuis origin/{issue_key}"
        )

        create_result = run_git_command(

            [
                "git",
                "switch",
                "-c",
                issue_key,
                "--track",
                f"origin/{issue_key}"
            ],

            project_dir
        )

        if not create_result["success"]:

            return {

                "success":
                    False,

                "error":
                    (
                        f"Impossible de créer "
                        f"{issue_key} depuis "
                        f"origin/{issue_key}.\n"
                        + create_result["stderr"]
                    )
            }

        return {

            "success":
                True,

            "branch":
                issue_key,

            "created":
                True
        }

    # ========================================================
    # REMOTE DOES NOT EXIST
    # ========================================================

    print(
        f"\nℹ️ Remote '{issue_key}' "
        f"n'existe pas."
    )

    # ========================================================
    # CHECK LOCAL
    # ========================================================

    local_result = run_git_command(

        [
            "git",
            "branch",
            "--list",
            issue_key
        ],

        project_dir
    )

    if not local_result["success"]:

        return {

            "success":
                False,

            "error":
                (
                    f"Impossible de vérifier "
                    f"la branche locale {issue_key}.\n"
                    + local_result["stderr"]
                )
        }

    # ========================================================
    # LOCAL EXISTS
    # ========================================================

    if local_result["stdout"].strip():

        print(
            f"\n⚠️ Branche locale "
            f"{issue_key} existe déjà."
        )

        switch_result = run_git_command(

            [
                "git",
                "switch",
                issue_key
            ],

            project_dir
        )

        if not switch_result["success"]:

            return {

                "success":
                    False,

                "error":
                    (
                        f"Impossible de sélectionner "
                        f"{issue_key}.\n"
                        + switch_result["stderr"]
                    )
            }

        return {

            "success":
                True,

            "branch":
                issue_key,

            "created":
                False
        }

    # ========================================================
    # CREATE NEW LOCAL BRANCH FROM CURRENT MAIN
    # ========================================================

    print(
        f"\n➡️ Création branche "
        f"{issue_key}"
    )

    create_result = run_git_command(

        [
            "git",
            "switch",
            "-c",
            issue_key
        ],

        project_dir
    )

    if not create_result["success"]:

        return {

            "success":
                False,

            "error":
                (
                    f"Impossible de créer "
                    f"{issue_key}.\n"
                    + create_result["stderr"]
                )
        }

    print(
        f"\n✅ Branche "
        f"{issue_key} créée depuis "
        f"la branche principale."
    )

    return {

        "success":
            True,

        "branch":
            issue_key,

        "created":
            True
    }


# ============================================================
# MAIN GIT AGENT
# ============================================================

def git_agent(
    state
) -> dict:

    print("\n" + "=" * 80)
    print("🤖 GIT PREPARATION AGENT")
    print("=" * 80)

    # ========================================================
    # 1. ISSUE KEY
    # ========================================================

    issue_key = state.get(
        "issue_key"
    )

    if not issue_key:

        return git_error_state(

            None,

            state.get(
                "github_url"
            ),

            None,

            "Issue key manquante."
        )

    issue_key = str(
        issue_key
    ).strip().upper()

    # ========================================================
    # 2. GITHUB URL
    # ========================================================

    github_url = state.get(
        "github_url"
    )

    if not github_url:

        return git_error_state(

            None,

            None,

            issue_key,

            "URL GitHub manquante."
        )

    github_url = str(
        github_url
    ).strip()

    print(
        f"\n🎫 Issue : {issue_key}"
    )

    print(
        f"🔗 GitHub : {github_url}"
    )

    # ========================================================
    # 3. PROJECT DIRECTORY
    # ========================================================

    project_dir = get_project_dir()

    if not project_dir:

        return git_error_state(

            None,

            github_url,

            issue_key,

            (
                "OPENCODE_PROJECT_DIR "
                "n'est pas défini dans .env."
            )
        )

    print(
        f"📁 Project : {project_dir}"
    )

    # ========================================================
    # 4. CLONE
    # ========================================================

    clone_result = clone_repository(
        github_url
    )

    if not clone_result["success"]:

        return git_error_state(

            project_dir,

            github_url,

            issue_key,

            clone_result.get(
                "error",
                "git clone a échoué."
            )
        )

    # ========================================================
    # 5. VERIFY .GIT
    # ========================================================

    verify_result = verify_git_repository(
        project_dir
    )

    if not verify_result["success"]:

        return git_error_state(

            project_dir,

            github_url,

            issue_key,

            verify_result.get(
                "error",
                "Le projet n'est pas git."
            )
        )

    # ========================================================
    # 6. STATUS
    # ========================================================

    status_result = get_git_status(
        project_dir
    )

    if not status_result["success"]:

        return git_error_state(

            project_dir,

            github_url,

            issue_key,

            status_result.get(
                "error",
                "git status a échoué."
            ),

            status_result.get(
                "git_status",
                ""
            )
        )

    git_status = status_result[
        "git_status"
    ]

    # ========================================================
    # 7. FETCH
    # ========================================================

    fetch_result = fetch_origin(
        project_dir
    )

    if not fetch_result["success"]:

        return git_error_state(

            project_dir,

            github_url,

            issue_key,

            fetch_result.get(
                "error",
                "git fetch origin a échoué."
            ),

            git_status
        )

    # ========================================================
    # 8. MAIN / MASTER
    # ========================================================

    branch_result = detect_main_branch(
        project_dir
    )

    if not branch_result["success"]:

        return git_error_state(

            project_dir,

            github_url,

            issue_key,

            branch_result.get(
                "error",
                "Impossible de détecter main/master."
            ),

            git_status
        )

    base_branch = branch_result[
        "branch"
    ]

    # ========================================================
    # 9. SWITCH MAIN / MASTER
    # ========================================================

    switch_result = switch_to_main_branch(

        project_dir,

        base_branch
    )

    if not switch_result["success"]:

        return git_error_state(

            project_dir,

            github_url,

            issue_key,

            switch_result.get(
                "error",
                "Impossible de sélectionner main/master."
            ),

            git_status,

            base_branch
        )

    # ========================================================
    # 10. PULL MAIN / MASTER
    # ========================================================

    pull_result = pull_main_branch(

        project_dir,

        base_branch
    )

    if not pull_result["success"]:

        return git_error_state(

            project_dir,

            github_url,

            issue_key,

            pull_result.get(
                "error",
                "git pull a échoué."
            ),

            git_status,

            base_branch
        )

    # ========================================================
    # 11. ISSUE BRANCH
    # ========================================================

    issue_result = prepare_issue_branch(

        project_dir,

        issue_key
    )

    if not issue_result["success"]:

        return git_error_state(

            project_dir,

            github_url,

            issue_key,

            issue_result.get(
                "error",
                "Impossible de préparer la branche Jira."
            ),

            git_status,

            base_branch
        )

    final_branch = issue_result[
        "branch"
    ]

    branch_created = issue_result[
        "created"
    ]

    # ========================================================
    # 12. FINAL STATUS
    # ========================================================

    final_status_result = run_git_command(

        [
            "git",
            "status",
            "--short"
        ],

        project_dir
    )

    final_status = ""

    if final_status_result["success"]:

        final_status = (
            final_status_result["stdout"]
        )

    # ========================================================
    # SUCCESS
    # ========================================================

    print("\n" + "=" * 80)
    print("✅ GIT PREPARATION TERMINÉE")
    print("=" * 80)

    print(
        f"\n📁 Project : {project_dir}"
    )

    print(
        f"🔗 GitHub  : {github_url}"
    )

    print(
        f"🌿 Base    : {base_branch}"
    )

    print(
        f"🎫 Issue   : {final_branch}"
    )

    print(
        f"🆕 Created : {branch_created}"
    )

    print(
        "\n🚀 OpenCode peut maintenant travailler."
    )

    print(
        "\n✅ git_ready = True"
    )

    return {

        "git_ready":
            True,

        "project_dir":
            project_dir,

        "github_url":
            github_url,

        "repository_url":
            github_url,

        "issue_key":
            issue_key,

        "git_status":
            final_status,

        "git_branch":
            final_branch,

        "git_branch_created":
            branch_created,

        "git_base_branch":
            base_branch,

        "git_error":
            None,

        "error":
            None
    }


# ============================================================
# END OF FILE
# ============================================================