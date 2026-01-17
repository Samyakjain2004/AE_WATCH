import os  
from dataclasses import dataclass  
from dotenv import load_dotenv  
  
load_dotenv()  
  
@dataclass  
class Settings:  
    AZURE_OPENAI_ENDPOINT: str = os.environ["AZURE_OPENAI_ENDPOINT"]  
    AZURE_OPENAI_API_KEY: str = os.environ["AZURE_OPENAI_API_KEY"]  
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")  
  
    AZURE_TRANSCRIBE_DEPLOYMENT: str = os.getenv("AZURE_TRANSCRIBE_DEPLOYMENT", "gpt-4o-transcribe")  
    AZURE_LLM_DEPLOYMENT: str = os.getenv("AZURE_LLM_DEPLOYMENT", "gpt-5.2")  
  
    OPENFDA_API_KEY: str | None = os.getenv("OPENFDA_API_KEY")  
  
    FAERS_START: str = os.getenv("FAERS_START", "20210101")  
    FAERS_END: str = os.getenv("FAERS_END", "20251231")  
  
    OPENFDA_BASE: str = "https://api.fda.gov/drug/event.json"  
  
SETTINGS = Settings()  