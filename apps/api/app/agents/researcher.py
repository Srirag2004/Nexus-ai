from app.agents.state import AgentState


async def researcher_agent(state: AgentState) -> AgentState:
    if state.retrieved_documents:
        state.plan.append("Researcher attached relevant document snippets.")
    return state

