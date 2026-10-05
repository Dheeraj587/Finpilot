from app.state import financestate
from app.mcp_client import call_mcp_tool


def execute_write_node(state: financestate) -> dict:
    if not state.approved:
        return {"final_response": "Action cancelled. Nothing was changed."}

    action = state.pending_action

    if "error" in action:
        return {"final_response": f"Couldn't complete this: {action['error']}"}

    if action["action"] == "add":
        call_mcp_tool("create_expense", {
            "category": action["category"],
            "amount": action["amount"],
            "date": action["date"],
        })
        return {"final_response": f"Added {action['category']} expense of {action['amount']} on {action['date']}."}

    if action["action"] == "delete":
        call_mcp_tool("delete_expense", {"category": action["category"]})
        return {"final_response": f"Deleted {action['category']} expense (via MCP)."}

    return {"final_response": f"'{action['action']}' is not implemented yet."}