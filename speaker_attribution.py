import json  
from pydantic import BaseModel  
from azure_clients import client  
from config import SETTINGS  
  
class Turn(BaseModel):  
    speaker: str  # "patient" | "nurse" | "other"  
    text: str  
  
class AttributedTranscript(BaseModel):  
    turns: list[Turn]  
  
SYSTEM = """You are a medical call transcript structurer.  
Split transcript into turns and label each turn speaker as patient or nurse.  
If unclear, use "other".  
  
Return ONLY JSON in EXACTLY this shape:  
{  
  "turns": [  
    {"speaker": "nurse", "text": "..."},  
    {"speaker": "patient", "text": "..."}  
  ]  
}  
"""  
  
def _parse_json_strict(s: str):  
    s = s.strip()  
    # handle accidental ```json ... ``` wrappers  
    if s.startswith("```"):  
        s = s.strip("`")  
        # sometimes begins with json\n{...}  
        s = s[s.find("\n")+1:] if "\n" in s else s  
    return json.loads(s)  
  
def attribute_speakers(transcript: str) -> AttributedTranscript:  
    resp = client.chat.completions.create(  
        model=SETTINGS.AZURE_LLM_DEPLOYMENT,  
        messages=[  
            {"role": "system", "content": SYSTEM},  
            {"role": "user", "content": json.dumps({"transcript": transcript})},  
        ],  
        temperature=0  
    )  
  
    raw = resp.choices[0].message.content  
    data = _parse_json_strict(raw)  
  
    # Accept both formats:  
    # - {"turns":[...]}  (preferred)  
    # - [...]           (LLM sometimes returns this)  
    if isinstance(data, list):  
        data = {"turns": data}  
  
    return AttributedTranscript.model_validate(data)  
  
def turns_to_text(at: AttributedTranscript) -> str:  
    return "\n".join([f"{t.speaker.upper()}: {t.text}" for t in at.turns])  