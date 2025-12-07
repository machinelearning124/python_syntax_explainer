import streamlit as st
from code_editor import code_editor

st.title("Editor Test")

code = """def hello():
    print("Hello world")
"""

response = code_editor(code, lang="python", theme="dracula")
st.write("Output:", response)
