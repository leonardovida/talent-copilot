import logging
from typing import Type

import httpx
import instructor
from openai import OpenAI

from cv_copilot.settings import settings


async def get_text_from_image(image: str) -> httpx.Response:
    """Get text from an image using OpenAI's API.

    :param image: The image file encoded in base64.
    :return: The full response from the API.
    """
    payload = {
        "model": settings.vision_model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": settings.vision_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                    },
                ],
            },
        ],
        "max_tokens": settings.max_tokens,
    }

    client = OpenAI(api_key=settings.openai_api_key)
    return client.chat.completions.create(**payload)


async def oa_async_request(
    system_prompt: str,
    user_prompt: str,
    response_model: Type,
) -> Type:
    """Send a request to OpenAI asynchronously.

    :param system_prompt: The system prompt to send to OpenAI.
    :param user_prompt: The user prompt to send to OpenAI.
    :param response_model: The response model to use.
    :param is_async: Whether to use the async client or not.
    :return: The parsed skills formatted following the pydantic class.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if settings.gpt4_model_name == "gpt-3.5-turbo-16k-0613":
        client = instructor.patch(OpenAI(api_key=settings.openai_api_key))
        logging.info(f"Sending Job description messages to OpenAI: {messages}")
        model = client.chat.completions.create(
            model=settings.gpt4_model_name,
            messages=messages,
            response_model=response_model,  # instructor injection
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
    else:
        client = instructor.patch(OpenAI(api_key=settings.openai_api_key))
        logging.info(f"Sending Job description messages to OpenAI: {messages}")
        model = client.chat.completions.create(
            model=settings.gpt4_model_name,
            messages=messages,
            response_model=response_model,  # instructor injection
            response_format=settings.response_format,
            seed=settings.seed,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )

    logging.info(f"Received response from OpenAI: {model}")
    if not model:
        raise ValueError("No content received from OpenAI response")
    return model
