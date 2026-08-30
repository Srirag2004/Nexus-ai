import re
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.entities import CareerAnalysis
from app.schemas.career import CareerAnalyzeRequest


# Keep matching focused on concrete skills, rather than counting filler words in a job ad.
SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python",), "JavaScript": ("javascript", "js"), "TypeScript": ("typescript", "ts"),
    "Java": ("java",), "C++": ("c++", "cpp"), "C#": ("c#", "csharp"),
    "React": ("react", "reactjs", "react.js"), "Next.js": ("next.js", "nextjs"), "Node.js": ("node.js", "nodejs"),
    "FastAPI": ("fastapi",), "Django": ("django",), "Flask": ("flask",), "Spring Boot": ("spring boot",),
    "SQL": ("sql",), "PostgreSQL": ("postgresql", "postgres"), "MySQL": ("mysql",), "MongoDB": ("mongodb", "mongo"), "Redis": ("redis",),
    "Docker": ("docker",), "Kubernetes": ("kubernetes", "k8s"), "AWS": ("aws", "amazon web services"),
    "Google Cloud": ("gcp", "google cloud"), "Azure": ("azure",), "Git": ("git",), "GitHub Actions": ("github actions",),
    "CI/CD": ("ci/cd", "continuous integration", "continuous delivery"), "Terraform": ("terraform",), "Linux": ("linux",),
    "REST APIs": ("rest api", "restful"), "GraphQL": ("graphql",), "Microservices": ("microservices", "microservice"),
    "System Design": ("system design",), "Testing": ("testing", "unit tests", "integration tests"), "Pytest": ("pytest",),
    "Machine Learning": ("machine learning", "ml"), "Deep Learning": ("deep learning",), "LLMs": ("llm", "llms", "large language model"),
    "RAG": ("rag", "retrieval augmented generation"), "LangChain": ("langchain",), "OpenAI API": ("openai", "openai api"),
    "Gemini API": ("gemini", "gemini api"), "Pandas": ("pandas",), "NumPy": ("numpy",), "PyTorch": ("pytorch",),
    "TensorFlow": ("tensorflow",), "Power BI": ("power bi",), "Tableau": ("tableau",), "Figma": ("figma",),
    "Agile": ("agile",), "Scrum": ("scrum",), "Leadership": ("leadership",),
    "Project Management": ("project management",), "Communication": ("communication", "stakeholder management"),
}


class CareerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def analyze(self, user_id: UUID, payload: CareerAnalyzeRequest) -> CareerAnalysis:
        resume_skills = _extract_skills(payload.resume_text)
        job_skills = _extract_skills(payload.job_description)
        matched = [skill for skill in job_skills if skill in resume_skills]
        missing = [skill for skill in job_skills if skill not in resume_skills]
        score = round(len(matched) / len(job_skills), 2) if job_skills else 0.0
        if job_skills:
            summary = (
                f"Your resume shows {len(matched)} of the {len(job_skills)} concrete skills detected in this job description. "
                "Use the gaps below to tailor your resume only where you have real evidence."
            )
        else:
            summary = "NEXUS could not identify common skills in the job description. Add more detail for a useful comparison."
        analysis = CareerAnalysis(
            user_id=user_id,
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            match_score=score,
            matched_skills=matched,
            missing_skills=missing,
            recommendations=_recommendations(matched, missing),
            summary=summary,
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis


def _extract_skills(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.lower())
    return [
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if any(re.search(rf"(?<!\w){re.escape(alias.lower())}(?!\w)", normalized) for alias in aliases)
    ]


def _recommendations(matched: list[str], missing: list[str]) -> list[str]:
    recommendations: list[str] = []
    if matched:
        recommendations.append(f"Move evidence of {', '.join(matched[:3])} into your resume summary or strongest project bullets.")
    if missing:
        recommendations.append(f"If you have relevant experience, add proof for {', '.join(missing[:3])} with a project, result, or certification.")
    if len(missing) > 3:
        recommendations.append("Prioritize the most repeated role requirements instead of trying to add every gap at once.")
    recommendations.append("Use measurable outcomes in your bullets, such as performance improvements, users served, or delivery time.")
    return recommendations[:3]
