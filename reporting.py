# reporting.py  
from typing import Dict, Any  
  
URGENCY_RANK = {"emergent": 3, "urgent": 2, "monitor": 1, "none": 0}  
  
def summarize(out: Dict[str, Any], top_n:int=3) -> Dict[str, Any]:  
    flags = out.get("flags", [])  
    occurred = [f for f in flags if f.get("type") == "possible_ae_occurring"]  
    risks = [f for f in flags if f.get("type") == "elevated_risk"]  
  
    # overall triage = max urgency among occurred AEs  
    overall = "none"  
    for f in occurred:  
        u = f.get("urgency", "none")  
        if URGENCY_RANK.get(u, 0) > URGENCY_RANK[overall]:  
            overall = u  
  
    facts = out.get("extracted_facts", {})  
    return {  
        "triage": overall,  
        "suspected_adverse_events": [  
            {  
                "drug": f.get("drug"),  
                "event_meddra_pt": f.get("event_meddra_pt"),  
                "evidence": {  
                    "symptom": f.get("symptom"),  
                    "quote": f.get("symptom_quote"),  
                    "timing_plausible": f.get("timing_plausible"),  
                },  
                "faers_signal": {  
                    "ror_lcl95": f.get("ror_lcl95"),  
                    "nDE": f.get("nDE"),  
                    "serious_fraction": f.get("serious_fraction"),  
                },  
                "prediction": {  
                    "p_ae_now": f.get("p_ae_now"),  
                    "p_serious_24_72h": f.get("p_serious_24_72h"),  
                },  
                "urgency": f.get("urgency"),  
            }  
            for f in occurred[:top_n]  
        ],  
        "elevated_risks_to_monitor": [  
            {  
                "drug": r.get("drug"),  
                "event_meddra_pt": r.get("event_meddra_pt"),  
                "prediction": {  
                    "p_ae_now": r.get("p_ae_now"),  
                    "p_serious_24_72h": r.get("p_serious_24_72h"),  
                },  
                "urgency": r.get("urgency"),  
            }  
            for r in risks[:top_n]  
        ],  
        "follow_up_questions": facts.get("missing_info", [])[:8],  
        "safety_note": "Flags indicate possible adverse events based on conversation + FAERS disproportionality; not a diagnosis and does not prove causality."  
    }  
  
def to_human_text(summary: Dict[str, Any]) -> str:  
    lines = [f"TRIAGE: {summary['triage'].upper()}"]  
    for i, ae in enumerate(summary["suspected_adverse_events"], 1):  
        lines += [  
            f"- Suspected AE #{i}: {ae['event_meddra_pt']} (drug: {ae['drug']}, urgency: {ae['urgency']})",  
            f"  Evidence: {ae['evidence']['symptom']} | quote: {ae['evidence']['quote']}",  
            f"  Timing plausible: {ae['evidence']['timing_plausible']}",  
            f"  FAERS: ROR LCL95={ae['faers_signal']['ror_lcl95']:.2f} nDE={ae['faers_signal']['nDE']} serious_frac={ae['faers_signal']['serious_fraction']:.2f}",  
        ]  
    if summary["follow_up_questions"]:  
        lines.append("FOLLOW-UP QUESTIONS:")  
        for q in summary["follow_up_questions"]:  
            lines.append(f"  - {q.get('question')}")  
    lines.append(summary["safety_note"])  
    return "\n".join(lines)  

# reporting.py  
# reporting.py  
# from __future__ import annotations  
  
# import re  
# from typing import Any, Dict, List, Optional  
  
  
# URGENCY_RANK = {"routine": 1, "monitor": 2, "urgent": 3, "emergent": 4}  
  
  
# def _as_list(x):  
#     if x is None:  
#         return []  
#     return x if isinstance(x, list) else [x]  
  
  
# def _clean(s: str) -> str:  
#     s = (s or "").lower()  
#     s = re.sub(r"[\r\n\t]+", " ", s)  
#     s = re.sub(r"\s+", " ", s).strip()  
#     return s  
  
  
# def _shorten(s: Optional[str], n: int = 260) -> Optional[str]:  
#     if not s:  
#         return None  
#     s = s.strip()  
#     return s if len(s) <= n else s[: n - 1].rstrip() + "…"  
  
  
# def _first_sentence(s: Optional[str]) -> Optional[str]:  
#     if not s:  
#         return None  
#     s = s.strip()  
#     parts = re.split(r"(?<=[.!?])\s+", s, maxsplit=1)  
#     return parts[0].strip() if parts else s  
  
  
# # -------------------------  
# # Extractors aligned to your pipeline schema  
# # -------------------------  
  
