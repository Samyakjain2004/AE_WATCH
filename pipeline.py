import json  
from azure_clients import transcribe_audio  
from speaker_attribution import attribute_speakers, turns_to_text  
from extraction import extract_facts  
from rxnorm import normalize_drug  
from faers_signals import (  
    N_reports, top_events_for_drug, nD, nE, nDE, serious_frac, ror_ci, q  
)  
from scoring import timing_plausible, faers_tier, score  
  
from rapidfuzz import process, fuzz  
from azure_clients import client  
from config import SETTINGS  
from red_flagger import llm_red_flags
from creative_reporter import build_creative_package  
from scoring import timing_plausible, faers_tier, score, predict_probs  

RED_FLAG_PHRASES = [  
    "CHEST PAIN","SHORTNESS OF BREATH","THROAT TIGHT","THROAT SWELL",  
    "LIP SWELL","FACE SWELL","BLACK STOOL","VOMITING BLOOD","FAINTING",  
    "SUICIDAL","SEIZURE"  
]  
  
def build_drug_or_query(names: list[str]) -> str:  
    # openFDA: (field:"A" OR field:"B")  
    parts = [f'patient.drug.medicinalproduct.exact:{q(n)}' for n in names]  
    return " OR ".join(parts)  
  
def constrained_meddra_map(symptom_text: str, candidates: list[str]) -> str:  
    best = process.extractOne(symptom_text.upper(), candidates, scorer=fuzz.WRatio)  
    if best and best[1] >= 85:  
        return best[0]  
  
    # LLM pick from shortlist  
    resp = client.chat.completions.create(  
        model=SETTINGS.AZURE_LLM_DEPLOYMENT,  
        messages=[  
            {"role":"system","content":"Return ONLY JSON."},  
            {"role":"user","content": json.dumps({  
                "task":"Pick the best MedDRA PT from candidates for the symptom phrase.",  
                "symptom": symptom_text,  
                "candidates": candidates[:200],  
                "output": {"meddra_pt":"ONE_OF_CANDIDATES"}  
            })}  
        ],  
        temperature=0  
    )  
    pt = json.loads(resp.choices[0].message.content).get("meddra_pt")  
    return pt if pt in candidates else (best[0] if best else candidates[0])  
  
# def has_red_flag(facts) -> bool:  
#     sym = " ".join([s.text for s in facts.symptoms]).upper()  
#     rf = " ".join([(r.text if hasattr(r, "text") else str(r)) for r in facts.red_flags]).upper()  
#     joined = (sym + " " + rf).strip()  
  
#     return any(p in joined for p in RED_FLAG_PHRASES) or len(facts.red_flags) > 0  
def has_red_flag(attributed_text: str) -> bool:  
    rf = llm_red_flags(attributed_text)  
    return any(c in rf.categories for c in [  
        "airway_swelling_anaphylaxis",  
        "severe_bleeding",  
        "suicidality_self_harm",  
        "stroke_like_neuro_deficit",  
        "seizure_syncope",  
        "respiratory_distress",  
        "chest_pain_cardiac"  
    ])  
  
