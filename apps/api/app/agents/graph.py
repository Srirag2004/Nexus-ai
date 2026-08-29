from app.agents.career import career_agent
from app.agents.developer import developer_agent
from app.agents.planner import planner_agent
from app.agents.researcher import researcher_agent
from app.agents.reviewer import reviewer_agent
from app.agents.state import AgentState


async def run_agent_flow(state: AgentState) -> AgentState:
    for agent in (planner_agent, researcher_agent, developer_agent, career_agent, reviewer_agent):
        state = await agent(state)
    return state

