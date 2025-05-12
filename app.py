import streamlit as st
from PIL import Image
import pytesseract
from docx import Document
import pandas as pd
import PyPDF2

# Detect if text looks English (basic heuristic)
import re
def is_probably_english(text):
    letters = re.findall(r'[a-zA-Z]', text)
    return len(letters) >= 0.5 * max(1, len(text))  # At least 50% English letters

# OCR for image
def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image, lang="eng")

# DOCX parser
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# PDF parser
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# TXT parser
def extract_text_from_txt(file):
    return file.read().decode("utf-8")

# CSV parser
def extract_text_from_csv(file):
    df = pd.read_csv(file)
    return df.to_string(index=False)

# Excel parser
def extract_text_from_excel(file):
    df = pd.read_excel(file)
    return df.to_string(index=False)

# App UI
st.title("📄 Multi-file English Text Parser with Warning Filter")

st.sidebar.header("🚫 Words/Phrases to Avoid")
default_avoid = "password, confidential, secret"
user_avoid = st.sidebar.text_area("Comma-separated:", default_avoid)
avoid_list = [w.strip().lower() for w in user_avoid.split(",") if w.strip()]

uploaded_file = st.file_uploader("📤 Upload a file", type=["png", "jpg", "jpeg", "docx", "pdf", "txt", "csv", "xls", "xlsx"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()

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
            st.error("❌ Unsupported file type.")
            st.stop()

        if not is_probably_english(extracted):
            st.warning("⚠️ Only English text can be parsed.")
        else:
            st.subheader("📝 Extracted Text")
            st.text_area("Parsed Content:", extracted, height=300)

            # Match check
            matched = [w for w in avoid_list if w in extracted.lower()]
            if matched:
                st.error(f"⚠️ Avoid these strings found: {', '.join(matched)}")
            else:
                st.success("✅ No matched strings detected.")

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
