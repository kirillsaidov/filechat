# module storage

# system
import os
import shutil

# db
import pymongo

# langchain
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings

# local
from log import log_print
from llm import llm_get_embedding_function
from fileuploader import fu_calculate_document_ids


def storage_documents_to_dict(documents: list[Document]) -> list[dict]:
    """Convert documents to dictionary

    Args:
        documents (list[Document]): documents

    Returns:
        list[dict]: list of dicts
    """
    return [ {'page_content': d.page_content, 'metadata': d.metadata} for d in documents ]


def storage_dict_to_documents(dicts: list[dict]) -> list[Document]:
    """Convert dict encoded documents to Documents object

    Args:
        dicts (list[dict]): dict of previously encoded documents

    Returns:
        list[Document]: list of Document object
    """
    return [ Document(page_content=d['page_content'], metadata=d['metadata']) for d in dicts ]


def storage_add_documents(
    documents: list[Document], 
    mongo_connect: str = 'mongodb://localhost:27017/', 
    mongo_dbname: str = 'filechat',
    mongo_colname: str = 'documents', 
    verbose: bool = True,
) -> int:
    """Adds documents to database

    Args:
        documents (list[Document]): documents
        mongo_connect (str, optional): connection url. Defaults to 'mongodb://localhost:27017/'.
        mongo_dbname (str, optional): database name. Defaults to 'filechat'.
        mongo_colname (str, optional): collection name. Defaults to 'documents'.
        verbose (bool, optional): verbose output. Defaults to True.
        
    Returns:
        int: number of documents added
    """    
    # init storage
    db = pymongo.MongoClient(mongo_connect)
    dbcol = db[mongo_dbname][mongo_colname]
    
    # calculate document ids
    documents_with_ids = fu_calculate_document_ids(documents)

    # add or update the documents
    existing_items = storage_dict_to_documents(dbcol.find({}, {'_id':0}))
    existing_ids = set([item.metadata['id'] for item in existing_items])
    if verbose: log_print(f'Number of existing documents in DB: {len(existing_ids)}')

    # count new documents that don't exist in the DB to add later
    new_documents = []
    for chunk in documents_with_ids:
        if chunk.metadata['id'] not in existing_ids:
            new_documents.append(chunk)

    # add new documents
    if len(new_documents):
        if verbose: log_print(f'👉 Adding new documents: {len(new_documents)}')
        dbcol.insert_many(storage_documents_to_dict(new_documents))
    else:
        if verbose: log_print('✅ No new documents to add')
    
    return len(new_documents)


def storage_clear_database(mongo_connect: str = 'mongodb://localhost:27017/', mongo_dbname: str = 'filechat'):
    """Delete database

    Args:
        mongo_connect (str, optional): connection url. Defaults to 'mongodb://localhost:27017/'.
        mongo_dbname (str, optional): database name. Defaults to 'filechat'.
    """
    db = pymongo.MongoClient(mongo_connect)
    db.drop_database(mongo_dbname)


def storage_get_all_documents(mongo_connect: str = 'mongodb://localhost:27017/', mongo_dbname: str = 'filechat', mongo_colname: str = 'documents') -> list[Document]:
    # init storage
    db = pymongo.MongoClient(mongo_connect)
    dbcol = db[mongo_dbname][mongo_colname]
    
    # retreive documents
    dicts = dbcol.find({}, {'_id':0})
    documents = storage_dict_to_documents(dicts)
    
    return documents


def storage_load_vectorstore(documents: list[Document], embedding: OllamaEmbeddings) -> FAISS:
    return FAISS.from_documents(documents, embedding)


