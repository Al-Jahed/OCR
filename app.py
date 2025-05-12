import streamlit as st
from PIL import Image
import pytesseract
from docx import Document
import pandas as pd
import PyPDF2
import re

# ------------------ Helper Functions ------------------

def is_probably_english(text):
    letters = re.findall(r'[a-zA-Z]', text)
    return len(letters) >= 0.5 * max(1, len(text))

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image, lang="eng")

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_txt(file):
    return file.read().decode("utf-8", errors="ignore")

def extract_text_from_csv(file):
    df = pd.read_csv(file)
    return df.to_string(index=False)

def extract_text_from_excel(file):
    df = pd.read_excel(file)
    return df.to_string(index=False)

# ------------------ Streamlit App ------------------

st.set_page_config(page_title="Text Parser", layout="wide")
st.title("📄 Universal English Text Parser")

st.sidebar.header("🚫 Words/Phrases to Avoid")
avoid_input = st.sidebar.text_area("Comma-separated list of forbidden words/phrases:", "password, confidential, secret")
avoid_list = [w.strip().lower() for w in avoid_input.split(",") if w.strip()]

uploaded_file = st.file_uploader(
    "📤 Upload an image, document, or spreadsheet:",
    type=["png", "jpg", "jpeg", "docx", "pdf", "txt", "csv", "xls", "xlsx"]
)

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type not in ["png", "jpg", "jpeg", "docx", "pdf", "txt", "csv", "xls", "xlsx"]:
        st.error("❌ Unsupported file type. Please upload a valid image, document, or spreadsheet file.")
        st.stop()

    try:
        if file_type in ["png", "jpg", "jpeg"]:
            extracted = extract_text_from_image(uploaded_file)
        elif file_type == "docx":
            extracted = extract_text_from_docx(uploaded_file)
        elif file_type == "pdf":
            extracted = extract_text_from_pdf(uploaded_file)
        elif file_type == "txt":
            extracted = extract_text_from_txt(uploaded_file)
        elif file_type == "csv":
            extracted = extract_text_from_csv(uploaded_file)
        elif file_type in ["xls", "xlsx"]:
            extracted = extract_text_from_excel(uploaded_file)
        else:
            extracted = ""

        if not extracted.strip():
            st.warning("⚠️ No readable text found in the file.")
        elif not is_probably_english(extracted):
            st.warning("⚠️ Only English text can be parsed.")
        else:
            st.subheader("📝 Extracted Text")
            st.text_area("Parsed Content:", extracted, height=300)

            matched = [word for word in avoid_list if word in extracted.lower()]
            if matched:
                st.error(f"⚠️ Forbidden strings found: {', '.join(matched)}")
            else:
                st.success("✅ No forbidden content detected.")

    except Exception as e:
        st.error(f"❌ Error while processing file: {str(e)}")
