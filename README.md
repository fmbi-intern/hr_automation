# 📄 Stamp Certificate PDF Extractor

A **Streamlit web application** that extracts key information from multiple **stamp certificate PDFs** contained within a **ZIP file**.  
It automatically processes all uploaded documents and provides an Excel output with structured results.

---

## 🚀 Features

- 📦 **Batch processing** — Upload a ZIP file containing multiple PDF files.
- 🔍 **Automatic data extraction** for key fields:

  | Field | Description |
  |--------|-------------|
  | `FILENAME` | Name of the PDF file |
  | `CARA_BAYARAN` | Payment Method |
  | `NO_ADJUDIKASI` | Adjudication Number |
  | `JENIS_SURAT_CARA` | Instrument Type |
  | `TARIKH_SURAT_CARA` | Date of Instrument |
  | `BALASAN_RM` | Consideration Amount (RM) |
  | `PIHAK_PERTAMA` | First Party |
  | `PIHAK_KEDUA` | Second Party |

- 📊 **Interactive data preview** within the app.
- 📥 **Download extracted results** as an Excel file.

---

## 🧰 Requirements

- Python **3.11** or higher  
- `streamlit`  
- `pandas`  
- `pdfplumber`  
- `openpyxl`

---

## ⚙️ Setup Instructions

### 1. Create and activate a virtual environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run streamlit.py
```