# def extract_transcript(out: Dict[str, Any]) -> str:  
#     # Prefer raw transcript (your pipeline provides this)  
#     rt = out.get("raw_transcript")  
#     if isinstance(rt, str) and rt.strip():  
#         return rt.strip()  
  
#     # Otherwise, reconstruct from attributed turns if present  
#     at = out.get("attributed_transcript") or {}  
#     turns = at.get("turns")  
#     if isinstance(turns, list) and turns:  
#         lines = []  
#         for t in turns:  
#             if not isinstance(t, dict):  
#                 continue  
#             spk = (t.get("speaker") or "speaker").upper()  
#             txt = (t.get("text") or "").strip()  
#             if txt:  
#                 lines.append(f"{spk}: {txt}")  
#         if lines:  
#             return "\n".join(lines)  
  
#     # Fallback: older keys  
#     for k in ("transcript", "text", "asr_text"):  
#         v = out.get(k)  
#         if isinstance(v, str) and v.strip():  
#             return v.strip()  
  
#     return ""  
  
  
# def extract_medications(out: Dict[str, Any]) -> List[Dict[str, Any]]:  
#     facts = out.get("extracted_facts") or {}  
#     meds = facts.get("medications") or []  
#     if isinstance(meds, list) and meds:  
#         return [m for m in meds if isinstance(m, dict)]  
  
#     # fallback  
#     dn = out.get("drug_normalization") or []  
#     if isinstance(dn, dict):  
#         dn = [dn]  
#     return [d for d in dn if isinstance(d, dict)]  
  
  
# def extract_symptom_objs(out: Dict[str, Any]) -> List[Dict[str, Any]]:  
#     facts = out.get("extracted_facts") or {}  
#     sx = facts.get("symptoms") or []  
#     if not isinstance(sx, list):  
#         return []  
  
#     # Ignore negated symptoms  
#     out_sx = []  
#     for s in sx:  
#         if not isinstance(s, dict):  
#             continue  
#         if s.get("negated") is True:  
#             continue  
#         txt = s.get("text")  
#         if isinstance(txt, str) and txt.strip():  
#             out_sx.append(s)  
#     return out_sx  
  
  
# def extract_symptom_texts(out: Dict[str, Any]) -> List[str]:  
#     return [s["text"].strip() for s in extract_symptom_objs(out) if isinstance(s.get("text"), str)]  
  
  
# def extract_red_flags(out: Dict[str, Any]) -> List[Dict[str, Any]]:  
#     facts = out.get("extracted_facts") or {}  
#     rf = facts.get("red_flags") or []  
#     return [r for r in rf if isinstance(r, dict)] if isinstance(rf, list) else []  
  
  
# def extract_missing_info_questions(out: Dict[str, Any]) -> List[str]:  
#     # Prefer pipeline missing_info  
#     facts = out.get("extracted_facts") or {}  
#     mi = facts.get("missing_info") or []  
#     qs = []  
#     if isinstance(mi, list):  
#         for item in mi:  
#             if isinstance(item, dict) and isinstance(item.get("question"), str):  
#                 qs.append(item["question"].strip())  
  
#     # Fallback: creative follow-up questions  
#     cr = out.get("creative") or {}  
#     fu = ((cr.get("follow_up_questions") or {}).get("questions")) or []  
#     if isinstance(fu, list):  
#         for q in fu:  
#             if isinstance(q, str) and q.strip():  
#                 if q.strip() not in qs:  
#                     qs.append(q.strip())  
  
#     return qs  
  
  
# def extract_ae_flags(out: Dict[str, Any]) -> List[Dict[str, Any]]:  
#     flags = out.get("flags") or []  
#     if not isinstance(flags, list):  
#         return []  
#     ae = [f for f in flags if isinstance(f, dict) and f.get("type") == "possible_ae_occurring"]  
#     # sort by urgency rank then score  
#     def key(f):  
#         u = (f.get("urgency") or "routine").lower()  
#         return (-URGENCY_RANK.get(u, 0), -(f.get("score") or 0))  
#     return sorted(ae, key=key)  
  
  
# def compute_triage(out: Dict[str, Any]) -> str:  
#     # If creative already computed triage, use it  
#     cr = out.get("creative") or {}  
#     ps = cr.get("patient_script") or {}  
#     if isinstance(ps, dict) and isinstance(ps.get("triage"), str):  
#         return ps["triage"]  
  
