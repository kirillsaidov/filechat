# module fileuploader

# system
import os, io

# loaders
import docx
from PyPDF2 import PdfReader
from odf import text as odfText
from odf.opendocument import load as odtload
from streamlit.runtime.uploaded_file_manager import UploadedFile
from langchain.schema import Document


def fu_make_upload(file: UploadedFile | str) -> tuple[io.BytesIO, str, str]:
    """Converts file to tuple pair of file data and type, and loads the file to memory

    Args:
        file (UploadedFile | str): uploaded file from uploader or filepath

    Returns:
        tuple[io.BytesIO, str, str]: file data, file type, file name
    """
    if isinstance(file, UploadedFile):
        return (io.BytesIO(file.read()), file.type, file.name)
    else:
        with open(file, 'rb') as f:
            data = f.read()
            type = file.split('.')[-1]
        return (io.BytesIO(data), fu_get_encoded_type(type), os.path.basename(file))


def fu_get_encoded_type(ext: str) -> str:
    """Returns official document type name based off its extension

    Args:
        ext (str): file extension

    Raises:
        Exception: unsupported document type

    Returns:
        str: document type
    
    Note:
        supported document types: ['pdf', 'odt', 'docx', 'txt']
    """
    if ext == 'pdf': return 'application/pdf'
    elif ext == 'odt': return 'application/vnd.oasis.opendocument.text'
    elif ext == 'docx': return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif ext == 'txt': return 'text/plain'
    else: raise Exception('Unsupported document type!')


def fu_get_content(file: io.BytesIO, type: str, source: str = '') -> list[Document]:
    """Reads file contents based in its text

    Args:
        file (io.BytesIO): uploaded file object
        type (str): document type
        source (str, optional): filename. Defaults to ''.

    Returns:
        list[Document]: list of documents(page_content, metadata={'source', 'page'})
    """
    if type == 'application/pdf': return fu_get_content_pdf(file, source)
    elif type == 'application/vnd.oasis.opendocument.text': return fu_get_content_odt(file, source)
    elif type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': return fu_get_content_docx(file, source)
    elif type == 'text/plain': return fu_get_content_txt(file, source)
    else: raise Exception('Unsupported document type!')


def fu_get_content_txt(file: io.BytesIO, source: str = '') -> list[Document]:
    """Reads TXT file contents

    Args:
        file (io.BytesIO): uploaded file object
        source (str, optional): filename. Defaults to ''.

    Returns:
        list[Document]: list of documents(page_content, metadata={'source', 'page'})
    """
    documents = [Document(
        page_content=file.read().decode(errors='replace'),
        metadata={
            'source': source,
            'page': 0,
        }
    )]
    return documents


def fu_get_content_pdf(file: io.BytesIO, source: str = '') -> list[Document]:
    """Reads PDF file contents

    Args:
        file (io.BytesIO): uploaded file object
        source (str, optional): filename. Defaults to ''.

    Returns:
        list[Document]: list of documents(page_content, metadata={'source', 'page'})
    """
    documents = []
    loader = PdfReader(file)
    for i, chunk in enumerate(loader.pages):
        documents.append(Document(
            page_content=chunk.extract_text(),
            metadata={
                'source': source,
                'page': i,
            }
        ))
    return documents


def fu_get_content_odt(file: io.BytesIO, source: str = '') -> list[Document]:
    """Reads ODT file contents

    Args:
        file (io.BytesIO): uploaded file object
        source (str, optional): filename. Defaults to ''.

    Returns:
        list[Document]: list of documents(page_content, metadata={'source', 'page'})
    """    
    documents = []
    loader = odtload(file)
    for i, chunk in enumerate(loader.getElementsByType(odfText.P)):
        documents.append(Document(
            page_content=chunk.firstChild.data,
            metadata={
                'source': source,
                'page': i,
            }
        ))
    return documents


def fu_get_content_docx(file: io.BytesIO, source: str = '') -> list[Document]:
    """Reads DOCX file contents

    Args:
        file (io.BytesIO): uploaded file object
        source (str, optional): filename. Defaults to ''.

    Returns:
        list[Document]: list of documents(page_content, metadata={'source', 'page'})
    """
    documents = []
    loader = docx.Document(file)
    for i, chunk in enumerate(loader.paragraphs): 
        documents.append(Document(
            page_content=chunk.text,
            metadata={
                'source': source,
                'page': i,
            }
        ))
    return documents


