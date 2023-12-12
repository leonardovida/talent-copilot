from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Skill(BaseModel):  # noqa: D101
    name: str
    description: str
    long_description: str
    skill_categories: List[str]


class Skills(BaseModel):  # noqa: D101
    hard_skills: Optional[Dict[str, Skill]] = Field(default_factory=dict)
    soft_skills: Optional[Dict[str, Skill]] = Field(default_factory=dict)


class SkillsExtract(BaseModel):  # noqa: D101
    required_skills: Skills
    nice_to_have_skills: Skills


class EvaluationSkill(BaseModel):  # noqa: D101
    name: str
    match: str
    content_match: str
    reasoning: str


class EvaluationSkills(BaseModel):  # noqa: D101
    hard_skills: Optional[Dict[str, EvaluationSkill]] = Field(default_factory=dict)
    soft_skills: Optional[Dict[str, EvaluationSkill]] = Field(default_factory=dict)


class EvaluationExtract(BaseModel):  # noqa: D101
    required_skills: EvaluationSkills
    nice_to_have_skills: EvaluationSkills
