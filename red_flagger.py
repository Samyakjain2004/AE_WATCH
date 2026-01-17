import json  
from pydantic import BaseModel  
from azure_clients import client  
from config import SETTINGS  
  
ALLOWED = [  
  "airway_swelling_anaphylaxis",  
  "respiratory_distress",  
  "chest_pain_cardiac",  
  "stroke_like_neuro_deficit",  
  "severe_bleeding",  
  "suicidality_self_harm",  
  "seizure_syncope",  
]  
  
class RedFlagOut(BaseModel):  
    categories: list[str]  
    evidence_quotes: list[str]  
  
SYSTEM = f"""  
Return ONLY JSON matching:  
{{"categories":[...], "evidence_quotes":[...]}}  
Choose categories ONLY from: {ALLOWED}  
Use categories only if positively supported (handle negation).  
"""  
  
def llm_red_flags(attributed_text) -> RedFlagOut:  
    if not isinstance(attributed_text, str):  
        # if it's a pydantic model, you can also do: attributed_text = attributed_text.model_dump()  
        attributed_text = json.dumps(attributed_text, default=str)  
    print("type(attributed_text) =", type(attributed_text))  
    r = client.chat.completions.create(  
        model=SETTINGS.AZURE_LLM_DEPLOYMENT,  
        messages=[  
            {"role": "system", "content": SYSTEM},  
            {"role": "user", "content": attributed_text},  
        ],  
        temperature=0,  
    )  
    data = json.loads(r.choices[0].message.content)  
    # enforce allowed set  
    data["categories"] = [c for c in data.get("categories", []) if c in ALLOWED]  
    return RedFlagOut.model_validate(data)  