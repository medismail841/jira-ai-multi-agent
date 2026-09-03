# ============================================================
# graph/visualize_workflow.py
#
# VISUALIZATION OF LANGGRAPH WORKFLOWS
# ============================================================

from graph.workflow import (
    build_git_prepare_graph,
    build_prompt_graph,
    build_git_deploy_graph,
    build_opencode_graph,
    build_main_graph,
)


# ============================================================
# FUNCTION
# ============================================================

def save_workflow_png(workflow, filename):
    """
    Generate a PNG image from a LangGraph workflow.
    """

    png_data = (
        workflow
        .get_graph()
        .draw_mermaid_png()
    )

    with open(filename, "wb") as f:
        f.write(png_data)

    print(f"✅ {filename} créé")


# ============================================================
# WORKFLOW A
#
# GIT PREPARATION
# ============================================================

print()
print("========================================")
print("     WORKFLOW A — GIT PREPARATION")
print("========================================")

git_prepare_workflow = build_git_prepare_graph()

save_workflow_png(
    git_prepare_workflow,
    "git_prepare_workflow.png"
)


# ============================================================
# WORKFLOW A — DETAIL
#
# This is a conceptual diagram showing the
# internal Git logic.
# ============================================================

print()
print("========================================")
print("     WORKFLOW A — GIT PREPARATION — DETAIL")
print("========================================")

git_prepare_diagram = """
flowchart TD

    A["GitHub URL"]

    B["GIT AGENT"]

    C["git clone"]

    D["Dossier local"]

    E["git status"]

    F{".git existe ?"}

    G["Continuer"]

    H["ERROR<br/>Le projet n'est pas Git"]

    I["git fetch origin"]

    J["Détecter main / master"]

    K["git switch main / master"]

    L["git pull origin main / master"]

    M["Vérifier branche ISSUE"]

    N["Créer / switch ISSUE"]

    O["git_ready = True"]


    A --> B
    B --> C
    C --> D
    D --> E
    E --> F

    F -->|OUI| G
    F -->|NON| H

    G --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
"""

print(git_prepare_diagram)


# ============================================================
# WORKFLOW B
#
# JIRA → ANALYSIS → PROMPT
# ============================================================

print()
print("========================================")
print("     WORKFLOW B — JIRA → ANALYSIS → PROMPT")
print("========================================")

prompt_workflow = build_prompt_graph()

save_workflow_png(
    prompt_workflow,
    "prompt_workflow.png"
)


# ============================================================
# WORKFLOW B — DETAIL
# ============================================================

print()
print("========================================")
print("     WORKFLOW B — DETAIL")
print("========================================")

prompt_diagram = """
flowchart TD

    A["START"]

    B["JIRA AGENT"]

    C["ANALYSIS AGENT"]

    D["PROMPT AGENT"]

    E["END"]


    A --> B
    B --> C
    C --> D
    D --> E
"""

print(prompt_diagram)


# ============================================================
# WORKFLOW C
#
# GIT DEPLOY
# ============================================================

print()
print("========================================")
print("     WORKFLOW C — GIT DEPLOY")
print("========================================")

git_deploy_workflow = build_git_deploy_graph()

save_workflow_png(
    git_deploy_workflow,
    "git_deploy_workflow.png"
)


# ============================================================
# WORKFLOW C — DETAIL
# ============================================================

print()
print("========================================")
print("     WORKFLOW C — DETAIL")
print("========================================")

git_deploy_diagram = """
flowchart TD

    A["START"]

    B["GIT DEPLOY AGENT"]

    C["git status"]

    D["git add ."]

    E["git commit"]

    F["git push"]

    G["Pull Request"]

    H["END"]


    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
"""

print(git_deploy_diagram)


# ============================================================
# WORKFLOW D
#
# OPENCODE
# ============================================================

print()
print("========================================")
print("     WORKFLOW D — OPENCODE")
print("========================================")

opencode_workflow = build_opencode_graph()

save_workflow_png(
    opencode_workflow,
    "opencode_workflow.png"
)


# ============================================================
# WORKFLOW D — DETAIL
# ============================================================

print()
print("========================================")
print("     WORKFLOW D — DETAIL")
print("========================================")

opencode_diagram = """
flowchart TD

    A["START"]

    B["OPENCODE AGENT"]

    C["Inspect project"]

    D["Modify code"]

    E["Run checks"]

    F["END"]


    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
"""

print(opencode_diagram)


# ============================================================
# GLOBAL WORKFLOW
#
# ALL AGENTS TOGETHER
# ============================================================

print()
print("========================================")
print("     GLOBAL WORKFLOW — ALL AGENTS")
print("========================================")

main_workflow = build_main_graph()

save_workflow_png(
    main_workflow,
    "main_workflow.png"
)


# ============================================================
# GLOBAL WORKFLOW — DETAIL
#
# Shows the complete order between agents.
# ============================================================

print()
print("========================================")
print("     GLOBAL WORKFLOW — DETAIL")
print("========================================")

main_diagram = """
flowchart TD

    A["START"]

    B["GIT AGENT"]

    C["JIRA AGENT"]

    D["ANALYSIS AGENT"]

    E["PROMPT AGENT"]

    F["OPENCODE AGENT"]

    G["GIT DEPLOY AGENT"]

    H["END"]


    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
"""

print(main_diagram)


# ============================================================
# SUMMARY
# ============================================================

print()
print("========================================")
print("     VISUALIZATION TERMINÉE")
print("========================================")

print()
print("Fichiers générés :")

print("  ✅ git_prepare_workflow.png")
print("  ✅ prompt_workflow.png")
print("  ✅ git_deploy_workflow.png")
print("  ✅ opencode_workflow.png")
print("  ✅ main_workflow.png")

print()
print("Architecture globale :")

print("""
START
  ↓
GIT AGENT
  ↓
JIRA AGENT
  ↓
ANALYSIS AGENT
  ↓
PROMPT AGENT
  ↓
OPENCODE AGENT
  ↓
GIT DEPLOY AGENT
  ↓
END
""")