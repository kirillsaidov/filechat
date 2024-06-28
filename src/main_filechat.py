# module main_filechat

# system
import os
import sys
import time
import argparse

# webui
import streamlit as st

# langchain
from langchain.prompts import ChatPromptTemplate
from langchain.chains.question_answering import load_qa_chain

# ollama
from ollama import Client as OllamaClient

# local
from llm import *
from widgets import *
from storage import *
from fileuploader import *


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}

If no context or context is insufficient, give the following answer: Insufficient context.

ONLY DIRECT ANSWERS. DO NOT ADD ANY COMMENTS OR EXPLANATIONS. NO NARRATOR OR AI ASSISTANT, DO NOT ADD ANY REFERENCE BOOK OR ACCOMPANYING INFORMATION. NO DISCLAIMERS, WARNINGS, OR RECOMMENDATIONS FOR USE.DO NOT ADD
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--mongo_connect', help='mongo connect url', default='mongodb://localhost:27017/', type=str)
    parser.add_argument('--mongo_dbname', help='mongo database name', default='filechat', type=str)
    parser.add_argument('--mongo_colname', help='mongo collection name', default='documents', type=str)
    parser.add_argument('--ollama_model', help='ollama model name', default='llama3', type=str)
    parser.add_argument('--ollama_base_url', help='ollama url:port', default='http://localhost:11434', type=str)
    parser.add_argument('--verbose', help='verbose output', action='store_true')
    args = parser.parse_args()
    
    # setup
    mongo_connect = args.mongo_connect
    mongo_dbname = args.mongo_dbname
    mongo_colname = args.mongo_colname
    ollama_model = args.ollama_model
    ollama_base_url = args.ollama_base_url
    verbose = args.verbose
    supported_doctypes = ['pdf', 'docx', 'odt', 'txt']
        
    # init vectorstore
    def vectorstore_load() -> FAISS | None:
        documents = storage_get_all_documents(mongo_connect, mongo_dbname, mongo_colname)
        return storage_load_vectorstore(
            documents=documents,
            embedding=llm_get_embedding_function(ollama_model, ollama_base_url),
        ) if documents else None
    if 'vectorStore' not in st.session_state:
        st.session_state.vectorStore = vectorstore_load()
    
    # init ollama
    if 'ollama_model' not in st.session_state:
        st.session_state.ollama_model = OllamaClient(ollama_base_url)

    # init messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # ---
    # SIDEBAR
    
    with st.sidebar:
        st.title('🤗💬 LLM File Chat')
        st.markdown('''
        # About
        This app is an LLM-powered chatbot. Configure as you see fit.
        
        # Configuration
        ''')
        
        # flags
        flag_load_from_folder = st.toggle('Load from folder', help='Drag & drop files or load from folder.')
        flag_private_chat = st.toggle('Private chat', help='Do not save files to database for repeated usage.')
        flag_ask_llm = st.toggle('Ask LLM', help='Ask LLM not the knowledge base.')
        
        # cache
        st.markdown('''
        # Cache
        ''')
        if st.button('Delete database', use_container_width=True, on_click=storage_clear_database, args=(mongo_connect, mongo_dbname)):
            widget_info_notification('Database deleted!')
        if st.button('Delete messages', use_container_width=True, on_click=lambda: st.session_state.messages.clear()):
            widget_info_notification('Messages deleted!')
        
    # ---
    # MAIN WINDOW
    
    st.header("Chat with files 💬")
    
    # file uploader widget
    files = None
    if flag_load_from_folder:
        dirpath = st.text_input('Enter path:')
        if os.path.isdir(dirpath):
            # find and filter files in the directory
            fnames = list(filter(lambda x: x.split('.')[-1] in supported_doctypes, os.listdir(dirpath)))
            
            if len(fnames):
                # list files to be uploaded
                with st.expander(f'To be processed: {len(fnames)} files'):
                    for i, fname in enumerate(fnames):
                        st.write(f'{i+1}. {fname}')
                
                # upload files
                files = [os.path.join(dirpath, fname) for fname in fnames]
    else:
        files = st.file_uploader('Upload your files', type=supported_doctypes, accept_multiple_files=True)
    
    # upload files
    documents = []
    submitIsPressed = st.button('Submit', use_container_width=True)
    if submitIsPressed and files:
        # upload and convert to documents
        for file in files: documents += fu_get_content(*fu_make_upload(file))
    
        # process documents
        documents = fu_split_documents(documents, chunk_size=1000, chunk_overlap=200)
        docs_added = storage_add_documents(
            documents=documents,
            mongo_connect=mongo_connect,
            mongo_dbname=mongo_dbname,
            mongo_colname=mongo_colname,
            verbose=verbose,
        )
        
        # display number of documents added
        if docs_added:
            widget_info_notification(f'{docs_added} chunks added!')
            
            # update vectorstore
            st.session_state.vectorStore = vectorstore_load()
        else: widget_info_notification(f'All up to date!')
    
    # ---
    # CHAT
     
    # display history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # chat
    if query_text := st.chat_input("What's your question?"):
        # user
        st.session_state.messages.append({'role': 'user', 'content': query_text})
        with st.chat_message('user'): 
            st.markdown(query_text)

        # llm
        with st.chat_message('assistant'):
            # generate response
            prompt = ''
            if flag_ask_llm: 
                prompt = query_text
            else:
                results = None
                if st.session_state.vectorStore:
                    # find relevant documents
                    results = st.session_state.vectorStore.similarity_search_with_score(query=query_text, k=5)
                    
                # generate context
                context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results]) if results else ''

                # create prompt query
                prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
                prompt = prompt_template.format(context=context_text, question=query_text)
                
            # invoke llm
            response = llm_model_chat(prompt, st.session_state.ollama_model)
            st.markdown(prompt)
        st.session_state.messages.append({'role': 'assistant', 'content': response})


