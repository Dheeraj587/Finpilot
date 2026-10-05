from typing import Literal
from pydantic import BaseModel, Field

from app.state import financestate
from app.config import get_llm

class routedecsion(BaseModel):
    """the exact shape the LLM must return."""
    route:Literal['query','write','report'] =Field(
        description='which specialist should handle the request.'

    )
    reason:str =Field(description='one short sentence explaining the choice.')

ROUTER_PROMPT = """You are the router of a personal finance assistant.
Classify the user's message into exactly one route:

query  = asks a question about existing expense data.
         Examples: "How much did I spend on food this month?", "List my last 5 expenses",
         "What was my biggest expense?"
write  = wants to add, update or delete an expense.
         Examples: "Add 400 for groceries today", "Change my Netflix entry to 649",
         "Delete my Uber expense from yesterday"
report = wants a summary or breakdown over a period.
         Examples: "Give me my October report", "Monthly spending summary",
         "Show a category-wise breakdown for this year"

Rules:
- If the message changes data in any way, choose write.
- A single number or fact -> query. A full summary or breakdown -> report.
- Choose only from: query, write, report."""

def router_node(state:financestate)->dict:
    try:
        llm =get_llm().with_structured_output(routedecsion)
        decision =llm.invoke([
            ('system',ROUTER_PROMPT),
            ('human',state.user_message),
        ])
        return {'route':decision.route,'route_reason':decision.reason}
    except Exception as e:
        return{
            'route':'query',
            'route_reason':f"Router failed ({type(e).__name__}); defaulted to read-only",
        }
    