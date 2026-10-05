"""
MCP SERVER
----------
Exposes our database functions as MCP tools.
"""

from mcp.server.fastmcp import FastMCP
from app.db import init_db,get_all_expenses,add_expense,delete_expense_by_category

mcp =FastMCP("finpilot-expenses")

init_db()

@mcp.tool()
def list_expenses()-> list[dict]:
    """Return every expenses record: category,amount, and date"""
    return get_all_expenses()

@mcp.tool()
def create_expense(category:str,amount:float,date:str)->dict:
    """Add a new expense. category e.g. 'groceries', amount in rupees, date as YYYY-MM-DD."""
    new_id =add_expense(category,amount,date)
    return {'status':'created','id':new_id,'category':amount,'date':date}

@mcp.tool()
def delete_expense(category:str)->dict:
    """Delete the first expense matching this category."""
    deleted =delete_expense_by_category(category)
    if deleted:
        return {'status':'deleted','category':category}
    return {'status':'not_found','category':category}

if __name__ =="__main__":
    mcp.run(transport ='stdio')
