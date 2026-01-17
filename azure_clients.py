from openai import AzureOpenAI  
from config import SETTINGS  
  
client = AzureOpenAI(  
    azure_endpoint=SETTINGS.AZURE_OPENAI_ENDPOINT,  
    api_key=SETTINGS.AZURE_OPENAI_API_KEY,  
    api_version=SETTINGS.AZURE_OPENAI_API_VERSION,  
)  
  
def transcribe_audio(audio_path: str) -> str:  
    # Azure OpenAI audio transcription  
    with open(audio_path, "rb") as f:  
        r = client.audio.transcriptions.create(  
            model=SETTINGS.AZURE_TRANSCRIBE_DEPLOYMENT,  
            file=f  
        )  
    return getattr(r, "text", str(r))  