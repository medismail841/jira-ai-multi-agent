


def jira_tiket_information(issue_key: str):
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
    
    return ticket




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
