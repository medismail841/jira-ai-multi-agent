🧠 Le rôle du Git Agent

Après qu'OpenCode ait terminé son travail :

OpenCode
   │
   │ crée/modifie des fichiers
   ▼
Al_habib/

Le Git Agent arrive et demande :

"Quelle est la situation de ce projet ?"

Il regarde deux endroits :

             GIT AGENT
                 │
        ┌────────┴────────┐
        ▼                 ▼
      LOCAL             GITHUB
        │                 │
   Al_habib/          repository


🟦 Partie LOCAL

Le Git Agent regarde :

C:\Users\User\Desktop\جامع الغفار\Al_habib

et pose ces questions :

Question 1
Est-ce que le dossier existe ?
Question 2
Est-ce que le dossier contient des fichiers ?
Question 3
Est-ce qu'il contient .git ?
Question 4

Si .git existe :

git status
Question 5
git branch --show-current
Question 6
git remote -v






🟩 Partie GITHUB

Ensuite le Git Agent regarde le repository GitHub grâce au GitHub MCP Server.

Il demande :

Est-ce que le repository existe ?

Puis :

Est-ce qu'il contient déjà des fichiers ?

Puis :

Quelle est sa branche principale ?





🟨 Ensuite LangGraph décide

Quand on connaît les deux côtés :

LOCAL                    GITHUB

.git ?                   repo ?
vide ?                   vide ?
status                   fichiers ?
remote ?                 branch ?

LangGraph peut prendre une décision.

Cas 1
LOCAL                    GITHUB

vide                     vide
.git ❌                   vide

Alors :

git init
   ↓
git add .
   ↓
git commit
   ↓
git remote add
   ↓
git push
Cas 2
LOCAL                    GITHUB

vide                     plein
.git ❌                   plein

Alors :

git clone
Cas 3
LOCAL                    GITHUB

plein                    plein
.git ❌                   plein

Alors :

❌ ERREUR

Parce que deux projets existent indépendamment.

On ne veut pas que l'agent mélange automatiquement les deux.

Cas 4 — le cas normal après OpenCode
LOCAL                    GITHUB

plein                    plein
.git ✅                   plein

Alors :

git status
    ↓
créer nouvelle branche
    ↓
git add .
    ↓
git commit
    ↓
git push
    ↓
GitHub MCP
    ↓
Pull Request

Donc :

main
 │
 └──── feature/KAN-1
              │
              │ modifications OpenCode
              ↓
            commit
              ↓
            push
              ↓
        Pull Request
              ↓
             main
🔥 Et pourquoi MCP ?

Parce que nous avons deux mondes.

Git local

Le MCP GitHub ne peut pas simplement faire :

cd C:\Users\...\Al_habib
git status

Donc pour le local, notre Python utilise :

subprocess
   ↓
git status
git init
git add
git commit
git clone
git push
GitHub

Pour GitHub, notre agent utilise :

Git Agent
    ↓
LangChain MCP Client
    ↓
GitHub MCP Server
    ↓
GitHub
🧩 Pourquoi LangGraph ?

LangGraph va orchestrer tout ça :

             START
               ↓
       inspect LOCAL
               ↓
       inspect GITHUB
               ↓
          DECISION
          /   |   \
         /    |    \
        ↓     ↓     ↓
      INIT  CLONE  ERROR
                  ou
               BRANCH
                  ↓
                COMMIT
                  ↓
                 PUSH
                  ↓
                  PR
                  ↓
                 END
📍 Où sommes-nous actuellement ?

Nous avons déjà fait :

1. AgentState
       ✅
       ↓
2. outils Git local
       ✅
       ↓
3. inspection LOCAL
       ✅

Mais notre test de l'étape 3 utilisait le mauvais dossier uniquement pour vérifier techniquement le code.

Le vrai dossier cible est :

C:\Users\User\Desktop\جامع الغفار\Al_habib

Donc maintenant :

                    GIT AGENT
                        │
                        ▼
             Al_habib ← VRAI PROJET
                        │
                 ┌──────┴──────┐
                 ▼             ▼
               LOCAL         GITHUB
                 │             │
                 └──────┬──────┘
                        ▼
                     DECISION 