def run(audio_path=None, transcript=None, k_prior=30):  
    if transcript is None:  
        transcript = transcribe_audio(audio_path)  
  
    # speaker attribution  
    attributed = attribute_speakers(transcript)  
    attributed_text = turns_to_text(attributed) 
    red_flag_present = has_red_flag(attributed_text)   
  
    # fact extraction with timing fields  
    facts = extract_facts(attributed_text)  
  
    # RxNorm normalize + synonym expansion  
    drug_norms = []  
    for m in facts.medications:  
        dn = normalize_drug(m.mention if m.mention else (m.normalized_name_hint or ""))  
        dn["start_days_ago"] = m.start_days_ago  
        dn["change_days_ago"] = m.change_days_ago  
        drug_norms.append(dn)  
  
    # Build openFDA drug query per med using synonyms  
    drug_queries = []  
    for dn in drug_norms:  
        syn = dn["synonyms"]  
        drug_queries.append({  
            "canonical": dn["canonical"],  
            "synonyms": syn,  
            "query": build_drug_or_query(syn),  
            "start_days_ago": dn["start_days_ago"],  
            "change_days_ago": dn["change_days_ago"],  
        })  
  
    # Candidate MedDRA list: union of top events across drugs 
    # Candidate MedDRA list: union of top events across drugs  
    candidate_pts = set()  
    for dq in drug_queries:  
        for pt, _ in top_events_for_drug(dq["query"], k=100):  
            candidate_pts.add(pt)   

    # Add a small always-available safety set so mapping doesn't get forced into wrong PTs (e.g., stomatitis)  
    ALWAYS_CANDIDATE_PTS = {  
        "ANGIOEDEMA",  
        "THROAT TIGHTNESS",  
        "PHARYNGEAL SWELLING",  
        "LARYNGEAL EDEMA",  
        "TONGUE SWELLING",  
        "LIP SWELLING",  
        "SWELLING",  
        "DYSPNOEA",  
        "URTICARIA",  
        "RASH",  
    }  
    
    candidate_pts = sorted(candidate_pts | ALWAYS_CANDIDATE_PTS) if candidate_pts else sorted(ALWAYS_CANDIDATE_PTS)  
    
    # Map symptoms to MedDRA PTs  
    symptom_pts = []  
    for s in facts.symptoms:  
        if s.negated:  
            continue  
        pt = constrained_meddra_map(s.text, candidate_pts)  
        symptom_pts.append((s, pt)) 
  
    # Scoring  
    N = N_reports()  
    flags = []  
    for dq in drug_queries:  
        nD_ = nD(dq["query"])  
  
        # A) symptom-present candidates (occurred)  
        for s, pt in symptom_pts:  
            nE_ = nE(pt)  
            nDE_ = nDE(dq["query"], pt)  
            if nDE_ == 0:  
                continue  
            ser = serious_frac(dq["query"], pt)  
            ror, lcl, ucl = ror_ci(nDE_, nD_, nE_, N)  
            tier = faers_tier(lcl, nDE_)  
            t_ok = timing_plausible(dq["start_days_ago"], dq["change_days_ago"], s.onset_days_ago)  
            #sc, urg = score(symptom_present=True, timing_ok=t_ok, tier=tier, serious_fraction=ser) 
            sc, urg = score(symptom_present=True, timing_ok=t_ok, tier=tier, serious_fraction=ser)  
  
            p_ae_now, p_serious = predict_probs(  
                symptom_present=True,  
                timing_ok=t_ok,  
                tier=tier,  
                serious_fraction=ser,  
                ror_lcl95=lcl,  
                has_red_flag=red_flag_present,  
            )  
            
            flag = {  
                "type": "possible_ae_occurring",  
                "drug": dq["canonical"],  
                "event_meddra_pt": pt,  
                "symptom": s.text,  
                "symptom_quote": s.quote,  
                "symptom_onset_days_ago": s.onset_days_ago,  
                "drug_start_days_ago": dq["start_days_ago"],  
                "timing_plausible": t_ok,  
                "nDE": nDE_, "nD": nD_, "nE": nE_, "N": N,  
                "ror": ror, "ror_lcl95": lcl, "ror_ucl95": ucl,  
                "serious_fraction": ser,  
                "score": sc,  
                "urgency": urg,  
                "p_ae_now": p_ae_now,  
                "p_serious_24_72h": p_serious,  
            }  
            flags.append(flag)  
  
        # B) prior risk candidates (future)  
        for pt, cnt in top_events_for_drug(dq["query"], k=k_prior):  
            nE_ = nE(pt)  
            nDE_ = nDE(dq["query"], pt)  
            ser = serious_frac(dq["query"], pt)  
            ror, lcl, ucl = ror_ci(nDE_, nD_, nE_, N)  
            tier = faers_tier(lcl, nDE_)  
            sc, urg = score(symptom_present=False, timing_ok=None, tier=tier, serious_fraction=ser)  
            if urg == "none":  
                continue  
            flags.append({  
                "type": "elevated_risk",  
                "drug": dq["canonical"],  
                "event_meddra_pt": pt,  
                "nDE": nDE_, "nD": nD_, "nE": nE_, "N": N,  
                "ror": ror, "ror_lcl95": lcl, "ror_ucl95": ucl,  
                "serious_fraction": ser,  
                "score": sc,  
                "urgency": urg  
            })  
  
    # Red-flag override  
    if has_red_flag(attributed_text):  
        for f in flags:  
            if f["type"] == "possible_ae_occurring":  
                f["urgency"] = "emergent" 
  
    flags.sort(key=lambda x: (x["urgency"]!="emergent", x["urgency"]!="urgent", -x["score"], -x.get("ror_lcl95",0)))  
    
        # overall triage (deterministic)  
    if any(f["urgency"] == "emergent" for f in flags):  
        triage = "emergent"  
    elif any(f["urgency"] == "urgent" for f in flags):  
        triage = "urgent"  
    else:  
        triage = "none"  
  
    symptom_pts_dump = []  
    for s, pt in symptom_pts:  
        symptom_pts_dump.append({  
            "text": s.text,  
            "quote": s.quote,  
            "negated": s.negated,  
            "onset_days_ago": s.onset_days_ago,  
            "meddra_pt": pt  
        })  
  
    creative = build_creative_package(  
        attributed_text=attributed_text,  
        facts_dump=facts.model_dump(),  
        flags=flags[:25],                 # keep payload bounded  
        symptom_pts=symptom_pts_dump,  
        triage=triage,  
        temperature=0.4  
    )  
    
    creative = None  
    creative_error = None  
    
    try:  
        creative = build_creative_package(  
            attributed_text=attributed_text,  
            facts_dump=facts.model_dump(),  
            flags=flags[:25],  
            symptom_pts=symptom_pts_dump,  
            triage=triage,  
            temperature=0.4  
        )  
    except Exception as e:  
        creative_error = f"{type(e).__name__}: {e}"  
        print("creative generation failed:", creative_error)   
    
    return {  
    "raw_transcript": transcript,  
    "attributed_transcript": attributed.model_dump(),  
    "extracted_facts": facts.model_dump(),  
    "drug_normalization": drug_norms,  
    "flags": flags[:25],  
    "creative": creative.model_dump() if creative else None,  
    "creative_error": creative_error,  
    }   