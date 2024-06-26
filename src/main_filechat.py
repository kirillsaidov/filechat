# module main_filechat

# system
import os, io

# webui
import streamlit as st

# local
from fileuploader import *

        
if __name__ == '__main__':
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
            uploaded_file = fu_make_upload(file)
            content = fu_get_content(*uploaded_file[:2])
            print(uploaded_file)
            print(content)



