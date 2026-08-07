from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "config", "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "config", "token.json")