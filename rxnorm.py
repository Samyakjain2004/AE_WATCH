import os, time, random  
import requests  
from cache import CACHE  
  
RXNAV_BASE = "https://rxnav.nlm.nih.gov/REST"  
RXNORM_DISABLE = os.getenv("RXNORM_DISABLE", "0") == "1"  
  
def _get_json(url: str, params: dict | None = None, timeout=20) -> dict:  
    headers = {  
        "Accept": "application/json",  
        "User-Agent": "ae-flagger/0.1 (+https://example.local)"  
    }  
  
    for attempt in range(5):  
        try:  
            r = requests.get(url, params=params, headers=headers, timeout=timeout)  
            # Retry on transient errors  
            if r.status_code in (429, 500, 502, 503, 504):  
                time.sleep((2 ** attempt) + random.random())  
                continue  
  
            if r.status_code != 200:  
                return {}  
  
            try:  
                return r.json()  
            except Exception:  
                # Non-JSON body (HTML, empty, proxy error, etc.)  
                time.sleep((2 ** attempt) + random.random())  
                continue  
  
        except requests.RequestException:  
            time.sleep((2 ** attempt) + random.random())  
            continue  
  
    return {}  
  
def rxnorm_approximate(term: str, max_entries=5):  
    key = f"RXNAV_APPROX::{term}"  
    cached = CACHE.get(key)  
    if cached is not None:  
        return cached  
    url = f"{RXNAV_BASE}/approximateTerm.json"  
    data = _get_json(url, params={"term": term, "maxEntries": max_entries})  
    CACHE.set(key, data, ttl_sec=7 * 24 * 3600)  
    return data  
  
def rxnorm_rxcui_props(rxcui: str):  
    key = f"RXNAV_PROPS::{rxcui}"  
    cached = CACHE.get(key)  
    if cached is not None:  
        return cached  
    url = f"{RXNAV_BASE}/rxcui/{rxcui}/properties.json"  
    data = _get_json(url)  
    CACHE.set(key, data, ttl_sec=7 * 24 * 3600)  
    return data  
  
def rxnorm_related(rxcui: str):  
    key = f"RXNAV_RELATED::{rxcui}"  
    cached = CACHE.get(key)  
    if cached is not None:  
        return cached  
    url = f"{RXNAV_BASE}/rxcui/{rxcui}/related.json"  
    params = {"tty": "BN+IN+MIN+PIN+SBD+SCD"}  
    data = _get_json(url, params=params)  
    CACHE.set(key, data, ttl_sec=7 * 24 * 3600)  
    return data  
  
def normalize_drug(term: str) -> dict:  
    # Hard fallback: run without RxNorm (useful behind proxies / offline)  
    canon = " ".join((term or "").strip().upper().split())  
    if RXNORM_DISABLE or not canon:  
        return {"input": term, "rxcui": None, "canonical": canon, "synonyms": [canon]}  
  
    approx = rxnorm_approximate(term)  
    candidates = approx.get("approximateGroup", {}).get("candidate", []) if isinstance(approx, dict) else []  
    if not candidates:  
        return {"input": term, "rxcui": None, "canonical": canon, "synonyms": [canon]}  
  
    rxcui = candidates[0].get("rxcui")  
    if not rxcui:  
        return {"input": term, "rxcui": None, "canonical": canon, "synonyms": [canon]}  
  
    props = rxnorm_rxcui_props(rxcui).get("properties", {})  
    name = (props.get("name") or canon).upper()  
  
    related = rxnorm_related(rxcui)  
    syn = set([name, canon])  
    groups = related.get("relatedGroup", {}).get("conceptGroup", []) if isinstance(related, dict) else []  
    for g in groups:  
        for c in g.get("conceptProperties", []) or []:  
            n = c.get("name")  
            if n:  
                syn.add(n.upper())  
  
    syn_list = list(sorted(syn))[:15]  
    return {"input": term, "rxcui": rxcui, "canonical": name, "synonyms": syn_list}  