# FileChat (WIP)
Chat with files using LLM. Supports the following document types:
* Microsoft World (DOCX)
* Open Document (ODT)
* Portable Document Format (PDF)
* Plain Text (TXT)

## Install
```sh
# clone repository
$ git clone https://github.com/kirillsaidov/filechat.git
$ cd filechat/

# install python dependencies
$ python3 -m venv venv && source ./venv/bin/activate
$ pip install -r requirements.txt
```

## Run
```sh
$ streamlit run src/main_filechat.py
```
Output:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://xxx.xxx.xxx.xxx:8501
```

Copy and paste any of the above URLs to your web browser. 

## LICENSE
All code is licensed under the MIT license.
