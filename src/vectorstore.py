# module vectorstore

# system
import os
import pickle

# langchain
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

# local
from llm import *
from storage import *

# constants
VECTORSTORE_DB = 'vectorstore.pkl'


def vectorstore_load(
    mongo_connect: str = 'mongodb://localhost:27017/', 
    mongo_dbname: str = 'filechat', 
    mongo_colname: str = 'documents',
    ollama_model: str = 'llama3', 
    ollama_base_url: str = 'http://localhost:11434',
) -> FAISS | None:
    """Load FAISS vectorstore object

    Args:
        mongo_connect (str, optional): mongo connection url. Defaults to 'mongodb://localhost:27017/'.
        mongo_dbname (str, optional): mongo database name. Defaults to 'filechat'.
        mongo_colname (str, optional): mongo collection name. Defaults to 'documents'.
        ollama_model (str, optional): ollama model. Defaults to 'llama3'.
        ollama_base_url (_type_, optional): ollama base url. Defaults to 'http://localhost:11434'.

    Returns:
        FAISS | None: FAISS object if found or documents in DB else None
    """
    # load vectorstore from pickle
    if os.path.exists(VECTORSTORE_DB):
        with open(VECTORSTORE_DB, 'rb') as f: 
            vectorStore = pickle.load(f)
        return vectorStore
    
    # create new vectorstore from all documents in db
    documents = storage_get_all_documents(mongo_connect, mongo_dbname, mongo_colname)
    vectorStore = storage_load_vectorstore(
        documents=documents,
        embedding=llm_get_embedding_function(ollama_model, ollama_base_url),
    ) if documents else None
    
    # save vectorstore to pickle
    if vectorStore:
        with open(VECTORSTORE_DB, 'wb') as f:
            pickle.dump(vectorStore, f)
        
    return vectorStore


def vectorstore_update(
    vectorStore: FAISS, 
    documents: dict[Document], 
    ollama_model: str = 'llama3', 
    ollama_base_url: str = 'http://localhost:11434'
) -> FAISS:
    """Updates vectorStore from documents (if none creates anew)

    Args:
        vectorStore (FAISS): FAISS object if update else None to create a new
        documents (dict[Document]): list of documents
        ollama_model (str, optional): ollama model. Defaults to 'llama3'.
        ollama_base_url (str, optional): ollama base url. Defaults to 'http://localhost:11434'.

    Returns:
        FAISS: valid vectorstore object
    """
    # add documents
    if vectorStore: vectorStore.add_documents(documents)
    else: vectorStore = FAISS.from_documents(documents, embedding=llm_get_embedding_function(ollama_model, ollama_base_url))
    
    # save vectorstore to pickle
    with open(VECTORSTORE_DB, 'wb') as f:
        pickle.dump(vectorStore, f)
        
    return vectorStore


