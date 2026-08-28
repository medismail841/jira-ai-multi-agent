import subprocess
from pathlib import Path


# ============================================================
# EXECUTE GIT COMMAND
# ============================================================

def run_git(
    project_dir: str,
    *args: str
) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=project_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
        )

    return result.stdout.strip()


# ============================================================
# CHECK .GIT
# ============================================================

def git_exists(
    project_dir: str
) -> bool:
    git_path = (
        Path(project_dir) / ".git"
    )

    return git_path.exists()


# ============================================================
# CHECK LOCAL DIRECTORY
# ============================================================

def is_directory_empty(
    project_dir: str
) -> bool:
    path = Path(project_dir)

    return not any(
        path.iterdir()
    )


# ============================================================
# GIT STATUS
# ============================================================

def git_status(
    project_dir: str
) -> str:
    return run_git(
        project_dir,
        "status",
        "--short"
    )


# ============================================================
# GIT CURRENT BRANCH
# ============================================================

def git_current_branch(
    project_dir: str
) -> str:
    return run_git(
        project_dir,
        "branch",
        "--show-current"
    )


# ============================================================
# GIT REMOTE
# ============================================================

def git_remote(
    project_dir: str
) -> str:
    return run_git(
        project_dir,
        "remote",
        "-v"
    )


# ============================================================
# GIT INIT
# ============================================================

def git_init(
    project_dir: str
) -> str:
    return run_git(
        project_dir,
        "init"
    )


# ============================================================
# GIT ADD
# ============================================================

def git_add_all(
    project_dir: str
) -> str:
    return run_git(
        project_dir,
        "add",
        "."
    )


# ============================================================
# GIT COMMIT
# ============================================================

def git_commit(
    project_dir: str,
    message: str
) -> str:
    return run_git(
        project_dir,
        "commit",
        "-m",
        message
    )


# ============================================================
# CREATE BRANCH
# ============================================================

def git_create_branch(
    project_dir: str,
    branch_name: str
) -> str:
    return run_git(
        project_dir,
        "checkout",
        "-b",
        branch_name
    )


# ============================================================
# GIT PUSH
# ============================================================

def git_push(
    project_dir: str,
    remote: str,
    branch: str
) -> str:
    return run_git(
        project_dir,
        "push",
        "-u",
        remote,
        branch
    )