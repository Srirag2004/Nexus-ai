from app.agents.state import AgentState


async def planner_agent(state: AgentState) -> AgentState:
    state.plan = [
        "Interpret the request and identify required context.",
        "Gather supporting memories, knowledge, or repository data.",
        "Draft a grounded response and review it.",
    ]
    return state