Ce que ton agent vient de faire
                 START
                   │
                   ▼
      ┌─────────────────────────┐
      │ Local Inspection        │
      │                         │
      │ .git = NON              │
      │ dossier = VIDE          │
      └────────────┬────────────┘
                   │
                   ▼
      ┌─────────────────────────┐
      │ GitHub MCP Inspection   │
      │                         │
      │ Repository = EXISTE     │
      │ Remote = VIDE           │
      └────────────┬────────────┘
                   │
                   ▼
      ┌─────────────────────────┐
      │ Git Decision            │
      │                         │
      │ action = init           │
      └─────────────────────────┘






      PULL_REQUEST
      ↓
1. créer une nouvelle branche
      ↓
2. git add .
      ↓
3. git commit
      ↓
4. git push
      ↓
5. GitHub MCP → create_pull_request












































inspection → router → branche → add → commit → push

Ton workflow actuel :

INSPECTION
    ↓
ROUTER
    ↓
BRANCHE
    ↓
ADD
    ↓
COMMIT
    ↓
PUSH
    ↓
PULL REQUEST

Voici exactement ce que fait chaque nœud.

1. 🔎 INSPECTION

Tu as en réalité deux inspections :

inspect_local_repository
        +
inspect_github_repository
A. inspect_local_repository

Son rôle est de regarder l'état du projet local sans le modifier.

Il vérifie :

Projet local
│
├── Est-ce que le dossier existe ?
├── Est-ce qu'il est vide ?
├── Est-ce que .git existe ?
├── Quelle est la branche actuelle ?
├── Est-ce qu'un remote existe ?
└── Quel est le git status ?

Exemple :

📁 Test
├── .git
├── main.py
└── jira_KAN-1_prompt.md

Résultat :

{
    "git_exists": True,
    "local_is_empty": False,
    "git_current_branch": "master",
    "git_has_remote": True
}

Important : ce nœud ne fait pas git init, git add, git commit, etc.

Il observe seulement.

B. inspect_github_repository

Même principe, mais côté GitHub.

Il utilise :

GitHub MCP

pour savoir si le repository distant contient déjà quelque chose.

Par exemple :

GitHub
└── Test_ia

Repository vide :

Test_ia
└── rien

Résultat :

{
    "github_repo_exists": True,
    "github_remote_is_empty": True,
    "github_remote_is_full": False
}

Donc après les deux inspections, ton state contient une photographie de la situation :

LOCAL                         GITHUB
─────                         ──────
.git = OUI                    repo = OUI
fichiers = OUI                fichiers = NON
remote = OUI
branche = master
2. 🧠 ROUTER

Fonction :

decide_git_action(state)

C'est le cerveau décisionnel du Git Agent.

Il ne fait pas d'opération Git.

Il répond uniquement :

"Qu'est-ce que je dois faire maintenant ?"

Par exemple :

Cas 1
Local vide
.git absent
GitHub vide

→

{
    "git_action": "init"
}
Cas 2
Local plein
.git absent
GitHub vide

→

{
    "git_action": "init_and_push"
}
Cas 3
Local vide
.git absent
GitHub plein

→

{
    "git_action": "clone"
}
Cas 4
Local Git existant
remote existant

→

{
    "git_action": "pull_request"
}

Donc :

              INSPECTIONS
                   ↓
             ┌───────────┐
             │  ROUTER   │
             └─────┬─────┘
                   │
       ┌───────────┼────────────┐
       ↓           ↓            ↓
      init       clone      pull_request

Le router décide. Il n'exécute pas.

C'est très important dans ton architecture.

3. 🌿 BRANCHE

Fonction :

create_git_branch(state)

Elle est utilisée lorsque le router décide :

git_action = "pull_request"

Son rôle :

master
   ↓
feature/KAN-1

Elle exécute :

git checkout -b feature/KAN-1

Pourquoi créer une branche ?

Parce qu'on ne veut généralement pas modifier directement :

main

On travaille sur :

feature/KAN-1

Donc :

main/master
      │
      └──── feature/KAN-1
                  ↑
             modifications

Le résultat est stocké dans le state :

