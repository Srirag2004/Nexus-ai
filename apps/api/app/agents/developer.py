from app.agents.state import AgentState


async def developer_agent(state: AgentState) -> AgentState:
    if state.repository_context:
        state.plan.append("Developer agent reviewed repository context.")
    return state

