from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Skill(BaseModel):
    name: str
    description: str
    long_description: str
    skill_categories: List[str]


class Skills(BaseModel):
    hard_skills: Optional[Dict[str, Skill]] = Field(default_factory=dict)
    soft_skills: Optional[Dict[str, Skill]] = Field(default_factory=dict)


class SkillsExtract(BaseModel):
    required_skills: Skills
    nice_to_have_skills: Skills


class EvaluationSkill(BaseModel):
    name: str
    match: str
    content_match: str
    reasoning: str


class EvaluationSkills(BaseModel):
    hard_skills: Optional[Dict[str, EvaluationSkill]] = Field(default_factory=dict)
    soft_skills: Optional[Dict[str, EvaluationSkill]] = Field(default_factory=dict)


class EvaluationExtract(BaseModel):
    required_skills: EvaluationSkills
    nice_to_have_skills: EvaluationSkills
