# module fileuploader

# system
import os, io

# loaders
import docx
from PyPDF2 import PdfReader
from odf import text as odfText
from odf.opendocument import load as odtload
from streamlit.runtime.uploaded_file_manager import UploadedFile


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


def fu_get_content(file: io.BytesIO, type: str) -> str:
    """Reads file contents based in its text

    Args:
        file (io.BytesIO): uploaded file object

    Returns:
        str: contents
    """
    if type == 'application/pdf': return fu_get_content_pdf(file)
    elif type == 'application/vnd.oasis.opendocument.text': return fu_get_content_odt(file)
    elif type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': return fu_get_content_docx(file)
    elif type == 'text/plain': return fu_get_content_txt(file)
    else: raise Exception('Unsupported document type!')


def fu_get_content_txt(file: io.BytesIO) -> str:
    """Reads TXT file contents

    Args:
        file (io.BytesIO): uploaded file object

    Returns:
        str: contents
    """
    return file.read().decode()


def fu_get_content_pdf(file: io.BytesIO) -> str:
    """Reads PDF file contents

    Args:
        file (io.BytesIO): uploaded file object

    Returns:
        str: contents
    """
    text = ''
    loader = PdfReader(file)
    for chunk in loader.pages: text += chunk.extract_text()
    return text


def fu_get_content_odt(file: io.BytesIO) -> str:
    """Reads ODT file contents

    Args:
        file (io.BytesIO): uploaded file object

    Returns:
        str: contents
    """    
    text = ''
    loader = odtload(file)
    for chunk in loader.getElementsByType(odfText.P): text += chunk.firstChild.data + '\n'
    return text


def fu_get_content_docx(file: io.BytesIO) -> str:
    """Reads DOCX file contents

    Args:
        file (io.BytesIO): uploaded file object

    Returns:
        str: contents
    """
    text = ''
    loader = docx.Document(file)
    for chunk in loader.paragraphs: text += chunk.text + '\n'
    return text


