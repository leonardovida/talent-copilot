from cv_copilot.db.models.job_descriptions import ParsedJobDescriptionModel
from cv_copilot.db.models.texts import TextModel
from cv_copilot.services.llm.models.skills import EvaluationExtract, SkillsExtract
from cv_copilot.services.llm.prompt_templates.cv import system_prompt_cv, user_prompt_cv
from cv_copilot.services.llm.prompt_templates.job_descriptions import (
    system_prompt_job_description,
    user_prompt_job_description,
)
from cv_copilot.services.llm.utils import oa_async_request
from cv_copilot.web.dto.job_description.schema import JobDescriptionModel


async def parse_skills_job_description(
    job_description: JobDescriptionModel,
) -> SkillsExtract:
    """Parse the skills from the job description.

    This function calls in an async way to OpenAI (so that in theory we could
    make more calls at the same time, if the frontend would support it). And
    parses the answer using the 'instructor' library. This library is used to
    automatically transform the output of the LLM into a Pydantic object
    following a 'model'.

    :param job_description: The complete JobDescription model used to extract the description.
    :return: The parsed skills.
    """

    formatted_user_prompt = user_prompt_job_description.format(
        job_description=job_description.description,
    )

    return await oa_async_request(
        system_prompt=system_prompt_job_description,
        user_prompt=formatted_user_prompt,
        response_model=SkillsExtract,
    )


async def evaluate_cv(
    parsed_job_description: ParsedJobDescriptionModel,
    parsed_text: TextModel,
) -> SkillsExtract:
    """
    Evaluate the CV.

    :param pdf_id: The ID of the PDF to evaluate.
    """
    formatted_user_prompt = user_prompt_cv.format(
        parsed_skills=parsed_job_description.parsed_skills,
        parsed_cv=parsed_text.text,
    )

    return await oa_async_request(
        system_prompt=system_prompt_cv,
        user_prompt=formatted_user_prompt,
        response_model=EvaluationExtract,
    )
