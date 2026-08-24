# 🤖 Jira AI Multi-Agent System

> **AI-powered multi-agent system for Jira ticket analysis, coding instruction generation and automated project execution.**

This project implements a multi-agent software engineering workflow that transforms a Jira ticket into a technical analysis, generates a coding instruction for an AI coding agent, executes the requested changes with OpenCode, and can be extended with a GitHub MCP deployment agent.

---

## 📌 Table of Contents

- [1. Overview](#1-overview)
- [2. Objectives](#2-objectives)
- [3. Main Features](#3-main-features)
- [4. Architecture](#4-architecture)
- [5. Project Structure](#5-project-structure)
- [6. Technology Stack](#6-technology-stack)
- [7. Prerequisites](#7-prerequisites)
- [8. Clone the Project](#8-clone-the-project)
- [9. Environment Configuration](#9-environment-configuration)
- [10. Obtain the API Credentials](#10-obtain-the-api-credentials)
- [11. Install Backend Dependencies](#11-install-backend-dependencies)
- [12. Run the Backend](#12-run-the-backend)
- [13. Run the Frontend](#13-run-the-frontend)
- [14. Application Workflow](#14-application-workflow)
- [15. Step-by-Step Mode](#15-step-by-step-mode)
- [16. Orchestrator Mode](#16-orchestrator-mode)
- [17. OpenCode Execution](#17-opencode-execution)
- [18. MCP Architecture](#18-mcp-architecture)
- [19. GitHub MCP Deployment](#19-github-mcp-deployment)
- [20. API Endpoints](#20-api-endpoints)
- [21. Security](#21-security)
- [22. Troubleshooting](#22-troubleshooting)
- [23. Git Workflow](#23-git-workflow)
- [24. Future Improvements](#24-future-improvements)

---

# 1. Overview

The **Jira AI Multi-Agent System** connects Jira, Large Language Models, LangGraph, MCP and OpenCode into a single software-engineering workflow.

The objective is to automate the path:

```text
Jira Ticket
     ↓
Jira Agent
     ↓
Technical Analysis Agent
     ↓
Prompt / Coding Instruction Agent
     ↓
Human Review
     ↓
OpenCode Agent
     ↓
Project Modification
     ↓
GitHub Deployment Agent (MCP)
```

The system supports two execution modes:

### Step-by-Step Mode

The user controls each stage manually:

```text
1. Retrieve Jira ticket
2. Analyze ticket
3. Generate coding prompt
4. Review / modify prompt
5. Execute with OpenCode
```

### Orchestrator Mode

LangGraph manages the sequence automatically:

```text
Jira Agent
    ↓
Analysis Agent
    ↓
Prompt Agent
    ↓
OpenCode Agent
    ↓
Git Deploy Agent
```

The `AgentState` object is shared between the agents and contains the information produced by each stage.

---

# 2. Objectives

The project aims to provide:

- Automated Jira ticket retrieval
- AI-powered technical analysis
- Automatic generation of implementation instructions
- Human-in-the-loop validation
- Automated code modification through OpenCode
- Shared state between agents
- Explicit workflow orchestration with LangGraph
- MCP integration for external services
- GitHub automation through a GitHub MCP Server
- A REST API through FastAPI
- An Angular web interface

---

# 3. Main Features

## 🎫 Jira Agent

Retrieves Jira issues through Atlassian MCP.

Responsibilities:

- Receive a Jira issue key such as `KAN-1`
- Connect to Atlassian MCP
- Discover MCP tools
- Ask the LLM to use the appropriate Jira tool
- Retrieve the Jira issue
- Format the ticket
- Store the result in `AgentState`

---

## 🧠 Analysis Agent

Receives the formatted Jira ticket.

Responsibilities:

- Understand the requirement
- Identify the problem
- Determine expected behavior
- Identify technical requirements
- Identify frontend/backend impact
- Identify implementation constraints
- Produce a structured technical analysis

---

## 📝 Prompt Agent

Receives:

```text
Ticket
+
Technical Analysis
```

and generates a detailed coding instruction.

The instruction is intended for OpenCode.

---

## 👨‍💻 OpenCode Agent

Receives the coding instruction and executes it against the configured project directory.

OpenCode is responsible for applying the requested code changes to the target project.

---

## 🚀 Git Deploy Agent

The Git deployment agent is designed to communicate with GitHub through MCP.

Target architecture:

```text
Git Deploy Agent
       ↓
Ollama
       ↓
GitHub MCP Client
       ↓
GitHub MCP Server
       ↓
GitHub Repository
```

The exact GitHub MCP tools available should be discovered dynamically from the MCP server before implementing tool-specific calls.

---

# 4. Architecture

## Global Architecture

```text
                         ┌──────────────────┐
                         │      User        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Angular Frontend │
                         └────────┬─────────┘
                                  │ HTTP
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    LangGraph     │
                         │   Orchestrator   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              Jira Agent    Analysis Agent  Prompt Agent
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   AgentState     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  OpenCode Agent  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Git Deploy Agent │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  GitHub MCP      │
                         └──────────────────┘
```

---

# 5. Project Structure

```text
multi-agents/
│
├── backend/
│   │
│   ├── agents/
│   │   ├── jira_agent.py
│   │   ├── jira_agent_vf.py
│   │   ├── analysis_agent.py
│   │   ├── prompt_agent.py
│   │   ├── opencode_agent.py
│   │   └── git_agent.py
│   │
│   ├── api/
│   │   └── main.py
│   │
│   ├── chatbot/
│   │   └── chatbot.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   ├── mcp/
│   │   └── client.py
│   │
│   ├── skills/
│   │   └── jira_to_prompt/
│   │       └── skill.md
│   │
│   └── jobs/
│       └── jira_agent_job.py
│
├── frontend/
│   ├── src/
│   │   └── app/
│   ├── angular.json
│   ├── package.json
│   └── package-lock.json
│
├── .gitignore
├── architecture.txt
├── explication.txt
└── README.md
```

---

# 6. Technology Stack

| Technology | Role |
|---|---|
| Python 3.11 | Backend / AI agents |
| FastAPI | REST API |
| Uvicorn | ASGI server |
| LangGraph | Agent orchestration |
| LangChain | LLM/tool integration |
| Ollama | LLM provider |
| `gemma4:31b-cloud` | Main configured Ollama model |
| MCP | External tool integration |
| `langchain-mcp-adapters` | MCP ↔ LangChain integration |
| Atlassian Rovo MCP | Jira integration |
| GitHub MCP Server | GitHub integration |
| OpenCode | AI coding/execution agent |
| Angular | Frontend |
| Node.js 24.11.1 | Frontend runtime |
| npm 11.6.2 | Frontend package manager |
| Git | Source control |

### Environment versions

The development environment used for the project includes:

```text
Python 3.11
Node.js 24.11.1
npm 11.6.2
Docker 27.2.0
```

The Python and Angular library versions are defined by the project's dependency files and should be installed from those files when available.

---

# 7. Prerequisites

Before running the project, install:

- Python 3.11
- Node.js
- npm
- Git
- Angular CLI
- OpenCode
- Access to Ollama Cloud
- Atlassian/Jira account
- Atlassian MCP access
- GitHub account and repository access if GitHub deployment is enabled

Verify:

```powershell
python --version
node --version
npm --version
git --version
```

Expected development environment:

```text
Python 3.11.x
Node.js 24.11.1
npm 11.6.2
```

---

# 8. Clone the Project

```powershell
git clone https://github.com/medismail841/jira-ai-multi-agent.git

cd jira-ai-multi-agent
```

---

# 9. Environment Configuration

## 9.1 Create `.env`

Create:

```text
multi-agents/
└── .env
```

The `.env` file must NEVER be committed to Git.

Example:

```env
# ============================================================
# OLLAMA
# ============================================================

OLLAMA_API_KEY=YOUR_OLLAMA_API_KEY
OLLAMA_MODEL=gemma4:31b-cloud


# ============================================================
# ATLASSIAN / JIRA
# ============================================================

JIRA_EMAIL=YOUR_ATLASSIAN_EMAIL
ROVO_MCP_API_TOKEN=YOUR_ATLASSIAN_ROVO_MCP_TOKEN
JIRA_CLOUD_ID=YOUR_JIRA_CLOUD_ID

ATLASSIAN_MCP_URL=https://mcp.atlassian.com/v1/mcp


# ============================================================
# OPENCODE
# ============================================================

OPENCODE_PROJECT_DIR=C:\path\to\target\project


# ============================================================
# GITHUB MCP
# ============================================================

GIT_MCP_URL=https://api.githubcopilot.com/mcp/
GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_TOKEN

GIT_REPOSITORY=YOUR_USERNAME/YOUR_REPOSITORY
GIT_BRANCH=main
GIT_COMMIT_MESSAGE=feat: implementation from Jira AI agent
```

Do not copy this file with real credentials into Git.

---

# 10. Obtain the API Credentials

## 10.1 Ollama API Key

The project uses Ollama Cloud through:

```text
https://ollama.com
```

The application uses:

```env
OLLAMA_API_KEY=YOUR_OLLAMA_API_KEY
```

The configured model is:

```env
OLLAMA_MODEL=gemma4:31b-cloud
```

The key must be private.

The backend verifies the Ollama connection when the relevant agent modules are loaded.

---

## 10.2 Atlassian / Jira Configuration

The Jira agent uses Atlassian MCP.

Required values:

```env
JIRA_EMAIL=your-atlassian-email
ROVO_MCP_API_TOKEN=your-token
JIRA_CLOUD_ID=your-cloud-id
```

### Jira Cloud ID

The Cloud ID identifies the Jira Cloud tenant.

It must be placed in:

```env
JIRA_CLOUD_ID=...
```

Do not use:

```text
your-cloud-id
```

The actual Cloud ID must be provided.

### Atlassian MCP

The configured MCP endpoint is:

```env
ATLASSIAN_MCP_URL=https://mcp.atlassian.com/v1/mcp
```

The Jira agent connects to this MCP server and dynamically retrieves the available tools.

---

## 10.3 GitHub Token

If GitHub deployment is enabled, create a GitHub Personal Access Token with the permissions required for the target repository.

Store it only in `.env`:

```env
GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_TOKEN
```

Never place a real token inside Python source code.

Never commit `.env`.

---

# 11. Install Backend Dependencies

Move into the backend:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the required packages used by the backend:

```powershell
pip install fastapi uvicorn python-dotenv
pip install langgraph langchain-core langchain-ollama
pip install langchain-mcp-adapters mcp
```

If the repository contains a `requirements.txt`, prefer:

```powershell
pip install -r requirements.txt
```

---

# 12. Run the Backend

From:

```text
multi-agents/backend
```

run:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

The API should be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative:

```text
http://localhost:8000/docs
```

Root endpoint:

```text
GET /
```

Expected response:

```json
{
  "message": "Jira AI Multi-Agent API",
  "status": "running"
}
```

---

# 13. Run the Frontend

Open a second terminal.

Move to:

```powershell
cd frontend
```

Install Angular dependencies:

```powershell
npm install
```

Run the development server:

```powershell
npm start
```

or:

```powershell
ng serve
```

The frontend is normally available at:

```text
http://localhost:4200
```

The backend CORS configuration allows:

```text
http://localhost:4200
```

---

# 14. Application Workflow

The complete workflow is based on the following sequence:

```text
User
 │
 │ Jira issue key
 ▼
Angular
 │
 │ HTTP request
 ▼
FastAPI
 │
 ▼
LangGraph / Agent
 │
 ▼
AgentState
 │
 ├── Jira Agent
 │       │
 │       ▼
 │   Atlassian MCP
 │       │
 │       ▼
 │      Jira
 │
 ├── Analysis Agent
 │       │
 │       ▼
 │     Ollama
 │
 ├── Prompt Agent
 │       │
 │       ▼
 │     Ollama
 │
 ├── Human Review
 │
 ├── OpenCode Agent
 │       │
 │       ▼
 │   Target Project
 │
 └── Git Deploy Agent
         │
         ▼
     GitHub MCP
         │
         ▼
       GitHub
```

---

# 15. Step-by-Step Mode

The step-by-step mode allows the user to validate each stage.

## Step 1 — Retrieve Jira Ticket

Request:

```http
GET /api/jira/KAN-1
```

The Jira agent retrieves and formats the issue.

Result:

```text
Ticket
 ├── key
 ├── summary
 ├── description
 ├── status
 ├── priority
 ├── project
 ├── reporter
 └── assignee
```

---

## Step 2 — Analyze Ticket

Request:

```http
POST /api/analysis
```

Body:

```json
{
  "ticket": {
    "key": "KAN-1",
    "summary": "Example ticket",
    "description": "..."
  }
}
```

The Analysis Agent produces:

```text
Technical Analysis
 ├── Problem
 ├── Expected Behavior
 ├── Technical Requirements
 └── Technical Impact
```

---

## Step 3 — Generate Coding Prompt

Request:

```http
POST /api/prompt
```

Body:

```json
{
  "ticket": {},
  "analysis": "..."
}
```

The Prompt Agent generates the coding instruction.

---

## Step 4 — Human Review

The generated instruction can be reviewed before execution.

The user can:

```text
Accept
   ↓
Execute

or

Modify
   ↓
Execute
```

This provides a Human-in-the-Loop control point before modifying the target project.

---

# 16. Orchestrator Mode

The orchestrator exposes:

```http
GET /api/agents/{issue_key}
```

Example:

```http
GET /api/agents/KAN-1
```

LangGraph executes:

```text
START
  ↓
jira_agent_vf
  ↓
analysis_agent
  ↓
prompt_agent
  ↓
END
```

The shared `AgentState` carries information from one agent to the next.

For example:

```text
issue_key
    ↓
jira_agent
    ↓
ticket
    ↓
analysis_agent
    ↓
analysis
    ↓
prompt_agent
    ↓
coding_instruction
```

The OpenCode stage is handled separately in the current workflow unless the complete execution workflow is explicitly connected.

---

# 17. OpenCode Execution

OpenCode receives the generated coding instruction.

Configure:

```env
OPENCODE_PROJECT_DIR=C:\path\to\target\project
```

Example:

```env
OPENCODE_PROJECT_DIR=C:\Users\User\Desktop\my-project
```

The directory must point to the project that OpenCode is allowed to modify.

The conceptual flow is:

```text
Jira Ticket
     ↓
Analysis
     ↓
Coding Instruction
     ↓
OpenCode Agent
     ↓
OpenCode
     ↓
Target Project
```

The OpenCode agent stores execution information in `AgentState`, including:

```text
opencode_result
opencode_return_code
```

A return code of:

```text
0
```

indicates successful process execution.

---

# 18. MCP Architecture

MCP stands for **Model Context Protocol**.

In this project, MCP provides a standardized communication layer between AI agents and external services.

The architecture is:

```text
AI Agent
   ↓
MCP Client
   ↓
MCP Server
   ↓
External Service
```

## Jira

```text
Jira Agent
    ↓
MultiServerMCPClient
    ↓
Atlassian MCP Server
    ↓
Jira Cloud
```

## GitHub

```text
Git Deploy Agent
    ↓
MultiServerMCPClient
    ↓
GitHub MCP Server
    ↓
GitHub
```

The MCP client discovers available tools dynamically:

```python
tools = await mcp_client.get_tools()
```

The tools can then be connected to the LLM:

```python
llm_with_tools = llm.bind_tools(tools)
```

LangGraph can execute tool calls using `ToolNode`.

---

# 19. GitHub MCP Deployment

The GitHub deployment extension uses the official GitHub MCP Server.

Repository:

```text
https://github.com/github/github-mcp-server
```

Remote MCP endpoint:

```env
GIT_MCP_URL=https://api.githubcopilot.com/mcp/
```

Authentication:

```env
GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_TOKEN
```

The intended architecture is:

```text
                 AgentState
                     │
                     ▼
              Git Deploy Agent
                     │
                     ▼
                  Ollama
                     │
                 tool call
                     ▼
              GitHub MCP Client
                     │
                     ▼
              GitHub MCP Server
                     │
                     ▼
                  GitHub
```

### Important

Do not assume a tool name such as:

```text
git_push
```

until the MCP server exposes that tool.

First discover the tools:

```python
tools = await client.get_tools()

for tool in tools:
    print(tool.name)
```

Then implement the Git agent according to the tools actually provided by the configured MCP server.

---

# 20. API Endpoints

## Root

```http
GET /
```

Checks that the API is running.

---

## Jira

```http
GET /api/jira/{issue_key}
```

Example:

```http
GET /api/jira/KAN-1
```

---

## Analysis

```http
POST /api/analysis
```

---

## Prompt

```http
POST /api/prompt
```

---

## OpenCode

```http
POST /api/opencode/execute
```

Example:

```json
{
  "issue_key": "KAN-1",
  "prompt": "Implement the requested feature..."
}
```

---

## Orchestrator

```http
GET /api/agents/{issue_key}
```

Example:

```http
GET /api/agents/KAN-1
```

---

# 21. AgentState

`AgentState` is the shared state used by LangGraph.

Conceptually:

```python
class AgentState(TypedDict, total=False):

    user_request: str

    messages: list

    issue_key: str

    ticket: dict

    analysis: str

    coding_instruction: str

    prompt_file: str

    opencode_result: str

    opencode_return_code: int

    error: str
```

The state allows agents to communicate without directly depending on each other.

Example:

```text
Jira Agent
   │
   │ writes ticket
   ▼
AgentState
   │
   ▼
Analysis Agent
   │
   │ writes analysis
   ▼
AgentState
   │
   ▼
Prompt Agent
   │
   │ writes coding_instruction
   ▼
AgentState
```

This is one of the central design principles of the project.

---

# 22. LangGraph Workflow

The main graph:

```text
START
  ↓
jira_agent_vf
  ↓
analysis_agent
  ↓
prompt_agent
  ↓
END
```

The OpenCode graph:

```text
START
  ↓
opencode_agent
  ↓
END
```

The Git deployment graph can extend the architecture:

```text
START
  ↓
jira_agent
  ↓
analysis_agent
  ↓
prompt_agent
  ↓
opencode_agent
  ↓
git_deploy_agent
  ↓
END
```

The complete automated workflow should only be enabled once each stage has been validated independently.

---

# 23. Security

## Never commit secrets

The following files must remain local:

```text
.env
```

`.gitignore` should contain:

```gitignore
.env
.env.*
!.env.example

__pycache__/
*.pyc

.venv/
venv/

node_modules/
dist/
```

Never commit:

```text
OLLAMA_API_KEY
ROVO_MCP_API_TOKEN
JIRA_API_TOKEN
GITHUB_PERSONAL_ACCESS_TOKEN
```

Never hard-code API keys inside Python source files.

---

# 24. Troubleshooting

## `uvicorn` is not recognized

Instead of:

```powershell
uvicorn api.main:app --reload --port 8000
```

use:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

This ensures Uvicorn is executed using the active Python installation.

---

## `ModuleNotFoundError`

Verify that the terminal is inside:

```text
multi-agents/backend
```

and that the virtual environment is activated.

Then install dependencies again.

---

## `GIT_MCP_URL manquante`

Add:

```env
GIT_MCP_URL=https://api.githubcopilot.com/mcp/
```

to `.env`.

---

## `OLLAMA_API_KEY manquante`

Add:

```env
OLLAMA_API_KEY=YOUR_OLLAMA_API_KEY
```

---

## Jira authentication error

Verify:

```env
JIRA_EMAIL=...
ROVO_MCP_API_TOKEN=...
JIRA_CLOUD_ID=...
```

Also verify that the Atlassian MCP credentials are valid.

---

## Angular cannot connect to backend

Verify that the backend is running:

```text
http://localhost:8000
```

and that Angular is running:

```text
http://localhost:4200
```

The FastAPI CORS configuration must allow:

```text
http://localhost:4200
```

---

# 25. Git Workflow

After modifying the project:

```powershell
git status
```

Review changes:

```powershell
git diff
```

Stage:

```powershell
git add .
```

Commit:

```powershell
git commit -m "feat: describe the change"
```

Push:

```powershell
git push
```

The main repository is:

```text
https://github.com/medismail841/jira-ai-multi-agent
```

The main branch is:

```text
main
```

---

# 26. Recommended Development Sequence

When developing or debugging the system, validate the components progressively.

## Phase 1 — Backend

```text
FastAPI
   ↓
Swagger
```

Verify:

```text
http://localhost:8000/docs
```

---

## Phase 2 — Ollama

Verify:

```text
OLLAMA_API_KEY
OLLAMA_MODEL
```

and confirm that the LLM responds.

---

## Phase 3 — Jira MCP

Verify:

```text
Jira Agent
   ↓
MCP Client
   ↓
Atlassian MCP
   ↓
Jira
```

Test with:

```text
KAN-1
```

or another valid issue key.

---

## Phase 4 — Analysis

Verify:

```text
Ticket
 ↓
Analysis Agent
 ↓
Analysis
```

---

## Phase 5 — Prompt

Verify:

```text
Ticket + Analysis
        ↓
 Prompt Agent
        ↓
Coding Instruction
```

---

## Phase 6 — OpenCode

Verify:

```text
Coding Instruction
        ↓
OpenCode Agent
        ↓
OpenCode
        ↓
Target Project
```

---

## Phase 7 — GitHub MCP

Verify:

```text
Git Agent
   ↓
GitHub MCP Client
   ↓
GitHub MCP Server
   ↓
GitHub tools
```

Only after these individual stages work should the complete automated orchestrator be enabled.

---

# 27. Final Architecture

The final target architecture is:

```text
                         ┌──────────────┐
                         │     USER     │
                         └──────┬───────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Angular         │
                       │ Frontend        │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ FastAPI         │
                       │ REST API        │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ LangGraph       │
                       │ Orchestrator    │
                       └────────┬────────┘
                                │
                         ┌──────┴──────┐
                         │ AgentState  │
                         └──────┬──────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
        Jira Agent       Analysis Agent     Prompt Agent
              │                 │                 │
              ▼                 ▼                 ▼
        Atlassian MCP         Ollama            Ollama
              │
              ▼
             Jira
                                │
                                ▼
                         Human Review
                                │
                                ▼
                        OpenCode Agent
                                │
                                ▼
                            OpenCode
                                │
                                ▼
                         Target Project
                                │
                                ▼
                       Git Deploy Agent
                                │
                                ▼
                       GitHub MCP Client
                                │
                                ▼
                       GitHub MCP Server
                                │
                                ▼
                             GitHub
```

---

# 28. Project Status

Current project capabilities include:

- [x] FastAPI backend
- [x] Angular frontend
- [x] Jira agent
- [x] Atlassian MCP integration
- [x] Ollama integration
- [x] Analysis agent
- [x] Prompt generation agent
- [x] Shared `AgentState`
- [x] LangGraph orchestration
- [x] OpenCode execution workflow
- [x] Human-in-the-loop step-by-step workflow
- [ ] Complete automatic OpenCode + GitHub deployment workflow
- [ ] Production deployment
- [ ] CI/CD automation
- [ ] Automated tests for the complete multi-agent workflow

---

## 👨‍💻 Author

**GRAEA MOHAMED ISMAIL**

GitHub:

```text
https://github.com/medismail841
```

Project:

```text
https://github.com/medismail841/jira-ai-multi-agent
```

---

## 📄 License

This project is currently intended as an academic / internship project.

Add an explicit license to the repository if the project is intended for public redistribution or external contributions.
