"""
WRITE AGENT
-----------
Job: turn a write request into a structured action, WITHOUT executing it.
Touches only: pending_action.
The actual database change happens later, only after human approval.
"""

from typing import Literal,Optional
from pydantic import BaseModel, Field

from app.state import financestate
from app.config import get_llm

class writeAction(BaseModel):
    action: Literal['add','update','delete'] =Field(description="what kind of change.")
    category:str = Field(description='Expense category, e.g. groceries, food, transport')
    amount: Optional[float]=Field(default=None,description="amount in rupess,if mentioned")
    date: Optional[str]= Field(default=None,description="date in YYYY-MM-DD if mentioned, else'today'.")

WRITE_PROMPT ="""Extract the write action from the user's message.
Today's date is 2026-09-29. If the user says "today", use this date.
If no date is mentioned, use today's date."""

def write_agent_node(state:financestate)->dict:
    try:
        llm=get_llm().with_structured_output(writeAction)
        parsed =llm.invoke([
            ('system',WRITE_PROMPT),
            ('human',state.user_message),
        ])
        pending_action =parsed.model_dump()
    except Exception as e:
        pending_action={'error':f"could not understand the request ({type(e).__name__})"}


    return {'pending_action':pending_action}