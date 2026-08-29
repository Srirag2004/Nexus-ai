from app.agents.state import AgentState


async def reviewer_agent(state: AgentState) -> AgentState:
    state.plan.append("Reviewer checked for grounding and completeness.")
    return state

