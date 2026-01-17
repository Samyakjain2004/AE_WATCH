# creative_reporter.py  
import json  
import re  
from typing import Any, Literal, Optional  
  
from pydantic import BaseModel, Field, ConfigDict  
  
from azure_clients import client  
from config import SETTINGS  
  
  
# ---------- Pydantic schema ----------  
  
class SymptomEvidence(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    symptom_text: str  
    meddra_pt: Optional[str] = None  
    onset_days_ago: Optional[int] = None  
    quote: Optional[str] = None  
  
  
class CaseNarrative(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    summary: str  
    timeline: list[str]  
    symptom_evidence: list[SymptomEvidence] = Field(default_factory=list)  
  
  
class FlagExplanationItem(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    flag_index: int  
    headline: str  
    rationale: str  
    evidence_quotes: list[str] = Field(default_factory=list)  
    uncertainties: list[str] = Field(default_factory=list)  
  
  
class WhyFlagged(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    items: list[FlagExplanationItem] = Field(default_factory=list)  
  
  
class FollowUpQuestions(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    questions: list[str]  
  
  
class PatientScript(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    triage: Literal["emergent", "urgent", "none"]  
    script: str  
    emergency_instructions_block: Optional[str] = None  
  
  
class CodingIssue(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    issue: str  
    evidence_quotes: list[str] = Field(default_factory=list)  
    needs_human_review: bool = True  
  
  
class MeddraSuggestion(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    symptom_text: str  
    current_meddra_pt: Optional[str] = None  
    suggested_meddra_pt: Optional[str] = None  
    note: str  
  
  
class CodingAssistant(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    meddra_suggestions: list[MeddraSuggestion] = Field(default_factory=list)  
    contradictions_or_negation_issues: list[CodingIssue] = Field(default_factory=list)  
    needs_human_review_tags: list[str] = Field(default_factory=list)  
  
  
class CreativePackage(BaseModel):  
    model_config = ConfigDict(extra="ignore")  
    case_narrative: CaseNarrative  
    why_flagged: WhyFlagged  
    follow_up_questions: FollowUpQuestions  
    patient_script: PatientScript  
    coding_assistant: CodingAssistant  
  
  
# ---------- helpers ----------  
  
def _load_json_relaxed(s: str) -> dict[str, Any]:  
    try:  
        return json.loads(s)  
    except Exception:  
        pass  
  
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)  
    if not m:  
        raise ValueError(f"Model did not return JSON. Raw:\n{s[:1000]}")  
    return json.loads(m.group(0))  
  
  
SYSTEM = """  
Return ONLY valid JSON (no markdown, no comments).  
  
Rules:  
- Use ONLY the provided input data. Do not invent symptoms, drugs, numbers, dates, diagnoses, or quotes.  
- Any evidence quote must be a verbatim substring of attributed_text.  
- patient_script.triage MUST equal the provided triage input.  
  
Required JSON shape:  
{  
  "case_narrative": {  
    "summary": "3–6 sentences",  
    "timeline": ["- ...", "- ..."],  
    "symptom_evidence": [  
      {"symptom_text":"...", "meddra_pt":"...", "onset_days_ago": 3, "quote":"..."}  
    ]  
  },  
  "why_flagged": {  
    "items": [  
      {  
        "flag_index": 0,  
        "headline": "...",  
        "rationale": "...",  
        "evidence_quotes": ["..."],  
        "uncertainties": ["..."]  
      }  
    ]  
  },  
  "follow_up_questions": {  
    "questions": ["...", "..."]  
  },  
  "patient_script": {  
    "triage": "emergent|urgent|none",  
    "script": "...",  
    "emergency_instructions_block": null  
  },  
  "coding_assistant": {  
    "meddra_suggestions": [  
      {"symptom_text":"...", "current_meddra_pt":"...", "suggested_meddra_pt":"...", "note":"..."}  
    ],  
    "contradictions_or_negation_issues": [  
      {"issue":"...", "evidence_quotes":["..."], "needs_human_review": true}  
    ],  
    "needs_human_review_tags": ["..."]  
  }  
}  
""".strip()  
  
  
def build_creative_package(  
    attributed_text: str,  
    facts_dump: dict[str, Any],  
    flags: list[dict[str, Any]],  
    symptom_pts: list[dict[str, Any]],  
    triage: Literal["emergent", "urgent", "none"],  
    temperature: float = 0.4,  
) -> CreativePackage:  
  
    payload = {  
        "attributed_text": attributed_text,  
        "facts": facts_dump,  
        "symptom_pts": symptom_pts,  
        "flags": flags,  
        "triage": triage,  
        "constraints": {  
            "no_new_facts": True,  
            "no_new_numbers": True,  
            "no_new_symptoms": True,  
            "quotes_must_be_verbatim": True,  
        },  
    }  
  
    # If your Azure deployment supports it, uncomment response_format for stricter JSON:  
    # response_format={"type": "json_object"}  
  
    r = client.chat.completions.create(  
        model=SETTINGS.AZURE_LLM_DEPLOYMENT,  
        messages=[  
            {"role": "system", "content": SYSTEM},  
            {"role": "user", "content": json.dumps(payload)},  
        ],  
        temperature=temperature,  
        # response_format={"type": "json_object"},  
    )  
  
    raw = r.choices[0].message.content or ""  
    data = _load_json_relaxed(raw)  
    out = CreativePackage.model_validate(data)  
  
    # best-effort quote verification  
    for se in out.case_narrative.symptom_evidence:  
        if se.quote and se.quote not in attributed_text:  
            se.quote = None  
  
    for item in out.why_flagged.items:  
        item.evidence_quotes = [q for q in item.evidence_quotes if q in attributed_text]  
  
    for ci in out.coding_assistant.contradictions_or_negation_issues:  
        ci.evidence_quotes = [q for q in ci.evidence_quotes if q in attributed_text]  
  
    # enforce triage consistency  
    out.patient_script.triage = triage  
  
    return out  