#     # Else derive from AE flags  
#     triage = "routine"  
#     for f in extract_ae_flags(out):  
#         u = (f.get("urgency") or "").lower()  
#         if URGENCY_RANK.get(u, 0) > URGENCY_RANK.get(triage, 0):  
#             triage = u  
  
#     # Red flags present -> at least urgent (configurable)  
#     if extract_red_flags(out) and URGENCY_RANK.get(triage, 0) < URGENCY_RANK["urgent"]:  
#         triage = "urgent"  
  
#     return triage  
  
  
# # -------------------------  
# # Label matching aligned to AE use-case  
# # -------------------------  
  
# # Map common patient phrases to label/MedDRA-ish keywords  
# SYMPTOM_TO_LABEL_KEYWORDS = {  
#     "lip swelling": ["angioedema", "swelling"],  
#     "throat tightness": ["angioedema", "laryngeal", "tongue", "glottis"],  
#     "shortness of breath": ["dyspnea", "dyspnoea", "respiratory distress", "wheezing"],  
# }  
  
# # Normalize MedDRA spelling differences  
# MEDDRA_NORMALIZE = {  
#     "dyspnoea": "dyspnea",  
# }  
  
  
# def build_medication_safety(out: Dict[str, Any]) -> List[Dict[str, Any]]:  
#     labels = out.get("drug_labels") or []  
#     if isinstance(labels, dict):  
#         labels = [labels]  
#     if not isinstance(labels, list):  
#         return []  
  
#     symptom_texts = extract_symptom_texts(out)  
#     symptom_norm = [_clean(s) for s in symptom_texts]  
  
#     ae_flags = extract_ae_flags(out)  
#     meddra_pts = []  
#     for f in ae_flags:  
#         pt = f.get("event_meddra_pt")  
#         if isinstance(pt, str) and pt.strip():  
#             ptn = _clean(pt)  
#             ptn = MEDDRA_NORMALIZE.get(ptn, ptn)  
#             meddra_pts.append(ptn)  
  
#     out_items = []  
  
#     for lbl in labels:  
#         if not isinstance(lbl, dict):  
#             continue  
  
#         boxed = lbl.get("boxed_warning") or ""  
#         contra = lbl.get("contraindications") or ""  
#         warn = lbl.get("warnings_and_precautions") or ""  
#         inter = lbl.get("drug_interactions") or ""  
#         adv = lbl.get("adverse_reactions") or ""  
  
#         blob = _clean(" ".join([boxed, contra, warn, inter, adv]))  
  
#         matched_symptoms = []  
#         matched_keywords = []  
  
#         for sx in symptom_norm:  
#             # direct substring match  
#             if sx and sx in blob:  
#                 matched_symptoms.append(sx)  
  
#             # mapped keyword match (important for angioedema scenario)  
#             for kw in SYMPTOM_TO_LABEL_KEYWORDS.get(sx, []):  
#                 if kw in blob:  
#                     matched_keywords.append(f"{sx}→{kw}")  
  
#         matched_meddra = [pt for pt in meddra_pts if pt in blob]  
  
#         out_items.append({  
#             "drug": lbl.get("drug"),  
#             "rxcui": lbl.get("rxcui"),  
#             "label_url": lbl.get("label_url"),  
#             "boxed_warning_highlight": _first_sentence(boxed) if boxed else None,  
#             "contraindications_highlight": _shorten(_first_sentence(contra), 280) if contra else None,  
#             "adverse_reactions_mentions_angioedema": ("angioedema" in blob),  
#             "matched_symptoms_direct": matched_symptoms,  
#             "matched_symptoms_via_keywords": matched_keywords,  
#             "matched_meddra_pts": matched_meddra,  
#             "label_fetch_error": lbl.get("error"),  
#         })  
  
#     return out_items  
  
  
# # -------------------------  
# # Public API  
# # -------------------------  
  
