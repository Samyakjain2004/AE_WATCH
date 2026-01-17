from __future__ import annotations  
  
import re  
from typing import Any, Dict, List, Optional  
  
# ---------- small helpers ----------  
def _clean(s: str) -> str:  
    s = (s or "").lower()  
    s = re.sub(r"[\r\n\t]+", " ", s)  
    s = re.sub(r"\s+", " ", s).strip()  
    return s  
  
def _shorten(s: Optional[str], n: int = 280) -> Optional[str]:  
    if not s:  
        return None  
    s = s.strip()  
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"  
  
def _first_sentence(s: Optional[str]) -> Optional[str]:  
    if not s:  
        return None  
    s = s.strip()  
    parts = re.split(r"(?<=[.!?])\s+", s, maxsplit=1)  
    return parts[0].strip() if parts else s  
  
# ---------- extractors aligned with your pipeline ----------  
def extract_transcript(out: Dict[str, Any]) -> str:  
    rt = out.get("raw_transcript")  
    if isinstance(rt, str) and rt.strip():  
        return rt.strip()  
    at = out.get("attributed_transcript") or {}  
    turns = at.get("turns") or []  
    if isinstance(turns, list) and turns:  
        lines = []  
        for t in turns:  
            if isinstance(t, dict) and t.get("text"):  
                lines.append(f"{(t.get('speaker') or 'speaker').upper()}: {t['text'].strip()}")  
        return "\n".join(lines)  
    return ""  
  
def extract_facts(out: Dict[str, Any]) -> Dict[str, Any]:  
    facts = out.get("extracted_facts") or {}  
    meds = facts.get("medications") or []  
    sx_all = facts.get("symptoms") or []  
    red_flags = facts.get("red_flags") or []  
    missing_info = facts.get("missing_info") or []  
  
    symptoms_present = []  
    symptoms_negated = []  
    if isinstance(sx_all, list):  
        for s in sx_all:  
            if not isinstance(s, dict):  
                continue  
            txt = s.get("text")  
            if not isinstance(txt, str) or not txt.strip():  
                continue  
            if s.get("negated") is True:  
                symptoms_negated.append(txt.strip())  
            else:  
                symptoms_present.append(txt.strip())  
  
    return {  
        "medications": [m for m in meds if isinstance(m, dict)],  
        "symptoms_present": symptoms_present,  
        "symptoms_negated": symptoms_negated,  
        "red_flags": [r for r in red_flags if isinstance(r, dict)],  
        "missing_info_questions": [mi.get("question") for mi in missing_info if isinstance(mi, dict) and isinstance(mi.get("question"), str)],  
    }  
  
def top_signals(out: Dict[str, Any], k: int = 5) -> List[Dict[str, Any]]:  
    flags = out.get("flags") or []  
    if not isinstance(flags, list):  
        return []  
    ae = [f for f in flags if isinstance(f, dict) and f.get("type") == "possible_ae_occurring"]  
    # sort by urgency then score  
    rank = {"routine": 1, "monitor": 2, "urgent": 3, "emergent": 4}  
    ae.sort(key=lambda f: (-rank.get((f.get("urgency") or "").lower(), 0), -(f.get("score") or 0)))  
    # remove obvious coding noise  
    out_ae = []  
    for f in ae:  
        if _clean(f.get("event_meddra_pt") or "") == "death":  
            # your own coding_assistant already says it's mismapped  
            continue  
        out_ae.append({  
            "drug": f.get("drug"),  
            "event_meddra_pt": f.get("event_meddra_pt"),  
            "symptom": f.get("symptom"),  
            "urgency": f.get("urgency"),  
            "score": f.get("score"),  
            "evidence_quote": f.get("symptom_quote"),  
        })  
        if len(out_ae) >= k:  
            break  
    return out_ae  
  
