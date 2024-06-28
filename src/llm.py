# module llm

# langchain
from langchain_community.embeddings import OllamaEmbeddings

# ollama
from ollama import Client as OllamaClient, Options as OllamaOptions


def llm_get_embedding_function(model: str = 'llama3', base_url: str = 'http://localhost:11434') -> OllamaEmbeddings:
    """Get ollama embedding function

    Args:
        model (str, optional): model name. Defaults to 'llama3'.
        base_url (_type_, optional): connection url. Defaults to 'http://localhost:11434'.

    Returns:
        OllamaEmbeddings: embedding
    """
    return OllamaEmbeddings(model=model, base_url=base_url)


def llm_model_chat(prompt: str, ollama_client: OllamaClient, system_task: str = 'You are an intelligent AI assistant.', model='llama3') -> str:
    """Chat with Ollama

    Args:
        prompt (str): prompt
        ollama_client (OllamaClient): ollama client
        system_task (str, optional): system task. Defaults to 'You are an intelligent AI assistant.'.
        model (str, optional): model name. Defaults to 'llama3'.

    Returns:
        str: response
    """
    response = ollama_client.chat(model=model, messages=[
        {
            'role': 'system',
            'content': system_task,
        },
        {
            'role': 'user',
            'content': prompt
        },
    ], options=OllamaOptions(temperature=0))
    return response['message']['content']
