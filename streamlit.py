import streamlit as st
import pdfplumber
import pandas as pd
import re
import os
import shutil
import zipfile
from io import BytesIO

# --- Helper extraction functions ---

def extract_payment_method(text):
    lines = text.splitlines()
    for line in lines:
        if re.search(r'(Cara\s*Bayaran|Payment\s*Method)', line, re.IGNORECASE):
            parts = re.split(r'(?:Cara\s*Bayaran|Payment\s*Method)', line, flags=re.IGNORECASE)
            value = parts[-1].strip()
            return value if value else None
    return None

def extract_adjudication_no(text):
    match = re.search(r'Adjudication\s*No\.?\s*([A-Z0-9]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip().replace("\n", " ")
    return None

def extract_instrument_type(text):
    lines = text.splitlines()
    malay_value = ""
    eng_value = ""

    for i, line in enumerate(lines):
        if re.search(r'Jenis\s+Surat\s+Cara', line, re.IGNORECASE):
            malay_value = re.sub(r'.*Jenis\s+Surat\s+Cara\s*', '', line, flags=re.IGNORECASE).strip()
        elif re.search(r'Type\s+Of\s+Instrument', line, re.IGNORECASE):
            eng_value = re.sub(r'.*Type\s+Of\s+Instrument\s*', '', line, flags=re.IGNORECASE).strip()

    if malay_value and eng_value:
        return f"{malay_value} {eng_value}".strip()
    return malay_value or eng_value or None

def extract_date_of_instrument(text):
    match = re.search(r'Tarikh\s+Surat\s+Cara\s*([0-9/]+)', text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_consideration(text):
    match = re.search(r'Balasan\s*Consideration\s*RM\s*([\d.,]+)', text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_first_party(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(r'Maklumat\s+Pihak\s+Pertama', line, re.IGNORECASE):
            if i + 1 < len(lines):
                return lines[i + 1].strip()
    return None

def extract_second_party(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(r'Maklumat\s+Pihak\s+Kedua', line, re.IGNORECASE):
            if i + 1 < len(lines):
                return lines[i + 1].strip()
    return None

# --- Streamlit setup ---
st.set_page_config(page_title="Stamp Certificate PDF Extractor", page_icon="📄", layout="wide")
st.title("📄 Stamp Certificate PDF Extractor")

st.markdown("""
Upload a **ZIP file** containing your PDFs.  
The app will extract key fields: `FILENAME`, `CARA_BAYARAN`, `NO_ADJUDIKASI`, `JENIS_SURAT_CARA`,  `TARIKH_SURAT_CARA`, `BALASAN_RM`, `PIHAK_PERTAMA`, `PIHAK_KEDUA`  
You may **download the results as Excel**.
""")

uploaded_zip = st.file_uploader("📂 Upload ZIP file containing PDFs", type=["zip"])

# --- Fixed extraction folder ---
BASE_DIR = os.getcwd()
EXTRACT_DIR = os.path.join(BASE_DIR, "temp_extracted")

# Always start clean
if os.path.exists(EXTRACT_DIR):
    shutil.rmtree(EXTRACT_DIR)
os.makedirs(EXTRACT_DIR, exist_ok=True)

# --- Cached processing function ---
@st.cache_data(show_spinner=False)
def process_uploaded_zip(zip_bytes):
    """Extract ZIP, process all PDFs, and return DataFrame."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        pdf_files = []
        for root, _, files in os.walk(tmpdir):
            for file in files:
                if file.lower().endswith(".pdf"):
                    pdf_files.append(os.path.join(root, file))

        records = []
        for i, pdf_path in enumerate(pdf_files):
            filename = os.path.basename(pdf_path)
            with pdfplumber.open(pdf_path) as pdf:
                all_text = [p.extract_text() for p in pdf.pages if p.extract_text()]
            full_text = "\n".join(all_text)

            data = {
                "FILENAME": filename,
                "CARA_BAYARAN": extract_payment_method(full_text),
                "NO_ADJUDIKASI": extract_adjudication_no(full_text),
                "JENIS_SURAT_CARA": extract_instrument_type(full_text),
                "TARIKH_SURAT_CARA": extract_date_of_instrument(full_text),
                "BALASAN_RM": extract_consideration(full_text),
                "PIHAK_PERTAMA": extract_first_party(full_text),
                "PIHAK_KEDUA": extract_second_party(full_text),
            }
            records.append(data)

        return pd.DataFrame(records)

# --- Run extraction ---
if uploaded_zip:
    st.info("⏳ Processing ZIP... Please wait while PDFs are extracted.")
    df = process_uploaded_zip(uploaded_zip.read())

    st.success(f"✅ Extraction completed for {len(df)} PDFs!")
    st.dataframe(df.head())

   # --- Excel download ---
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="📥 Download Extracted Excel",
        data=buffer,
        file_name="stamp_extracted_all.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- Auto-clean extracted folder after processing ---
    shutil.rmtree(EXTRACT_DIR)
    os.makedirs(EXTRACT_DIR, exist_ok=True)