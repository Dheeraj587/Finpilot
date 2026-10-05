from app.state import financestate
from app.config import get_llm
from app.mcp_client import call_mcp_tool


def query_agent_node(state: financestate) -> dict:
    tool_result = call_mcp_tool("list_expenses", {})

    prompt = f"""You are a finance assistant. Answer the user's question using
ONLY the expense data below. If the data doesn't contain the answer, say so.
Be concise — one or two sentences.

EXPENSE DATA:
{tool_result}

QUESTION:
{state.user_message}"""

    try:
        llm = get_llm()
        reply = llm.invoke(prompt)
        answer = reply.content[0]["text"] if isinstance(reply.content, list) else reply.content
    except Exception as e:
        answer = f"Sorry, I couldn't look that up right now ({type(e).__name__})."

    return {"tool_result": tool_result, "final_response": answer}