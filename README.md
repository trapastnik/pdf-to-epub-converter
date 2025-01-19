
# PDF to EPUB Converter

## Description

This application converts PDF documents into well-structured EPUB files, preserving the original document's organization (chapters, headings, etc.) as much as possible.

## Setup Instructions

1. **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd pdf-to-epub-converter
    ```
2. **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    ```
3. **Activate the virtual environment:**
    *   **Linux/macOS:** `source pdf-to-epub-converter/venv/bin/activate`
    *   **Windows:** `source pdf-to-epub-converter/venv/bin/activate`
4. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5. **Run the application:**
    ```bash
    python main.py
    ```

## Main Features

*   PDF Upload
*   Structure Analysis (automatic and user-assisted)
*   EPUB Conversion
*   Progress Display
*   EPUB Download

## Technology Stack

*   Python
*   Gradio
*   PyMuPDF (or similar PDF parsing library - to be determined)
*   ebooklib (or similar EPUB generation library)
*   JSON/SQLite (for data storage)

## Future Enhancements

*   OCR integration for scanned PDFs
*   Cloud storage integration
*   Batch conversion
*   User accounts
*   More customization options
*   API
*   Support for other document formats
