import os
from Backend.services.gemini_service import call_gemini, call_gemini_with_file
from Backend.prompts.upload_prompts import (
    UPLOAD_SYSTEM_PROMPT,
    ANALYZE_DOCUMENT_PROMPT,
    SUMMARIZE_DOCUMENT_PROMPT,
    EXTRACT_DATA_PROMPT,
)

# Storage paths
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage")
PDF_DIR = os.path.join(STORAGE_DIR, "pdf")
TEMP_DIR = os.path.join(STORAGE_DIR, "temp")

# Ensure directories exist
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """Save uploaded file to storage and return path"""
    safe_filename = filename.replace(" ", "_")
    file_path = os.path.join(PDF_DIR, safe_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    except ImportError:
        return "[PyPDF2 not installed — using Gemini file upload instead]"
    except Exception as e:
        return f"[Error extracting text: {str(e)}]"


def analyze_document(file_path: str, task: str = "analyze") -> str:
    """Main function — routes to correct analysis based on task"""
    
    # Try text extraction first
    content = extract_text_from_pdf(file_path)
    
    if task == "summarize":
        if content.startswith("["):
            # Text extraction failed — use Gemini file upload
            prompt = "Summarize this document. Provide executive summary, key takeaways, and action items."
            return call_gemini_with_file(prompt, file_path)
        else:
            prompt = SUMMARIZE_DOCUMENT_PROMPT.format(
                system_prompt=UPLOAD_SYSTEM_PROMPT,
                content=content,
            )
            return call_gemini(prompt)
    
    elif task == "extract_data":
        if content.startswith("["):
            prompt = "Extract all structured data: dates, financial figures, parties, obligations, and metrics from this document."
            return call_gemini_with_file(prompt, file_path)
        else:
            prompt = EXTRACT_DATA_PROMPT.format(
                system_prompt=UPLOAD_SYSTEM_PROMPT,
                content=content,
            )
            return call_gemini(prompt)
    
    else:  # Full analysis
        if content.startswith("["):
            prompt = "Analyze this document thoroughly. Provide overview, key insights, data points, risks, and recommended actions."
            return call_gemini_with_file(prompt, file_path)
        else:
            prompt = ANALYZE_DOCUMENT_PROMPT.format(
                system_prompt=UPLOAD_SYSTEM_PROMPT,
                content=content,
            )
            return call_gemini(prompt)


def auto_route(file_path: str, query: str = "") -> str:
    """Auto-detect what the user wants based on their query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["summarize", "summary", "brief"]):
        return analyze_document(file_path, task="summarize")
    elif any(word in query_lower for word in ["extract", "data", "table", "figure"]):
        return analyze_document(file_path, task="extract_data")
    else:
        return analyze_document(file_path, task="analyze")


def run_upload_agent(file_content: bytes, filename: str, query: str = "", task: str = "auto") -> str:
    """Entry point called by API layer"""
    
    # Step 1: Save file
    file_path = save_uploaded_file(file_content, filename)
    
    # Step 2: Route to correct analysis
    if task == "auto":
        return auto_route(file_path, query)
    else:
        return analyze_document(file_path, task=task)