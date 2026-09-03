# ============================================================
# api/main.py
#
# FASTAPI API
#
# ============================================================

from typing import Any

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.exceptions import (
    RequestValidationError
)

from fastapi.responses import (
    JSONResponse
)

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)


# ============================================================
# AGENTS
# ============================================================

from agents.jira_agent_vf import (
    jira_agent_vf
)
import traceback

from agents.analysis_agent import (
    analysis_agent
)

from agents.prompt_agent import (
    prompt_agent
)


# ============================================================
# WORKFLOWS
# ============================================================

from graph.workflow import (
    build_git_prepare_graph,
    build_prompt_graph,
    build_opencode_graph,
    build_git_deploy_graph,
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(

    title=
        "Jira AI Multi-Agent API",

    description=
        (
            "Jira AI Multi-Agent System "
            "with Git, OpenCode and Git Deploy workflows."
        ),

    version=
        "2.3.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:4200",

        "http://127.0.0.1:4200",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# VALIDATION ERROR HANDLER
# ============================================================

@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(

    request: Request,

    exc: RequestValidationError,

):

    print("\n" + "=" * 70)

    print(
        "❌ FASTAPI VALIDATION ERROR — 422"
    )

    print("=" * 70)

    print(
        f"\n📍 Method : "
        f"{request.method}"
    )

    print(
        f"📍 URL : "
        f"{request.url}"
    )

    print(
        "\n📦 Erreurs :"
    )

    for error in exc.errors():

        print(
            "--------------------------------------------------"
        )

        print(
            error
        )

    print(
        "\n📦 BODY ATTENDU :"
    )

    print(
        """
{
    "issue_key": "KAN-1",
    "github_url": "https://github.com/owner/repository.git"
}
        """
    )

    print("=" * 70)

    return JSONResponse(

        status_code=422,

        content={

            "success":
                False,

            "error":
                "Request validation failed.",

            "message":
                (
                    "Le JSON envoyé ne correspond "
                    "pas au modèle attendu."
                ),

            "path":
                str(request.url),

            "method":
                request.method,

            "details":
                exc.errors(),
        },
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "message":
            "Jira AI Multi-Agent API",

        "status":
            "running",

        "version":
            "2.3.0",

        "workflows": {

            "A":
                "GitHub URL → Git Agent → Clone → Git Preparation",

            "B":
                "Jira → Analysis → Prompt",

            "C":
                "Git Deploy → Commit → Push → Pull Request",

            "D":
                "OpenCode",
        },
    }


# ============================================================
# WORKFLOW A
#
# GIT PREPARATION
# ============================================================

class GitPrepareRequest(
    BaseModel
):

    """
    Request du Workflow A.

    JSON :

    {
        "issue_key": "KAN-1",
        "github_url":
            "https://github.com/owner/repository.git"
    }
    """

    model_config = ConfigDict(
        extra="ignore"
    )

    issue_key: str = Field(

        ...,

        min_length=1,

        description=
            "Clé Jira, exemple KAN-1",
    )

    github_url: str = Field(

        ...,

        min_length=1,

        description=
            "URL du repository GitHub",
    )


@app.post(
    "/api/git/prepare"
)
def prepare_git_repository(

    request: GitPrepareRequest,

):

    """
    ========================================================
    WORKFLOW A — GIT PREPARATION
    ========================================================

        Frontend
            ↓
        POST /api/git/prepare
            ↓
        Git Agent
            ↓
        git clone
            ↓
        dossier local
            ↓
        git status
            ↓
        .git ?
          /      \
        OUI      NON
         ↓        ↓
      continuer  ERROR
         ↓
      git fetch
         ↓
    main / master
         ↓
    switch main/master
         ↓
       git pull
         ↓
    issue branch
         ↓
    git_ready=True

    ========================================================

    Aucun :

        ❌ OpenCode
        ❌ git init
        ❌ git add
        ❌ git commit
        ❌ git push
        ❌ Pull Request
    """

    try:

        print("\n" + "=" * 80)

        print(
            "🔧 WORKFLOW A — GIT PREPARATION"
        )

        print("=" * 80)

        # ====================================================
        # REQUEST
        # ====================================================

        print(
            "\n📦 Request :"
        )

        print(
            request.model_dump()
        )

        # ====================================================
        # ISSUE
        # ====================================================

        issue_key = (
            request.issue_key
            .strip()
            .upper()
        )

        if not issue_key:

            raise HTTPException(

                status_code=400,

                detail=
                    "Issue key manquante."
            )

        # ====================================================
        # GITHUB URL
        # ====================================================

        github_url = (
            request.github_url
            .strip()
        )

        if not github_url:

            raise HTTPException(

                status_code=400,

                detail=
                    "URL GitHub manquante."
            )

        print(
            f"\n🎫 Issue : {issue_key}"
        )

        print(
            f"🔗 GitHub : {github_url}"
        )

        # ====================================================
        # INITIAL STATE
        # ====================================================

        initial_state = {

            "issue_key":
                issue_key,

            "github_url":
                github_url,
        }

        print(
            "\n📦 Initial State :"
        )

        print(
            initial_state
        )

        # ====================================================
        # BUILD GRAPH
        # ====================================================

        workflow = (
            build_git_prepare_graph()
        )

        if workflow is None:

            raise RuntimeError(

                "build_git_prepare_graph() "
                "a retourné None."
            )

        # ====================================================
        # EXECUTE
        # ====================================================

        print(
            "\n🚀 Exécution du Git Agent..."
        )

        result = workflow.invoke(
            initial_state
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(

                "Le Workflow A "
                "n'a pas retourné un dictionnaire."
            )

        print(
            "\n📦 Result :"
        )

        print(
            result
        )

        # ====================================================
        # VALUES
        # ====================================================

        git_ready = result.get(
            "git_ready",
            False
        )

        project_dir = result.get(
            "project_dir"
        )

        git_branch = result.get(
            "git_branch"
        )

        git_base_branch = result.get(
            "git_base_branch"
        )

        git_branch_created = result.get(
            "git_branch_created",
            False
        )

        git_status = result.get(
            "git_status"
        )

        git_error = result.get(
            "git_error"
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        if git_ready:

            print("\n" + "=" * 80)

            print(
                "✅ WORKFLOW A TERMINÉ"
            )

            print("=" * 80)

            return {

                "success":
                    True,

                "workflow":
                    "A",

                "stage":
                    "git_prepare",

                "issue_key":
                    issue_key,

                "github_url":
                    result.get(
                        "github_url",
                        github_url
                    ),

                "repository_url":
                    result.get(
                        "repository_url",
                        github_url
                    ),

                "project_dir":
                    project_dir,

                "git_ready":
                    True,

                "git_base_branch":
                    git_base_branch,

                "git_branch":
                    git_branch,

                "git_branch_created":
                    git_branch_created,

                "git_status":
                    git_status,

                "git_error":
                    None,

                "next_step":
                    "Workflow D — OpenCode",
            }

        # ====================================================
        # FAILURE
        # ====================================================

        print("\n" + "=" * 80)

        print(
            "❌ WORKFLOW A ÉCHOUÉ"
        )

        print("=" * 80)

        return {

            "success":
                False,

            "workflow":
                "A",

            "stage":
                "git_prepare",

            "issue_key":
                issue_key,

            "github_url":
                result.get(
                    "github_url",
                    github_url
                ),

            "repository_url":
                result.get(
                    "repository_url",
                    github_url
                ),

            "project_dir":
                project_dir,

            "git_ready":
                False,

            "git_base_branch":
                git_base_branch,

            "git_branch":
                git_branch,

            "git_branch_created":
                git_branch_created,

            "git_status":
                git_status,

            "git_error":
                git_error,

            "next_step":
                None,
        }

    except HTTPException:

        raise

    except Exception as e:

        print("\n" + "=" * 80)

        print(
            "❌ ERREUR WORKFLOW A"
        )

        print("=" * 80)

        print(
            f"\n{type(e).__name__}: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ============================================================
# WORKFLOW B — STEP 1
#
# JIRA
# ============================================================

@app.get(
    "/api/jira/{issue_key}"
)
async def get_jira_ticket(

    issue_key: str,
):

    try:

        issue_key = (
            issue_key
            .strip()
            .upper()
        )

        if not issue_key:

            raise HTTPException(

                status_code=400,

                detail=
                    "Issue key manquante."
            )

        state = {

            "issue_key":
                issue_key
        }

        result = await jira_agent_vf(
            state
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(

                "jira_agent_vf() "
                "n'a pas retourné un dictionnaire."
            )

        ticket = result.get(
            "ticket"
        )

        if not ticket:

            raise ValueError(
                "Aucun ticket Jira retourné."
            )

        return ticket

    except HTTPException:

        raise

    except Exception as e:

        print(
            f"\n❌ Erreur Jira : {e}"
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ============================================================
# WORKFLOW B — STEP 2
#
# ANALYSIS
# ============================================================

class AnalysisRequest(
    BaseModel
):

    ticket: dict[str, Any]


@app.post(
    "/api/analysis"
)
def analyze_ticket(

    request: AnalysisRequest,
):

    try:

        ticket = request.ticket

        if not ticket:

            raise HTTPException(

                status_code=400,

                detail=
                    "Ticket manquant."
            )

        state = {

            "ticket":
                ticket
        }

        result = analysis_agent(
            state
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(

                "analysis_agent() "
                "n'a pas retourné un dictionnaire."
            )

        analysis = result.get(
            "analysis"
        )

        if not analysis:

            raise ValueError(
                "L'analyse n'a pas été générée."
            )

        return {

            "workflow":
                "B",

            "stage":
                "analysis",

            "ticket":
                ticket,

            "analysis":
                analysis,
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ============================================================
# WORKFLOW B — STEP 3
#
# PROMPT
# ============================================================

class PromptRequest(
    BaseModel
):

    ticket: dict[str, Any]

    analysis: str


@app.post(
    "/api/prompt"
)
def generate_prompt(

    request: PromptRequest,
):

    try:

        ticket = request.ticket

        analysis = request.analysis

        if not ticket:

            raise HTTPException(

                status_code=400,

                detail=
                    "Ticket manquant."
            )

        if not analysis:

            raise HTTPException(

                status_code=400,

                detail=
                    "Analysis manquante."
            )

        state = {

            "ticket":
                ticket,

            "analysis":
                analysis,
        }

        result = prompt_agent(
            state
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(

                "prompt_agent() "
                "n'a pas retourné un dictionnaire."
            )

        prompt = result.get(
            "coding_instruction"
        )

        if not prompt:

            raise ValueError(
                "Le prompt n'a pas été généré."
            )

        return {

            "workflow":
                "B",

            "stage":
                "prompt",

            "ticket":
                ticket,

            "analysis":
                analysis,

            "prompt":
                prompt,
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ============================================================
# WORKFLOW D — OPENCODE
# ============================================================

class OpenCodeRequest(
    BaseModel
):

    issue_key: str = Field(

        ...,

        min_length=1
    )

    prompt: str = Field(

        ...,

        min_length=1
    )

    github_url: str | None = None

    project_dir: str | None = None


@app.post(
    "/api/opencode/execute"
)
def execute_opencode(

    request: OpenCodeRequest,
):

    try:

        issue_key = (
            request.issue_key
            .strip()
            .upper()
        )

        prompt = (
            request.prompt
            .strip()
        )

        if not issue_key:

            raise HTTPException(

                status_code=400,

                detail=
                    "Issue key manquante."
            )

        if not prompt:

            raise HTTPException(

                status_code=400,

                detail=
                    "Prompt manquant."
            )

        initial_state = {

            "issue_key":
                issue_key,

            "github_url":
                request.github_url,

            "project_dir":
                request.project_dir,

            "coding_instruction":
                prompt,
        }

        workflow = (
            build_opencode_graph()
        )

        result = workflow.invoke(
            initial_state
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(

                "Le Workflow D "
                "n'a pas retourné un dictionnaire."
            )

        return_code = result.get(
            "opencode_return_code"
        )

        success = (
            return_code == 0
        )

        return {

            "success":
                success,

            "workflow":
                "D",

            "stage":
                "opencode",

            "issue_key":
                issue_key,

            "prompt":
                prompt,

            "project_dir":
                result.get(
                    "project_dir",
                    request.project_dir
                ),

            "opencode_executed":
                True,

            "opencode_result":
                result.get(
                    "opencode_result"
                ),

            "return_code":
                return_code,

            "next_step":
                (
                    "Workflow C — Git Deploy"
                    if success
                    else None
                ),
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            f"\n❌ Erreur OpenCode : {e}"
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ============================================================
# WORKFLOW C — GIT DEPLOY
# ============================================================

class GitDeployRequest(
    BaseModel
):

    issue_key: str = Field(

        ...,

        min_length=1
    )

    github_url: str | None = None

    project_dir: str | None = None


@app.post(
    "/api/git/deploy"
)
def deploy_git_repository(

    request: GitDeployRequest,
):

    try:

        issue_key = (
            request.issue_key
            .strip()
            .upper()
        )

        if not issue_key:

            raise HTTPException(

                status_code=400,

                detail=
                    "Issue key manquante."
            )

        initial_state = {

            "issue_key":
                issue_key,

            "github_url":
                request.github_url,

            "project_dir":
                request.project_dir,
        }

        workflow = (
            build_git_deploy_graph()
        )

        result = workflow.invoke(
            initial_state
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(

                "Le Workflow C "
                "n'a pas retourné un dictionnaire."
            )

        deploy_success = result.get(
            "git_deploy_success",
            False
        )

        return {

            "success":
                deploy_success,

            "workflow":
                "C",

            "stage":
                "git_deploy",

            "issue_key":
                issue_key,

            "github_url":
                result.get(
                    "github_url",
                    request.github_url
                ),

            "project_dir":
                result.get(
                    "project_dir",
                    request.project_dir
                ),

            "git_branch":
                result.get(
                    "git_branch"
                ),

            "git_status":
                result.get(
                    "git_status"
                ),

            "commit_message":
                result.get(
                    "commit_message"
                ),

            "commit_success":
                result.get(
                    "commit_success",
                    False
                ),

            "push_success":
                result.get(
                    "push_success",
                    False
                ),

            "pull_request_url":
                result.get(
                    "pull_request_url"
                ),

            "git_deploy_skipped":
                result.get(
                    "git_deploy_skipped",
                    False
                ),

            "git_deploy_error":
                result.get(
                    "git_deploy_error"
                ),

            "message":
                result.get(
                    "message"
                ),
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            f"\n❌ Erreur Workflow C : {e}"
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ============================================================
# ORCHESTRATOR — WORKFLOW B
# ============================================================

@app.get(
    "/api/agents/{issue_key}"
)
async def run_agents(

    issue_key: str,
):

    try:

        issue_key = (
            issue_key
            .strip()
            .upper()
        )

        if not issue_key:

            raise HTTPException(

                status_code=400,

                detail=
                    "Issue key manquante."
            )

        workflow = (
            build_prompt_graph()
        )

        initial_state = {

            "issue_key":
                issue_key
        }

        result = await workflow.ainvoke(
            initial_state
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(

                "Le Workflow B "
                "n'a pas retourné un dictionnaire."
            )

        return {

            "success":
                True,

            "workflow":
                "B",

            "mode":
                "orchestrator",

            "issue_key":
                result.get(
                    "issue_key"
                ),

            "ticket":
                result.get(
                    "ticket"
                ),

            "analysis":
                result.get(
                    "analysis"
                ),

                       "prompt":
                result.get(
                    "coding_instruction"
                ),

            "complexity":
                result.get(
                    "complexity"
                ),

            "subtasks":
                result.get(
                    "subtasks"
                ),

            "next_step":
                (
                    "Workflow A — Git Preparation "
                    "→ Workflow D — OpenCode "
                    "→ Workflow C — Git Deploy"
                ),
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            f"\n❌ Erreur Workflow B : {e}"
        )
        traceback.print_exc()

        status_code = 503 if str(e).startswith(
            "MCP_WRITE_TOOLS_UNAVAILABLE:"
        ) else 500

        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health"
)
def health_check():

    return {

        "status":
            "ok",

        "api":
            "running",

        "version":
            "2.3.0",
    }


# ============================================================
# END OF FILE
# ============================================================