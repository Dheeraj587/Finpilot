from app.state import financestate
from app.config import get_llm
from app.mcp_client import call_mcp_tool


def report_agent_node(state: financestate) -> dict:
    tool_result = call_mcp_tool("list_expenses", {})

    prompt = f"""You are a finance assistant. Using ONLY the expense data below,
write a short report answering the user's request. Include a total, a
category-wise breakdown, and one observation (e.g. highest category).
Keep it under 5 sentences.

EXPENSE DATA:
{tool_result}

REQUEST:
{state.user_message}"""

    try:
        llm = get_llm()
        reply = llm.invoke(prompt)
        answer = reply.content[0]["text"] if isinstance(reply.content, list) else reply.content
    except Exception as e:
        answer = f"Sorry, I couldn't generate the report right now ({type(e).__name__})."

    return {"tool_result": tool_result, "final_response": answer}