{
    "git_branch_name": "feature/KAN-1",
    "git_current_branch": "feature/KAN-1"
}
4. 📦 ADD

Fonction :

git_add_files(state)

Elle exécute :

git add .

Son rôle est de mettre les modifications dans la staging area.

Avant :

Working Directory
│
├── main.py          modified
└── config.py        new

Après :

Working Directory
        ↓
   git add .
        ↓
Staging Area
│
├── main.py
└── config.py

Mais attention :

git add ne crée PAS de commit.

Il prépare seulement les fichiers.

5. 💾 COMMIT

Fonction :

git_commit(state)

Elle exécute par exemple :

git commit -m "feat(KAN-1): implement changes"

Le commit crée une version enregistrée dans Git.

Avant :

Staging Area
     ↓
   commit
     ↓
Git History

Tu as obtenu :

44c42df feat(KAN-1): implement changes

Donc maintenant :

LOCAL
│
├── feature/KAN-1
│
└── commit
    └── 44c42df

Mais ce commit est encore uniquement local.

C'est exactement ce que tu avais constaté avant le push.

6. 🚀 PUSH

Fonction :

git_push(state)

Elle exécute :

git push -u origin feature/KAN-1

Son rôle est de transférer le commit :

LOCAL
│
└── feature/KAN-1
        │
        └── 44c42df
               │
               │ git push
               ↓
           GITHUB
               │
               └── feature/KAN-1

Dans ton test, tu as obtenu :

[new branch] feature/KAN-1 -> feature/KAN-1

Donc cette étape est validée. ✅

7. 🔀 PULL REQUEST

C'est la prochaine étape que tu dois implémenter.

Elle sera différente des précédentes.

Jusqu'à maintenant :

git init
git checkout
git add
git commit
git push

sont des commandes Git locales.

La Pull Request, elle, sera créée avec ton :

GitHub MCP

Tu as déjà découvert le tool :

create_pull_request

Le workflow sera :

GitHub
│
├── main
│
└── feature/KAN-1
         │
         │
         └──────────────┐
                        ↓
                 CREATE PULL REQUEST
                        ↓
                 feature/KAN-1
                        ↓
                       main

Résultat attendu :

Pull Request #1

feature/KAN-1 → main

feat(KAN-1): implement changes
🧩 Donc ton architecture complète

Ton Git Agent devient :

                    ┌──────────────────────┐
                    │   LOCAL INSPECTION   │
                    │                      │
                    │ .git ?              │
                    │ fichiers ?           │
                    │ remote ?             │
                    │ branch ?             │
                    └──────────┬───────────┘
                               │
                               ↓
                    ┌──────────────────────┐
                    │  GITHUB INSPECTION   │
                    │                      │
                    │ repo existe ?        │
                    │ repo vide ?          │
                    │ repo plein ?        │
                    └──────────┬───────────┘
                               │
                               ↓
                    ┌──────────────────────┐
                    │        ROUTER        │
                    │                      │
                    │ decide_git_action()  │
                    └──────────┬───────────┘
                               │
                         pull_request
                               ↓
                    ┌──────────────────────┐
                    │       BRANCHE        │
                    │                      │
                    │ feature/KAN-1        │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │         ADD          │
                    │                      │
                    │ git add .            │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │       COMMIT         │
                    │                      │
                    │ feat(KAN-1): ...     │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │        PUSH          │
                    │                      │
                    │ origin/feature/KAN-1 │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │    PULL REQUEST      │
                    │                      │
                    │ GitHub MCP           │
                    │ feature → main       │
                    └──────────────────────┘
🎯 Et surtout : séparation des responsabilités

C'est ça qui rend ton architecture propre :

Nœud	Responsabilité	Modifie ?
inspect_local_repository	Observer le local	❌
inspect_github_repository	Observer GitHub	❌
decide_git_action	Décider	❌
create_git_branch	Créer branche	✅
git_add_files	Préparer fichiers	✅
git_commit	Créer version Git	✅
git_push	Envoyer vers GitHub	✅
create_git_pull_request	Créer PR GitHub	✅

Dans ton état actuel, les 7 premières étapes sont pratiquement en place. La prochaine vraie étape est donc create_git_pull_request() via create_pull_request du GitHub MCP.