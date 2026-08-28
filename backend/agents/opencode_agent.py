import os
import shutil
import subprocess

from dotenv import load_dotenv

from graph.state import AgentState


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(override=True)


# ============================================================
# OPENCODE CONFIGURATION
# ============================================================

OPENCODE_MODEL = os.getenv(

    "OPENCODE_MODEL",

    "opencode/big-pickle"

)


OPENCODE_PROJECT_DIR = os.getenv(
    "OPENCODE_PROJECT_DIR"
)


if not OPENCODE_PROJECT_DIR:

    raise ValueError(
        """
❌ OPENCODE_PROJECT_DIR n'est pas défini.
"""
    )


OPENCODE_PROJECT_DIR = os.path.abspath(

    os.path.expandvars(
        OPENCODE_PROJECT_DIR
    )

)


if not os.path.isdir(
    OPENCODE_PROJECT_DIR
):

    raise ValueError(

        f"""
❌ Le projet OpenCode n'existe pas :

{OPENCODE_PROJECT_DIR}
"""

    )

# ============================================================
# FIND OPENCODE
# ============================================================

def find_opencode():

    commands = [

        "opencode",
        "opencode.cmd",
        "opencode.exe",

    ]


    for command in commands:

        path = shutil.which(
            command
        )


        if path:

            return path


    return None


OPENCODE_COMMAND = find_opencode()


if not OPENCODE_COMMAND:

    raise RuntimeError(
        """
❌ OpenCode n'a pas été trouvé dans le PATH.

Teste :

opencode --version

Puis :

where.exe opencode
"""
    )


# ============================================================
# OPENCODE AGENT
# ============================================================

def opencode_agent(
    state: AgentState
) -> AgentState:

    """
    LangGraph Node 4.

    Coding instruction
          ↓
       OpenCode
          ↓
       Project
    """

    coding_instruction = state.get(
        "coding_instruction"
    )


    issue_key = state.get(
        "issue_key",
        ""
    )


    if not coding_instruction:

        raise ValueError(
            "❌ Coding instruction manquante."
        )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "🚀 AGENT 4 — OPENCODE"
    )

    print(
        "=" * 60
    )


    print(
        f"\n📁 Projet :"
    )

    print(
        OPENCODE_PROJECT_DIR
    )


    print(
        f"\n🤖 Modèle :"
    )

    print(
        OPENCODE_MODEL
    )


    # ========================================================
    # SAVE PROMPT
    # ========================================================

    prompt_file = os.path.join(

        OPENCODE_PROJECT_DIR,

        f"jira_{issue_key}_prompt.md"

    )


    with open(

        prompt_file,

        "w",

        encoding="utf-8"

    ) as file:

        file.write(
            coding_instruction
        )


    print(
        "\n💾 Instruction sauvegardée :"
    )

    print(
        prompt_file
    )


    # ========================================================
    # MESSAGE
    # ========================================================

    opencode_message = (
    "Read the attached Jira coding instruction "
    "and implement it in the current project. "
    "First inspect the project. "
    "Then make the necessary changes. "
    "IMPORTANT: All main implementation code must be written directly inside `main.py` " # <-- Contrainte stricte
    "unless explicitly instructed otherwise in the prompt file. "
    "Run the relevant tests or commands. "
    "Verify the acceptance criteria. "
    "Do not create unnecessary extra files. "
    "Execute the task directly and report the results."
)


    # ========================================================
    # COMMAND
    # ========================================================

    command = [

        OPENCODE_COMMAND,

        "run",

        "--model",
        OPENCODE_MODEL,

        "--auto",

        "--dir",
        OPENCODE_PROJECT_DIR,

        opencode_message,

        "--file",
        prompt_file,

    ]


    print(
        "\n📨 Lancement OpenCode..."
    )


    print(
        "=" * 60
    )


    # ========================================================
    # EXECUTE
    # ========================================================

    try:

        process = subprocess.Popen(

            command,

            cwd=OPENCODE_PROJECT_DIR,

            stdout=subprocess.PIPE,

            stderr=subprocess.STDOUT,

            text=True,

            encoding="utf-8",

            errors="replace",

            bufsize=1,

        )

    except Exception as e:

        raise RuntimeError(

            f"""
❌ Impossible de lancer OpenCode :

{e}
"""

        )


    output_lines = []


    if process.stdout:

        for line in process.stdout:

            print(
                line,
                end=""
            )

            output_lines.append(
                line
            )


    return_code = process.wait()


    output = "".join(
        output_lines
    )


    print(
        "\n"
        + "=" * 60
    )


    if return_code == 0:

        print(
            "✅ OpenCode terminé avec succès."
        )

    else:

        print(

            f"❌ OpenCode terminé avec "
            f"le code {return_code}"

        )


    print(
        "=" * 60
    )


    # ========================================================
    # STATE
    # ========================================================

    return {

        "opencode_result":
            output,

        "opencode_return_code":
            return_code,

    }