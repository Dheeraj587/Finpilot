from typing import Optional,Literal
from pydantic import BaseModel

class financestate(BaseModel):
    # input
    user_message:str

    # set by: guardrail node
    is_safe:Optional[bool]=None
    block_reason:Optional[str]=None

    # set by: router node
    route:Optional[Literal['query','write','report']]=None
    route_reason: Optional[str]=None

    # set by: query_agent /report_agent
    tool_result:Optional[str]=None

    # set by write_agent
    pending_action:Optional[dict]=None

    # set by: human approval step
    approved:Optional[bool]=None

    #final
    final_response:Optional[str]=None