# module main_filechat

# system
import os
import sys
import time
import argparse

# webui
import streamlit as st

# local
from storage import *
from fileuploader import *

        
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
        flag_ask_llm = st.toggle('Ask LLM', help='Ask LLM when unable to find the answer in the uploaded files.')
        
        # cache
        st.markdown('''
        # Cache
        ''')
        if st.button('Clear database', use_container_width=True, on_click=storage_clear_database, args=(mongo_connect, mongo_dbname)):
            widget = st.success('Database cleared!', icon='✅')
            time.sleep(2)
            widget.empty()
        
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
                with st.expander('To be processed:'):
                    for i, fname in enumerate(fnames):
                        st.write(f'{i}. {fname}')
                
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
        documents = fu_split_documents(documents)
        docs_added = storage_add_documents(
            documents=documents,
            mongo_connect=mongo_connect,
            mongo_dbname=mongo_dbname,
            mongo_colname=mongo_colname,
            verbose=verbose,
        )
        
        # display number of documents added
        widget = st.success(f'{docs_added} chunks added/updated!', icon='✅')
        time.sleep(2)
        widget.empty()
    
        from pprint import pprint
        for doc in documents: pprint(doc)


