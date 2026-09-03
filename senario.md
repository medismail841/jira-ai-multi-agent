                 MANUELLEMENT
                      │
                      ▼
              git clone <repo>
                      │
                      ▼
              dossier projet
                  contient .git
                      │
                      ▼
              Git Agent
                      │
              ┌───────┴────────┐
              │                │
         git status        pas de .git
              │                │
              ▼                ▼
          OK              ❌ ERROR
              │
              ▼
          git switch main
              │
              ▼
          git pull
              │
              ▼
       git switch -c KAN-1
              │
              ▼
          OpenCode
              │
              ▼
       modification du code