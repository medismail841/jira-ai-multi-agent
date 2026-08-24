""" récupérer le ticket Jira et le mettre dans le State. """
""" Ce fichier contient un Node LangGraph, mais pas le Graph complet.
 """
import os
import base64
import requests

from dotenv import load_dotenv

from graph.state import AgentState


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(override=True)


JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_URL = os.getenv("JIRA_URL")


if not JIRA_EMAIL:
    raise ValueError(
        "JIRA_EMAIL n'est pas défini dans .env"
    )


if not JIRA_API_TOKEN:
    raise ValueError(
        "JIRA_API_TOKEN n'est pas défini dans .env"
    )


if not JIRA_URL:
    raise ValueError(
        "JIRA_URL n'est pas défini dans .env"
    )


# ============================================================
# JIRA AUTHENTICATION
# ============================================================

credentials = (
    f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
)


encoded_credentials = base64.b64encode(
    credentials.encode("utf-8")
).decode("utf-8")


JIRA_HEADERS = {

    "Authorization":
        f"Basic {encoded_credentials}",

    "Accept":
        "application/json",

    "Content-Type":
        "application/json",

}


# ============================================================
# ADF → TEXT
# ============================================================

def extract_adf_text(adf) -> str:

    if not adf:
        return "Information manquante"

    if isinstance(adf, str):
        return adf

    texts = []

    def walk(node):

        if isinstance(node, dict):

            if node.get("type") == "text":

                text = node.get("text")

                if text:
                    texts.append(text)

            for value in node.values():

                if isinstance(
                    value,
                    (dict, list)
                ):
                    walk(value)

        elif isinstance(node, list):

            for item in node:
                walk(item)

    walk(adf)

    if not texts:
        return "Information manquante"

    return " ".join(texts)


# ============================================================
# GET JIRA ISSUE
# ============================================================

def get_jira_issue(issue_key: str) -> dict:

    issue_key = (
        issue_key
        .strip()
        .upper()
    )

    url = (
        f"{JIRA_URL.rstrip('/')}"
        f"/rest/api/3/issue/{issue_key}"
    )

    print("\n" + "=" * 60)
    print("🔎 AGENT 1 — JIRA AGENT")
    print("=" * 60)

    print(f"Ticket : {issue_key}")

    try:

        response = requests.get(
            url,
            headers=JIRA_HEADERS,
            timeout=30
        )

    except requests.RequestException as e:

        raise RuntimeError(
            f"Erreur de connexion Jira : {e}"
        )

    print(
        f"HTTP Status : {response.status_code}"
    )

    if response.status_code != 200:

        raise RuntimeError(
            f"""
Jira REST a retourné :

HTTP {response.status_code}

{response.text}
"""
        )

    try:

        return response.json()

    except ValueError:

        raise RuntimeError(
            "Jira a retourné un JSON invalide."
        )


# ============================================================
# FORMAT TICKET
# ============================================================

def format_ticket(data: dict) -> dict:

    fields = data.get(
        "fields",
        {}
    )

    status = fields.get(
        "status",
        {}
    )

    issue_type = fields.get(
        "issuetype",
        {}
    )

    priority = fields.get(
        "priority",
        {}
    )

    project = fields.get(
        "project",
        {}
    )

    assignee = fields.get(
        "assignee"
    )

    if isinstance(assignee, dict):

        assignee_name = (
            assignee.get("displayName")
            or assignee.get("emailAddress")
            or "Information manquante"
        )

    else:

        assignee_name = "Non assigné"

    return {

        "key":
            data.get(
                "key",
                "Information manquante"
            ),

        "summary":
            fields.get(
                "summary",
                "Information manquante"
            ),

        "description":
            extract_adf_text(
                fields.get("description")
            ),

        "status":
            status.get(
                "name",
                "Information manquante"
            )
            if isinstance(status, dict)
            else "Information manquante",

        "priority":
            priority.get(
                "name",
                "Information manquante"
            )
            if isinstance(priority, dict)
            else "Information manquante",

        "issue_type":
            issue_type.get(
                "name",
                "Information manquante"
            )
            if isinstance(issue_type, dict)
            else "Information manquante",

        "assignee":
            assignee_name,

        "project": {

            "name":
                project.get(
                    "name",
                    "Information manquante"
                ),

            "key":
                project.get(
                    "key",
                    "Information manquante"
                )

        }

    }


# ============================================================
# LANGGRAPH NODE
# ============================================================

def jira_agent(
    state: AgentState
) -> AgentState:

    issue_key = state.get(
        "issue_key"
    )

    if not issue_key:

        raise ValueError(
            "❌ issue_key manquant dans le State."
        )

    data = get_jira_issue(
        issue_key
    )

    ticket = format_ticket(
        data
    )

    print("\n✅ Ticket Jira récupéré")

    print(
        f"Summary : {ticket['summary']}"
    )

    print(
        f"Status  : {ticket['status']}"
    )

    return {

        "ticket": ticket

    }
    
