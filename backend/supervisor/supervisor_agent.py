# supervisor agent - orchestrator

import os
from typing import Literal

from langchain_groq import ChatGroq
from opik.integrations.langchain import OpikTracer
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from .state import SupervisorState
from agents.wellness.agent import get_wellness_agent
from agents.productivity.agent import get_productivity_agent

from agents.constants import FORMATTING_PROMPT

# The supervisor's system prompt instructs it to route queries.
SYSTEM_PROMPT = f"""You are the Supervisor Agent for Equinox.
Your job is to route user requests to the appropriate specialist agent.

Specialist Agents:
1. Wellness Agent: Handles health, sleep, readiness, and workout related queries.
2. Productivity Agent: Handles emails, notes, todos, and task management.

If the user greets you or asks a general question, you can answer directly, but try to steer them to a topic.
If you answer directly, set 'next' to 'end'.
If you route to an agent, set 'next' to 'wellness' or 'productivity'.

{FORMATTING_PROMPT} (when answering directly)
"""

# Output structure for routing
class RouteResponse(BaseModel):
    next: Literal["wellness", "productivity", "end"]
    response: str = Field(description="Response to the user if ending, or reasoning if routing.")

def create_supervisor_graph():
    """create and return the supervisor graph"""
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1, # Low temp for precise routing
        api_key=os.getenv("GROQ_API_KEY")
    )
    # structured output for routing
    router = llm.with_structured_output(RouteResponse)
    
    def supervisor_node(state: SupervisorState):
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
            
        result = router.invoke(messages, config={"callbacks": [OpikTracer(project_name="equinox")]})
        
        # We append the supervisor's thought/response to history
        return {
            "next": result.next,
            "messages": [AIMessage(content=result.response)]
        }
    
    def call_wellness_agent(state: SupervisorState, config: RunnableConfig):
        """Invoke wellness agent graph"""
        wellness_agent = get_wellness_agent()
        
        # Extract thread_id from metadata if present
        metadata = config.get("metadata", {})
        thread_id = metadata.get("thread_id")
        
        # Transform state for sub-agent
        sub_state = {
            "messages": state["messages"],
            "user_id": state["user_id"],
            "timezone": "Asia/Kolkata", # Defaulting for now
             # other fields init to None
            "today_health": None
        }
        
        # Pass metadata to sub-agent
        invoke_config = {"callbacks": [OpikTracer(project_name="equinox")]}
        if thread_id:
            invoke_config["metadata"] = {"thread_id": thread_id}
            
        result = wellness_agent.invoke(sub_state, config=invoke_config)
        # We want to capture the LAST message from the sub-agent
        last_msg = result["messages"][-1]
        return {"messages": [last_msg]}

    def call_productivity_agent(state: SupervisorState, config: RunnableConfig):
        """Invoke productivity agent graph"""
        prod_agent = get_productivity_agent()
        
        # Extract thread_id from metadata if present
        metadata = config.get("metadata", {})
        thread_id = metadata.get("thread_id")
        
        sub_state = {
            "messages": state["messages"],
            "user_id": state["user_id"]
        }
        
        # Pass metadata to sub-agent
        invoke_config = {"callbacks": [OpikTracer(project_name="equinox")]}
        if thread_id:
            invoke_config["metadata"] = {"thread_id": thread_id}
            
        result = prod_agent.invoke(sub_state, config=invoke_config)
        last_msg = result["messages"][-1]
        return {"messages": [last_msg]}

    graph = StateGraph(SupervisorState)
    
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("wellness", call_wellness_agent)
    graph.add_node("productivity", call_productivity_agent)
    
    graph.set_entry_point("supervisor")
    
    # Conditional routing
    graph.add_conditional_edges(
        "supervisor",
        lambda x: x["next"],
        {
            "wellness": "wellness",
            "productivity": "productivity",
            "end": END
        }
    )
    
    # Sub-agents return to supervisor? Or end?
    # Simple pattern: Sub-agents do work, then we END (one turn). 
    # Or we can loop back to supervisor. For now, let's END after sub-agent work 
    # so the user gets the response.
    graph.add_edge("wellness", END)
    graph.add_edge("productivity", END)
    
    return graph.compile()


_supervisor_graph = None

def get_supervisor_graph():
    global _supervisor_graph
    if _supervisor_graph is None:
        _supervisor_graph = create_supervisor_graph()
    return _supervisor_graph
