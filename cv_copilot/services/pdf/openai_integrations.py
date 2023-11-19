import httpx

from cv_copilot.settings import settings


async def get_text_from_image(image: str) -> httpx.Response:
    """Get text from an image using OpenAI's API.

    :param image: The image file encoded in base64.
    :return: The full response from the API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.openai_api_key}",
    }

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

    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.openai_url_chat,
            headers=headers,
            json=payload,
        )
    return response
