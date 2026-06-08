from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator


class SubQuestion(BaseModel):
	question: str
	tool: str = Field(description="One of: rag_search, sql_query, web_search")
	rationale: str


class Plan(BaseModel):
	sub_questions: List[SubQuestion]


class Evidence(BaseModel):
	source: str
	content: str
	url: Optional[str] = None


class CriticReport(BaseModel):
	faithfulness: float = Field(ge=0, le=1)
	citation_coverage: float = Field(ge=0, le=1)
	completeness: float = Field(ge=0, le=1)
	overall: float = Field(ge=0, le=1)
	feedback: str
	approved: bool


class AgentState(TypedDict):
	question: str
	plan: Optional[Plan]
	evidence: Annotated[List[Evidence], operator.add]
	draft: Optional[str]
	critic_report: Optional[CriticReport]
	iterations: int
	final_answer: Optional[str]
