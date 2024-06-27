# module main_filechat

# system
import os, sys, argparse

# webui
import streamlit as st

# llm
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# local
from fileuploader import *

        
if __name__ == '__main__':
    # parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # parser.add_argument('--device', help='[ cpu, cuda, auto ]', default='cuda', type=str)
    # parser.add_argument('--model_type', help='[ small, base, medium, large, large-v2 ]', default='large-v2', type=str)
    # parser.add_argument('--temperature', help='temperature used for sampling [0, 0.2, 0.4, 0.6, 0.8, 1]', default=0, type=float)
    # parser.add_argument('--mongo_connect', help='mongo connect url', default='mongodb://dev.happydebt.kz:27017/', type=str)
    # parser.add_argument('--mongo_db', help='mongo database name', default='gepard', type=str)
    # parser.add_argument('--mongo_col', help='mongo collection name', default='stt_service', type=str)
    # parser.add_argument('--mongo_query_again_s', help='queary again after N seconds (if all requests are processed)', default=30, type=float)
    # parser.add_argument('--mongo_hardinfo_rps', help='update rate per second or update every 1/rps seconds', default=1, type=float)
    # parser.add_argument('--max_instances', help='maximum number of instances running simultaneously in parallel threads', default=1, type=int)
    # parser.add_argument('--tmp', help='folder for storing temporary files', default='tmp', type=str)
    # parser.add_argument('--delete_files', help='delete audio files from minio db and temporary folder after usage', default=False, type=bool)
    # parser.add_argument('--with_ailb', help='use AI Load Balancer to receive jobs', default=False, type=bool)
    # parser.add_argument('--verbose', help='verbose output', default=True, type=bool)
    # args = parser.parse_args()
    
    # setup
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
        st.button('Clear database', use_container_width=True, on_click=lambda: None)
        
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
    submitIsPressed = st.button('Submit', use_container_width=True)
    if submitIsPressed and files:
        for file in files:
            documents = fu_get_content(*fu_make_upload(file))
            print(documents)


