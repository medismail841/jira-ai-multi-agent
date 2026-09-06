# 🤖 Multi-Agent AI 

Multi-Agent AI basé sur LangGraph permettant d'automatiser le traitement des tickets Jira : analyse des tickets, génération de code via OpenCode et automatisation du workflow Git, de la préparation de la branche jusqu'au déploiement des modifications.

---

## 📖 Table des matières

1. [Introduction](#-introduction)
2. [Architecture du projet](#️-architecture-du-projet)
3. [Fonctionnalités](#-fonctionnalités)
4. [Workflow global](#-workflow-global)
5. [Technologies utilisées](#️-technologies-utilisées)
6. [Prérequis](#-prérequis)
7. [Installation du projet](#-installation-du-projet)
8. [Configuration du fichier .env](#-configuration-du-fichier-env)
9. [Installation des dépendances Python](#-installation-des-dépendances-python)
10. [Installation des dépendances Angular](#-installation-des-dépendances-angular)
11. [Lancement du backend](#-lancement-du-backend)
12. [Lancement du frontend](#-lancement-du-frontend)
13. [Tests](#-tests)
14. [Génération des diagrammes LangGraph](#-génération-des-diagrammes-langgraph)
15. [Explication des agents](#️-explication-des-agents)
16. [Explication des workflows](#-explication-des-workflows)
17. [Dépannage / Troubleshooting](#-dépannage--troubleshooting)
18. [Sécurité](#-sécurité)
19. [Structure du projet](#-structure-du-projet)
20. [Auteur](#-auteur)

---

## 📖 Introduction

**Multi-Agent AI Orchestrator** est une plateforme qui automatise le cycle de développement à partir d'un ticket Jira :

- récupération et analyse du ticket,
- classification (simple ou complexe),
- génération d'instructions de développement,
- génération de code via **OpenCode**,
- gestion du dépôt Git (branche, commit, push),
- automatisation du déploiement des modifications sur la branche Jira.

Le projet s'appuie sur **LangGraph** pour orchestrer les agents, un backend **FastAPI**, et un frontend **Angular**.

---

## 🏗️ Architecture du projet

```
Frontend Angular
      │
      │ HTTP
      ▼
FastAPI Backend
      │
      ▼
   LangGraph
      │
      ├── Jira Agent
      ├── Analysis Agent
      ├── Prompt Agent
      ├── Git Agent
      ├── OpenCode Agent
      └── Git Deploy Agent
```

---

## ✨ Fonctionnalités

- 🔗 Intégration native avec **Jira** (via Rovo MCP)
- 🧠 Analyse et classification automatique des tickets
- ✍️ Génération d'instructions de développement
- 🤖 Génération de code via **OpenCode**
- 🔀 Gestion automatisée de Git (branches, commits, push)
- 🔁 Création automatique de Pull Requests GitHub
- 📊 Génération de diagrammes visuels des workflows LangGraph
- 🖥️ Interface frontend Angular pour le suivi des exécutions

---

## 🔄 Workflow global

```
START
  │
  ▼
JIRA AGENT
  │
  ▼
ANALYSIS AGENT
  │
  ▼
CLASSIFICATION
  │
  ├────────────── SIMPLE ──────────────┐
  │                                    │
  ▼                                    ▼
PROMPT AGENT                     SPLIT TICKET
  │                                    │
  ▼                                    ▼
GIT AGENT                       CREATE SUBTASKS
  │                                    │
  ▼                                   END
OPENCODE AGENT
  │
  ▼
GIT DEPLOY AGENT
  │
  ▼
PULL REQUEST
  │
  ▼
END
```

---

## 🛠️ Technologies utilisées

| Composant       | Technologie                         |
|-----------------|--------------------------------------|
| Orchestration   | LangGraph, LangChain                 |
| Backend         | FastAPI, Uvicorn, Python             |
| Frontend        | Angular                              |
| LLM             | Ollama                               |
| Génération code | OpenCode                             |
| Gestion tickets | Jira (via Rovo MCP)                  |
| Versioning      | Git, GitHub (via MCP)                |

---

## 📋 Prérequis

Avant de démarrer, assurez-vous d'avoir installé :

- **Python** (vérifiez votre version avec `python --version`)
- **Node.js** (vérifiez votre version avec `node --version`)
- **npm** (vérifiez votre version avec `npm --version`)
- **Angular CLI** (`ng version`)
- **Git**
- **Ollama** (avec un compte et une clé API)
- **OpenCode**

> 💡 Les versions exactes utilisées dans ce projet sont indiquées ci-dessous à titre d'exemple ; vérifiez toujours vos propres versions avant l'installation.

```bash
python --version      # ex: Python 3.11.1
node --version        # ex: v24.11.1
npm --version         # ex: 11.6.2
ng version            # affiche Angular CLI, Node, Package Manager, Angular
```

---

## 📥 Installation du projet

```
Clone repository
       │
       ▼
Create Python environment
       │
       ▼
Install Python dependencies
       │
       ▼
Install Angular dependencies
       │
       ▼
Create .env
       │
       ▼
Configure API keys
       │
       ▼
Start backend
       │
       ▼
Start frontend
```

```bash
git clone https://github.com/medismail841/jira-ai-multi-agent.git
cd jira-ai-multi-agent
```

---

## 🔐 Configuration du fichier .env

⚠️ **Ne jamais committer de clés réelles dans le dépôt Git.** Le fichier `.env` doit toujours figurer dans `.gitignore`. Un fichier `.env.example` (sans valeurs sensibles) doit être fourni pour montrer les variables attendues.

### 1. Copier le modèle

```
.env.example
     │
     │ copy
     ▼
   .env
     │
     ▼
Remplacer les valeurs
     │
     ▼
Lancer le projet
```

```Sous Windows (PowerShell)
Copy-Item .env.example .env
```

### 2. Contenu de `.env.example`

```env
# ============================================================
# OLLAMA
# ============================================================
OLLAMA_API_KEY=your_ollama_api_key


# ============================================================
# JIRA
# ============================================================
JIRA_URL=https://your-domain.atlassian.net
JIRA_CLOUD_ID=your_jira_cloud_id

JIRA_EMAIL=your_jira_email
JIRA_API_TOKEN=your_jira_api_token

ROVO_MCP_API_TOKEN=your_rovo_mcp_api_token


# ============================================================
# OPENCODE
# ============================================================
OPENCODE_PROJECT_DIR=C:\path\to\your\project
OPENCODE_MODEL=opencode/big-pickle


# ============================================================
# GITHUB
# ============================================================
GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/

GITHUB_OWNER=your_github_username
GITHUB_REPOSITORY=your_repository
GITHUB_BRANCH=main

GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token
```

### 3. Comment obtenir chaque clé

#### 🔸 Ollama

1. Créer/ouvrir un compte Ollama.
2. Générer une API key.
3. Copier la clé.
4. L'ajouter dans `.env` sous `OLLAMA_API_KEY`.

#### 🔸 Jira

| Variable          | Description                                   |
|-------------------|------------------------------------------------|
| `JIRA_URL`        | URL de l'organisation Jira (`https://your-domain.atlassian.net`) |
| `JIRA_CLOUD_ID`   | Identifiant Cloud de l'instance Jira            |
| `JIRA_EMAIL`      | Adresse email associée au compte Jira           |
| `JIRA_API_TOKEN`  | Jeton d'API personnel                           |

Pour générer un `JIRA_API_TOKEN` :

```
Jira
 ↓
Account settings
 ↓
Security
 ↓
API tokens
 ↓
Create API token
 ↓
Copy token
 ↓
.env
```

> Le token Jira ne doit **jamais** être commité dans Git.

#### 🔸 Rovo MCP

`ROVO_MCP_API_TOKEN` permet l'accès MCP/Rovo à Jira.

```
Generate token
      ↓
Copy token
      ↓
.env
```

#### 🔸 OpenCode

| Variable               | Description                                                        |
|------------------------|----------------------------------------------------------------------|
| `OPENCODE_PROJECT_DIR` | Chemin vers le projet sur lequel OpenCode doit travailler            |
| `OPENCODE_MODEL`       | Modèle utilisé par OpenCode (ex : `opencode/big-pickle`)              |

> Utilisez un chemin générique dans le README (`C:\path\to\Test_ia`) : votre chemin personnel ne doit pas être copié par les autres développeurs.

#### 🔸 GitHub

| Variable                       | Rôle                                 |
|---------------------------------|---------------------------------------|
| `GITHUB_MCP_URL`                | URL du serveur MCP GitHub             |
| `GITHUB_OWNER`                  | Propriétaire du repository            |
| `GITHUB_REPOSITORY`             | Nom du repository                     |
| `GITHUB_BRANCH`                 | Branche principale                    |
| `GITHUB_PERSONAL_ACCESS_TOKEN`  | Authentification GitHub               |

Pour générer un token GitHub :

```
GitHub
 ↓
Settings
 ↓
Developer settings
 ↓
Personal access tokens
 ↓
Generate token
 ↓
Configure permissions
 ↓
Generate
 ↓
Copy token
 ↓
.env
```

---

## 📦 Installation des dépendances Python

### 1. Créer un environnement virtuel

```bash
python -m venv .venv
```

### 2. Activer l'environnement (Windows)

```bash
.venv\Scripts\activate
```

### 3. Mettre à jour pip

```bash
python -m pip install --upgrade pip
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

Le projet utilise notamment :

- `langgraph`
- `langchain-ollama`
- `langchain-core`
- `python-dotenv`
- `mcp`
- `langchain-mcp-adapters`

> Le fichier `requirements.txt` peut être régénéré avec `pip freeze > requirements.txt` (à nettoyer des paquets superflus avant de le committer).

### 5. Quitter l'environnement virtuel

```bash
deactivate
```

---

## 📦 Installation des dépendances Angular

Depuis le dossier `frontend/` :

```bash
npm install
```

---

## 🚀 Lancement du backend

```bash
uvicorn api.main:app --reload
```

- Backend : http://127.0.0.1:8000
- Swagger : http://127.0.0.1:8000/docs

---

## 🚀 Lancement du frontend

Depuis le dossier `frontend/` :

```bash
ng serve
```

ou

```bash
npm start
```

Application disponible sur : http://localhost:4200

---

## 🧪 Tests

- Vérifier que le backend répond correctement via Swagger (`/docs`).
- Vérifier que le frontend Angular se connecte bien à l'API.
- Ajouter ici la procédure spécifique de vos tests unitaires/intégration (ex. `pytest`, `ng test`) selon votre projet.

---

## 📊 Génération des diagrammes LangGraph

Le script `graph/visualize_workflow.py` génère des diagrammes PNG représentant les workflows LangGraph.

```bash
python graph/visualize_workflow.py
```

Diagrammes générés :

- `git_prepare_workflow.png`
- `prompt_workflow.png`
- `git_deploy_workflow.png`
- `opencode_workflow.png`
- `main_workflow.png`

### Comment le diagramme est créé

```
LangGraph Workflow
        │
        ▼
workflow.get_graph()
        │
        ▼
draw_mermaid_png()
        │
        ▼
PNG
```

```python
png_data = (
    workflow
    .get_graph()
    .draw_mermaid_png()
)

with open(output_path, "wb") as f:
    f.write(png_data)
```

LangGraph transforme le graphe en représentation **Mermaid**, puis génère l'image PNG correspondante.

### Deux types de visualisation

1. **Diagramme généré depuis LangGraph** : `workflow.get_graph().draw_mermaid_png()`
2. **Diagramme conceptuel Mermaid**, écrit manuellement, par exemple :

```python
main_diagram = """
flowchart TD

    A["START"]
    B["JIRA AGENT"]
    C["ANALYSIS AGENT"]

    A --> B
    B --> C
"""
```

---

## 🗂️ Explication des agents

| Agent              | Responsabilité                                  |
|--------------------|--------------------------------------------------|
| **Jira Agent**      | Récupère le ticket Jira                          |
| **Analysis Agent**  | Analyse le ticket                                |
| **Classification**  | Détermine si le ticket est simple ou complexe    |
| **Prompt Agent**    | Génère les instructions de développement         |
| **Git Agent**       | Prépare le repository et la branche              |
| **OpenCode Agent**  | Travaille sur le code                            |
| **Git Deploy Agent**| Commit et push des modifications sur la branche Jira      |
| **Split Ticket**    | Découpe un ticket complexe en sous-tâches        |

---

## 🔀 Explication des workflows

Le workflow global orchestre l'ensemble des agents (voir [Workflow global](#-workflow-global)) :

- Un ticket **simple** suit le chemin : `Prompt Agent → Git Agent → OpenCode Agent → Git Deploy Agent `.
- Un ticket **complexe** est découpé via `Split Ticket → Create Subtasks`, sans passer par la génération de code directe.

---

## 🐛 Dépannage / Troubleshooting

**Python introuvable**
```bash
python --version
```
Si Python n'est pas reconnu, réinstaller Python en cochant l'option d'ajout au `PATH`.

**Échec de `pip install`**
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**`ng` non reconnu**
```bash
node --version
npm --version
npm install -g @angular/cli
```

**Backend inaccessible**
- Vérifier que Uvicorn tourne.
- Vérifier http://127.0.0.1:8000/docs

**`.env` non chargé**
- Vérifier que le fichier `.env` est à la racine du projet.
- Vérifier l'orthographe exacte des variables.

**Erreur d'authentification Git**
- Vérifier `GITHUB_OWNER`, `GITHUB_REPOSITORY`, `GITHUB_BRANCH`.
- Vérifier que `GITHUB_PERSONAL_ACCESS_TOKEN` est valide et possède les bonnes permissions.

---

## 🔒 Sécurité

- `.env` → **PRIVÉ**, ne jamais committer.
- `.env.example` → **PUBLIC**, sans valeurs sensibles.

Contenu recommandé du `.gitignore` :

```gitignore
.env
.venv/
node_modules/
__pycache__/
```

---
## 📁 Structure du projet

```text
backend/
│
├── main_workflow.png
│
├── agents/
│   ├── analysis_agent.py
│   ├── git_agent.py
│   ├── git_deploy_agent.py
│   ├── jira_agent_vf.py
│   ├── opencode_agent.py
│   ├── prompt_agent.py
│   └── scénario.md
│
├── api/
│   └── main.py
│
├── git/
│   └── local_git.py
│
├── graph/
│   ├── state.py
│   ├── visualize_workflow.py
│   └── workflow.py
│
└── skills/
    ├── analysis_agent/
    │   └── skill.md
    │
    └── prompt_agent/
        └── skill.md
```

### 📌 Description des principaux dossiers

| Dossier   | Rôle                                                                                             |
| --------- | ------------------------------------------------------------------------------------------------ |
| `agents/` | Contient les différents agents du système : Jira, Analysis, Prompt, Git, OpenCode et Git Deploy. |
| `api/`    | Contient l'API backend développée avec FastAPI.                                                  |
| `git/`    | Contient les fonctions utilitaires liées à la gestion locale de Git.                             |
| `graph/`  | Contient l'état partagé, le workflow LangGraph et les outils de visualisation.                   |
| `skills/` | Contient les instructions spécialisées utilisées par les agents Analysis et Prompt.              |




## 👨‍💻 Lien youtube