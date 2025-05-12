import streamlit as st
import re
import docx2txt
import pandas as pd
import io
from PyPDF2 import PdfReader

st.set_page_config(page_title="Numbered Passage Counter", layout="centered")
st.title("📘 Numbered Passage Counter")

st.markdown("""
Upload a `.txt`, `.docx`, `.pdf`, `.xls/.xlsx`, or `.csv` file below.  
This app will extract the text and count how many **numbered passages** are present (like `1.`, `2,`, etc.).
""")

# Supported file upload
uploaded_file = st.file_uploader("Upload your file", type=["txt", "docx", "pdf", "csv", "xls", "xlsx"])

def extract_text(file, filetype):
    text = ""
    if filetype == "txt":
        text = file.read().decode("utf-8", errors="ignore")

    elif filetype == "docx":
        text = docx2txt.process(file)

    elif filetype == "pdf":
        reader = PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

    elif filetype in ["csv", "xls", "xlsx"]:
        try:
            if filetype == "csv":
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            text = "\n".join(df.astype(str).apply(lambda row: " ".join(row), axis=1))
        except Exception as e:
            st.error(f"Error reading {filetype} file: {e}")
    
    return text

# Function to count numbered passages
def count_numbered_passages(text):
    pattern = r"(?m)^\s*\d+[.,]"  # Start of line, digits, then . or ,
    return len(re.findall(pattern, text))

if uploaded_file:
    filetype = uploaded_file.name.split(".")[-1].lower()
    with st.spinner("Extracting text..."):
        text = extract_text(uploaded_file, filetype)

    if text:
        count = count_numbered_passages(text)
        st.success(f"✅ Found **{count}** numbered passage(s) in the file!")
        with st.expander("📄 View Extracted Text"):
            st.text_area("Text Preview", text, height=300)
    else:
        st.warning("No text found or unsupported format.")
else:
    st.info("Please upload a file to get started.")
