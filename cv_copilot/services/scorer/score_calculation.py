from typing import List

from cv_copilot.db.models.texts import ParsedTextModel


class ScoreError(Exception):
    """Exception raised when a Score cannot be calculated."""


def calc_skill_matches(skills: List[dict], skill_type: str) -> int:
    """Calculate the match score for skills.
    :param skills: List of skills and their matches.
    :param skill_type: Type of skills (hard_skills or soft_skills).

    :return int: The calculated match score.
    """

    skill_match_score: float = 0.0
    yes_match_weight: float = 1.0
    partial_match_weight: float = 0.5
    no_match_weight: float = 0.0

    if skills[skill_type]:
        for skill in skills[skill_type]:
            if skills[skill_type][skill]["match"] == "NO":
                skill_match_score += no_match_weight
            elif skills[skill_type][skill]["match"] == "PARTIAL":
                skill_match_score += partial_match_weight
            elif skills[skill_type][skill]["match"] == "YES":
                skill_match_score += yes_match_weight

    return skill_match_score


async def score_calculation(parsed_text: ParsedTextModel) -> dict:
    """Calculate the Score using job description and CV matches.
    :param parsed_text: Parsed text containing job description and CV matches.
    :return dict: A dictionary containing the calculated score.
    :raises ValueError: Exception raised when a score cannot be calculated.
    """
    required_skills: List[dict] = parsed_text.parsed_skills.get("required_skills", [])
    nice_to_have_skills: List[dict] = parsed_text.parsed_skills["nice_to_have_skills"]

    # Defining weights
    result: float = 0
    required_skills_weight: float = 0.8
    nice_to_have_skills_weight: float = 0.2
    hard_skills_weights: float = 0.5
    soft_skills_weights: float = 0.5

    # Calc total for each skill/type
    total_required_hard_skills: int = (
        len(required_skills["hard_skills"]) if required_skills["hard_skills"] else 0
    )
    total_required_soft_skills: int = (
        len(required_skills["soft_skills"]) if required_skills["soft_skills"] else 0
    )
    total_nice_to_have_hard_skills: int = (
        len(nice_to_have_skills["hard_skills"])
        if nice_to_have_skills["hard_skills"]
        else 0
    )
    total_nice_to_have_soft_skills: int = (
        len(nice_to_have_skills["soft_skills"])
        if nice_to_have_skills["soft_skills"]
        else 0
    )

    # Calc score for each skill/type
    score_required_hard_skills: float = calc_skill_matches(
        required_skills,
        "hard_skills",
    )
    score_required_soft_skills: float = calc_skill_matches(
        required_skills,
        "soft_skills",
    )
    score_nice_to_have_hard_skills: float = calc_skill_matches(
        nice_to_have_skills,
        "hard_skills",
    )
    score_nice_to_have_soft_skills: float = calc_skill_matches(
        nice_to_have_skills,
        "soft_skills",
    )

    # Calc final score
    if total_required_hard_skills > 0:
        result += (
            (score_required_hard_skills / total_required_hard_skills)
            * required_skills_weight
            * hard_skills_weights
        )

    if total_required_soft_skills > 0:
        result += (
            (score_required_soft_skills / total_required_soft_skills)
            * required_skills_weight
            * soft_skills_weights
        )

    if total_nice_to_have_hard_skills > 0:
        result += (
            (score_nice_to_have_hard_skills / total_nice_to_have_hard_skills)
            * nice_to_have_skills_weight
            * hard_skills_weights
        )

    if total_nice_to_have_soft_skills > 0:
        result += (
            (score_nice_to_have_soft_skills / total_nice_to_have_soft_skills)
            * nice_to_have_skills_weight
            * soft_skills_weights
        )

    response = {"score": result}
    if response:
        return response
    else:
        raise ValueError("Exception raised when a Score cannot be calculated")
