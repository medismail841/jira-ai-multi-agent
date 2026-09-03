from graph.workflow import build_prompt_graph
from graph.workflow import build_opencode_graph


print("========================================")
print("     PROMPT WORKFLOW")
print("========================================")

prompt_workflow = build_prompt_graph()

with open("prompt_workflow.png", "wb") as f:
    f.write(
        prompt_workflow
        .get_graph()
        .draw_mermaid_png()
    )

print("✅ prompt_workflow.png créé")


print("========================================")
print("     OPENCODE WORKFLOW")
print("========================================")

opencode_workflow = build_opencode_graph()

with open("opencode_workflow.png", "wb") as f:
    f.write(
        opencode_workflow
        .get_graph()
        .draw_mermaid_png()
    )

print("✅ opencode_workflow.png créé")