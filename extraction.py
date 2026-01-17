import json  
from typing import Any  
from pydantic import BaseModel, Field, field_validator  
from azure_clients import client  
from config import SETTINGS  
  
class Medication(BaseModel):  
    mention: str  
    normalized_name_hint: str | None = None  
    start_days_ago: int | None = Field(default=None, description="Integer days before call when started. 0=today.")  
    change_days_ago: int | None = Field(default=None, description="If dose change happened, days ago.")  
    dose: str | None = None  
    frequency: str | None = None  
  
class Symptom(BaseModel):  
    text: str  
    onset_days_ago: int | None = None  
    severity: str | None = None  
    negated: bool = False  
    quote: str | None = None  
  
class RedFlag(BaseModel):  
    text: str  
    quote: str | None = None  
  
class MissingInfo(BaseModel):  
    field: str | None = None  
    question: str  
  
class ExtractedFacts(BaseModel):  
    medications: list[Medication] = []  
    symptoms: list[Symptom] = []  
    conditions: list[str] = []  
    risk_factors: list[str] = []  
    red_flags: list[RedFlag] = []  
    missing_info: list[MissingInfo] = []  

    @field_validator("red_flags", mode="before")  
    @classmethod  
    def coerce_red_flags(cls, v: Any):  
        if v is None:  
            return []  
        if isinstance(v, list):  
            out = []  
            for item in v:  
                if isinstance(item, str):  
                    out.append({"text": item})  
                else:  
                    out.append(item)  
            return out  
        return v  
  
    @field_validator("missing_info", mode="before")  
    @classmethod  
    def coerce_missing_info(cls, v: Any):  
        if v is None:  
            return []  
        if isinstance(v, list):  
            out = []  
            for item in v:  
                if isinstance(item, str):  
                    out.append({"question": item})  
                else:  
                    out.append(item)  
            return out  
        return v  
    
    @field_validator("conditions", "risk_factors", mode="before")  
    @classmethod  
    def coerce_str_list(cls, v: Any):  
        if v is None:  
            return []  
        if isinstance(v, str):  
            return [v]  
        if isinstance(v, dict):  
            t = v.get("text") or v.get("name")  
            return [t] if t else []  
        if isinstance(v, list):  
            out = []  
            for item in v:  
                if isinstance(item, str):  
                    out.append(item)  
                elif isinstance(item, dict):  
                    t = item.get("text") or item.get("name")  
                    if t:  
                        out.append(t)  
            return out  
        return []  
  
SYSTEM = """Extract structured facts from a nurse-patient call.  
Return ONLY JSON. Do NOT diagnose. Do NOT claim causality.  
  
You MUST:  
- Identify meds and symptoms.  
- Mark negated symptoms.  
- Convert relative time into integer days_ago when possible (e.g., "yesterday"=1, "last week"=7).  
- red_flags MUST be a list of objects: [{"text":"...", "quote":"..."}]  
- missing_info MUST be a list of objects: [{"field":"...", "question":"..."}]  
"""  
  
def _parse_json_strict(s: str):  
    s = s.strip()  
    if s.startswith("```"):  
        s = s.strip("`")  
        s = s[s.find("\n")+1:] if "\n" in s else s  
    return json.loads(s)  
  
def extract_facts(attributed_transcript_text: str) -> ExtractedFacts:  
    schema_example = {  
        "medications": [{"mention":"lisinopril", "normalized_name_hint":"lisinopril", "start_days_ago":3, "change_days_ago":None, "dose":"10 mg", "frequency":"once daily"}],  
        "symptoms": [{"text":"lips swollen", "onset_days_ago":1, "severity":"moderate", "negated":False, "quote":"Since yesterday my lips feel swollen"}],  
        "conditions": [],  
        "risk_factors": [],  
        "red_flags": [{"text":"throat tightness", "quote":"my throat feels tight"}],  
        "missing_info": [{"field":"symptoms[0].onset_days_ago", "question":"When did this start (how many days ago)?"}]  
    }  
  
    resp = client.chat.completions.create(  
        model=SETTINGS.AZURE_LLM_DEPLOYMENT,  
        messages=[  
            {"role":"system", "content": SYSTEM},  
            {"role":"user", "content": json.dumps({  
                "transcript": attributed_transcript_text,  
                "output_schema_example": schema_example  
            })}  
        ],  
        temperature=0  
    )  
    raw = resp.choices[0].message.content  
    data = _parse_json_strict(raw)  
    return ExtractedFacts.model_validate(data)  