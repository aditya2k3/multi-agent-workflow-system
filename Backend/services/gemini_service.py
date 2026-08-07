import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from huggingface_hub import InferenceClient
from Backend.config.settings import HF_TOKEN

# DeepSeek-V4-Flash via Hugging Face Inference API
client = InferenceClient(
    provider="together", 
    api_key=HF_TOKEN,
)

MODEL = "deepseek-ai/DeepSeek-V4-Flash-0731"


def call_gemini(prompt: str) -> str:
    """
    Main function all agents call.
    Uses DeepSeek-V4-Flash instead of Gemini.
    Function name stays same so no other files need changes.
    """
    try:
        response = client.chat_completion(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.7,
        )
        return response.choices[0].message.content
    
    except Exception as e:
        # Fallback: try with HF inference provider
        try:
            fallback_client = InferenceClient(api_key=HF_TOKEN)
            response = fallback_client.chat_completion(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e2:
            return f"⚠️ API Error: {str(e)} | Fallback: {str(e2)}"


def call_gemini_with_file(prompt: str, file_path: str) -> str:
    """
    Extract text from file, then send to DeepSeek.
    DeepSeek doesn't support direct file upload like Gemini.
    """
    content = ""
    
    try:
        if file_path.lower().endswith(".pdf"):
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content += (page.extract_text() or "") + "\n"
        else:
            # Text/CSV files
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception as e:
        content = f"[Could not extract text: {str(e)}]"

    # Combine prompt + document content
    full_prompt = f"{prompt}\n\nDOCUMENT CONTENT:\n{content[:8000]}"
    return call_gemini(full_prompt)