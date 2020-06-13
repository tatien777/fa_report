import pandas as pd
import streamlit as st
# import plotly.express as px
import os

from enum import Enum
from io import BytesIO, StringIO
from typing import Union
import base64


STYLE = """
<style>
img {
    max-width: 100%;
}
</style>
"""

FILE_TYPES = ["csv", "py", "png", "jpg"]
class FileType(Enum):
    """Used to distinguish between file types"""

    IMAGE = "Image"
    CSV = "csv"
    PYTHON = "Python"


def get_file_type(file: Union[BytesIO, StringIO]) -> FileType:
    """The file uploader widget does not provide information on the type of file uploaded so we have
    to guess using rules or ML

    I've implemented rules for now :-)

    Arguments:
        file {Union[BytesIO, StringIO]} -- The file uploaded

    Returns:
        FileType -- A best guess of the file type
    """

    if isinstance(file, BytesIO):
        return FileType.IMAGE
    content = file.getvalue()
    if (
        content.startswith('"""')
        or "import" in content
        or "from " in content
        or "def " in content
        or "class " in content
        or "print" in content
    ):
        return FileType.PYTHON

    return FileType.CSV


def import_file(name):
    st.write("run file name: " + str(name))
    file = st.file_uploader("Upload file", type=FILE_TYPES,key=name)
    show_file = st.empty()
    if not file:
        show_file.info("Please upload a file of type: " + ", ".join(FILE_TYPES))
        return

    file_type = get_file_type(file)
    if file_type == FileType.IMAGE:
        show_file.image(file)
    elif file_type == FileType.PYTHON:
        st.code(file.getvalue())
    else:
        data = pd.read_csv(file)
        st.dataframe(data.head(5))
        st.markdown('*** số lượng dòng của file *** ')
        st.dataframe(data.count())
    file.close()
    return data
