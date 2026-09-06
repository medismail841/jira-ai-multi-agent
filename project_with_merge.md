                         ┌──────────────────┐
                         │      START       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    GIT AGENT     │
                         │                  │
                         │ git clone        │
                         │ git status       │
                         │ vérifier .git    │
                         │ préparer branche │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    JIRA AGENT    │
                         │                  │
                         │ récupérer ticket │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  ANALYSIS AGENT  │
                         │                  │
                         │ analyser ticket  │
                         └────────┬─────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   CLASSIFY TICKET    │
                       │                      │
                       │ SIMPLE / COMPLEX     │
                       └──────────┬───────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                  SIMPLE                     COMPLEX
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐       ┌──────────────────┐
          │   PROMPT AGENT   │       │  SPLIT TICKET    │
          │                  │       │                  │
          │ créer prompt     │       │ décomposer       │
          │ pour OpenCode    │       │ créer subtasks   │
          └────────┬─────────┘       └────────┬─────────┘
                   │                          │
                   │                          │
                   └────────────┬─────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  OPENCODE AGENT  │
                       │                  │
                       │ coder            │
                       │ modifier projet  │
                       │ tester           │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────────┐
                       │ GIT DEPLOY AGENT     │
                       │                      │
                       │ git status           │
                       │ git add .            │
                       │ git commit           │
                       │ git push             │
                       │ Pull Request         │
                       └──────────┬───────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │       END        │
                         └──────────────────┘