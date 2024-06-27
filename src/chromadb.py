# module chromadb

# system
import os
import shutil

# db
from langchain.schema import Document
# from langchain_mongodb.vector

# local
from log import log_print
from llm import llm_get_embedding_function
from fileuploader import fu_calculate_document_ids


def chromadb_add_documents(documents: list[Document], path: str = 'chroma', model: str = 'llama3', base_url: str = 'http://localhost:11434', verbose: bool = True) -> int:
    """Adds documents to database

    Args:
        documents (list[Document]): documents
        path (str, optional): database path with name. Defaults to 'chroma'.
        model (str, optional): ollama model name. Defaults to 'llama3'.
        base_url (_type_, optional): ollama ulr:port. Defaults to 'http://localhost:11434'.
        verbose (bool, optional): verbose output. Defaults to True.
        
    Returns:
        int: number of documents added
    """
    # create or load an existing database
    db = Chroma(persist_directory=path, embedding_function=llm_get_embedding_function(model, base_url))
    
    # calculate document ids
    documents_with_ids = fu_calculate_document_ids(documents)

    # add or update the documents
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    if verbose: log_print(f"Number of existing documents in DB: {len(existing_ids)}")

    # count new documents that don't exist in the DB to add later
    new_documents = []
    for chunk in documents_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_documents.append(chunk)

    # add new documents
    if len(new_documents):
        if verbose: log_print(f"👉 Adding new documents: {len(new_documents)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_documents]
        db.add_documents(new_documents, ids=new_chunk_ids)
        db.persist()
    else:
        if verbose: log_print("✅ No new documents to add")
    
    return len(new_documents)


def chromadb_clear_database(path: str = 'chroma'):
    """Delete database

    Args:
        path (str, optional): database path with name. Defaults to 'chroma'.
    """
    if os.path.exists(path):
        shutil.rmtree(path)

