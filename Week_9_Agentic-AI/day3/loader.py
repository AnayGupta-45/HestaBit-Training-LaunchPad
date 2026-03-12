import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


def get_model_client():

    return OpenAIChatCompletionClient(
        model="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
        model_info={
            "family": "openai",
            "context_length": 8192,
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "structured_output": False,
        },
    )