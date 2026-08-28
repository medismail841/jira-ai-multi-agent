import asyncio
from graph.workflow import build_git_graph


async def main():

    print("\n")
    print("=" * 60)
    print("🚀 TEST GIT LANGGRAPH")
    print("=" * 60)

    # ========================================================
    # BUILD GRAPH
    # ========================================================

    workflow = build_git_graph()

    # ========================================================
    # INITIAL STATE
    # ========================================================

    state = {
        "project_dir":
            r"C:\Users\User\Desktop\Summer Internship AI\Projects\Formation\multi-agents\Test"
    }

    # ========================================================
    # EXECUTE
    # ========================================================

    result = await workflow.ainvoke(state)

    # ========================================================
    # RESULT
    # ========================================================

    print("\n")
    print("=" * 60)
    print("✅ GIT WORKFLOW TERMINÉ")
    print("=" * 60)

    print("\n📊 RESULTAT :")

    for key, value in result.items():
        print(f"{key} : {value}")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())