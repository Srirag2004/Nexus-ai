from app.agents.state import AgentState


async def career_agent(state: AgentState) -> AgentState:
    if "job" in state.user_message.lower() or "resume" in state.user_message.lower():
        state.plan.append("Career agent flagged career-specific reasoning.")
    return state

