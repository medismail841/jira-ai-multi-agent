Jira
  │
  ▼
Agent 1 — Jira
  │
  ▼
Agent 2 — Analysis
  │
  ▼
Agent 3 — Prompt
  │
  ▼
Agent 4 — OpenCode
  │
  │ modifie réellement le projet local
  ▼
Project Collector
  │
  │ lit les fichiers réellement présents
  ▼
Agent 5 — GitHub
  │
  │ utilise GitHub MCP
  ▼
GitHub




                    ┌─────────────────┐
                    │   Jira Ticket   │
                    │      KAN-1      │
                    └────────┬────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  Agent 1 — Jira     │
                  │                     │
                  │ Récupère le ticket  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Agent 2 — Analysis  │
                  │                     │
                  │ Comprend le besoin  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Agent 3 — Prompt    │
                  │                     │
                  │ Génère instruction  │
                  │ pour le développeur │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Agent 4 — OpenCode  │
                  │                     │
                  │ Modifie le projet   │
                  │ + lance les tests   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Agent 5 — Git       │
                  │                     │
                  │ Vérifie les changements
                  │ commit / push       │
                  └─────────────────────┘













                                   🎫 Jira Ticket
                      │
                      ▼
              ┌───────────────┐
              │  Jira Agent   │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Analysis Agent│
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Prompt Agent   │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ OpenCode Agent │
              └───────┬───────┘
                      │
             explore / modify / test
                      │
                      ▼
              ┌───────────────┐
              │   Git Agent   │
              └───────┬───────┘
                      │
                      ▼
                    DONE