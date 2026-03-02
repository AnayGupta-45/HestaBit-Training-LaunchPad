from autogen_ext.models.ollama import OllamaChatCompletionClient

def get_model_client():
    return OllamaChatCompletionClient(
        model="phi3",
        temperature=0.2, 
    )