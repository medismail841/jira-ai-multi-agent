le fonctionnement que tu cherches est plutôt :

                    USER
                     │
                     ↓
              🎫 Jira Ticket
                     │
                     ↓
             ┌──────────────┐
             │ 1 Jira Agent │
             └──────┬───────┘
                    │
              Ticket récupéré
                    ↓
          ┌──────────────────┐
          │ 2 Analysis Agent │
          └────────┬─────────┘
                   │
                Analysis
                   ↓
          ┌─────────────────┐
          │ 3 Prompt Agent  │
          └────────┬────────┘
                   │
             Coding Prompt
                   ↓
          ┌─────────────────┐
          │  Git Preparation│
          │     Agent       │
          └────────┬────────┘
                   │
          ┌────────┴─────────┐
          │                  │
      switch main          pull
          │                  │
          └────────┬─────────┘
                   ↓
             create branch
                KAN-1
                   ↓
          ┌─────────────────┐
          │ 4 OpenCode Agent│
          └────────┬────────┘
                   ↓
          OpenCode travaille
          sur le projet
                   ↓
          modification du code
Donc oui : avant OpenCode, les 3 autres agents travaillent

Par exemple, pour KAN-1 :

1️⃣ Jira Agent

Il récupère :

KAN-1
Title: Add authentication
Description: ...
Acceptance criteria: ...

↓

2️⃣ Analysis Agent

Il analyse le ticket :

Backend concerné : Spring Boot
Frontend concerné : Angular

Fichiers probablement concernés :
- AuthController
- AuthService
- login.component.ts
...

↓

3️⃣ Prompt Agent

Il transforme l'analyse en instruction pour OpenCode :

Implement authentication according to the Jira ticket.

Modify the Spring Boot backend...
Modify the Angular frontend...
Run tests...
Do not modify unrelated files...

↓

Git Preparation

Avant de laisser OpenCode modifier le projet :

git switch main
git pull origin main
git switch -c KAN-1

↓

4️⃣ OpenCode Agent

Il reçoit le prompt produit par le Prompt Agent et travaille réellement sur le code :

Prompt Agent
      ↓
coding_instruction
      ↓
OpenCode Agent
      ↓
OpenCode
      ↓
modification du projet
Et ça explique pourquoi ton AgentState est important

Ton state transporte progressivement les résultats :

issue_key
    ↓
ticket
    ↓
analysis
    ↓
coding_instruction
    ↓
git_ready
    ↓
git_branch
    ↓
OpenCode

Donc conceptuellement :

AgentState

issue_key
   │
   ├── Jira Agent
   │      ↓
   │    ticket
   │
   ├── Analysis Agent
   │      ↓
   │    analysis
   │
   ├── Prompt Agent
   │      ↓
   │    coding_instruction
   │
   ├── Git Preparation
   │      ↓
   │    git_ready
   │    git_branch = KAN-1
   │
   └── OpenCode Agent
          ↓
       modification

Donc tu avais raison de préciser "OpenCode". Quand tu dis "OpenCode", dans ton architecture, tu parles de l'agent #4 qui intervient après Jira → Analysis → Prompt, pas simplement du git_agent.

La prochaine étape logique est donc de regarder ton graph/workflow.py, car c'est lui qui doit orchestrer correctement cette séquence.












                         ┌─────────────────────┐
                         │   GIT CLONE         │
                         │ /api/git/clone      │
                         └──────────┬──────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────┐
│ WORKFLOW A — GIT PREPARATION                                │
│                                                             │
│ Git Agent                                                   │
│    ↓                                                        │
│ status                                                      │
│    ↓                                                        │
│ fetch                                                       │
│    ↓                                                        │
│ switch main                                                 │
│    ↓                                                        │
│ pull                                                        │
│    ↓                                                        │
│ create ISSUE branch                                         │
│    ↓                                                        │
│ END                                                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────┐
│ WORKFLOW B — JIRA → ANALYSIS → PROMPT                       │
│                                                             │
│ Jira Agent                                                   │
│    ↓                                                        │
│ Analysis Agent                                               │
│    ↓                                                        │
│ Prompt Agent                                                 │
│    ↓                                                        │
│ END                                                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────┐
│ WORKFLOW D — OPENCODE                                        │
│                                                             │
│ OpenCode Agent                                               │
│    ↓                                                        │
│ END                                                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────┐
│ WORKFLOW C — GIT DEPLOY                                      │
│                                                             │
│ Git Deploy Agent                                             │
│    ↓                                                        │
│ git status                                                   │
│    ↓                                                        │
│ git add .                                                    │
│    ↓                                                        │
│ git commit                                                   │
│    ↓                                                        │
│ git push                                                     │
│    ↓                                                        │
│ Pull Request                                                 │
│    ↓                                                        │
│ END                                                         │
└─────────────────────────────────────────────────────────────┘


















             WORKFLOW A
          GIT PREPARATION
                │
                ▼
        Vérifier dossier local
                │
        ┌───────┴────────┐
        │                │
      existe           absent
        │                │
        ▼                ▼
     .git ?          git clone
        │                │
   ┌────┴────┐           │
   │         │           │
  oui       non          │
   │         │           │
   │       erreur        │
   │                     │
   └─────────┬───────────┘
             ▼
        git status
             ↓
        git fetch origin
             ↓
       détecter main
             ↓
       git switch main
             ↓
       git pull origin main
             ↓
     vérifier KAN-1
             ↓
     git switch -c KAN-1
             ↓
          END