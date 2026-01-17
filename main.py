# main.py  
import json  
import argparse  
  
from pipeline import run  
from reporting import summarize, to_human_text  
from drug_label import fetch_label  
  
  
def pick_drug_name(d: dict):  
    """Best-effort name to use for openFDA fallback search."""  
    for k in ("normalized_name", "drug", "mention", "text", "name", "generic_name", "brand_name"):  
        v = d.get(k)  
        if isinstance(v, str) and v.strip():  
            return v.strip()  
        if isinstance(v, list) and v and isinstance(v[0], str) and v[0].strip():  
            return v[0].strip()  
    return None  
  
  
if __name__ == "__main__":  
    p = argparse.ArgumentParser()  
    p.add_argument("--audio", type=str, default=None)  
    p.add_argument("--transcript", type=str, default=None)  
    p.add_argument("--k_prior", type=int, default=30)  
    args = p.parse_args()  
  
    if not args.audio and not args.transcript:  
        raise SystemExit("Provide --audio path OR --transcript text")  
  
    out = run(audio_path=args.audio, transcript=args.transcript, k_prior=args.k_prior)  
  
    # --- FETCH + ATTACH LABELS HERE ---  
    labels = []  
    dn = out.get("drug_normalization") or []  
    if isinstance(dn, dict):  # just in case it's not a list  
        dn = [dn]  
  
    for d in dn:  
        rxcui = d.get("rxcui")  
        drug_name = pick_drug_name(d)  
  
        if not rxcui:  
            labels.append({"drug_norm": d, "error": "missing rxcui"})  
            continue  
  
        try:  
            # fetch_label tries RxCUI first, then (if provided) falls back to name search  
            labels.append(fetch_label(str(rxcui), drug_name))  
        except Exception as e:  
            labels.append({"rxcui": str(rxcui), "drug": drug_name, "error": str(e)})  
  
    out["drug_labels"] = labels  
  
    summary = summarize(out)  
    out["summary"] = summary  
    out["triage_text"] = to_human_text(summary)  
  
    result_json = json.dumps(out, indent=2)  
  
    print(result_json)  
  
    with open("result.json", "w", encoding="utf-8") as f:  
        f.write(result_json) 
# main.py  
# import os  
# import json  
# import argparse  
# import json
# from pipeline import run  
# from reporting import summarize, to_human_text  
# from drug_label import fetch_label  
  
# from openai import AzureOpenAI  
# from final_generation import generate_final_answer_json  
  
  
# def pick_drug_name(d: dict):  
#     for k in ("normalized_name", "drug", "mention", "text", "name", "generic_name", "brand_name"):  
#         v = d.get(k)  
#         if isinstance(v, str) and v.strip():  
#             return v.strip()  
#         if isinstance(v, list) and v and isinstance(v[0], str) and v[0].strip():  
#             return v[0].strip()  
#     return None  
  
  
# def _require_env(name: str) -> str:  
#     v = os.environ.get(name)  
#     if not v:  
#         raise SystemExit(f"Missing environment variable: {name}")  
#     return v  
  
  
# if __name__ == "__main__":  
#     p = argparse.ArgumentParser()  
#     p.add_argument("--audio", type=str, default=None)  
#     p.add_argument("--transcript", type=str, default=None)  
#     p.add_argument("--k_prior", type=int, default=30)  
#     args = p.parse_args()  
  
#     if not args.audio and not args.transcript:  
#         raise SystemExit("Provide --audio path OR --transcript text")  
  
#     out = run(audio_path=args.audio, transcript=args.transcript, k_prior=args.k_prior)  
  
#     # --- FETCH + ATTACH LABELS HERE ---  
#     labels = []  
#     dn = out.get("drug_normalization") or []  
#     if isinstance(dn, dict):  
#         dn = [dn]  
  
#     for d in dn:  
#         rxcui = d.get("rxcui")  
#         drug_name = pick_drug_name(d)  
  
#         if not rxcui:  
#             labels.append({"drug_norm": d, "error": "missing rxcui"})  
#             continue  
  
#         try:  
#             labels.append(fetch_label(str(rxcui), drug_name))  
#         except Exception as e:  
#             labels.append({"rxcui": str(rxcui), "drug": drug_name, "error": str(e)})  
  
#     out["drug_labels"] = labels  
  
#     # Existing intermediate summary (optional)  
#     summary = summarize(out)  
#     out["summary"] = summary  
#     out["triage_text"] = to_human_text(summary)  
  
#     # ---- FINAL LLM CALL (Azure OpenAI) ----  
#     client = AzureOpenAI(  
#         api_key=_require_env("AZURE_OPENAI_API_KEY"),  
#         azure_endpoint=_require_env("AZURE_OPENAI_ENDPOINT"),  # e.g. https://<resource>.openai.azure.com  
#         api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),  
#     )  
  
#     # Use ONE of these env vars (preferred: AZURE_OPENAI_DEPLOYMENT)  
#     deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT") or os.environ.get("AZURE_LLM_DEPLOYMENT")  
#     if not deployment:  
#         raise SystemExit("Missing env var: AZURE_OPENAI_DEPLOYMENT (or AZURE_LLM_DEPLOYMENT)")  
  
#     out["final_answer"] = generate_final_answer_json(out, client, model=deployment)  
    
#     # with open("result.json", "w") as f:  
#     #     json.dump(out, f, indent=2)  
#     print(json.dumps(out, indent=2))  

#     result_json = json.dumps(out, indent=2)  
  
#     print(result_json)  
  
#     with open("result.json", "w", encoding="utf-8") as f:  
#         f.write(result_json) 