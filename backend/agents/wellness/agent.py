# wellness agent - langgraph implementation

import os
from typing import Literal

from langchain_groq import ChatGroq
from opik.integrations.langchain import OpikTracer
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .state import WellnessState
from .tools import WELLNESS_TOOLS

from agents.constants import FORMATTING_PROMPT

# system prompt for the wellness agent
SYSTEM_PROMPT = f"""You are a friendly wellness coach AI. Your name is Equinox.

Your job is to help users track and improve their wellness. You have access to tools that can:
- Get their health data for today
- Calculate their readiness score
- Check their sleep debt
- Analyze wellness trends
- Suggest activities based on their energy

Guidelines:
1. Be encouraging but realistic
2. ALWAYS use tools to get REAL data before giving advice - never guess or assume values. If a tool returns no data, state that.
3. If they ask about workouts/activities, FIRST call get_readiness_score() to get their actual zone, THEN call suggest_activity()
4. If they haven't logged today, encourage them to do so
5. Use emoji sparingly but warmly

EXERCISE SPECIFICITY:
When users ask for workout suggestions or specific exercises, provide DETAILED recommendations:
- Name specific exercises (e.g., "Push-ups", "Dumbbell rows", "Squats")
- Include sets and reps (e.g., "3 sets of 12 reps")
- Suggest duration for cardio (e.g., "20 minutes at moderate pace")
- Organize by muscle group when relevant
- Adjust intensity based on their readiness zone

Example for upper body:
- Bench Press: 3 sets x 10 reps
- Dumbbell Rows: 3 sets x 12 reps each arm
- Overhead Press: 3 sets x 10 reps
- Bicep Curls: 3 sets x 12 reps
- Tricep Dips: 3 sets x 15 reps

{FORMATTING_PROMPT}

IMPORTANT: Do NOT hallucinate or make up readiness zones. Always fetch real data first.
"""


def create_wellness_agent():
    """create and return the wellness agent graph"""
    
    # init llm with tools
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY")
    )
    llm_with_tools = llm.bind_tools(WELLNESS_TOOLS)
    
    # define nodes
    def call_model(state: WellnessState):
        """call the llm, possibly requesting tool use"""
        messages = state["messages"]
        
        # add system message if first call
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: WellnessState) -> Literal["tools", "end"]:
        """check if we need to call tools or end"""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
    
    # build graph
    graph = StateGraph(WellnessState)
    
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(WELLNESS_TOOLS))
    
    graph.set_entry_point("agent")
    
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END}
    )
    graph.add_edge("tools", "agent")
    
    return graph.compile()


# singleton agent instance
_wellness_agent = None


def get_wellness_agent():
    """get or create the wellness agent"""
    global _wellness_agent
    if _wellness_agent is None:
        _wellness_agent = create_wellness_agent()
    return _wellness_agent


def chat_with_wellness_agent(user_id: str, message: str) -> str:
    """
    send a message to the wellness agent and get response
    
    args:
        user_id: the user's uuid
        message: their message
    
    returns:
        the agent's response text
    """
    agent = get_wellness_agent()
    
    # prepare initial state
    initial_state = {
        "messages": [HumanMessage(content=message)],
        "user_id": user_id,
        "timezone": "Asia/Kolkata",
        "today_health": None,
        "readiness_score": None,
        "readiness_zone": None,
        "sleep_debt": None,
        "weekly_trend": None,
        "response": None
    }
    
    # run the graph
    opik_tracer = OpikTracer(project_name="equinox")
    result = agent.invoke(initial_state, config={"callbacks": [opik_tracer]})
    
    # extract response
    last_message = result["messages"][-1]
    return last_message.content
