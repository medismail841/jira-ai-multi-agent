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
# JIRA → ANALYSIS → CLASSIFICATION
# ============================================================

print()
print("========================================")
print("     WORKFLOW B — JIRA → ANALYSIS")
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

    D{"Classification"}

    E["PROMPT AGENT"]

    F["SPLIT TICKET"]

    G["Create Jira subtasks"]

    H["END"]


    A --> B
    B --> C
    C --> D

    D -->|SIMPLE| E
    D -->|COMPLEX| F

    E --> H

    F --> G
    G --> H
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
# GLOBAL ARCHITECTURE
#
# CONCEPTUAL VIEW
# ============================================================

print()
print("========================================")
print("     GLOBAL ARCHITECTURE")
print("========================================")

main_diagram = """
flowchart TD

    A["WORKFLOW B<br/>JIRA"]

    B["ANALYSIS"]

    C{"Classification"}

    D["PROMPT AGENT"]

    E["WORKFLOW A<br/>GIT PREPARATION"]

    F["WORKFLOW D<br/>OPENCODE"]

    G["WORKFLOW C<br/>GIT DEPLOY"]

    H["Pull Request"]


    A --> B
    B --> C

    C -->|SIMPLE| D
    D --> E

    E --> F
    F --> G
    G --> H

    C -->|COMPLEX| I["SPLIT TICKET"]
    I --> J["Jira Subtasks"]
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

print()
print("Architecture globale :")

print("""
                    WORKFLOW B
               JIRA → ANALYSIS
                      ↓
                 CLASSIFICATION
                 /            \\
            SIMPLE            COMPLEX
               ↓                 ↓
        PROMPT AGENT      SPLIT TICKET
               ↓                 ↓
        WORKFLOW A         Jira Subtasks
        GIT PREPARE
               ↓
        WORKFLOW D
          OPENCODE
               ↓
        WORKFLOW C
         GIT DEPLOY
               ↓
          Pull Request
""")


# ============================================================
# END OF FILE
# ============================================================