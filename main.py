from app.graph import app_graph
from app.state import financestate
import uuid

def run_write_flow(message: str, thread_id: str = None):
    # Give every unrelated test message its own thread, so old state
    # from a previous message never leaks into this one.
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"\nMessage : {message}")
    result = app_graph.invoke(financestate(user_message=message), config)

    snapshot = app_graph.get_state(config)
    if snapshot.next == ("execute_write",):
        action = result["pending_action"]
        print(f"APPROVAL NEEDED: {action}")
        answer = input("Approve this action? (y/n): ").strip().lower()

        if answer == "y":
            app_graph.update_state(config, {"approved": True})
            final = app_graph.invoke(None, config)
            print("Final   :", final.get("final_response"))
        else:
            app_graph.update_state(config, {"approved": False})
            final = app_graph.invoke(None, config)
            print("Final   :", final.get("final_response"))
    else:
        print("Safe    :", result.get("is_safe"))
        print("Route   :", result.get("route"))
        print("Final   :", result.get("final_response"))


if __name__ == "__main__":
    run_write_flow("Add 400 for groceries today")
    print("-" * 50)
    run_write_flow("How much did I spend on food this month?")
    print("-" * 50)
    run_write_flow("Give me a summary of my expenses")