# def summarize(out: Dict[str, Any]) -> Dict[str, Any]:  
#     cr = out.get("creative") or {}  
#     narrative = ((cr.get("case_narrative") or {}).get("summary")) if isinstance(cr, dict) else None  
  
#     summary: Dict[str, Any] = {  
#         "transcript": extract_transcript(out) or None,  
#         "medications": extract_medications(out),  
#         "symptoms": extract_symptom_objs(out),      # keep rich objects (onset, quote, severity)  
#         "red_flags": extract_red_flags(out),  
#         "possible_ae_flags": extract_ae_flags(out),  
#         "triage": compute_triage(out),  
#         "case_summary": narrative,  
#         "missing_info_questions": extract_missing_info_questions(out),  
#         "medication_safety": build_medication_safety(out),  # <-- uses drug_labels properly  
#     }  
#     return summary  
  
  
# def to_human_text(summary: Dict[str, Any]) -> str:  
#     lines: List[str] = []  
  
#     # Case summary (prefer creative narrative if available)  
#     if summary.get("case_summary"):  
#         lines.append("Case summary:")  
#         lines.append(summary["case_summary"].strip())  
#         lines.append("")  
#     else:  
#         # fallback: build from meds + symptoms  
#         meds = summary.get("medications") or []  
#         sx = summary.get("symptoms") or []  
#         if meds:  
#             m0 = meds[0]  
#             mname = m0.get("mention") or m0.get("canonical") or m0.get("input") or "medication"  
#             lines.append(f"Medication: {mname}")  
#         if sx:  
#             lines.append("Symptoms:")  
#             for s in sx:  
#                 txt = s.get("text")  
#                 q = s.get("quote")  
#                 if txt:  
#                     lines.append(f"- {txt}" + (f' (quote: "{q}")' if q else ""))  
#         lines.append("")  
  
#     # Triage / urgency  
#     triage = (summary.get("triage") or "routine").lower()  
#     lines.append(f"Triage: {triage}")  
  
#     # Use AE flags (these are already aligned to the transcript in your pipeline)  
#     ae_flags = summary.get("possible_ae_flags") or []  
#     if ae_flags:  
#         lines.append("")  
#         lines.append("Possible adverse event signals (from flags):")  
#         for f in ae_flags[:5]:  
#             drug = f.get("drug")  
#             pt = f.get("event_meddra_pt")  
#             sx = f.get("symptom")  
#             uq = f.get("urgency")  
#             quote = f.get("symptom_quote")  
#             lines.append(f"- {drug}: {pt} (symptom: {sx}, urgency: {uq})" + (f' | "{quote}"' if quote else ""))  
  
#     # Medication label corroboration (from openFDA label text)  
#     ms = summary.get("medication_safety") or []  
#     if ms:  
#         lines.append("")  
#         lines.append("Medication label context (openFDA/DailyMed):")  
#         for item in ms:  
#             drug = item.get("drug") or "(unknown)"  
#             lines.append(f"- {drug} (RxCUI: {item.get('rxcui')})")  
#             if item.get("boxed_warning_highlight"):  
#                 lines.append(f"  Boxed warning: {item['boxed_warning_highlight']}")  
#             if item.get("contraindications_highlight"):  
#                 lines.append(f"  Contraindications: {item['contraindications_highlight']}")  
#             if item.get("adverse_reactions_mentions_angioedema"):  
#                 lines.append("  Label mentions angioedema in adverse reactions.")  
#             if item.get("matched_symptoms_via_keywords"):  
#                 lines.append("  Symptom/keyword matches:")  
#                 for m in item["matched_symptoms_via_keywords"][:10]:  
#                     lines.append(f"  - {m}")  
#             if item.get("matched_meddra_pts"):  
#                 lines.append("  MedDRA PT matches in label text:")  
#                 for pt in item["matched_meddra_pts"][:10]:  
#                     lines.append(f"  - {pt}")  
#             if item.get("label_url"):  
#                 lines.append(f"  Label: {item['label_url']}")  
  
#     # Follow-up questions  
#     qs = summary.get("missing_info_questions") or []  
#     if qs:  
#         lines.append("")  
#         lines.append("Follow-up questions:")  
#         for q in qs:  
#             lines.append(f"- {q}")  
  
#     return "\n".join(lines)  