# ---------- label compression (no raw label dumping to LLM) ----------  
def compress_drug_labels(out: Dict[str, Any]) -> List[Dict[str, Any]]:  
    labels = out.get("drug_labels") or []  
    if isinstance(labels, dict):  
        labels = [labels]  
    if not isinstance(labels, list):  
        return []  
  
    transcript = _clean(extract_transcript(out))  
    facts = extract_facts(out)  
    reported = set(_clean(s) for s in facts["symptoms_present"])  
    negated = set(_clean(s) for s in facts["symptoms_negated"])  
  
    # small mapping so “throat tightness/lip swelling” maps to “angioedema”  
    symptom_to_keywords = {  
        "lip swelling": ["angioedema", "swelling", "lips", "tongue"],  
        "throat tightness": ["angioedema", "laryngeal", "glottis", "tongue", "throat"],  
        "shortness of breath": ["dyspnea", "dyspnoea", "wheezing", "respiratory distress"],  
        "rash": ["rash", "urticaria", "hives"],  
        "hives": ["urticaria", "hives", "rash"],  
    }  
  
    pregnancy_terms = ["pregnan", "pregnant", "fetal", "fetus", "trying to conceive"]  
    pregnancy_relevant = any(t in transcript for t in pregnancy_terms)  
  
    out_labels = []  
    for lbl in labels:  
        if not isinstance(lbl, dict):  
            continue  
  
        drug = lbl.get("drug")  
        adverse = lbl.get("adverse_reactions") or ""  
        contra = lbl.get("contraindications") or ""  
        boxed = lbl.get("boxed_warning") or ""  
  
        # parse "dizziness (7.5%)" style common adverse reactions  
        common = []  
        for m in re.findall(r"([A-Za-z][A-Za-z\s/-]+?)\s*$(\d+(?:\.\d+)?)%$", adverse):  
            term = m[0].strip().lower()  
            if term and term not in common:  
                common.append(term)  
  
        # build candidate effects list for the LLM to classify  
        candidates = set(common)  
  
        # add special “serious” candidates if label mentions them  
        blob = _clean(" ".join([adverse, contra]))  
        if "angioedema" in blob:  
            candidates.add("angioedema")  
        if "hypotension" in blob:  
            candidates.add("hypotension")  
        if "syncope" in blob:  
            candidates.add("syncope")  
        if "dyspnea" in blob or "dyspnoea" in blob:  
            candidates.add("dyspnea")  
  
        # add any keyword candidates derived from reported/negated symptoms  
        for sx in list(reported | negated):  
            for kw in symptom_to_keywords.get(sx, []):  
                candidates.add(_clean(kw))  
  
        out_labels.append({  
            "drug": drug,  
            "rxcui": lbl.get("rxcui"),  
            "label_url": lbl.get("label_url"),  
            # only include boxed warning if pregnancy is actually relevant to transcript  
            #"boxed_warning": _first_sentence(boxed) if (boxed and pregnancy_relevant) else None,  
            # keep contraindications short (LLM can use if relevant)  
            #"contraindications_hint": _shorten(_first_sentence(contra), 260) if contra else None,  
            # the actual “effects” list to classify  
            "effect_candidates": sorted([c for c in candidates if c])[:40],  
            # note possible mismatch (your example label includes HCTZ)  
            "label_may_not_match_exact_product": ("hydrochlorothiazide" in _clean(drug or "")),  
        })  
  
    return out_labels  
  
# ---------- LLM prompt + schema ----------  
FINAL_JSON_SCHEMA = {  
    "name": "final_answer_schema",  
    "schema": {  
        "type": "object",  
        "additionalProperties": False,  
        "properties": {  
            "case_summary": {"type": "string"},  
            "triage": {"type": "string"},  
            "suspected_adverse_events": {  
                "type": "array",  
                "items": {  
                    "type": "object",  
                    "additionalProperties": False,  
                    "properties": {  
                        "event": {"type": "string"},  
                        "drug": {"type": "string"},  
                        "urgency": {"type": "string"},  
                        "evidence": {"type": "array", "items": {"type": "string"}}  
                    },  
                    "required": ["event", "drug", "urgency", "evidence"]  
                }  
            },  
            "label_alignment": {  
                "type": "object",  
                "additionalProperties": False,  
                "properties": {  
                    "happened_or_suspected": {  
                        "type": "array",  
                        "items": {"type": "object",  
                                  "additionalProperties": False,  
                                  "properties": {  
                                      "effect": {"type": "string"},  
                                      "why": {"type": "string"},  
                                      "evidence": {"type": "array", "items": {"type": "string"}}  
                                  },  
                                  "required": ["effect", "why", "evidence"]}  
                    },  
                    "can_happen_but_not_happened": {  
                        "type": "array",  
                        "items": {"type": "object",  
                                  "additionalProperties": False,  
                                  "properties": {  
                                      "effect": {"type": "string"},  
                                      "why": {"type": "string"}  
                                  },  
                                  "required": ["effect", "why"]}  
                    },  
                    "no_possibility_of_happening": {  
                        "type": "array",  
                        "items": {"type": "object",  
                                  "additionalProperties": False,  
                                  "properties": {  
                                      "effect": {"type": "string"},  
                                      "why": {"type": "string"},  
                                      "evidence": {"type": "array", "items": {"type": "string"}}  
                                  },  
                                  "required": ["effect", "why", "evidence"]}  
                    }  
                },  
                "required": ["happened_or_suspected", "can_happen_but_not_happened", "no_possibility_of_happening"]  
            },  
            "follow_up_questions": {"type": "array", "items": {"type": "string"}},  
            "notes": {"type": "array", "items": {"type": "string"}}  
        },  
        "required": ["case_summary", "triage", "suspected_adverse_events", "label_alignment", "follow_up_questions", "notes"]  
    }  
}  
  
SYSTEM_PROMPT = """You are generating the final JSON answer for a medication safety triage pipeline.  
  
Rules:  
- Use ONLY the provided transcript-derived facts/signals; do not invent.  
- Use drug label information ONLY by aligning it to transcript facts.  
- For label_alignment:  
  - happened_or_suspected: effects that match reported symptoms or high-confidence AE signals.  
  - can_happen_but_not_happened: label-listed effects that are plausible but not mentioned/observed in this call.  
  - no_possibility_of_happening: effects that are explicitly negated in the transcript (e.g., "no rash") or clearly not applicable given transcript context (e.g., pregnancy-only warnings when pregnancy not mentioned).  
- If label_may_not_match_exact_product is true, add a note about possible label mismatch.  
Return ONLY valid JSON matching the schema.  
"""  
  
def build_final_llm_input(out: Dict[str, Any]) -> Dict[str, Any]:  
    facts = extract_facts(out)  
    creative = out.get("creative") or {}  
    case_summary = ((creative.get("case_narrative") or {}).get("summary")) if isinstance(creative, dict) else None  
    triage = ((creative.get("patient_script") or {}).get("triage")) if isinstance(creative, dict) else None  
  
    return {  
        "transcript": extract_transcript(out),  
        "facts": facts,  
        "top_signals": top_signals(out, k=5),  
        "case_summary_from_pipeline": case_summary,  
        "triage_from_pipeline": triage,  
        "drug_labels_compact": compress_drug_labels(out),  
    }  
  
# ---------- OpenAI call (Responses API) ----------  
# ---------- OpenAI call (Responses API with fallback) ----------  
def generate_final_answer_json(out: Dict[str, Any], client, model: str = "gpt-4.1-mini") -> Dict[str, Any]:  
    import json  
    import re  
  
    llm_input = build_final_llm_input(out)  
    user_text = json.dumps(llm_input, ensure_ascii=False)  
  
    # 1) Try Responses API + json_schema (newer SDKs)  
    try:  
        resp = client.responses.create(  
            model=model,  
            input=[  
                {"role": "system", "content": SYSTEM_PROMPT},  
                {"role": "user", "content": user_text},  
            ],  
            response_format={"type": "json_schema", "json_schema": FINAL_JSON_SCHEMA},  
        )  
        # Newer SDKs provide parsed output directly  
        if hasattr(resp, "output_parsed") and resp.output_parsed is not None:  
            return resp.output_parsed  
  
        # If parsed output not available, parse text  
        text = getattr(resp, "output_text", None) or ""  
        return json.loads(text)  
  
    except TypeError:  
        # Your SDK error: Responses.create() got an unexpected keyword argument 'response_format'  
        pass  
  
    # 2) Fallback: Chat Completions (older SDKs)  
    messages = [  
        {"role": "system", "content": SYSTEM_PROMPT + "\nReturn ONLY JSON. No markdown. No extra text."},  
        {"role": "user", "content": user_text},  
    ]  
  
    try:  
        resp = client.chat.completions.create(  
            model=model,  
            messages=messages,  
            temperature=0,  
            response_format={"type": "json_object"},  
        )  
        text = resp.choices[0].message.content or ""  
        return json.loads(text)  
    except TypeError:  
        # If this SDK also doesn't support response_format here  
        resp = client.chat.completions.create(  
            model=model,  
            messages=messages,  
            temperature=0,  
        )  
        text = resp.choices[0].message.content or ""  
  
        try:  
            return json.loads(text)  
        except json.JSONDecodeError:  
            m = re.search(r"\{.*\}", text, flags=re.S)  
            if not m:  
                raise  
            return json.loads(m.group(0))  