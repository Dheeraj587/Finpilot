from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.state import financestate
from app.nodes.guardrail import guardrail_node
from app.nodes.router import router_node
from app.nodes.query_agent import query_agent_node
from app.nodes.write_agent import write_agent_node
from app.nodes.execute_write import execute_write_node
from app.nodes.report_agent import report_agent_node


def route_after_guadrail(state: financestate) -> str:
    if state.is_safe:
        return "router"
    return "blocked"


def blocked_node(state: financestate) -> dict:
    return {"final_response": f"Sorry, I can't process that: {state.block_reason}"}


def route_after_router(state: financestate) -> str:
    if state.route == "query":
        return "query_agent"
    if state.route == "write":
        return "write_agent"
    if state.route == "report":
        return "report_agent"
    return "end"

def build_graph():
    graph = StateGraph(financestate)

    graph.add_node('guardrail', guardrail_node)
    graph.add_node('router', router_node)
    graph.add_node('blocked', blocked_node)
    graph.add_node('query_agent', query_agent_node)
    graph.add_node('write_agent', write_agent_node)
    graph.add_node('execute_write', execute_write_node)
    graph.add_node('report_agent',report_agent_node)

    graph.set_entry_point('guardrail')

    graph.add_conditional_edges(
        "guardrail", route_after_guadrail,
        {'router': 'router', "blocked": 'blocked'},
    )
    graph.add_conditional_edges(
        "router", route_after_router,
        {'query_agent': 'query_agent', 'write_agent': 'write_agent', 
         'report_agent':'report_agent','end': END},
    )

    graph.add_edge('blocked', END)
    graph.add_edge('query_agent', END)
    graph.add_edge('write_agent', 'execute_write')
    graph.add_edge('execute_write', END)
    graph.add_edge('report_agent',END)
    

    checkpointer = MemorySaver()

    # THE KEY LINE: pause right before execute_write runs.
    return graph.compile(checkpointer=checkpointer, interrupt_before=["execute_write"])


app_graph = build_graph()