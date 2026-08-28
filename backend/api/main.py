# ============================================================
# FASTAPI — JIRA AI MULTI-AGENT API
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================
# AGENTS
# ============================================================

from agents.jira_agent_vf import jira_agent_vf
from agents.analysis_agent import analysis_agent
from agents.prompt_agent import prompt_agent

# ============================================================
# LANGGRAPH WORKFLOWS
# ============================================================

from graph.workflow import (
    build_prompt_graph,
    build_opencode_graph,
    build_git_graph,
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Jira AI Multi-Agent API",
    description="Jira AI Multi-Agent System",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Jira AI Multi-Agent API",
        "status": "running",
    }


# ============================================================
# ============================================================
# MODE STEP BY STEP
# ============================================================
# ============================================================


# ============================================================
# STEP 1 — JIRA
#
# GET /api/jira/KAN-1
#
# Agent 1 uniquement
# ============================================================

@app.get("/api/jira/{issue_key}")
async def get_jira_ticket(issue_key: str):

    try:

        issue_key = (
            issue_key
            .strip()
            .upper()
        )

        print(
            "\n"
            + "=" * 60
        )

        print(
            "🔎 STEP 1 — JIRA MCP AGENT"
        )

        print(
            "=" * 60
        )

        print(
            f"Ticket : {issue_key}"
        )

        # ====================================================
        # STATE
        # ====================================================

        state = {
            "issue_key": issue_key
        }

        # ====================================================
        # JIRA AGENT
        # ====================================================

        result = await jira_agent_vf(
            state
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return result["ticket"]

    except Exception as e:

        print(
            f"\n❌ Erreur Jira : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# REQUEST MODEL — ANALYSIS
# ============================================================

class AnalysisRequest(BaseModel):

    ticket: dict


# ============================================================
# STEP 2 — ANALYSIS
#
# POST /api/analysis
#
# Agent 2 uniquement
# ============================================================

@app.post("/api/analysis")
def analyze_ticket(
    request: AnalysisRequest,
):

    try:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "🧠 STEP 2 — ANALYSIS AGENT"
        )

        print(
            "=" * 60
        )

        ticket = request.ticket

        # ====================================================
        # VALIDATION
        # ====================================================

        if not ticket:

            raise ValueError(
                "❌ Ticket manquant."
            )

        # ====================================================
        # STATE
        # ====================================================

        state = {
            "ticket": ticket
        }

        # ====================================================
        # EXECUTE AGENT
        # ====================================================

        result = analysis_agent(
            state
        )

        analysis = result.get(
            "analysis"
        )

        print(
            "\n✅ Analyse générée."
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "ticket": ticket,

            "analysis": analysis,

        }

    except Exception as e:

        print(
            f"\n❌ Erreur Analysis : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# REQUEST MODEL — PROMPT
# ============================================================

class PromptRequest(BaseModel):

    ticket: dict

    analysis: str


# ============================================================
# STEP 3 — PROMPT
#
# POST /api/prompt
#
# Agent 3 uniquement
# ============================================================

@app.post("/api/prompt")
def generate_prompt(
    request: PromptRequest,
):

    try:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "📝 STEP 3 — PROMPT AGENT"
        )

        print(
            "=" * 60
        )

        ticket = request.ticket

        analysis = request.analysis

        # ====================================================
        # VALIDATION
        # ====================================================

        if not ticket:

            raise ValueError(
                "❌ Ticket manquant."
            )

        if not analysis:

            raise ValueError(
                "❌ Analysis manquante."
            )

        # ====================================================
        # STATE
        # ====================================================

        state = {

            "ticket": ticket,

            "analysis": analysis,

        }

        # ====================================================
        # EXECUTE AGENT
        # ====================================================

        result = prompt_agent(
            state
        )

        prompt = result.get(
            "coding_instruction"
        )

        print(
            "\n✅ Prompt généré."
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "ticket": ticket,

            "analysis": analysis,

            "prompt": prompt,

        }

    except Exception as e:

        print(
            f"\n❌ Erreur Prompt : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# REQUEST MODEL — OPENCODE
# ============================================================

class OpenCodeRequest(BaseModel):

    issue_key: str

    prompt: str


# ============================================================
# STEP 4 — OPENCODE
#
# POST /api/opencode/execute
#
# Agent 4 uniquement
# ============================================================

@app.post("/api/opencode/execute")
def execute_opencode(
    request: OpenCodeRequest,
):

    try:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "🚀 STEP 4 — OPENCODE AGENT"
        )

        print(
            "=" * 60
        )

        # ====================================================
        # INPUT
        # ====================================================

        issue_key = (
            request.issue_key
            .strip()
            .upper()
        )

        prompt = request.prompt

        # ====================================================
        # VALIDATION
        # ====================================================

        if not issue_key:

            raise ValueError(
                "❌ Issue key manquante."
            )

        if not prompt:

            raise ValueError(
                "❌ Prompt manquant."
            )

        print(
            f"\n🎫 Ticket : {issue_key}"
        )

        print(
            "\n📝 Prompt reçu :"
        )

        print(
            prompt
        )

        # ====================================================
        # BUILD OPENCODE GRAPH
        # ====================================================

        workflow = build_opencode_graph()

        # ====================================================
        # STATE
        # ====================================================

        state = {

            "issue_key":
                issue_key,

            "coding_instruction":
                prompt,

        }

        # ====================================================
        # EXECUTE
        # ====================================================

        result = workflow.invoke(
            state
        )

        # ====================================================
        # PROJECT COLLECTOR RESULT
        # ====================================================

        project_files = result.get(
            "project_files",
            {},
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "success":
                result.get(
                    "opencode_return_code"
                ) == 0,

            "issue_key":
                issue_key,

            "prompt":
                prompt,

            "opencode_result":
                result.get(
                    "opencode_result"
                ),

            "return_code":
                result.get(
                    "opencode_return_code"
                ),

            "project_dir":
                result.get(
                    "project_dir"
                ),

            "project_files_count":
                len(project_files),

            "project_files":
                list(
                    project_files.keys()
                ),

        }

    except Exception as e:

        print(
            f"\n❌ Erreur OpenCode : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# ============================================================
# STEP 5 — GIT DEPLOYMENT
# ============================================================
#
# POST /api/git/deploy
#
# Angular
#     ↓
# FastAPI
#     ↓
# build_git_graph()
#     ↓
# Git Agent
#     ↓
# Git
#     ↓
# GitHub MCP
#     ↓
# Pull Request
#
# ============================================================


# ============================================================
# REQUEST MODEL — GIT DEPLOYMENT
# ============================================================

class GitDeployRequest(BaseModel):

    issue_key: str

    project_dir: str


# ============================================================
# GIT DEPLOYMENT ENDPOINT
#
# POST /api/git/deploy
# ============================================================

@app.post("/api/git/deploy")
async def deploy_to_git(
    request: GitDeployRequest,
):

    try:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "🚀 STEP 5 — GIT DEPLOYMENT"
        )

        print(
            "=" * 60
        )

        # ====================================================
        # INPUT
        # ====================================================

        issue_key = (
            request.issue_key
            .strip()
            .upper()
        )

        project_dir = (
            request.project_dir
            .strip()
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        if not issue_key:

            raise ValueError(
                "❌ Issue key manquante."
            )

        if not project_dir:

            raise ValueError(
                "❌ Project directory manquant."
            )

        print(
            f"🎫 Ticket : {issue_key}"
        )

        print(
            f"📁 Project : {project_dir}"
        )

        # ====================================================
        # BUILD GIT GRAPH
        # ====================================================

        workflow = build_git_graph()

        # ====================================================
        # INITIAL STATE
        # ====================================================

        state = {

            "issue_key":
                issue_key,

            "project_dir":
                project_dir,

        }

        # ====================================================
        # EXECUTE GIT WORKFLOW
        # ====================================================

        print(
            "\n🚀 Lancement du Git Workflow..."
        )

        result = await workflow.ainvoke(
            state
        )

        # ====================================================
        # RESULT
        # ====================================================

        error = result.get(
            "error"
        )

        pull_request_url = result.get(
            "pull_request_url"
        )

        success = (
            error is None
            and pull_request_url is not None
        )

        # ====================================================
        # LOG SUCCESS
        # ====================================================

        if success:

            print(
                "\n"
                + "=" * 60
            )

            print(
                "✅ GIT DEPLOYMENT TERMINÉ"
            )

            print(
                "=" * 60
            )

            print(
                f"🌿 Branche : "
                f"{result.get('git_branch_name')}"
            )

            print(
                f"💾 Commit : "
                f"{result.get('git_commit_message')}"
            )

            print(
                f"🔗 Pull Request : "
                f"{pull_request_url}"
            )

        # ====================================================
        # LOG ERROR
        # ====================================================

        else:

            print(
                "\n"
                + "=" * 60
            )

            print(
                "❌ GIT DEPLOYMENT ÉCHOUÉ"
            )

            print(
                f"Erreur : {error}"
            )

            print(
                "=" * 60
            )

        # ====================================================
        # RESPONSE TO ANGULAR
        # ====================================================

        return {

            "success":
                success,

            "issue_key":
                issue_key,

            "project_dir":
                project_dir,

            "git_action":
                result.get(
                    "git_action"
                ),

            "git_action_reason":
                result.get(
                    "git_action_reason"
                ),

            "git_branch_name":
                result.get(
                    "git_branch_name"
                ),

            "git_commit_message":
                result.get(
                    "git_commit_message"
                ),

            "git_push_result":
                result.get(
                    "git_push_result"
                ),

            "pull_request_number":
                result.get(
                    "pull_request_number"
                ),

            "pull_request_url":
                pull_request_url,

            "error":
                error,

        }

    except Exception as e:

        print(
            f"\n❌ Erreur Git Deployment : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# ============================================================
# MODE ORCHESTRATEUR
# ============================================================
# ============================================================


# ============================================================
# ORCHESTRATOR
#
# GET /api/agents/KAN-1
#
# Agent 1 → Agent 2 → Agent 3
#
# OpenCode NON exécuté
# Git NON exécuté
#
# ============================================================

@app.get("/api/agents/{issue_key}")
async def run_agents(
    issue_key: str,
):

    try:

        issue_key = (
            issue_key
            .strip()
            .upper()
        )

        print(
            "\n"
            + "=" * 60
        )

        print(
            "🤖 ORCHESTRATOR"
        )

        print(
            "=" * 60
        )

        print(
            f"Ticket : {issue_key}"
        )

        # ====================================================
        # BUILD WORKFLOW
        # ====================================================

        workflow = build_prompt_graph()

        # ====================================================
        # INITIAL STATE
        # ====================================================

        initial_state = {

            "issue_key":
                issue_key,

        }

        # ====================================================
        # EXECUTE
        # ====================================================

        result = await workflow.ainvoke(
            initial_state
        )

        # ====================================================
        # GET PROMPT
        # ====================================================

        prompt = result.get(
            "coding_instruction"
        )

        # ====================================================
        # LOG
        # ====================================================

        print(
            "\n"
            + "=" * 60
        )

        print(
            "✅ ORCHESTRATOR TERMINÉ"
        )

        print(
            "=" * 60
        )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

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
                prompt,

        }

    except Exception as e:

        print(
            f"\n❌ Erreur Orchestrateur : {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )