# module llm

# langchain
from langchain_community.embeddings import OllamaEmbeddings


def llm_get_embedding_function(model: str = 'llama3', base_url: str = 'http://localhost:11434'):
    return OllamaEmbeddings(model=model, base_url=base_url)



